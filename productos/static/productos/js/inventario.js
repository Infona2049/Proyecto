/*
  inventario.js
  Scripts específicos para la página de inventario:
    - Confirmación de eliminación con SweetAlert2
    - Modal visualizador de imagen (abrir imagen centrada al hacer click en el ojo)
*/

document.addEventListener('DOMContentLoaded', function() {
  // Confirmación de eliminación
  document.querySelectorAll('.btn-eliminar').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const form = btn.closest('form');
      if (!form) return;
      Swal.fire({
        title: '¿Estás seguro?',
        text: '¡Esta acción eliminará el registro de forma permanente!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });

  // Modal visualizador de imagen
  const modalEl = document.getElementById('imagenModal');
  const modalImg = document.getElementById('imagenModalImg');
  if (!modalEl || !modalImg) return; // Solo ejecutar si existe el modal en la página

  if (typeof bootstrap === 'undefined') return; // requiere bootstrap.bundle

  const bsModal = new bootstrap.Modal(modalEl);
  document.querySelectorAll('.btn-visualizar').forEach(btn => {
    btn.addEventListener('click', function(e){
      const url = this.dataset.imageUrl;
      if (!url) return;
      modalImg.src = url;
      const row = this.closest('tr');
      const nombre = row ? row.querySelector('td:nth-child(2)')?.innerText.trim() : '';
      modalImg.alt = nombre || 'Imagen producto';
      bsModal.show();
    });
  });

  modalEl.addEventListener('hidden.bs.modal', function(){
    modalImg.src = '';
    modalImg.alt = '';
  });
});

