// Archivo: validacion_correo.js
// Lógica separada para envío y verificación de código de validación de correo

// Variables globales para almacenar el correo y código
let emailGlobal = '';
let codigoGlobal = '';
let tiempoRestante = 0;
let intervaloReenvio = null;
// Indica si venimos del flujo de registro (para mostrar alerta y redirigir)
let is_registration_flow = false;
// Indica si venimos del flujo de cambio de correo (para mostrar éxito y redirigir al login)
let is_email_change_flow = false;

async function reenviarCodigo() {
  const linkReenviar = document.getElementById('reenviar-codigo');
  if (!linkReenviar || linkReenviar.classList.contains('disabled')) return;

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
    if(err){ err.textContent = 'El correo es obligatorio.'; err.classList.remove('hidden'); }
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if(!emailRegex.test(correo)){
    if(err){ err.textContent = 'El formato del correo no es válido.'; err.classList.remove('hidden'); }
    return;
  }

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
      mostrarPantalla('codigo');
      iniciarTemporizadorReenvio();
    } else {
      if(err){ err.textContent = data.message || 'Error al enviar el código.'; err.classList.remove('hidden'); }
    }
  } catch(e){
    console.error('Error:', e);
    if(err){ err.textContent = 'Error de conexión. Inténtalo de nuevo.'; err.classList.remove('hidden'); }
    } finally {
    if(btnEl){ btnEl.disabled = false; btnEl.textContent = 'Enviar código'; }
  }
}

async function verificarCodigo(){
  const codigoEl = document.getElementById('codigo-input');
  const codigo = codigoEl ? codigoEl.value.trim() : '';
  const err = document.getElementById('codigo-error');
  const btnEl = (codigoEl ? codigoEl.closest('div').querySelector('button') : null);

  if(!codigo){ if(err){ err.textContent = 'Debes ingresar el código.'; err.classList.remove('hidden'); } return; }
  if(codigo.length !== 6){ if(err){ err.textContent = 'El código debe tener 6 dígitos.'; err.classList.remove('hidden'); } return; }

  if(btnEl){ btnEl.disabled = true; btnEl.textContent = 'Verificando...'; }

  try{
    const response = await fetch('/api/verificar-codigo-recuperacion/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ email: emailGlobal, codigo: codigo })
    });
    const data = await response.json();
    if(data.status === 'ok'){
      codigoGlobal = codigo;
      // Si el backend indica que el correo fue cambiado (flujo de cambio), o que el registro se completó,
      // mostrar éxito y redirigir al login
      if((data.email_changed || data.registration_complete || is_email_change_flow) && typeof Swal !== 'undefined'){
        try{
          const text = data.registration_complete ? 'Registro completado. Inicia sesión con tu nuevo correo.' : 'Tu correo fue validado y actualizado. Inicia sesión con tu nuevo correo.';
          Swal.fire({ icon: 'success', title: 'Operación exitosa', text: text, showConfirmButton: false, timer: 2200, timerProgressBar: true });
          setTimeout(() => { window.location.href = '/login/'; }, 2200);
        } catch(e){ window.location.href = '/login/'; }
      } else if((data.email_changed || data.registration_complete || is_email_change_flow)){
        window.location.href = '/login/';
      }
      // Si venimos del registro, mostrar SweetAlert2 de usuario registrado y redirigir al login
      else if(is_registration_flow && typeof Swal !== 'undefined'){
        try{
          Swal.fire({ icon: 'success', title: 'Usuario registrado con éxito', showConfirmButton: false, timer: 2000, timerProgressBar: true });
          setTimeout(() => { window.location.href = '/login/'; }, 2000);
        }catch(e){ window.location.href = '/login/'; }
      } else if(is_registration_flow){
        window.location.href = '/login/';
      } else {
        mostrarPantalla('success_email');
      }
    } else {
      if(err){ err.textContent = data.message || 'Código incorrecto.'; err.classList.remove('hidden'); }
    }
  } catch(e){ console.error('Error:', e); if(err){ err.textContent = 'Error de conexión. Inténtalo de nuevo.'; err.classList.remove('hidden'); } }
  finally { if(btnEl){ btnEl.disabled = false; btnEl.textContent = 'Verificar código'; } }
}

// Al cargar: si hay hash o fallback mostrar pantalla correspondiente
// Nota: la inicialización del estado (mostrar pantalla por hash o por `auto_email`)
// se realiza desde la plantilla. Las utilidades compartidas (mostrarPantalla,
// iniciarTemporizadorReenvio, getCookie) están en `validacion_common.js`.
