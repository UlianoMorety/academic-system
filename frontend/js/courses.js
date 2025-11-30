/**
 * Lógica de gestión de cursos (Frontend)
 */

let currentPage = 1;
let isEditMode = false;

document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación
    if (!requireAuth()) return;
    
    const user = getUser();
    
    // Mostrar información del usuario
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userRole').textContent = user.role;
    
    // Mostrar botón crear solo para admin y teacher
    if (hasAnyRole(['admin', 'teacher'])) {
        document.getElementById('createBtn').style.display = 'block';
    }
    
    // Cargar cursos
    loadCourses();
});

/**
 * Carga la lista de cursos
 */
async function loadCourses(page = 1) {
    currentPage = page;
    const container = document.getElementById('coursesContainer');
    
    try {
        const response = await apiRequest(`/courses?page=${page}&limit=20`);
        
        if (response && response.ok && response.data.success) {
            const { courses, pagination } = response.data.data;
            renderCourses(courses, pagination);
        } else {
            container.innerHTML = '<div class="error-message">Error al cargar cursos</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="error-message">Error de conexión</div>';
    }
}

/**
 * Renderiza los cursos
 */
function renderCourses(courses, pagination) {
    const container = document.getElementById('coursesContainer');
    const user = getUser();
    
    if (courses.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📚</div>
                <p>No hay cursos disponibles</p>
            </div>
        `;
        return;
    }
    
    let html = '<div style="display: grid; gap: 20px;">';
    
    courses.forEach(course => {
        const canEdit = user.role === 'admin' || course.teacher_id === user.id;
        const formattedDate = formatDate(course.created_at);
        
        html += `
            <div class="card" style="margin: 0;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h3 style="margin: 0 0 10px 0; color: var(--primary-color);">
                            ${escapeHtml(course.name)}
                        </h3>
                        <p style="margin: 5px 0; color: #666;">
                            <strong>Código:</strong> ${escapeHtml(course.code)}
                        </p>
                        <p style="margin: 5px 0; color: #666;">
                            <strong>Profesor:</strong> ${escapeHtml(course.teacher_name)}
                        </p>
                        ${course.description ? `
                            <p style="margin: 10px 0; color: #444;">
                                ${escapeHtml(course.description)}
                            </p>
                        ` : ''}
                        <p style="margin: 5px 0; font-size: 12px; color: #999;">
                            Creado: ${formattedDate}
                        </p>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <button class="btn btn-sm btn-primary" onclick="viewAssignments(${course.id})">
                            📝 Asignaciones
                        </button>
                        ${canEdit || user.role === 'admin' ? `
                            <button class="btn btn-sm btn-success" onclick="viewStudents(${course.id})">
                                👥 Estudiantes
                            </button>
                        ` : ''}
                        ${canEdit ? `
                            <button class="btn btn-sm btn-primary" onclick="editCourse(${course.id})">
                                ✏️ Editar
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteCourse(${course.id}, '${escapeHtml(course.name)}')">
                                🗑️ Eliminar
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
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
    
    if (pagination.page > 1) {
        html += `<button class="btn btn-secondary btn-sm" onclick="loadCourses(${pagination.page - 1})">← Anterior</button> `;
    }
    
    html += `<span style="margin: 0 15px;">Página ${pagination.page} de ${pagination.pages}</span>`;
    
    if (pagination.page < pagination.pages) {
        html += ` <button class="btn btn-secondary btn-sm" onclick="loadCourses(${pagination.page + 1})">Siguiente →</button>`;
    }
    
    html += '</div>';
    return html;
}

/**
 * Muestra el modal para crear curso
 */
function showCreateModal() {
    isEditMode = false;
    document.getElementById('modalTitle').textContent = 'Nuevo Curso';
    document.getElementById('courseForm').reset();
    document.getElementById('courseId').value = '';
    document.getElementById('formMessage').innerHTML = '';
    document.getElementById('courseModal').classList.add('show');
}

/**
 * Edita un curso
 */
async function editCourse(courseId) {
    try {
        const response = await apiRequest(`/courses/${courseId}`);
        
        if (response && response.ok && response.data.success) {
            const course = response.data.data;
            
            isEditMode = true;
            document.getElementById('modalTitle').textContent = 'Editar Curso';
            document.getElementById('courseId').value = course.id;
            document.getElementById('name').value = course.name;
            document.getElementById('code').value = course.code;
            document.getElementById('description').value = course.description || '';
            document.getElementById('formMessage').innerHTML = '';
            document.getElementById('courseModal').classList.add('show');
        } else {
            showMessage('messageContainer', 'Error al cargar curso', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('messageContainer', 'Error de conexión', 'error');
    }
}

/**
 * Guarda el curso (crear o editar)
 */
async function saveCourse() {
    const courseId = document.getElementById('courseId').value;
    const name = document.getElementById('name').value.trim();
    const code = document.getElementById('code').value.trim();
    const description = document.getElementById('description').value.trim();
    
    // Validaciones
    if (!name || !code) {
        document.getElementById('formMessage').innerHTML = 
            '<div class="error-message">Por favor completa todos los campos requeridos</div>';
        return;
    }
    
    const data = { name, code, description };
    
    try {
        let response;
        if (isEditMode) {
            response = await apiRequest(`/courses/${courseId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            response = await apiRequest('/courses', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
        
        if (response && response.ok && response.data.success) {
            closeModal();
            showMessage('messageContainer', response.data.message, 'success');
            loadCourses(currentPage);
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
 * Elimina un curso
 */
async function deleteCourse(courseId, courseName) {
    if (!confirm(`¿Estás seguro de eliminar el curso "${courseName}"?\n\nEsto también eliminará todas las asignaciones relacionadas.`)) {
        return;
    }
    
    try {
        const response = await apiRequest(`/courses/${courseId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok && response.data.success) {
            showMessage('messageContainer', 'Curso eliminado exitosamente', 'success');
            loadCourses(currentPage);
        } else {
            showMessage('messageContainer', response.data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('messageContainer', 'Error al eliminar curso', 'error');
    }
}

/**
 * Ver estudiantes inscritos
 */
async function viewStudents(courseId) {
    document.getElementById('studentsModal').classList.add('show');
    document.getElementById('studentsContent').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Cargando estudiantes...</p>
        </div>
    `;
    
    try {
        const response = await apiRequest(`/courses/${courseId}/students`);
        
        if (response && response.ok && response.data.success) {
            const students = response.data.data.students;
            renderStudents(students);
        } else {
            document.getElementById('studentsContent').innerHTML = 
                '<div class="error-message">Error al cargar estudiantes</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('studentsContent').innerHTML = 
            '<div class="error-message">Error de conexión</div>';
    }
}

/**
 * Renderiza la lista de estudiantes
 */
function renderStudents(students) {
    const container = document.getElementById('studentsContent');
    
    if (students.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👥</div>
                <p>No hay estudiantes inscritos</p>
            </div>
        `;
        return;
    }
    
    let html = '<table><thead><tr><th>Usuario</th><th>Email</th><th>Fecha Inscripción</th></tr></thead><tbody>';
    
    students.forEach(student => {
        html += `
            <tr>
                <td><strong>${escapeHtml(student.username)}</strong></td>
                <td>${escapeHtml(student.email)}</td>
                <td>${formatDate(student.enrolled_at)}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

/**
 * Ver asignaciones del curso
 */
function viewAssignments(courseId) {
    window.location.href = `assignments.html?course_id=${courseId}`;
}

/**
 * Cierra el modal
 */
function closeModal() {
    document.getElementById('courseModal').classList.remove('show');
}

function closeStudentsModal() {
    document.getElementById('studentsModal').classList.remove('show');
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

// Cerrar modales al hacer clic fuera
window.onclick = function(event) {
    const courseModal = document.getElementById('courseModal');
    const studentsModal = document.getElementById('studentsModal');
    
    if (event.target === courseModal) {
        closeModal();
    }
    if (event.target === studentsModal) {
        closeStudentsModal();
    }
}