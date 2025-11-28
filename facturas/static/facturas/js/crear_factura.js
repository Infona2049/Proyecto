// --- Configuración inicial ---
console.log("crear_factura.js cargado - Version: 20/Nov/2025 - 15:30"); // Log para confirmar carga del script
let consecutivoFactura = 1000; // Valor inicial del consecutivo
let subtotalGeneral = 0; // Valor inicial del subtotal
let ivaGeneral = 0; // Valor inicial del IVA
let totalGeneral = 0; // Valor inicial del total

// --- Función para mostrar alerta personalizada sin stock ---
function mostrarAlertaSinStock(nombreProducto, stockDisponible = 0) {
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.className = 'alert-overlay';
    
    // Crear contenido de la alerta
    overlay.innerHTML = `
        <div class="alert-box">
            <div class="alert-icon">
                <svg viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <circle cx="12" cy="16" r="1" fill="currentColor"/>
                </svg>
            </div>
            <div class="alert-title">¡Stock Insuficiente!</div>
            <div class="alert-message">
                Lo sentimos, no hay suficiente inventario disponible para:
            </div>
            <div class="alert-product-name">${nombreProducto}</div>
            <div class="alert-stock-info">
                Stock disponible: <strong>${stockDisponible} unidades</strong>
            </div>
            <button class="alert-button" onclick="this.closest('.alert-overlay').remove()">
                Entendido
            </button>
        </div>
    `;
    
    // Agregar al body
    document.body.appendChild(overlay);
    
    // Cerrar al hacer clic fuera de la alerta
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        if (document.body.contains(overlay)) {
            overlay.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => overlay.remove(), 300);
        }
    }, 5000);
}

// --- Función principal para agregar productos desde el lector ---
function agregarFilaDesdeCodigo({ nombre, precio, stock, iva, codigo }) {  // Agregar parámetro código
    // === VALIDAR STOCK DISPONIBLE ===
    if (stock <= 0) {
        mostrarAlertaSinStock(nombre, stock);
        return; // No agregar el producto si no hay stock
    }

    const tabla = document.getElementById("tablaProductos");// Asegurarse de que la tabla existe
    let tbody = tabla.querySelector("tbody"); // Buscar tbody existente

    if (!tbody) { // Si no existe tbody, crearlo
        tbody = document.createElement("tbody"); // Crear nuevo tbody
        tabla.appendChild(tbody); // Agregar tbody a la tabla
    }

    const fila = document.createElement("tr"); // Crear nueva fila
     
    // Rellenar la fila con los datos del producto
    fila.innerHTML = `    
        <td>${nombre}</td>
        <td>${precio.toFixed(2)}</td>
        <td><input type="number" class="cantidad-input" value="1" min="1"></td>
        <td>${iva.toFixed(2)}</td>
        <td class="subtotal">${(precio + iva).toFixed(2)}</td>
        <td>
            <button type="button" class="eliminar-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
            </button>
        </td>
    `;
    
    // Guardar código de barras y stock en data-attributes DESPUÉS de innerHTML
    // (innerHTML sobrescribe todo, incluyendo los data-attributes)
    if (codigo) {
        fila.dataset.codigo = codigo;
    }
    fila.dataset.stock = stock; // Guardar stock disponible
    fila.dataset.nombre = nombre; // Guardar nombre del producto

    tbody.appendChild(fila);

    actualizarTotales();
    activarEventosFila(fila);
}

function activarEventosFila(fila) { // Activar eventos para inputs y botones en la fila
    const cantidadInput = fila.querySelector(".cantidad-input");
    const eliminarBtn = fila.querySelector(".eliminar-btn");

    if (cantidadInput) {
        cantidadInput.addEventListener("input", () => {
            // === VALIDAR NÚMEROS NEGATIVOS ===
            let cantidadSolicitada = parseInt(cantidadInput.value);
            
            // Si es negativo o no es un número válido, establecer en 1
            if (isNaN(cantidadSolicitada) || cantidadSolicitada < 1) {
                cantidadInput.value = 1;
                cantidadSolicitada = 1;
            }
            
            // === VALIDAR STOCK AL CAMBIAR CANTIDAD ===
            const stockDisponible = parseInt(fila.dataset.stock) || 0;
            const nombreProducto = fila.dataset.nombre || "Producto";
            
            if (cantidadSolicitada > stockDisponible) {
                mostrarAlertaSinStock(nombreProducto, stockDisponible);
                cantidadInput.value = stockDisponible; // Limitar a stock disponible
            }
            
            actualizarTotales(); // Actualizar totales
        });
    }

    if (eliminarBtn) {
        eliminarBtn.addEventListener("click", (e) => { // Manejar eliminación de fila
            e.preventDefault();
            console.log("Eliminando fila...");
            fila.remove();
            actualizarTotales();
        });
    } else {
        console.warn("No se encontró el botón eliminar"); // Log de advertencia si no se encuentra el botón
    }
}

function actualizarTotales() { // Recalcular y actualizar totales
    subtotalGeneral = 0; // Reiniciar subtotal
    ivaGeneral = 0;// Reiniciar IVA
    totalGeneral = 0; // Reiniciar total

    const filas = document.querySelectorAll("#tablaProductos tbody tr"); // Seleccionar todas las filas de productos

    filas.forEach(fila => { // Iterar sobre cada fila
        let precio = parseFloat(fila.cells[1].innerText); // Precio unitario
        let cantidad = parseInt(fila.querySelector(".cantidad-input").value); // Cantidad del producto
        let iva = parseFloat(fila.cells[3].innerText); // IVA del producto

        let subtotal = (precio * cantidad) + (iva * cantidad);// Calcular subtotal para la fila
        fila.querySelector(".subtotal").innerText = subtotal.toFixed(2);// Actualizar subtotal en la fila

        subtotalGeneral += precio * cantidad;
        ivaGeneral += iva * cantidad;
        totalGeneral += subtotal;
    });

    // ids correctos del HTML para mostrar los totales
    const subtotalEl = document.getElementById("subtotal"); 
    const ivaEl = document.getElementById("ivaTotal"); 
    const totalEl = document.getElementById("granTotal");

    if (subtotalEl) subtotalEl.innerText = subtotalGeneral.toFixed(2);
    if (ivaEl) ivaEl.innerText = ivaGeneral.toFixed(2);
    if (totalEl) totalEl.innerText = totalGeneral.toFixed(2);
    
    console.log("Totales actualizados:", { subtotalGeneral, ivaGeneral, totalGeneral }); // Log para verificar totales
}

// --- DELEGACIÓN DE EVENTOS PARA BOTONES ELIMINAR ---
document.addEventListener("DOMContentLoaded", () => { 
    const tabla = document.getElementById("tablaProductos");
    
    // Usar delegación de eventos para botones que se agregan dinámicamente
    tabla.addEventListener("click", (e) => {
        if (e.target.classList.contains("eliminar-btn") || e.target.closest(".eliminar-btn")) {
            e.preventDefault();
            const btn = e.target.closest(".eliminar-btn") || e.target;
            const fila = btn.closest("tr");
            console.log("🗑️ Eliminando fila:", fila);
            fila.remove();
            actualizarTotales();
        }
    });
    
    console.log("✅ Delegación de eventos configurada para eliminar");
});

// --- LECTOR DE CÓDIGO DE BARRAS ---
document.addEventListener("DOMContentLoaded", () => { // Esperar a que el DOM esté cargado
    const inputCodigo = document.getElementById("codigo_barras_input"); /// Asegurarse de que el input existe

    if (inputCodigo) { // Si el input existe
        inputCodigo.addEventListener("change", function () { // Escuchar evento change que ocurre al presionar ENTER de cuando se escanea
            let codigo = this.value.trim(); // Obtener el código escaneado

            if (!codigo) { // Validar que no esté vacío
                return; // Salir si no hay código
            }

            console.log("Código enviado:", codigo); // Log del código enviado

            fetch(`/facturas/buscar_producto/?codigo=${codigo}`) // Hacer fetch al backend para buscar producto
                .then(res => res.json()) // Parsear respuesta JSON como objeto de JavaScript
                .then(data => { // Manejar datos recibidos
                    console.log("Respuesta recibida:", data); // Log de la respuesta recibida

                    // Si backend manda error, mostrar alerta personalizada
                    if (data.error) {
                        console.warn("Producto no encontrado:", data.error);
                        showCustomAlert();
                        this.value = "";
                        return;
                    }

                    // Crear IVA correctamente
                    const ivaCalculado = parseFloat(data.precio) * 0.19;

                    agregarFilaDesdeCodigo({// Agregar el producto a la tabla
                        nombre: data.nombre, // Nombre del producto
                        precio: parseFloat(data.precio), // Precio del producto
                        stock: data.stock,// Stock del producto
                        iva: ivaCalculado, // Calcular IVA correctamente
                        codigo: codigo  // Pasar el código de barras
                    });

                    this.value = "";
                })
                .catch(err => {
                    console.error("Error al buscar producto:", err);
                    this.value = "";
                });
        });
    }
});



// --- NUEVO: establecer fecha automática ---
document.addEventListener("DOMContentLoaded", () => { // Esperar a que el DOM esté cargado para establecer la fecha
    const fechaInput = document.getElementById("fecha"); // Obtener el input de fecha

    if (fechaInput) { // Si el input existe
        const hoy = new Date();
        const year = hoy.getFullYear();
        const month = String(hoy.getMonth() + 1).padStart(2, "0"); // Mes con dos dígitos
        const day = String(hoy.getDate()).padStart(2, "0"); // Día con dos dígitos  

        fechaInput.value = `${year}-${month}-${day}`; // Formato YYYY-MM-DD
        console.log("Fecha establecida:", fechaInput.value); // Log de confirmación
    } else {
        console.log("No se encontró el input con id 'fecha'");
    }

    // Conectar el botón de generar factura
    const btnGenerar = document.getElementById("btnGenerarFactura"); // Asegurarse de que el botón existe
    if (btnGenerar) {
        btnGenerar.addEventListener("click", generarFactura); // Conectar evento click para generar factura
        console.log("Botón 'Generar Factura' conectado");// Log de confirmación para el botón de generar factura
    } else {
        console.log("No se encontró el botón con id 'btnGenerarFactura'");
    }

    // === VALIDACIÓN EN TIEMPO REAL PARA TELÉFONO Y DOCUMENTO ===
    const telefonoInput = document.getElementById("telefono");
    const documentoInput = document.getElementById("cedulaCliente");

    // Evitar números negativos y caracteres no numéricos en teléfono
    if (telefonoInput) {
        // Validar en tiempo real
        telefonoInput.addEventListener("input", function(e) {
            // Remover todo lo que no sea dígito (incluyendo signo negativo)
            let valor = this.value.replace(/[^0-9]/g, '');
            
            // Si después de limpiar queda vacío y había un valor, mostrar 0
            if (valor === '' && this.value !== '') {
                valor = '';
            }
            
            this.value = valor;
        });

        // Prevenir teclas no permitidas
        telefonoInput.addEventListener("keydown", function(e) {
            // Prevenir teclas de signo negativo, más, menos, punto, e
            if (e.key === '-' || e.key === 'e' || e.key === '+' || e.key === '.' || e.key === ',') {
                e.preventDefault();
            }
        });

        // Validar al pegar
        telefonoInput.addEventListener("paste", function(e) {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const numbersOnly = pastedText.replace(/[^0-9]/g, '');
            this.value = numbersOnly;
        });
    }

    // Evitar números negativos y caracteres no numéricos en documento
    if (documentoInput) {
        // Validar en tiempo real
        documentoInput.addEventListener("input", function(e) {
            // Remover todo lo que no sea dígito (incluyendo signo negativo)
            let valor = this.value.replace(/[^0-9]/g, '');
            
            // Si después de limpiar queda vacío y había un valor, mostrar 0
            if (valor === '' && this.value !== '') {
                valor = '';
            }
            
            this.value = valor;
        });

        // Prevenir teclas no permitidas
        documentoInput.addEventListener("keydown", function(e) {
            // Prevenir teclas de signo negativo, más, menos, punto, e
            if (e.key === '-' || e.key === 'e' || e.key === '+' || e.key === '.' || e.key === ',') {
                e.preventDefault();
            }
        });

        // Validar al pegar
        documentoInput.addEventListener("paste", function(e) {
            e.preventDefault();
            const pastedText = (e.clipboardData || window.clipboardData).getData('text');
            const numbersOnly = pastedText.replace(/[^0-9]/g, '');
            this.value = numbersOnly;
        });
    }
});

// --- AUTOCOMPLETAR DATOS DEL CLIENTE POR DOCUMENTO ---
document.addEventListener("DOMContentLoaded", () => {
    const inputDocumento = document.getElementById("cedulaCliente");

    if (inputDocumento) {
        inputDocumento.addEventListener("blur", function () { // Evento blur se activa cuando el campo pierde el foco
            let documento = this.value.trim();

            if (!documento) {
                return; // Salir si no hay documento
            }

            console.log("Buscando usuario con documento:", documento);

            fetch(`/facturas/buscar_usuario/?documento=${documento}`)
                .then(res => res.json())
                .then(data => {
                    console.log("Respuesta recibida:", data);

                    if (data.error) {
                        console.warn("Usuario no encontrado:", data.error);
                        // Mostrar alerta de documento no registrado
                        showDocumentoAlert();
                        return;
                    }

                    // Autocompletar campos con los datos del usuario
                    const nombreInput = document.getElementById("nombreCliente");
                    const correoInput = document.getElementById("correoCliente");
                    const telefonoInput = document.getElementById("telefono");
                    const direccionInput = document.getElementById("direccion");
                    const tipoDocInput = document.getElementById("tipoDocumento");

                    if (nombreInput) nombreInput.value = data.nombre;
                    if (correoInput) correoInput.value = data.correo;
                    if (telefonoInput) telefonoInput.value = data.telefono;
                    if (direccionInput) direccionInput.value = data.direccion;
                    if (tipoDocInput && data.tipo_documento) {
                        // Mapear el valor del backend al valor del select
                        const tipoDocMap = {
                            'cc': 'cedula',
                            'ce': 'cedula_extranjera',
                            'pa': 'pasaporte',
                            'ppt': 'ppt',
                            'nit': 'nit',
                            'cif': 'cif',
                            'ruc': 'ruc'
                        };
                        tipoDocInput.value = tipoDocMap[data.tipo_documento] || '';
                    }

                    console.log("✅ Campos autocompletados");
                })
                .catch(err => {
                    console.error("Error al buscar usuario:", err);
                });
        });
    }
});


// --- Función para obtener el token de CSRF para peticiones POST y PUT para Django 
function getCSRFToken() {//
    const cookies = document.cookie.split(';'); // Dividir cookies en array para buscar csrftoken que es usado por Django
    for (let i = 0; i < cookies.length; i++) { // Iterar sobre cookies para encontrar csrftoken 
        const cookie = cookies[i].trim(); // Limpiar espacios en cookie
        if (cookie.startsWith('csrftoken=')) { // Si cookie es csrftoken
            return cookie.substring('csrftoken='.length); // Retornar valor del token
        }
    }
    // Alternativa: buscar en un input hidden
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]'); // Buscar token CSRF en input hidden para poder hacer peticiones POST
    return csrfInput ? csrfInput.value : '';
}

// --- Función auxiliar para construir items desde la tabla ---
function construirItemsDesdeTabla() {
    const items = [];
    const filas = document.querySelectorAll("#tablaProductos tbody tr"); // Seleccionar todas las filas de productos

    filas.forEach(fila => { // Iterar sobre cada fila para construir el array de items   
        const nombre = fila.cells[0].innerText;   // Obtener nombre del producto
        const precio = parseFloat(fila.cells[1].innerText); // Obtener precio del producto
        const cantidad = parseInt(fila.querySelector(".cantidad-input").value); // Obtener cantidad
        const iva = parseFloat(fila.cells[3].innerText); // Obtener IVA
        const subtotal = parseFloat(fila.querySelector(".subtotal").innerText); // Obtener subtotal
        items.push({ // Agregar objeto item al array para enviar la factura
            nombre: nombre, // Nombre del producto
            precio: precio, // Precio del producto
            cantidad: cantidad, // Cantidad del producto
            iva: iva, // IVA del producto
            total: subtotal, // Subtotal del producto   
            codigo_barras: fila.dataset.codigo || ""  // Si guardaste el código en data-attribute para enviarlo a backend
        }); 
    });

    return items;
}


function generarFactura() { // Función para generar la factura al hacer click en el botón   
  const nombreCliente = document.getElementById("nombreCliente")?.value?.trim(); // Obtener y limpiar nombre del cliente
  const correoCliente = document.getElementById("correoCliente")?.value?.trim();// Obtener y limpiar correo del cliente
  const telefonoCliente = document.getElementById("telefono")?.value?.trim(); // Obtener y limpiar teléfono del cliente
  const direccionCliente = document.getElementById("direccion")?.value?.trim(); // Obtener y limpiar dirección del cliente
  const cedulaCliente = document.getElementById("cedulaCliente")?.value?.trim(); // Obtener número de documento
  const metodoPago = document.getElementById("medioPago")?.value; // Obtener método de pago

  if (!nombreCliente || !correoCliente || !telefonoCliente || !direccionCliente) { // Validar datos del cliente
    alert("Debe llenar todos los datos del cliente.");
    return;
  }

  // === LIMPIAR Y VALIDAR TELÉFONO ===
  // Primero limpiar cualquier caracter no numérico
  const telefonoLimpio = telefonoCliente.replace(/[^0-9]/g, '');
  const cedulaLimpia = cedulaCliente.replace(/[^0-9]/g, '');

  // Actualizar los campos con valores limpios
  document.getElementById("telefono").value = telefonoLimpio;
  document.getElementById("cedulaCliente").value = cedulaLimpia;

  // === VALIDAR QUE TELÉFONO NO ESTÉ VACÍO DESPUÉS DE LIMPIAR ===
  if (!telefonoLimpio || telefonoLimpio === '') {
    Swal.fire({
      icon: "error",
      title: "Teléfono inválido",
      text: "El teléfono no puede estar vacío y solo debe contener números positivos.",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#d33"
    });
    return;
  }

  // === VALIDAR QUE DOCUMENTO NO ESTÉ VACÍO DESPUÉS DE LIMPIAR ===
  if (!cedulaLimpia || cedulaLimpia === '') {
    Swal.fire({
      icon: "error",
      title: "Documento inválido",
      text: "El número de documento no puede estar vacío y solo debe contener números positivos.",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#d33"
    });
    return;
  }

  // === VALIDAR QUE NO CONTENGAN SIGNO NEGATIVO O CARACTERES ESPECIALES ===
  if (telefonoCliente.includes("-") || /[^0-9]/.test(telefonoCliente)) {
    Swal.fire({
      icon: "error",
      title: "Teléfono inválido",
      text: "No se aceptan números negativos ni caracteres especiales en el teléfono. Por favor ingrese solo números positivos.",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#d33"
    });
    // Limpiar el campo
    document.getElementById("telefono").value = telefonoLimpio;
    return;
  }

  if (cedulaCliente.includes("-") || /[^0-9]/.test(cedulaCliente)) {
    Swal.fire({
      icon: "error",
      title: "Documento inválido",
      text: "No se aceptan números negativos ni caracteres especiales en el número de documento. Por favor ingrese solo números positivos.",
      confirmButtonText: "Entendido",
      confirmButtonColor: "#d33"
    });
    // Limpiar el campo
    document.getElementById("cedulaCliente").value = cedulaLimpia;
    return;
  }

  const tablaProductos = document.querySelector("#tablaProductos tbody");
  if (!tablaProductos || tablaProductos.rows.length === 0) {
    alert("Debe agregar al menos un producto.");
    return;
  }

  if (!metodoPago) {
    alert("Debe seleccionar un método de pago.");
    return;
  }

  const items = construirItemsDesdeTabla(); // Construir array de items desde la tabla para enviar al backend y porder generar la factura

  const data = { // Construir objeto de datos para enviar al backend
    nombre_receptor: nombreCliente,
    nit_receptor: cedulaLimpia, // Usar valor limpio
    correo_cliente: correoCliente,
    telefono: telefonoLimpio, // Usar valor limpio
    direccion: direccionCliente,
    metodo_pago_factura: metodoPago,
    fecha_factura: new Date().toLocaleDateString("en-CA"),
    estado: "Pendiente",
    sutotal_factura: subtotalGeneral,
    iva_total_factura: ivaGeneral,
    total_factura: totalGeneral,
    cliente_id: 1,
    cufe_factura: "TEMP" + Date.now(),
    productos: items
  };

  console.log("Datos a enviar:", data);

  fetch("/facturas/crear/", { // Hacer fetch al endpoint para crear factura 
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify(data)
  })
  .then(response => {
    console.log("Respuesta del servidor (status):", response.status);
    return response.json();
  })
  .then(result => {
    console.log("Respuesta del servidor (data):", result);
    if (result.status === "ok") {
      consecutivoFactura++;
      // Redirigir directamente sin alert
      window.location.href = "/facturas/exitosa/";
    } else {
      // Verificar si es un error de correo no registrado
      if (result.message && result.message.includes("no está registrado")) {
        showEmailAlert(result.message);
      } else {
        console.error("Error al generar la factura:", result.message || "Error desconocido");
        alert("Error: " + (result.message || "Error desconocido"));
      }
    }
  })
  .catch(error => {
    console.error("Error al generar factura:", error);
  });
}

// --- FUNCIONES PARA ALERTA PERSONALIZADA ---
function showCustomAlert() {
    const overlay = document.getElementById("customAlertOverlay");
    if (overlay) {
        overlay.classList.add("show");
        // Enfocar en el input de código de barras después de cerrar
        setTimeout(() => {
            const input = document.getElementById("codigo_barras_input");
            if (input) input.focus();
        }, 100);
    }
}

function closeCustomAlert() {
    const overlay = document.getElementById("customAlertOverlay");
    if (overlay) {
        overlay.classList.remove("show");
        // Enfocar en el input de código de barras después de cerrar
        const input = document.getElementById("codigo_barras_input");
        if (input) input.focus();
    }
}

// Cerrar alerta al hacer clic fuera de la caja
document.addEventListener("DOMContentLoaded", () => {
    const overlay = document.getElementById("customAlertOverlay");
    if (overlay) {
        overlay.addEventListener("click", function(e) {
            if (e.target === overlay) {
                closeCustomAlert();
            }
        });
    }
    
    // También para la alerta de correo
    const emailOverlay = document.getElementById("customAlertEmailOverlay");
    if (emailOverlay) {
        emailOverlay.addEventListener("click", function(e) {
            if (e.target === emailOverlay) {
                closeEmailAlert();
            }
        });
    }
    
    // También para la alerta de documento
    const documentoOverlay = document.getElementById("customAlertDocumentoOverlay");
    if (documentoOverlay) {
        documentoOverlay.addEventListener("click", function(e) {
            if (e.target === documentoOverlay) {
                closeDocumentoAlert();
            }
        });
    }
});

// --- FUNCIONES PARA ALERTA DE CORREO NO REGISTRADO ---
function showEmailAlert(message) {
    const overlay = document.getElementById("customAlertEmailOverlay");
    const messageElement = document.getElementById("emailAlertMessage");
    
    if (overlay) {
        if (messageElement && message) {
            messageElement.textContent = message;
        }
        overlay.classList.add("show");
        // Enfocar en el input de correo después de cerrar
        setTimeout(() => {
            const input = document.getElementById("correoCliente");
            if (input) input.focus();
        }, 100);
    }
}

function closeEmailAlert() {
    const overlay = document.getElementById("customAlertEmailOverlay");
    if (overlay) {
        overlay.classList.remove("show");
        // Enfocar en el input de correo después de cerrar
        const input = document.getElementById("correoCliente");
        if (input) input.focus();
    }
}

// --- FUNCIONES PARA ALERTA DE DOCUMENTO NO REGISTRADO ---
function showDocumentoAlert() {
    const overlay = document.getElementById("customAlertDocumentoOverlay");
    
    if (overlay) {
        overlay.classList.add("show");
        // Enfocar en el input de documento después de cerrar
        setTimeout(() => {
            const input = document.getElementById("cedulaCliente");
            if (input) input.focus();
        }, 100);
    }
}

function closeDocumentoAlert() {
    const overlay = document.getElementById("customAlertDocumentoOverlay");
    if (overlay) {
        overlay.classList.remove("show");
        // Enfocar en el input de documento después de cerrar
        const input = document.getElementById("cedulaCliente");
        if (input) input.focus();
    }
}
