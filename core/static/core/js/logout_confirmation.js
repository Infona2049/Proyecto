/**
 * ALERTA DE CONFIRMACIÓN PARA CERRAR SESIÓN
 * Muestra una alerta personalizada moderna con diseño mejorado
 */

function showLogoutConfirmation(event, url) {
    event.preventDefault(); // Prevenir navegación inmediata
    
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.className = 'logout-alert-overlay';
    overlay.id = 'logoutAlertOverlay';
    
    // Crear contenedor de la alerta
    overlay.innerHTML = `
        <div class="logout-alert-box">
            <div class="logout-alert-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
            </div>
            <h2 class="logout-alert-title">¿Cerrar sesión?</h2>
            <p class="logout-alert-message">¿Estás seguro de que deseas cerrar tu sesión actual?</p>
            <div class="logout-alert-buttons">
                <button class="logout-btn-cancel" onclick="closeLogoutAlert()">Cancelar</button>
                <button class="logout-btn-confirm" onclick="confirmLogout('${url}')">Cerrar sesión</button>
            </div>
        </div>
    `;
    
    // Agregar al body
    document.body.appendChild(overlay);
    
    // Animar entrada
    setTimeout(() => {
        overlay.classList.add('show');
    }, 10);
}

function closeLogoutAlert() {
    const overlay = document.getElementById('logoutAlertOverlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => {
            overlay.remove();
        }, 300);
    }
}

function confirmLogout(url) {
    // Cerrar alerta
    closeLogoutAlert();
    
    // Pequeño delay para animación y luego redirigir
    setTimeout(() => {
        window.location.href = url;
    }, 200);
}

// Cerrar al hacer clic fuera de la alerta
document.addEventListener('click', function(event) {
    const overlay = document.getElementById('logoutAlertOverlay');
    if (overlay && event.target === overlay) {
        closeLogoutAlert();
    }
});

// Cerrar con tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeLogoutAlert();
    }
});
