/**
 * Lógica de gestión de usuarios (Frontend)
 */

let currentPage = 1;
let isEditMode = false;

document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación y permisos
    if (!requireAuth()) return;
    
    const user = getUser();
    if (!hasAnyRole(['admin', 'administrative'])) {
        alert('No tienes permisos para acceder a esta página');
        window.location.href = 'dashboard.html';
        return;
    }
    
    // Mostrar información del usuario
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userRole').textContent = user.role;
    
    // Cargar usuarios
    loadUsers();
});

/**
 * Carga la lista de usuarios
 */
async function loadUsers(page = 1) {
    currentPage = page;
    const container = document.getElementById('usersTableContainer');
    
    try {
        const response = await apiRequest(`/users?page=${page}&limit=20`);
        
        if (response && response.ok && response.data.success) {
            const { users, pagination } = response.data.data;
            renderUsersTable(users, pagination);
        } else {
            container.innerHTML = '<div class="error-message">Error al cargar usuarios</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="error-message">Error de conexión</div>';
    }
}

/**
 * Renderiza la tabla de usuarios
 */
function renderUsersTable(users, pagination) {
    const container = document.getElementById('usersTableContainer');
    
    if (users.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No hay usuarios registrados</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Email</th>
                        <th>Rol</th>
                        <th>Estado</th>
                        <th>Fecha Registro</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    users.forEach(user => {
        const statusBadge = user.is_active 
            ? '<span class="badge badge-success">Activo</span>'
            : '<span class="badge badge-danger">Inactivo</span>';
        
        const roleBadge = getRoleBadge(user.role_name);
        const formattedDate = formatDate(user.created_at);
        
        html += `
            <tr>
                <td>${user.id}</td>
                <td><strong>${escapeHtml(user.username)}</strong></td>
                <td>${escapeHtml(user.email)}</td>
                <td>${roleBadge}</td>
                <td>${statusBadge}</td>
                <td>${formattedDate}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">
                            Editar
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')">
                            Eliminar
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    // Agregar paginación
    if (pagination.pages > 1) {
        html += renderPagination(pagination);
    }
    
    container.innerHTML = html;
}

/**
 * Renderiza la paginación
 */
function renderPagination(pagination) {
    let html = '<div style="margin-top: 20px; text-align: center;">';
    
    // Botón anterior
    if (pagination.page > 1) {
        html += `<button class="btn btn-secondary btn-sm" onclick="loadUsers(${pagination.page - 1})">← Anterior</button> `;
    }
    
    // Páginas
    html += `<span style="margin: 0 15px;">Página ${pagination.page} de ${pagination.pages}</span>`;
    
    // Botón siguiente
    if (pagination.page < pagination.pages) {
        html += ` <button class="btn btn-secondary btn-sm" onclick="loadUsers(${pagination.page + 1})">Siguiente →</button>`;
    }
    
    html += '</div>';
    return html;
}

/**
 * Muestra el modal para crear usuario
 */
function showCreateModal() {
    isEditMode = false;
    document.getElementById('modalTitle').textContent = 'Nuevo Usuario';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('passwordGroup').style.display = 'block';
    document.getElementById('password').required = true;
    document.getElementById('formMessage').innerHTML = '';
    document.getElementById('userModal').classList.add('show');
}

/**
 * Edita un usuario
 */
async function editUser(userId) {
    try {
        const response = await apiRequest(`/users/${userId}`);
        
        if (response && response.ok && response.data.success) {
            const user = response.data.data;
            
            isEditMode = true;
            document.getElementById('modalTitle').textContent = 'Editar Usuario';
            document.getElementById('userId').value = user.id;
            document.getElementById('username').value = user.username;
            document.getElementById('email').value = user.email;
            document.getElementById('role').value = user.role_name;
            document.getElementById('passwordGroup').style.display = 'none';
            document.getElementById('password').required = false;
            document.getElementById('formMessage').innerHTML = '';
            document.getElementById('userModal').classList.add('show');
        } else {
            showMessage('messageContainer', 'Error al cargar usuario', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('messageContainer', 'Error de conexión', 'error');
    }
}

/**
 * Guarda el usuario (crear o editar)
 */
async function saveUser() {
    const userId = document.getElementById('userId').value;
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    
    // Validaciones
    if (!username || !email || !role) {
        document.getElementById('formMessage').innerHTML = 
            '<div class="error-message">Por favor completa todos los campos requeridos</div>';
        return;
    }
    
    if (!isEditMode && !password) {
        document.getElementById('formMessage').innerHTML = 
            '<div class="error-message">La contraseña es requerida</div>';
        return;
    }
    
    const data = { username, email, role };
    if (!isEditMode) {
        data.password = password;
    }
    
    try {
        let response;
        if (isEditMode) {
            response = await apiRequest(`/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            response = await apiRequest('/users', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
        
        if (response && response.ok && response.data.success) {
            closeModal();
            showMessage('messageContainer', response.data.message, 'success');
            loadUsers(currentPage);
        } else {
            document.getElementById('formMessage').innerHTML = 
                `<div class="error-message">${response.data.message}</div>`;
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('formMessage').innerHTML = 
            '<div class="error-message">Error de conexión</div>';
    }
}

/**
 * Elimina un usuario
 */
async function deleteUser(userId, username) {
    if (!confirm(`¿Estás seguro de eliminar al usuario "${username}"?`)) {
        return;
    }
    
    try {
        const response = await apiRequest(`/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok && response.data.success) {
            showMessage('messageContainer', 'Usuario eliminado exitosamente', 'success');
            loadUsers(currentPage);
        } else {
            showMessage('messageContainer', response.data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('messageContainer', 'Error al eliminar usuario', 'error');
    }
}

/**
 * Cierra el modal
 */
function closeModal() {
    document.getElementById('userModal').classList.remove('show');
}

/**
 * Retorna el badge HTML según el rol
 */
function getRoleBadge(role) {
    const badges = {
        'admin': '<span class="badge badge-danger">Admin</span>',
        'teacher': '<span class="badge badge-primary">Profesor</span>',
        'student': '<span class="badge badge-success">Estudiante</span>',
        'administrative': '<span class="badge badge-warning">Administrativo</span>'
    };
    return badges[role] || role;
}

/**
 * Formatea una fecha
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('userModal');
    if (event.target === modal) {
        closeModal();
    }
}