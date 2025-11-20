"""
MÓDULO DE FACTURAS - VISTAS Y LÓGICA DE NEGOCIO
================================================
Este módulo maneja toda la funcionalidad relacionada con facturas electrónicas:
- Creación de facturas con descuento automático de inventario
- Generación de PDF y XML para facturación electrónica
- Envío de correos a clientes
- Historial y búsqueda de facturas
- Búsqueda de productos por código de barras

Última actualización: 20/11/2025
"""

# === IMPORTS DE DJANGO ===
from django.shortcuts import render, get_object_or_404  # Renderizado y búsqueda de objetos
from django.http import JsonResponse, HttpResponse      # Respuesta que trae JSON y respuestas HTTP para manejo de solicitudes  
from django.core.mail import EmailMultiAlternatives     # Envío de correos con HTML y archivos adjuntos
from django.core.paginator import Paginator              # Paginación de resultados
from django.conf import settings                         # Configuración del proyecto
from datetime import date                                # Manejo de fechas

# === IMPORTS DE MODELOS ===
from .models import Factura, DetalleFactura             # Modelos de factura
from productos.models import Producto, Inventario        # Modelos de productos e inventario
from .services import enviar_a_intermediario             # Servicio de generación de CUFE

# === IMPORTS PARA PDF Y QR ===
from reportlab.pdfgen import canvas                      # Generación de PDF
from reportlab.lib.utils import ImageReader              # Manejo de imágenes en PDF
import qrcode                                            # Generación de códigos QR
import base64                                            # Codificación base64 para imágenes

# === OTROS IMPORTS ===
from io import BytesIO                                   # Manejo de archivos en memoria
from pathlib import Path                                 # Manejo moderno de rutas de archivos
import json, traceback, os, uuid                         # para manejo de arhivos 
from django.contrib.auth.decorators import login_required #Importa la validacion de login dependiendo con que roll tenga el usuario


"""
================================================================================
VISTA: CREAR FACTURA
================================================================================
Descripción:
    Maneja la creación completa de facturas electrónicas con las siguientes funcionalidades:
    1. Valida datos del cliente y productos
    2. Descuenta automáticamente del inventario
    3. Genera CUFE (Código Único de Facturación Electrónica)
    4. Envía correo al cliente con los datos de la factura
    5. Retorna URLs para descargar PDF y XML

Método HTTP: POST (creación), GET (renderiza formulario)
Ruta: /facturas/crear/

Flujo:
    1. Validar campos obligatorios (cliente, productos)
    2. Crear factura en base de datos
    3. Por cada producto:
       - Buscar en inventario por código de barras
       - Validar stock disponible
       - Descontar cantidad vendida
       - Crear detalle de factura
    4. Generar CUFE vía servicio intermediario
    5. Enviar correo al cliente
    6. Retornar respuesta JSON con URLs de descarga

Última actualización: 20/11/2025
================================================================================
"""
def crear_factura(request):
    if request.method == "POST":
        try:
            # Parsear datos JSON enviados desde el frontend
            data = json.loads(request.body)
            
            # === DEBUG: Imprimir datos recibidos ===
            print("=" * 80)
            print("DATOS RECIBIDOS EN EL BACKEND:")
            print(json.dumps(data, indent=2))
            print("=" * 80)

            # === VALIDACIÓN DE CAMPOS OBLIGATORIOS ===
            # Verificar que todos los campos requeridos estén presentes y no vacíos
            campos_obligatorios = ["nombre_receptor", "nit_receptor", "correo_cliente", "productos"]
            for campo in campos_obligatorios:
                if campo not in data or not data[campo]:
                    print(f"❌ FALTA EL CAMPO: {campo}")
                    print(f"   Valor recibido: {data.get(campo, 'NO EXISTE')}")
                    return JsonResponse({
                        "status": "error", 
                        "message": f"El campo '{campo}' es obligatorio."
                    }, status=400)

            # === VALIDACIÓN DE PRODUCTOS ===
            # Asegurar que hay al menos un producto en la factura
            if not isinstance(data["productos"], list) or len(data["productos"]) == 0:
                return JsonResponse({
                    "status": "error", 
                    "message": "Debe agregar al menos un producto."
                }, status=400)

            # === CREAR FACTURA PRINCIPAL ===
            # Se crea la factura con un CUFE temporal que luego será reemplazado
            # por el CUFE real generado por el intermediario de facturación
            factura = Factura.objects.create(
                nombre_receptor=data["nombre_receptor"],          # Nombre del cliente
                nit_receptor=data["nit_receptor"],                # NIT o documento del cliente
                correo_cliente=data["correo_cliente"],            # Email para enviar factura
                telefono=data.get("telefono", ""),                # Teléfono (opcional)
                direccion=data.get("direccion", ""),              # Dirección (opcional)
                fecha=date.today(),                               # Fecha de creación
                fecha_factura=date.today(),                       # Fecha de emisión
                metodo_pago_factura=data.get("metodo_pago_factura"),  # Efectivo, tarjeta, etc.
                sutotal_factura=data.get("sutotal_factura", 0),   # Suma sin IVA
                iva_total_factura=data.get("iva_total_factura", 0),  # Total IVA (19%)
                total_factura=data.get("total_factura", 0),       # Subtotal + IVA
                cufe_factura=f"TEMP-{uuid.uuid4()}"               # CUFE temporal único
            )

            # === DESCUENTO AUTOMÁTICO DE INVENTARIO ===
            # Por cada producto vendido, se descuenta del stock disponible
            for prod in data["productos"]:
                try:
                    # Extraer datos del producto desde el JSON
                    codigo = prod.get("codigo_barras", None)           # Código de barras único
                    cantidad_vendida = int(prod.get("cantidad", 0))    # Unidades vendidas
                    precio = float(prod.get("precio", 0))              # Precio unitario sin IVA
                    iva = float(prod.get("iva", 0))                    # IVA unitario (19%)
                    total = float(prod.get("total", 0))                # Total por producto

                    print(f"🔍 Procesando producto: {prod.get('nombre')}")
                    print(f"   Código de barras: '{codigo}'")
                    print(f"   Cantidad: {cantidad_vendida}")

                    # === VALIDAR CÓDIGO DE BARRAS ===
                    if not codigo:
                        factura.delete()  # Rollback: eliminar factura si falla
                        return JsonResponse({
                            "status": "error",
                            "message": "Falta el código de barras del producto."
                        }, status=400)

                    # === BUSCAR PRODUCTO EN INVENTARIO ===
                    # select_related optimiza la consulta trayendo el producto relacionado
                    inventario = Inventario.objects.select_related("producto").filter(
                        codigo_barras_inventario=codigo
                    ).first()

                    print(f"   ¿Se encontró en inventario? {inventario is not None}")
                    if inventario:
                        print(f"   Producto encontrado: {inventario.producto.nombre_producto}")
                        print(f"   Stock disponible: {inventario.stock_actual_inventario}")

                    # Si no existe el producto en inventario
                    if not inventario:
                        factura.delete()  # Rollback
                        print(f"❌ ERROR: No se encontró el producto con código {codigo}")
                        return JsonResponse({
                            "status": "error",
                            "message": f"No se encontró el producto con código {codigo}"
                        }, status=404)

                    # === VALIDAR STOCK DISPONIBLE ===
                    # Asegurar que hay suficiente stock antes de vender
                    if inventario.stock_actual_inventario < cantidad_vendida:
                        factura.delete()  # Rollback
                        return JsonResponse({
                            "status": "error",
                            "message": f"No hay suficiente stock para '{inventario.producto.nombre_producto}'. "
                                       f"Disponible: {inventario.stock_actual_inventario}"
                        }, status=400)

                    # === DESCONTAR STOCK ===
                    # Restar la cantidad vendida del inventario disponible
                    inventario.stock_actual_inventario -= cantidad_vendida
                    inventario.save()

                    # === CREAR DETALLE DE FACTURA ===
                    # Registrar cada producto vendido como una línea en la factura
                    DetalleFactura.objects.create(
                        factura=factura,                      # Relación con la factura principal
                        producto=inventario.producto,         # Instancia del modelo Producto
                        cantidad=cantidad_vendida,            # Unidades vendidas
                        precio=precio,                        # Precio unitario sin IVA
                        iva=iva,                              # IVA unitario (19%)
                        total=total                           # Total de la línea (precio+IVA)*cantidad
                    )

                except Exception as e:
                    # === MANEJO DE ERRORES POR PRODUCTO ===
                    # Si algo falla con un producto, eliminar toda la factura (rollback)
                    factura.delete()
                    print("Error procesando producto:", e)
                    return JsonResponse({
                        "status": "error", 
                        "message": f"Error procesando producto: {e}"
                    }, status=500)

            # === GENERAR CUFE REAL ===
            # Llamar al servicio intermediario para obtener el CUFE oficial
            # El CUFE es el código único de facturación electrónica requerido por la DIAN
            cufe = enviar_a_intermediario(factura)
            factura.cufe_factura = cufe
            factura.save()

            # === ENVIAR CORREO AL CLIENTE ===
            # Notificar al cliente por email con los datos de su factura, logos y PDF adjunto
            if factura.correo_cliente:
                try:
                    # Generar el PDF de la factura con el mismo formato que factura_pdf()
                    from reportlab.lib.pagesizes import letter
                    from reportlab.lib import colors
                    
                    pdf_buffer = BytesIO()
                    pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
                    width, height = letter

                    # === LOGOS (MISMAS POSICIONES QUE EN factura_pdf) ===
                    # Buscar logos en múltiples ubicaciones posibles
                    base_paths = [
                        settings.BASE_DIR / "static" / "img",
                        settings.BASE_DIR / "staticfiles" / "img",
                    ]
                    if settings.STATIC_ROOT:
                        base_paths.insert(0, settings.STATIC_ROOT / "img")
                    
                    ecofact_logo = None
                    empresa_logo = None
                    
                    # Buscar logo EcoFact
                    for base_path in base_paths:
                        logo_path = base_path / "Logo azul sin fondo.png"
                        if os.path.exists(logo_path):
                            ecofact_logo = str(logo_path)
                            print(f"✅ Logo EcoFact encontrado en: {ecofact_logo}")
                            break
                    
                    # Buscar logo Apple Pereira
                    for base_path in base_paths:
                        logo_path = base_path / "logo empresa.png"
                        if os.path.exists(logo_path):
                            empresa_logo = str(logo_path)
                            print(f"✅ Logo Apple Pereira encontrado en: {empresa_logo}")
                            break
                    
                    if not ecofact_logo:
                        print(f"❌ Logo EcoFact NO encontrado. Rutas buscadas: {[str(p / 'Logo azul sin fondo.png') for p in base_paths]}")
                    if not empresa_logo:
                        print(f"❌ Logo Apple Pereira NO encontrado. Rutas buscadas: {[str(p / 'logo empresa.png') for p in base_paths]}")

                    y = height - 50
                    try:
                        # Logos juntos en la parte superior izquierda
                        if ecofact_logo and os.path.exists(ecofact_logo):
                            pdf_canvas.drawImage(ImageReader(ecofact_logo), 40, y - 30, width=60, height=30, preserveAspectRatio=True, mask='auto')
                            print("✅ Logo EcoFact dibujado en PDF")
                        if empresa_logo and os.path.exists(empresa_logo):
                            pdf_canvas.drawImage(ImageReader(empresa_logo), 110, y - 30, width=60, height=30, preserveAspectRatio=True, mask='auto')
                            print("✅ Logo Apple Pereira dibujado en PDF")
                    except Exception as e:
                        print(f"⚠️ Error cargando logos para correo: {e}")
                        import traceback
                        traceback.print_exc()

                    # === TÍTULO CENTRADO ===
                    y -= 60
                    pdf_canvas.setFont("Helvetica-Bold", 18)
                    pdf_canvas.setFillColor(colors.HexColor("#0056b3"))
                    titulo = "FACTURA ELECTRÓNICA"
                    titulo_width = pdf_canvas.stringWidth(titulo, "Helvetica-Bold", 18)
                    pdf_canvas.drawString((width - titulo_width) / 2, y, titulo)
                    
                    # Línea azul debajo del título
                    pdf_canvas.setStrokeColor(colors.HexColor("#0056b3"))
                    pdf_canvas.setLineWidth(2)
                    pdf_canvas.line(40, y - 5, width - 40, y - 5)

                    # === INFORMACIÓN DE LA EMPRESA (IZQUIERDA) ===
                    y -= 30
                    pdf_canvas.setFillColor(colors.black)
                    pdf_canvas.setFont("Helvetica-Bold", 10)
                    pdf_canvas.drawString(40, y, "Apple Pereira S.A.S")
                    pdf_canvas.setFont("Helvetica", 9)
                    pdf_canvas.drawString(40, y - 15, "NIT: 901.456.789-3")
                    pdf_canvas.drawString(40, y - 28, "Dirección: Cra 7 #23-15, Pereira - Risaralda")
                    pdf_canvas.drawString(40, y - 41, "Teléfono: (6) 311 2233")
                    pdf_canvas.drawString(40, y - 54, "Correo: contacto@applepereira.com")

                    # === INFORMACIÓN DEL CLIENTE (DERECHA) ===
                    pdf_canvas.setFont("Helvetica-Bold", 9)
                    pdf_canvas.drawRightString(width - 40, y, f"Número de Factura: {factura.id}")
                    pdf_canvas.setFont("Helvetica", 9)
                    pdf_canvas.drawRightString(width - 40, y - 15, f"Cliente: {factura.nombre_receptor[:30]}")
                    pdf_canvas.drawRightString(width - 40, y - 28, f"NIT: {factura.nit_receptor}")
                    pdf_canvas.drawRightString(width - 40, y - 41, f"Correo: {factura.correo_cliente}")
                    
                    # Fecha y hora de expedición
                    fecha_str = factura.fecha_factura.strftime('%d/%m/%Y')
                    hora_str = factura.hora_expedicion.strftime('%H:%M:%S') if factura.hora_expedicion else "00:00:00"
                    pdf_canvas.drawRightString(width - 40, y - 54, f"Fecha de emisión: {fecha_str}")
                    pdf_canvas.drawRightString(width - 40, y - 67, f"Hora de expedición: {hora_str}")
                    pdf_canvas.drawRightString(width - 40, y - 80, f"Método de pago: {factura.metodo_pago_factura.capitalize()}")

                    # === TABLA DE PRODUCTOS ===
                    y -= 115
                    
                    # Encabezados de la tabla con fondo azul
                    pdf_canvas.setFillColor(colors.HexColor("#0056b3"))
                    pdf_canvas.rect(40, y - 20, width - 80, 20, fill=True, stroke=False)
                    
                    pdf_canvas.setFillColor(colors.white)
                    pdf_canvas.setFont("Helvetica-Bold", 10)
                    pdf_canvas.drawString(50, y - 13, "Descripción")
                    pdf_canvas.drawCentredString(300, y - 13, "Cantidad")
                    pdf_canvas.drawRightString(400, y - 13, "Precio Unitario")
                    pdf_canvas.drawRightString(480, y - 13, "IVA")
                    pdf_canvas.drawRightString(width - 50, y - 13, "Total")

                    # Productos
                    y -= 35
                    pdf_canvas.setFillColor(colors.black)
                    pdf_canvas.setFont("Helvetica", 9)
                    
                    for detalle in factura.detalles.all():
                        if y < 150:
                            pdf_canvas.showPage()
                            y = height - 50
                        
                        pdf_canvas.drawString(50, y, detalle.producto.nombre_producto[:30])
                        pdf_canvas.drawCentredString(300, y, str(detalle.cantidad))
                        pdf_canvas.drawRightString(400, y, f"${detalle.precio:,.2f}")
                        pdf_canvas.drawRightString(480, y, f"${detalle.iva:,.2f}")
                        pdf_canvas.drawRightString(width - 50, y, f"${detalle.total:,.2f}")
                        y -= 20

                    # Línea separadora
                    y -= 10
                    pdf_canvas.setStrokeColor(colors.grey)
                    pdf_canvas.setLineWidth(1)
                    pdf_canvas.line(40, y, width - 40, y)

                    # === TOTALES (ALINEADOS A LA DERECHA) ===
                    y -= 25
                    pdf_canvas.setFont("Helvetica", 10)
                    pdf_canvas.drawRightString(width - 150, y, "Subtotal:")
                    pdf_canvas.drawRightString(width - 50, y, f"${factura.sutotal_factura:,.2f}")
                    
                    y -= 18
                    pdf_canvas.drawRightString(width - 150, y, "IVA:")
                    pdf_canvas.drawRightString(width - 50, y, f"${factura.iva_total_factura:,.2f}")
                    
                    y -= 23
                    pdf_canvas.setFont("Helvetica-Bold", 11)
                    pdf_canvas.drawRightString(width - 150, y, "Total a pagar:")
                    pdf_canvas.drawRightString(width - 50, y, f"${factura.total_factura:,.2f}")

                    # === QR Y CUFE JUNTOS ===
                    y -= 50
                    
                    # Generar QR
                    qr_data = f"CUFE: {factura.cufe_factura}\nTotal: ${factura.total_factura}\nFecha: {factura.fecha_factura}"
                    qr_img = qrcode.make(qr_data)
                    qr_buffer_temp = BytesIO()
                    qr_img.save(qr_buffer_temp, format="PNG")
                    qr_buffer_temp.seek(0)
                    
                    # Colocar QR
                    pdf_canvas.drawImage(ImageReader(qr_buffer_temp), 40, y - 80, width=80, height=80)
                    
                    # CUFE debajo del QR
                    pdf_canvas.setFont("Helvetica", 8)
                    pdf_canvas.setFillColor(colors.black)
                    pdf_canvas.drawString(40, y - 90, f"CUFE: {factura.cufe_factura[:50]}")

                    # === PIE DE PÁGINA ===
                    pdf_canvas.setFont("Helvetica-Oblique", 8)
                    pdf_canvas.drawCentredString(width / 2, 30, "Gracias por confiar en EcoFact.")
                    pdf_canvas.drawCentredString(width / 2, 18, "Factura generada electrónicamente - No requiere firma.")

                    pdf_canvas.showPage()
                    pdf_canvas.save()
                    pdf_buffer.seek(0)
                    
                    # === CREAR CORREO HTML ===
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            .header {{ text-align: center; margin-bottom: 30px; }}
                            .logos {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; }}
                            .logo {{ width: 80px; height: 80px; }}
                            h1 {{ color: #2563eb; margin: 0; }}
                            .info {{ background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                            .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                            .label {{ font-weight: bold; color: #475569; }}
                            .value {{ color: #1e293b; }}
                            .total {{ background-color: #2563eb; color: white; padding: 15px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; }}
                            .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; }}
                            .button {{ display: inline-block; background-color: #2563eb; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1>¡Gracias por su compra!</h1>
                                <p style="color: #64748b; font-size: 14px;">Su factura electrónica ha sido generada exitosamente</p>
                            </div>
                            
                            <div class="info">
                                <div class="info-row">
                                    <span class="label">Factura No:</span>
                                    <span class="value">#{factura.id}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">Fecha:</span>
                                    <span class="value">{factura.fecha_factura}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">Hora de Expedición:</span>
                                    <span class="value">{factura.hora_expedicion.strftime('%H:%M:%S') if factura.hora_expedicion else '00:00:00'}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">Cliente:</span>
                                    <span class="value">{factura.nombre_receptor}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">NIT/CC:</span>
                                    <span class="value">{factura.nit_receptor}</span>
                                </div>
                                <div class="info-row">
                                    <span class="label">Método de Pago:</span>
                                    <span class="value">{factura.metodo_pago_factura}</span>
                                </div>
                            </div>
                            
                            <div class="total">
                                TOTAL: ${factura.total_factura:,.2f}
                            </div>
                            
                            <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                                <p style="margin: 0; color: #92400e;"><strong>CUFE:</strong></p>
                                <p style="margin: 5px 0 0 0; color: #78350f; font-size: 11px; word-break: break-all;">{factura.cufe_factura}</p>
                            </div>
                            
                            <p style="text-align: center; color: #64748b;">
                                Su factura en formato PDF está adjunta a este correo. 
                                Por favor guárdela para sus registros.
                            </p>
                            
                            <div class="footer">
                                <p><strong>EcoFact - Sistema de Facturación Electrónica</strong></p>
                                <p>Este es un correo automático, por favor no responder.</p>
                                <p>© 2025 EcoFact. Todos los derechos reservados.</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Crear el mensaje de correo
                    subject = f"Factura Electrónica #{factura.id} - EcoFact"
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [factura.correo_cliente]
                    
                    # Texto plano alternativo
                    text_content = f"""
                    ¡Gracias por su compra!
                    
                    Factura No: #{factura.id}
                    Fecha: {factura.fecha_factura}
                    Cliente: {factura.nombre_receptor}
                    Total: ${factura.total_factura:,.2f}
                    
                    CUFE: {factura.cufe_factura}
                    
                    Su factura en PDF está adjunta a este correo.
                    
                    EcoFact - Sistema de Facturación Electrónica
                    """
                    
                    # Crear el mensaje
                    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                    msg.attach_alternative(html_content, "text/html")
                    
                    # Adjuntar el PDF
                    msg.attach(f"Factura_{factura.id}.pdf", pdf_buffer.getvalue(), "application/pdf")
                    
                    # Enviar
                    msg.send(fail_silently=False)
                    print(f"✅ Correo enviado exitosamente a {factura.correo_cliente}")
                    
                except Exception as e:
                    print(f"❌ Error enviando correo: {e}")
                    # No fallar la creación de factura si el correo falla
                    pass

            # === GENERAR URLs DE DESCARGA ===
            # Proporcionar enlaces para descargar la factura en PDF y XML
            pdf_url = f"/facturas/pdf/{factura.id}/"
            xml_url = f"/facturas/xml/{factura.id}/"

            # === RESPUESTA EXITOSA ===
            return JsonResponse({
                "status": "ok",
                "id_factura": factura.id,
                "cufe": factura.cufe_factura,
                "total": factura.total_factura,
                "pdf_url": pdf_url,
                "xml_url": xml_url
            })

        except Exception as e:
            # === MANEJO DE ERRORES GENERALES ===
            # Capturar cualquier error inesperado y registrarlo para debugging
            print("Error al crear factura:", str(e))
            traceback.print_exc()  # Imprimir stack trace completo en consola
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # === MÉTODO GET: RENDERIZAR FORMULARIO ===
    # Si no es POST, mostrar la página para crear facturas
    return render(request, "facturas/crear_factura.html")


"""
================================================================================
VISTA: FACTURA EXITOSA
================================================================================
Descripción:
    Página de confirmación que se muestra después de crear una factura exitosamente.
    Informa al usuario que la factura fue generada correctamente.

Método HTTP: GET
Ruta: /facturas/exitosa/
================================================================================
"""
def factura_exitosa(request):
    return render(request, "facturas/factura_exitosa.html")


"""
================================================================================
VISTA: HISTORIAL DE FACTURAS
================================================================================
Descripción:
    Muestra un listado paginado de todas las facturas generadas.
    Permite filtrar por rango de fechas.

Método HTTP: GET
Ruta: /facturas/historial/

Parámetros opcionales:
    - fecha_inicial: Fecha de inicio del filtro (formato: YYYY-MM-DD)
    - fecha_final: Fecha fin del filtro (formato: YYYY-MM-DD)
    - page: Número de página para la paginación

Paginación: 5 facturas por página
================================================================================
"""
@login_required
def historial_factura(request):
    # Obtener las fechas enviadas por el usuario en el filtro (GET)
    fecha_inicial = request.GET.get('fecha_inicial')
    fecha_final = request.GET.get('fecha_final')

    # Usuario autenticado que está haciendo la petición
    usuario = request.user

    # Por defecto, no mostramos ninguna factura hasta determinar el usuario
    facturas = Factura.objects.none()

    # Verificamos si el usuario está autenticado
    if usuario.is_authenticated:

        # Si el usuario es administrador o vendedor -> puede ver TODAS las facturas
        if usuario.rol_usuario in ['admin', 'vendedor']:
            facturas = Factura.objects.all().order_by('-id')

        else:
            # Si es cliente -> solo puede ver sus propias facturas
            # Comparamos el nit_receptor en Factura con numero_documento_usuario del cliente
            facturas = Factura.objects.filter(
                nit_receptor=usuario.numero_documento_usuario
            ).order_by('-id')

    # Si el usuario eligió un rango de fechas, filtramos también por fecha
    if fecha_inicial and fecha_final:
        facturas = facturas.filter(fecha_factura__range=[fecha_inicial, fecha_final])

    # Paginación: mostramos 10 facturas por página
    paginator = Paginator(facturas, 10)

    # Obtenemos el número de página actual desde la URL (?page=2)
    page_number = request.GET.get('page')

    # Obtenemos el objeto de paginación (las facturas correspondientes a esa página)
    page_obj = paginator.get_page(page_number)

    # Enviamos los datos al template
    context = {
        'facturas': page_obj,          # Lista de facturas paginada
        'fecha_inicial': fecha_inicial, # Para mantener el filtro seleccionado
        'fecha_final': fecha_final      # Para mantener el filtro seleccionado
    }

    # Renderizamos la plantilla HTML con los datos
    return render(request, 'facturas/historial_factura.html', context)

    

"""
================================================================================
VISTA: FACTURA EN HTML (IMPRIMIBLE)
================================================================================
Descripción:
    Genera una vista HTML de la factura para visualización e impresión.
    Incluye un código QR que apunta al PDF de la factura.

Método HTTP: GET
Ruta: /facturas/print/<id>/

Parámetros:
    - pk: ID de la factura a mostrar

Genera:
    - QR Code en formato base64 embebido en el HTML
================================================================================
"""
def factura_print(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    detalles = DetalleFactura.objects.filter(factura=factura)

    qr_data = f"http://{request.get_host()}/facturas/pdf/{factura.id}/"
    qr_img = qrcode.make(qr_data)

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    return render(request, "facturas/factura_print.html", {
        "factura": factura,
        "detalles": detalles,
        "qr_base64": qr_base64
    })


# FACTURA EN PDF (con logos y QR) - Diseño mejorado
def factura_pdf(request, pk):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    factura = get_object_or_404(Factura, pk=pk)
    detalles = DetalleFactura.objects.filter(factura=factura)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- ENCABEZADO CON LOGOS JUNTOS (sin fondo) ---
    ecofact_logo = os.path.join(settings.STATIC_ROOT, "img/Logo azul sin fondo.png")
    empresa_logo = os.path.join(settings.STATIC_ROOT, "img/logo empresa.png")

    y = height - 50
    try:
        # Logos juntos en la parte superior izquierda
        if os.path.exists(ecofact_logo):
            p.drawImage(ImageReader(ecofact_logo), 40, y - 30, width=60, height=30, preserveAspectRatio=True, mask='auto')
        if os.path.exists(empresa_logo):
            p.drawImage(ImageReader(empresa_logo), 110, y - 30, width=60, height=30, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"Error cargando logos: {e}")

    # --- TÍTULO CENTRADO ---
    y -= 60
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(colors.HexColor("#0056b3"))
    titulo = "FACTURA ELECTRÓNICA"
    titulo_width = p.stringWidth(titulo, "Helvetica-Bold", 18)
    p.drawString((width - titulo_width) / 2, y, titulo)
    
    # Línea azul debajo del título
    p.setStrokeColor(colors.HexColor("#0056b3"))
    p.setLineWidth(2)
    p.line(40, y - 5, width - 40, y - 5)

    # --- INFORMACIÓN DE LA EMPRESA (IZQUIERDA) Y CLIENTE (DERECHA) ---
    y -= 30
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Apple Pereira S.A.S")
    p.setFont("Helvetica", 9)
    p.drawString(40, y - 15, "NIT: 901.456.789-3")
    p.drawString(40, y - 28, "Dirección: Cra 7 #23-15, Pereira - Risaralda")
    p.drawString(40, y - 41, "Teléfono: (6) 311 2233")
    p.drawString(40, y - 54, "Correo: contacto@applepereira.com")

    # Información del cliente (derecha)
    p.setFont("Helvetica-Bold", 9)
    p.drawRightString(width - 40, y, f"Número de Factura: {factura.id}")
    p.setFont("Helvetica", 9)
    p.drawRightString(width - 40, y - 15, f"Cliente: {factura.nombre_receptor[:30]}")
    p.drawRightString(width - 40, y - 28, f"NIT: {factura.nit_receptor}")
    p.drawRightString(width - 40, y - 41, f"Correo: {factura.correo_cliente}")
    
    # Fecha y hora de expedición
    fecha_str = factura.fecha_factura.strftime('%d/%m/%Y')
    hora_str = factura.hora_expedicion.strftime('%H:%M:%S') if factura.hora_expedicion else "00:00:00"
    p.drawRightString(width - 40, y - 54, f"Fecha de emisión: {fecha_str}")
    p.drawRightString(width - 40, y - 67, f"Hora de expedición: {hora_str}")
    p.drawRightString(width - 40, y - 80, f"Método de pago: {factura.metodo_pago_factura.capitalize()}")

    # --- TABLA DE PRODUCTOS ---
    y -= 115
    
    # Encabezados de la tabla
    p.setFillColor(colors.HexColor("#0056b3"))
    p.rect(40, y - 20, width - 80, 20, fill=True, stroke=False)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y - 13, "Descripción")
    p.drawCentredString(300, y - 13, "Cantidad")
    p.drawRightString(400, y - 13, "Precio Unitario")
    p.drawRightString(480, y - 13, "IVA")
    p.drawRightString(width - 50, y - 13, "Total")

    # Productos
    y -= 35
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 9)
    
    for d in detalles:
        p.drawString(50, y, d.producto.nombre_producto)
        p.drawCentredString(300, y, str(d.cantidad))
        p.drawRightString(400, y, f"${d.precio:,.2f}")
        p.drawRightString(480, y, f"${d.iva:,.2f}")
        p.drawRightString(width - 50, y, f"${d.total:,.2f}")
        y -= 20

    # Línea separadora
    y -= 10
    p.setStrokeColor(colors.grey)
    p.setLineWidth(1)
    p.line(40, y, width - 40, y)

    # --- TOTALES (ALINEADOS A LA DERECHA) ---
    y -= 25
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 150, y, "Subtotal:")
    p.drawRightString(width - 50, y, f"${factura.sutotal_factura:,.2f}")
    
    y -= 18
    p.drawRightString(width - 150, y, "IVA:")
    p.drawRightString(width - 50, y, f"${factura.iva_total_factura:,.2f}")
    
    y -= 23
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(width - 150, y, "Total a pagar:")
    p.drawRightString(width - 50, y, f"${factura.total_factura:,.2f}")

    # --- QR Y CUFE JUNTOS ---
    y -= 50
    
    # Generar QR
    qr_data = f"CUFE: {factura.cufe_factura}\nTotal: ${factura.total_factura}\nFecha: {factura.fecha_factura}"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # Colocar QR
    p.drawImage(ImageReader(qr_buffer), 40, y - 80, width=80, height=80)
    
    # CUFE debajo del QR (más cerca)
    p.setFont("Helvetica", 8)
    p.drawString(40, y - 90, f"CUFE: {factura.cufe_factura}")

    # --- PIE DE PÁGINA ---
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(width / 2, 30, "Gracias por confiar en EcoFact.")
    p.drawCentredString(width / 2, 18, "Factura generada electrónicamente - No requiere firma.")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="Factura_{factura.id}.pdf"'
    return response


# FACTURA EN XML
def factura_xml(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    detalles = DetalleFactura.objects.filter(factura=factura)

    response = HttpResponse(content_type="application/xml")
    response["Content-Disposition"] = f'attachment; filename="Factura_{factura.id}.xml"'

    response.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    response.write("<factura>\n")
    response.write(f"  <id>{factura.id}</id>\n")
    response.write(f"  <cliente>{factura.nombre_receptor}</cliente>\n")
    response.write(f"  <nit>{factura.nit_receptor}</nit>\n")
    response.write(f"  <fecha>{factura.fecha_factura}</fecha>\n")
    response.write(f"  <total>{factura.total_factura}</total>\n")
    response.write("  <detalles>\n")
    for d in detalles:
        response.write("    <detalle>\n")
        response.write(f"      <producto>{d.producto.nombre_producto}</producto>\n")
        response.write(f"      <cantidad>{d.cantidad}</cantidad>\n")
        response.write(f"      <precio>{d.precio}</precio>\n")
        response.write(f"      <iva>{d.iva}</iva>\n")
        response.write(f"      <total>{d.total}</total>\n")
        response.write("    </detalle>\n")
    response.write("  </detalles>\n")
    response.write("</factura>\n")

    return response


# BUSCAR PRODUCTO POR CÓDIGO DE BARRAS (para lector o búsqueda manual)
def buscar_producto(request):
    codigo = request.GET.get("codigo", "").strip()

    print("Código recibido:", codigo)

    if not codigo:
        return JsonResponse({"error": "No se envió código"}, status=400)

    try:
        producto = Producto.objects.get(codigo_barras_producto=codigo)

        # Obtener stock
        try:
            inventario = Inventario.objects.get(producto=producto)
            stock = inventario.stock_actual_inventario
        except Inventario.DoesNotExist:
            stock = 0

        print("Producto encontrado:", {
            "nombre": producto.nombre_producto,
            "precio": float(producto.precio_producto),
            "stock": stock,
        })

        return JsonResponse({
            "nombre": producto.nombre_producto,
            "precio": float(producto.precio_producto),
            "stock": stock,
        })

    except Producto.DoesNotExist:
        print("Producto no encontrado en DB")
        return JsonResponse({"error": "Producto no encontrado"}, status=404)


