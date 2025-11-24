// JS para historial_inventario - replica comportamiento de historial_factura
document.addEventListener('DOMContentLoaded', function() {
  const botonBuscar = document.querySelector('.boton-buscar');
  const botonLimpiar = document.querySelector('.boton-limpiar');
  const fechaInicialInput = document.getElementById('fecha-inicial');
  const fechaFinalInput = document.getElementById('fecha-final');

  if (botonBuscar) {
    botonBuscar.addEventListener('click', function() {
      const fi = fechaInicialInput ? fechaInicialInput.value : '';
      const ff = fechaFinalInput ? fechaFinalInput.value : '';
      if (fi && ff) {
        // Redirige con parámetros GET al endpoint de productos
        window.location.href = `/productos/historial_inventario/?fecha_inicial=${fi}&fecha_final=${ff}`;
      } else {
        alert('Selecciona las dos fechas antes de buscar.');
      }
    });
  }

  if (botonLimpiar) {
    botonLimpiar.addEventListener('click', function() {
      if (fechaInicialInput) fechaInicialInput.value = '';
      if (fechaFinalInput) fechaFinalInput.value = '';
      window.location.href = `/productos/historial_inventario/`;
    });
  }
});
