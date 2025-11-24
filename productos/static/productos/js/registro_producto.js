// ...existing code...
/*
  registro_producto.js
  Propósito: scripts frontend para pages de productos:
    - dropdown de usuario (UX)
    - lógica dinámica del formulario de registro (mostrar/ocultar campos y rellenar opciones)
    - validaciones básicas en cliente antes de enviar formulario
    - confirmación modal al eliminar un registro en inventario

  Nota: las validaciones en cliente son solo UX. Siempre validar en servidor.
*/

/* ------------------------------
   Dropdown de usuario (si existe)
   - Busca elementos .usuario y .dropdown-usuario en el DOM.
   - Al hacer click en el toggle, alterna la visibilidad del menú.
   - Cierra el menú al hacer click fuera.
   ------------------------------ */
const dropdownToggle = document.querySelector(".usuario");
const dropdownMenu = document.querySelector(".dropdown-usuario");

if (dropdownToggle && dropdownMenu) {
  dropdownToggle.addEventListener("click", () => {
    dropdownMenu.classList.toggle("visible");
  });

  // Cerrar el dropdown si el click ocurre fuera de él
  window.addEventListener("click", function (e) {
    if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
      dropdownMenu.classList.remove("visible");
    }
  });
}

/* ------------------------------
   Lógica dinámica de productos
   - Inicializa cuando el DOM está listo.
   - Muestra/oculta controles adicionales según la categoría seleccionada.
   - Rellena el select modelo con opciones relevantes.
   - Variables:
     - categoriaSelect: select principal de categoría
     - modeloSelect: select de modelos (se rellena dinámicamente)
     - extrasMoviles: contenedor con campos extra (modelo, color, almacenamiento)
   ------------------------------ */
document.addEventListener("DOMContentLoaded", () => {
  // Ejecutar esta lógica solo en la página de registro de producto.
  // Evita que la misma lógica oculte campos (como el select de color)
  // en otras vistas como `inventario`.
  if (!document.getElementById('form-registro-producto')) return;

  const categoriaSelect = document.getElementById("categoria");
  const modeloSelect = document.getElementById("modelo");
  const extrasMoviles = document.getElementById("extras-moviles");

  const labelModelo = document.querySelector('label[for="modelo"]');
  const labelColor = document.querySelector('label[for="color"]');
  const labelAlmacenamiento = document.querySelector('label[for="almacenamiento"]');
  const colorSelect = document.getElementById("color");
  const almacenamientoSelect = document.getElementById("almacenamiento");



  // Helpers: limpiar opciones de modelo y controlar visibilidad de campos
  function limpiarModelos() {
    if (!modeloSelect) return;
    modeloSelect.innerHTML = '<option value="">Seleccione</option>';
  }

  function ocultarTodoExtras() {
    if (extrasMoviles) extrasMoviles.style.display = "none";
    if (labelModelo) labelModelo.style.display = "none";
    if (modeloSelect) modeloSelect.style.display = "none";
    if (labelColor) labelColor.style.display = "none";
    if (colorSelect) colorSelect.style.display = "none";
    if (labelAlmacenamiento) labelAlmacenamiento.style.display = "none";
    if (almacenamientoSelect) almacenamientoSelect.style.display = "none";
  }

  function mostrarSoloModelo() {
    if (extrasMoviles) extrasMoviles.style.display = "block";
    if (labelModelo) labelModelo.style.display = "block";
    if (modeloSelect) modeloSelect.style.display = "block";
    if (labelColor) labelColor.style.display = "none";
    if (colorSelect) colorSelect.style.display = "none";
    if (labelAlmacenamiento) labelAlmacenamiento.style.display = "none";
    if (almacenamientoSelect) almacenamientoSelect.style.display = "none";
  }

  function mostrarModeloColorAlmacenamiento() {
    if (extrasMoviles) extrasMoviles.style.display = "block";
    if (labelModelo) labelModelo.style.display = "block";
    if (modeloSelect) modeloSelect.style.display = "block";
    if (labelColor) labelColor.style.display = "block";
    if (colorSelect) colorSelect.style.display = "block";
    if (labelAlmacenamiento) labelAlmacenamiento.style.display = "block";
    if (almacenamientoSelect) almacenamientoSelect.style.display = "block";
  }

  // Rellena un select con una lista de texto (opciones)
  function llenarOpciones(select, opciones) {
    if (!select) return;
    limpiarModelos();
    opciones.forEach(txt => {
      const opt = document.createElement("option");
      opt.value = txt;
      opt.textContent = txt;
      select.appendChild(opt);
    });
  }

  // Muestra las opciones correctas según la categoría seleccionada
  function mostrarOpciones() {
    if (!categoriaSelect) return;

    const categoria = categoriaSelect.value;

    // Estado base: ocultar extras y limpiar modelos
    ocultarTodoExtras();
    limpiarModelos();

    if (categoria === "moviles") {
      mostrarModeloColorAlmacenamiento();
      llenarOpciones(modeloSelect, iphones);
    } else if (categoria === "cargadores") {
      mostrarSoloModelo();
      llenarOpciones(modeloSelect, cargadores);
    } else if (categoria === "auriculares") {
      mostrarSoloModelo();
      llenarOpciones(modeloSelect, auriculares);
    }
  }

  // Escuchar cambio de categoría y ajustar la UI
  if (categoriaSelect) {
    categoriaSelect.addEventListener("change", mostrarOpciones);
  }

  // Inicializar vista según el valor actual (útil cuando el formulario viene con datos)
  mostrarOpciones();
});

/* ------------------------------
   Validación frontend para registro de producto
   - Mejora UX evitando envíos con datos inválidos obvios.
   - Campos validados:
     - nombre_producto: solo letras, números y espacios
     - precio_producto: número > 0
     - stock_actual: número > 0
   - Si falla validación, se muestra alert() y se previene el submit.
   ------------------------------ */
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('form-registro-producto');
  if (!form) return;

  const nombreInput = form.querySelector('[name="nombre_producto"]');
  const precioInput = form.querySelector('[name="precio_producto"]');
  const stockInput = form.querySelector('[name="stock_actual"]');

  form.addEventListener('submit', function(e) {
    let valid = true;

    // Validar nombre: letras, números y espacios
    if (nombreInput && !/^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$/.test(nombreInput.value.trim())) {
      alert('El nombre solo puede contener letras, números y espacios.');
      nombreInput.focus();
      valid = false;
    }

    // Validar precio positivo
    if (precioInput && (isNaN(precioInput.value) || Number(precioInput.value) <= 0)) {
      alert('El precio debe ser un número positivo.');
      precioInput.focus();
      valid = false;
    }

    // Validar stock actual mayor a 0
    if (stockInput && (isNaN(stockInput.value) || Number(stockInput.value) <= 0)) {
      alert('El stock actual debe ser mayor a 0.');
      stockInput.focus();
      valid = false;
    }

    if (!valid) e.preventDefault(); // evitar envío si hay errores
  });
});

/* ------------------------------
   Confirmación de eliminación con SweetAlert2
   ------------------------------ */
/* Confirmación de eliminación (moved to inventario.js) */

/* ------------------------------
   Modal visualizador de imagen (moved from template)
   - Abre el modal con la imagen cuando se hace click en el botón .btn-visualizar
   - Limpia el src al cerrar
   ------------------------------ */
/* Modal visualizador de imagen (moved to inventario.js) */
