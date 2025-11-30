/**
 * Manejo de autenticación en el frontend
 */

document.addEventListener('DOMContentLoaded', function() {
    // Si ya está autenticado, redirigir al dashboard
    if (isAuthenticated()) {
        window.location.href = 'dashboard.html';
        return;
    }
    
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const errorMessage = document.getElementById('errorMessage');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Deshabilitar botón
        loginBtn.disabled = true;
        loginBtn.textContent = 'Iniciando sesión...';
        
        // Ocultar mensajes previos
        errorMessage.style.display = 'none';
        
        // Obtener datos del formulario
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        // Validación cliente
        if (!username || !password) {
            showError('Por favor completa todos los campos');
            loginBtn.disabled = false;
            loginBtn.textContent = 'Iniciar Sesión';
            return;
        }
        
        try {
            // Hacer petición al API
            const response = await fetch(`${CONFIG.API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Guardar token y usuario
                setToken(data.data.token);
                setUser(data.data.user);
                
                // Redirigir al dashboard
                window.location.href = 'dashboard.html';
            } else {
                // Mostrar error
                showError(data.message || 'Error al iniciar sesión');
                loginBtn.disabled = false;
                loginBtn.textContent = 'Iniciar Sesión';
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Error de conexión. Verifica que el servidor esté corriendo.');
            loginBtn.disabled = false;
            loginBtn.textContent = 'Iniciar Sesión';
        }
    });
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
});

/**
 * Cliente API genérico con manejo mejorado de errores
 */
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    // Agregar token si existe
    if (token) {
        defaultOptions.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Combinar opciones
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${CONFIG.API_URL}${endpoint}`, finalOptions);
        
        // Si es 401, mostrar mensaje y cerrar sesión después de 3 segundos
        if (response.status === 401) {
            const data = await response.json();
            alert('Tu sesión ha expirado. Serás redirigido al login.');
            setTimeout(() => {
                logout();
            }, 2000);
            return null;
        }
        
        // Si es 429 (rate limit)
        if (response.status === 429) {
            const data = await response.json();
            alert(data.message || 'Demasiadas peticiones. Espera un momento.');
            return { ok: false, status: 429, data };
        }
        
        const data = await response.json();
        return { ok: response.ok, status: response.status, data };
        
    } catch (error) {
        console.error('API Error:', error);
        // Verificar si es error de red
        if (error.message === 'Failed to fetch' || error.message.includes('NetworkError')) {
            alert('Error de conexión. Verifica que el servidor esté corriendo.');
        }
        throw error;
    }
}

/**
 * Función auxiliar para mostrar mensajes
 */
function showMessage(elementId, message, type = 'error') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.textContent = message;
    element.className = type === 'error' ? 'error-message' : 'success-message';
    element.style.display = 'block';
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}