function mostrarPantalla(id) {
  document.querySelectorAll('.container > div').forEach(div => div.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');

  ['correo-error','codigo-error','reset-error'].forEach(idErr => {
    const el = document.getElementById(idErr);
    if(el){ el.classList.add('hidden'); el.textContent = ''; }
  });
}

function enviarCodigo(){
  const correo = document.getElementById('correo-input').value.trim();
  const err = document.getElementById('correo-error');
  if(!correo){
    err.textContent = 'El correo es obligatorio.';
    err.classList.remove('hidden');
    return;
  }
  mostrarPantalla('codigo');
}

function verificarCodigo(){
  const codigo = document.getElementById('codigo-input').value.trim();
  const err = document.getElementById('codigo-error');
  if(!codigo){
    err.textContent = 'Debes ingresar el código.';
    err.classList.remove('hidden');
    return;
  }
  mostrarPantalla('reset');
}

function guardarNueva(){
  const p1 = document.getElementById('newpass').value;
  const p2 = document.getElementById('confpass').value;
  const err = document.getElementById('reset-error');

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

  mostrarPantalla('success');
}

function irLogin(){
  window.location.href = "../login.html"; 
}


// mostrar inicio (pantalla correo)
mostrarPantalla('correo');
