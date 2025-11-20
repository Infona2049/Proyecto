document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const password = document.getElementById("id_password1");
  const confirmPassword = document.getElementById("id_password2");
  const togglePassword = document.getElementById("togglePassword");
  const toggleConfirmPassword = document.getElementById("toggleConfirmPassword");

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

  // Validación del formulario
  form.addEventListener("submit", (e) => {
    // Validar que las contraseñas coincidan (si existen ambos campos)
    if (password && confirmPassword && password.value !== confirmPassword.value) {
      e.preventDefault();
      Swal.fire({
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
        e.preventDefault();
        Swal.fire({
          icon: "warning",
          title: "Correo inválido",
          text: "Por favor ingresa un correo electrónico válido.",
        });
        return;
      }
    }

    // Si llegamos aquí, permitir que el formulario se envíe normalmente
    // No hacer preventDefault() para que Django procese el formulario
  });
});
