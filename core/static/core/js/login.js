/* =========================================================
   LÓGICA DE INICIO DE SESIÓN (con SweetAlert2 y Django)
========================================================= */
function login(event) {
  event.preventDefault(); // Cancela el submit real

  const form = event.target;
  const formData = new FormData(form);

  // Realizar petición AJAX
  fetch(form.action || window.location.pathname, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      Swal.fire({
        icon: 'success',
        title: data.message,
        text: 'Redirigiendo a tu panel...',
        showConfirmButton: false,
        timer: 2000
      }).then(() => {
        window.location.href = data.redirect_url;
      });
    } else {
      // Verificar si el usuario está bloqueado
      if (data.bloqueado) {
        Swal.fire({
          icon: 'warning',
          title: 'Usuario Bloqueado',
          text: data.message,
          confirmButtonText: 'Entendido',
          allowOutsideClick: false,
          showCloseButton: false
        });
      } else if (data.intentos_restantes !== undefined) {
        // Mostrar intentos restantes
        let iconType = 'warning';
        let title = 'Credenciales Incorrectas';
        
        if (data.intentos_restantes === 1) {
          iconType = 'error';
          title = '¡Último Intento!';
        } else if (data.intentos_restantes === 2) {
          iconType = 'warning';
        }
        
        Swal.fire({
          icon: iconType,
          title: title,
          text: data.message,
          confirmButtonText: 'Intentar de nuevo',
          footer: data.intentos_restantes > 0 ? 
            `<span style="color: #e74c3c; font-weight: bold;">⚠️ Intentos restantes: ${data.intentos_restantes}</span>` : 
            '<span style="color: #e74c3c; font-weight: bold;">🚫 Sin intentos restantes</span>'
        });
      } else {
        // Error genérico
        Swal.fire({
          icon: 'error',
          title: 'Error de autenticación',
          text: data.message,
          confirmButtonText: 'Intentar de nuevo'
        });
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
    Swal.fire({
      icon: 'error',
      title: 'Error de conexión',
      text: 'No se pudo conectar con el servidor. Por favor, intenta de nuevo.',
      confirmButtonText: 'Intentar de nuevo'
    });
  });
}

/* =========================================================
   OJITO PARA MOSTRAR / OCULTAR CONTRASEÑA (FontAwesome)
========================================================= */
document.addEventListener("DOMContentLoaded", () => {
  const togglePassword = document.getElementById("togglePassword");
  const passwordInput = document.getElementById("password");

  if (togglePassword && passwordInput) {
    togglePassword.addEventListener("click", () => {
      const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
      passwordInput.setAttribute("type", type);

      // Cambiar el ícono con FontAwesome
      const icon = togglePassword.querySelector("i");
      if (type === "password") {
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
      } else {
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
      }
    });
  }
});
