document.addEventListener("DOMContentLoaded", () => {
  /* ========== Referencias a elementos del DOM ========== */
  const form        = document.getElementById("formulario");     
  const btnCancelar = document.getElementById("btn-cancelar");   
  const modal       = document.getElementById("modal-exito");   
  const closeBtn    = document.querySelector(".close-btn");      

  // === Botón "Cancelar" ===
  btnCancelar.addEventListener("click", () => {
    form.reset();
    window.location.href = "visualizacion_superAdmin.html";
  });

  // === Validación de formulario y mostrar modal ===
  form.addEventListener("submit", (e) => {
    e.preventDefault();  
    const numeroDocumento = document.getElementById("numeroDocumento");
    if (!/^\d+$/.test(numeroDocumento.value)) {
      alert("El número de documento solo debe contener dígitos.");
      numeroDocumento.focus();
      return;           
    }

    modal.style.display = "flex"; // Mostrar modal
  });

  // === Cerrar modal ===
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
    window.location.href = "visualizacion_superAdmin.html";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
      window.location.href = "visualizacion_superAdmin.html";
    }
  });

  /* ========== Dropdown usuario (Nombre) ========== */
  const dropdownToggle = document.querySelector(".usuario");
  const dropdownMenu = document.querySelector(".dropdown-usuario");

  if (dropdownToggle && dropdownMenu) {
    dropdownToggle.addEventListener("click", (e) => {
      e.stopPropagation(); // Evita que el evento global lo cierre
      dropdownMenu.classList.toggle("visible");
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".usuario-container")) {
        dropdownMenu.classList.remove("visible");
      }
    });

    // Opcional: cerrar con tecla ESC
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        dropdownMenu.classList.remove("visible");
      }
    });
  }
});
