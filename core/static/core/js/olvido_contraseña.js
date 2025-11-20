// Variables globales para almacenar el correo y código
let emailGlobal = '';
let codigoGlobal = '';
let tiempoRestante = 0;
let intervaloReenvio = null;

function mostrarPantalla(id) {
  document.querySelectorAll('.container > div').forEach(div => div.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');

  ['correo-error','codigo-error','reset-error'].forEach(idErr => {
    const el = document.getElementById(idErr);
    if(el){ el.classList.add('hidden'); el.textContent = ''; }
  });
}

function iniciarTemporizadorReenvio() {
  tiempoRestante = 60; // 60 segundos de espera
  const linkReenviar = document.getElementById('reenviar-codigo');
  
  if (linkReenviar) {
    linkReenviar.classList.add('disabled');
    linkReenviar.textContent = `Reenviar código (${tiempoRestante}s)`;
    
    if (intervaloReenvio) clearInterval(intervaloReenvio);
    
    intervaloReenvio = setInterval(() => {
      tiempoRestante--;
      linkReenviar.textContent = `Reenviar código (${tiempoRestante}s)`;
      
      if (tiempoRestante <= 0) {
        clearInterval(intervaloReenvio);
        linkReenviar.classList.remove('disabled');
        linkReenviar.textContent = 'Reenviar código';
      }
    }, 1000);
  }
}

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

async function reenviarCodigo() {
  const linkReenviar = document.getElementById('reenviar-codigo');
  
  if (linkReenviar.classList.contains('disabled')) {
    return;
  }
  
  // Reutilizar la función de enviar código
  const correoInput = document.getElementById('correo-input');
  const correoAnterior = correoInput.value;
  correoInput.value = emailGlobal;
  
  await enviarCodigo();
  
  correoInput.value = correoAnterior;
}

async function enviarCodigo(){
  const correo = document.getElementById('correo-input').value.trim();
  const err = document.getElementById('correo-error');
  const btn = event.target;
  
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
  btn.disabled = true;
  btn.textContent = 'Enviando...';

  try {
    const response = await fetch('/api/enviar-codigo-recuperacion/', {
      method: 'POST',
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
    btn.disabled = false;
    btn.textContent = 'Enviar código';
  }
}

async function verificarCodigo(){
  const codigo = document.getElementById('codigo-input').value.trim();
  const err = document.getElementById('codigo-error');
  const btn = event.target;
  
  if(!codigo){
    err.textContent = 'Debes ingresar el código.';
    err.classList.remove('hidden');
    return;
  }

  if(codigo.length !== 6){
    err.textContent = 'El código debe tener 6 dígitos.';
    err.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Verificando...';

  try {
    const response = await fetch('/api/verificar-codigo-recuperacion/', {
      method: 'POST',
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
      mostrarPantalla('reset');
    } else {
      err.textContent = data.message || 'Código incorrecto.';
      err.classList.remove('hidden');
    }
  } catch(error) {
    console.error('Error:', error);
    err.textContent = 'Error de conexión. Inténtalo de nuevo.';
    err.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Verificar código';
  }
}

async function guardarNueva(){
  const p1 = document.getElementById('newpass').value;
  const p2 = document.getElementById('confpass').value;
  const err = document.getElementById('reset-error');
  const btn = event.target;

  if(!p1 || !p2){
    err.textContent = 'Ambos campos son obligatorios.';
    err.classList.remove('hidden');
    return;
  }
  
  if(p1 !== p2){
    err.textContent = 'Las contraseñas no coinciden.';
    err.classList.remove('hidden');
    return;
  }

  if(p1.length < 8){
    err.textContent = 'La contraseña debe tener al menos 8 caracteres.';
    err.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Guardando...';

  try {
    const response = await fetch('/api/restablecer-contrasena/', {
      method: 'POST',
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
      err.textContent = data.message || 'Error al restablecer la contraseña.';
      err.classList.remove('hidden');
    }
  } catch(error) {
    console.error('Error:', error);
    err.textContent = 'Error de conexión. Inténtalo de nuevo.';
    err.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Guardar nueva contraseña';
  }
}

function irLogin(){
  window.location.href = "/login/"; 
}

// mostrar inicio (pantalla correo)
mostrarPantalla('correo');
