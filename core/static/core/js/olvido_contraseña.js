// Variables globales para almacenar el correo y código
let emailGlobal = '';
let codigoGlobal = '';
let tiempoRestante = 0;
let intervaloReenvio = null;
// Indica si llegamos desde el flujo de registro (para mostrar alerta de exito y redirigir)
let is_registration_flow = false;

// Función para mostrar/ocultar contraseñas
function togglePasswordVisibility(inputId, toggleIcon) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  if (input.type === 'password') {
    input.type = 'text';
    toggleIcon.classList.add('active');
  } else {
    input.type = 'password';
    toggleIcon.classList.remove('active');
  }
}

async function reenviarCodigo() {
  const linkReenviar = document.getElementById('reenviar-codigo');
  if (!linkReenviar || linkReenviar.classList.contains('disabled')) return;

  // Reutilizar la función de enviar código
  const correoInput = document.getElementById('correo-input');
  const correoAnterior = correoInput ? correoInput.value : '';
  if(correoInput) correoInput.value = emailGlobal;

  await enviarCodigo();

  if(correoInput) correoInput.value = correoAnterior;
}

async function enviarCodigo(btn = null){
  const correoEl = document.getElementById('correo-input');
  const correo = correoEl ? correoEl.value.trim() : '';
  const err = document.getElementById('correo-error');
  const btnEl = btn || (correoEl ? correoEl.closest('div').querySelector('button') : null);
  
  if(!correo){
    err.textContent = 'El correo es obligatorio.';
    err.classList.remove('hidden');
    return;
  }

  // Validar formato de correo
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if(!emailRegex.test(correo)){
    err.textContent = 'El formato del correo no es válido.';
    err.classList.remove('hidden');
    return;
  }

  // Deshabilitar botón mientras se procesa
  if(btnEl){ btnEl.disabled = true; btnEl.textContent = 'Enviando...'; }

  try {
    const response = await fetch('/api/enviar-codigo-recuperacion/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ email: correo })
    });

    const data = await response.json();

    if(data.status === 'ok'){
      emailGlobal = correo;
      console.log('✅ Código enviado exitosamente');
      mostrarPantalla('codigo');
      iniciarTemporizadorReenvio();
    } else {
      err.textContent = data.message || 'Error al enviar el código.';
      err.classList.remove('hidden');
    }
  } catch(error) {
    console.error('Error:', error);
    err.textContent = 'Error de conexión. Inténtalo de nuevo.';
    err.classList.remove('hidden');
  } finally {
    if(btnEl){ btnEl.disabled = false; btnEl.textContent = 'Enviar código'; }
  }
}

// (No password visibility toggles initialized here)

async function verificarCodigo(btn = null){
  const codigoEl = document.getElementById('codigo-input');
  const codigo = codigoEl ? codigoEl.value.trim() : '';
  const err = document.getElementById('codigo-error');
  const btnEl = btn || (codigoEl ? codigoEl.closest('div').querySelector('button') : null);

  if(!codigo){
    if(err){ err.textContent = 'Debes ingresar el código.'; err.classList.remove('hidden'); }
    return;
  }

  if(codigo.length !== 6){
    if(err){ err.textContent = 'El código debe tener 6 dígitos.'; err.classList.remove('hidden'); }
    return;
  }

  if(btnEl){ btnEl.disabled = true; btnEl.textContent = 'Verificando...'; }

  try {
    const response = await fetch('/api/verificar-codigo-recuperacion/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ 
        email: emailGlobal,
        codigo: codigo 
      })
    });

    const data = await response.json();

    if(data.status === 'ok'){
      codigoGlobal = codigo;
      console.log('✅ Código verificado');
      // Si venimos del registro, mostrar SweetAlert2 de usuario registrado y redirigir al login
      if(is_registration_flow && typeof Swal !== 'undefined'){
        try{
          Swal.fire({
            icon: 'success',
            title: 'Usuario registrado con éxito',
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true
          });
          // Redirigir al login después de 2 segundos
          setTimeout(() => { window.location.href = '/login/'; }, 2000);
        }catch(e){
          // Fallback: ir al login
          window.location.href = '/login/';
        }
      } else if(is_registration_flow){
        // Si Swal no está disponible, redirigir inmediatamente
        window.location.href = '/login/';
      } else {
        mostrarPantalla('reset');
      }
    } else {
      if(err){ err.textContent = data.message || 'Código incorrecto.'; err.classList.remove('hidden'); }
    }
  } catch(error) {
    console.error('Error:', error);
    if(err){ err.textContent = 'Error de conexión. Inténtalo de nuevo.'; err.classList.remove('hidden'); }
  } finally {
    if(btnEl){ btnEl.disabled = false; btnEl.textContent = 'Verificar código'; }
  }
}

async function guardarNueva(btn = null){
  const p1El = document.getElementById('newpass');
  const p2El = document.getElementById('confpass');
  const p1 = p1El ? p1El.value : '';
  const p2 = p2El ? p2El.value : '';
  const err = document.getElementById('reset-error');
  const btnEl = btn || ((document.activeElement && document.activeElement.tagName === 'BUTTON') ? document.activeElement : null);

  if(!p1 || !p2){
    if(err){ err.textContent = 'Ambos campos son obligatorios.'; err.classList.remove('hidden'); }
    return;
  }
  
  if(p1 !== p2){
    if(err){ err.textContent = 'Las contraseñas no coinciden.'; err.classList.remove('hidden'); }
    return;
  }

  if(p1.length < 8){
    if(err){ err.textContent = 'La contraseña debe tener al menos 8 caracteres.'; err.classList.remove('hidden'); }
    return;
  }

  if(btnEl){ btnEl.disabled = true; btnEl.textContent = 'Guardando...'; }

  try {
    const response = await fetch('/api/restablecer-contrasena/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ 
        email: emailGlobal,
        codigo: codigoGlobal,
        password: p1
      })
    });

    const data = await response.json();

    if(data.status === 'ok'){
      console.log('✅ Contraseña restablecida');
      mostrarPantalla('success');
    } else {
      if(err){ err.textContent = data.message || 'Error al restablecer la contraseña.'; err.classList.remove('hidden'); }
    }
  } catch(error) {
    console.error('Error:', error);
    if(err){ err.textContent = 'Error de conexión. Inténtalo de nuevo.'; err.classList.remove('hidden'); }
  } finally {
    if(btnEl){ btnEl.disabled = false; btnEl.textContent = 'Guardar nueva contraseña'; }
  }
}

function irLogin(){
  window.location.href = "/login/"; 
}

// La inicialización (mostrar pantalla por hash) se realiza en la plantilla
// y las utilidades compartidas se han movido a `validacion_common.js`.
