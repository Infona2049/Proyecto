document.addEventListener("DOMContentLoaded", () => {
  const hasSwal = typeof Swal !== "undefined";

  function showAlert(options = {}, callback) {
    const {
      icon = "info",
      title = "",
      html = "",
      text = "",
      confirmButtonText = "OK",
      confirmButtonColor = "#003f87",
      timer = null,
      allowOutsideClick = true,
      allowEscapeKey = true,
      customClass = {},
      showClass = {},
      hideClass = {},
      didOpen = null
    } = options;

    if (hasSwal) {
      Swal.fire({
        icon,
        title,
        html: html || text,
        confirmButtonText,
        confirmButtonColor,
        timer,
        timerProgressBar: !!timer,
        allowOutsideClick,
        allowEscapeKey,
        customClass,
        showClass,
        hideClass,
        didOpen
      }).then(() => {
        if (typeof callback === "function") callback();
      });
    } else {
      // Fallback simple: mostrar alert y ejecutar callback
      try {
        const plain = (html || text).replace(/<[^>]+>/g, "\n");
        window.alert((title ? title + "\n\n" : "") + plain);
      } catch (e) {
        window.alert(title || text || html || "");
      }
      if (typeof callback === "function") callback();
    }
  }

  // === MOSTRAR MENSAJES DE DJANGO (con fallback) ===
  const messagesContainer = document.getElementById("django-messages");
  if (messagesContainer) {
    const messages = messagesContainer.querySelectorAll(".message-item");

    messages.forEach((msgElement) => {
      const type = msgElement.getAttribute("data-type");
      const text = msgElement.getAttribute("data-text");

      if (type === "success") {
        // No mostrar la alerta de éxito en este caso; redirigir al apartado de foto
          window.location.href = "/validacion_correo/";
        return;
      } else if (type === "error") {
        showAlert({
          icon: "error",
          title: "Error",
          text: text,
          confirmButtonText: "Entendido",
          confirmButtonColor: "#dc3545"
        });
      } else {
        showAlert({
          icon: "warning",
          title: "Atención",
          text: text,
          confirmButtonText: "Entendido",
          confirmButtonColor: "#ffc107"
        });
      }
    });
  }

  const form = document.querySelector("form");
  const password = document.getElementById("id_password1");
  const confirmPassword = document.getElementById("id_password2");
  const togglePassword = document.getElementById("togglePassword");
  const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");
  const passwordRequirements = document.getElementById("passwordRequirements");

  // Validación en tiempo real de requisitos de contraseña
  if (password && passwordRequirements) {
    password.addEventListener("focus", () => {
      passwordRequirements.style.display = "block";
    });

    password.addEventListener("input", () => {
      const value = password.value;
      
      // Validar longitud mínima
      const reqLength = document.getElementById("req-length");
      if (value.length >= 8) {
        reqLength.className = "req-valid";
        reqLength.innerHTML = "✓ Mínimo 8 caracteres";
      } else {
        reqLength.className = "req-invalid";
        reqLength.innerHTML = "✗ Mínimo 8 caracteres";
      }
      
      // Validar letra mayúscula
      const reqUppercase = document.getElementById("req-uppercase");
      if (/[A-Z]/.test(value)) {
        reqUppercase.className = "req-valid";
        reqUppercase.innerHTML = "✓ Una letra mayúscula (A-Z)";
      } else {
        reqUppercase.className = "req-invalid";
        reqUppercase.innerHTML = "✗ Una letra mayúscula (A-Z)";
      }
      
      // Validar letra minúscula
      const reqLowercase = document.getElementById("req-lowercase");
      if (/[a-z]/.test(value)) {
        reqLowercase.className = "req-valid";
        reqLowercase.innerHTML = "✓ Una letra minúscula (a-z)";
      } else {
        reqLowercase.className = "req-invalid";
        reqLowercase.innerHTML = "✗ Una letra minúscula (a-z)";
      }
      
      // Validar número
      const reqNumber = document.getElementById("req-number");
      if (/\d/.test(value)) {
        reqNumber.className = "req-valid";
        reqNumber.innerHTML = "✓ Un número (0-9)";
      } else {
        reqNumber.className = "req-invalid";
        reqNumber.innerHTML = "✗ Un número (0-9)";
      }
      
      // Validar carácter especial
      const reqSpecial = document.getElementById("req-special");
      if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;`~]/.test(value)) {
        reqSpecial.className = "req-valid";
        reqSpecial.innerHTML = "✓ Un carácter especial (!@#$%^&*)";
      } else {
        reqSpecial.className = "req-invalid";
        reqSpecial.innerHTML = "✗ Un carácter especial (!@#$%^&*)";
      }
    });
  }

  // Mostrar / ocultar contraseña
  if (togglePassword && password) {
    togglePassword.addEventListener("click", () => {
      const type = password.type === "password" ? "text" : "password";
      password.type = type;
      
      // Cambiar icono
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

  if (toggleConfirmPassword && confirmPassword) {
    toggleConfirmPassword.addEventListener("click", () => {
      const type = confirmPassword.type === "password" ? "text" : "password";
      confirmPassword.type = type;
      
      // Cambiar icono
      const icon = toggleConfirmPassword.querySelector("i");
      if (type === "password") {
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
      } else {
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
      }
    });
  }

  // Validación y envío del formulario
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault(); // Siempre prevenir el envío por defecto
      console.log("Formulario enviado - validando términos...");
      
      // Validar checkbox de términos y condiciones PRIMERO
      const checkboxTerminos = document.getElementById("aceptarTerminos");
      console.log("Checkbox encontrado:", checkboxTerminos);
      console.log("Checkbox checked:", checkboxTerminos ? checkboxTerminos.checked : "no encontrado");
      
      if (checkboxTerminos && !checkboxTerminos.checked) {
        console.log("Mostrando alerta de términos...");

        showAlert({
          icon: "error",
          title: "Términos y Condiciones Requeridos",
          html: "Debes <strong>aceptar los Términos y Condiciones</strong> y la <strong>Política de Privacidad</strong> para poder registrarte.",
          confirmButtonText: "Entendido",
          confirmButtonColor: "#003f87"
        });
        
        // Resaltar el checkbox
        const terminosContainer = document.querySelector(".terminos-container");
        if (terminosContainer) {
          terminosContainer.style.border = "2px solid #dc3545";
          terminosContainer.style.padding = "10px";
          terminosContainer.style.borderRadius = "8px";
          terminosContainer.style.backgroundColor = "#fff3cd";
          
          setTimeout(() => {
            terminosContainer.style.border = "";
            terminosContainer.style.padding = "";
            terminosContainer.style.backgroundColor = "";
          }, 3000);
        }
        return;
      }

      // Validar requisitos de contraseña
      if (password && password.value) {
        const value = password.value;
        let errorMessage = "";
        
        if (value.length < 8) {
          errorMessage += "• Debe tener al menos 8 caracteres<br>";
        }
        if (!/[A-Z]/.test(value)) {
          errorMessage += "• Debe contener al menos una letra mayúscula<br>";
        }
        if (!/[a-z]/.test(value)) {
          errorMessage += "• Debe contener al menos una letra minúscula<br>";
        }
        if (!/\d/.test(value)) {
          errorMessage += "• Debe contener al menos un número<br>";
        }
        if (!/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;`~]/.test(value)) {
          errorMessage += "• Debe contener al menos un carácter especial (!@#$%^&*)<br>";
        }
        
        if (errorMessage) {
          showAlert({
            icon: "error",
            title: "Contraseña no válida",
            html: errorMessage,
            confirmButtonText: "Entendido",
            confirmButtonColor: "#003f87"
          });
          return;
        }
      }

      // Validar que las contraseñas coincidan (si existen ambos campos)
      if (password && confirmPassword && password.value !== confirmPassword.value) {
        showAlert({
          icon: "error",
          title: "Contraseñas no coinciden",
          text: "Debes asegurarte de que ambas contraseñas sean iguales.",
        });
        return;
      }

      // Validar que el email tenga formato correcto
      const email = form.querySelector("input[type='email']");
      if (email && email.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
          showAlert({
            icon: "warning",
            title: "Correo inválido",
            text: "Por favor ingresa un correo electrónico válido.",
          });
          return;
        }
      }

      // Si todas las validaciones pasan, enviar el formulario por AJAX
      const formData = new FormData(form);
      
      try {
        const response = await fetch(form.action || window.location.href, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest"
          }
        });
        
        const result = await response.json();
        
        if (result.success) {
          // No mostrar la alerta de éxito aquí (se utilizará después).
          // Redirigir directamente a la validación de correo y al apartado de foto.
            window.location.href = "/validacion_correo/";
        } else {
          // Mostrar errores
          showAlert({
            icon: "error",
            title: "Error en el registro",
            html: result.message || "Ocurrió un error al registrar el usuario.",
            confirmButtonText: "Entendido",
            confirmButtonColor: "#dc3545"
          });
        }
      } catch (error) {
        console.error("Error al enviar formulario:", error);
        showAlert({
          icon: "error",
          title: "Error de conexión",
          text: "No se pudo conectar con el servidor. Intenta de nuevo.",
          confirmButtonText: "Entendido",
          confirmButtonColor: "#dc3545"
        });
      }
    });
  } else {
    console.error("Formulario no encontrado!");
  }
});

// === FUNCIONES PARA MODALES DE TÉRMINOS Y POLÍTICAS ===
function abrirModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "block";
    document.body.style.overflow = "hidden"; // Prevenir scroll del body
  }
}

function cerrarModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "none";
    document.body.style.overflow = "auto"; // Restaurar scroll del body
  }
}

// Event listeners para abrir modales
document.addEventListener("DOMContentLoaded", () => {
  const linkTerminos = document.getElementById("linkTerminos");
  const linkPoliticas = document.getElementById("linkPoliticas");

  if (linkTerminos) {
    linkTerminos.addEventListener("click", (e) => {
      e.preventDefault();
      abrirModal("modalTerminos");
    });
  }

  if (linkPoliticas) {
    linkPoliticas.addEventListener("click", (e) => {
      e.preventDefault();
      abrirModal("modalPoliticas");
    });
  }

  // Cerrar modal al hacer clic en la X
  const closeButtons = document.querySelectorAll(".close");
  closeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const modalId = btn.getAttribute("data-modal");
      if (modalId) {
        cerrarModal(modalId);
      }
    });
  });

  // Cerrar modal al hacer clic fuera del contenido
  window.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal")) {
      e.target.style.display = "none";
      document.body.style.overflow = "auto";
    }
  });

  // Cerrar modal con tecla ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const modals = document.querySelectorAll(".modal");
      modals.forEach((modal) => {
        if (modal.style.display === "block") {
          modal.style.display = "none";
          document.body.style.overflow = "auto";
        }
      });
    }
  });
});
