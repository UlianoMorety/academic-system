/**
 * Configuración global de la aplicación
 */

const CONFIG = {
    API_URL: 'http://localhost:5000/api',
    TOKEN_KEY: 'academic_token',
    USER_KEY: 'academic_user'
};

/**
 * Obtiene el token almacenado
 */
function getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
}

/**
 * Guarda el token
 */
function setToken(token) {
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
}

/**
 * Elimina el token
 */
function removeToken() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
}

/**
 * Obtiene el usuario almacenado
 */
function getUser() {
    const userStr = localStorage.getItem(CONFIG.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Guarda el usuario
 */
function setUser(user) {
    localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
}

/**
 * Elimina el usuario
 */
function removeUser() {
    localStorage.removeItem(CONFIG.USER_KEY);
}

/**
 * Cierra sesión
 */
function logout() {
    removeToken();
    removeUser();
    window.location.href = 'login.html';
}

/**
 * Verifica si el usuario está autenticado
 */
function isAuthenticated() {
    return getToken() !== null;
}

/**
 * Redirige al login si no está autenticado
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/**
 * Verifica si el usuario tiene un rol específico
 */
function hasRole(role) {
    const user = getUser();
    return user && user.role === role;
}

/**
 * Verifica si el usuario tiene alguno de los roles especificados
 */
function hasAnyRole(roles) {
    const user = getUser();
    return user && roles.includes(user.role);
}