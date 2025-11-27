// Archivo: validacion_common.js
// Funciones y utilidades compartidas por las páginas de validación y restablecimiento

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function mostrarPantalla(id) {
  const containers = document.querySelectorAll('.container > div');
  containers.forEach(div => div.classList.add('hidden'));
  const el = document.getElementById(id);
  if (el) el.classList.remove('hidden');

  ['correo-error','codigo-error','reset-error'].forEach(idErr => {
    const elErr = document.getElementById(idErr);
    if (elErr) { elErr.classList.add('hidden'); elErr.textContent = ''; }
  });
}

function iniciarTemporizadorReenvio() {
  // Asume que los archivos que usan esta función declaran las variables
  // `tiempoRestante` y `intervaloReenvio` en su propio scope global.
  if (typeof tiempoRestante === 'undefined') tiempoRestante = 0;
  if (typeof intervaloReenvio !== 'undefined' && intervaloReenvio) clearInterval(intervaloReenvio);

  tiempoRestante = 60; // 60 segundos
  const linkReenviar = document.getElementById('reenviar-codigo');
  if (!linkReenviar) return;

  linkReenviar.classList.add('disabled');
  linkReenviar.textContent = `Reenviar código (${tiempoRestante}s)`;

  intervaloReenvio = setInterval(() => {
    tiempoRestante--;
    linkReenviar.textContent = `Reenviar código (${tiempoRestante}s)`;
    if (tiempoRestante <= 0) {
      clearInterval(intervaloReenvio);
      linkReenviar.classList.remove('disabled');
      linkReenviar.textContent = 'Reenviar código';
      intervaloReenvio = null;
    }
  }, 1000);
}

function irLogin(){
  window.location.href = '/login/';
}
