/**
 * Lógica de gestión de asignaciones (Frontend)
 */

let currentPage = 1;
let isEditMode = false;
let courseIdFilter = null;

document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticación
    if (!requireAuth()) return;
    
    const user = getUser();
    
    // Mostrar información del usuario
    document.getElementById('userName').textContent = user.username;
    document.getElementById('userRole').textContent = user.role;
    
    // Verificar si viene filtrado por curso
    const urlParams = new URLSearchParams(window.location.search);
    courseIdFilter = urlParams.get('course_id');
    
    // Mostrar botón crear solo para admin y teacher
    if (hasAnyRole(['admin', 'teacher'])) {
        document.getElementById('createBtn').style.display = 'block';
    }
    
    // Cargar asignaciones
    if (courseIdFilter) {
        loadCourseAssignments(courseIdFilter);
    } else {
        loadAllAssignments();
    }
});

/**
 * Carga todas las asignaciones del usuario
 */
async function loadAllAssignments(page = 1) {
    currentPage = page;
    const container = document.getElementById('assignmentsContainer');
    
    try {
        const response = await apiRequest(`/assignments?page=${page}&limit=20`);
        
        if (response && response.ok && response.data.success) {
            const { assignments, pagination } = response.data.data;
            renderAssignments(assignments, pagination);
        } else {
            container.innerHTML = '<div class="error-message">Error al cargar asignaciones</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="error-message">Error de conexión</div>';
    }
}

/**
 * Carga asignaciones de un curso específico
 */
async function loadCourseAssignments(courseId) {
    const container = document.getElementById('assignmentsContainer');
    
    try {
        const response = await apiRequest(`/courses/${courseId}/assignments`);
        
        if (response && response.ok && response.data.success) {
            const assignments = response.data.data.assignments;
            
            // Obtener nombre del curso
            const courseResponse = await apiRequest(`/courses/${courseId}`);
            if (courseResponse && courseResponse.ok) {
                const courseName = courseResponse.data.data.name;
                document.getElementById('pageTitle').textContent = `📝 Asignaciones: ${courseName}`;
            }
            
            renderAssignments(assignments, null);
        } else {
            container.innerHTML = '<div class="error-message">Error al cargar asignaciones</div>';
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<div class="error-message">Error de conexión</div>';
    }
}

/**
 * Renderiza las asignaciones
 */
function renderAssignments(assignments, pagination) {
    const container = document.getElementById('assignmentsContainer');
    const user = getUser();
    
    if (assignments.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <p>No hay asignaciones disponibles</p>
            </div>
        `;
        return;
    }
    
    let html = '<div style="display: grid; gap: 20px;">';
    
    assignments.forEach(assignment => {
        const canEdit = user.role === 'admin' || user.role === 'teacher';
        const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
        const isOverdue = dueDate && dueDate < new Date();
        const dueDateStr = dueDate ? formatDateTime(assignment.due_date) : 'Sin fecha límite';
        
        const statusBadge = isOverdue 
            ? '<span class="badge badge-danger">Vencida</span>'
            : '<span class="badge badge-success">Activa</span>';
        
        html += `
            <div class="card" style="margin: 0; ${isOverdue ? 'border-left: 4px solid var(--danger-color);' : ''}">
                <div style="display: flex; justify-content: space-between; align-items: start; gap: 20px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <h3 style="margin: 0; color: var(--primary-color);">
                                ${escapeHtml(assignment.title)}
                            </h3>
                            ${statusBadge}
                        </div>
                        
                        <p style="margin: 5px 0; color: #666;">
                            <strong>Curso:</strong> ${escapeHtml(assignment.course_name)} 
                            (${escapeHtml(assignment.course_code)})
                        </p>
                        
                        ${assignment.description ? `
                            <p style="margin: 10px 0; color: #444;">
                                ${escapeHtml(assignment.description)}
                            </p>
                        ` : ''}
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;">
                            <p style="margin: 0; color: #666;">
                                <strong>📅 Entrega:</strong> ${dueDateStr}
                            </p>
                            <p style="margin: 0; color: #666;">
                                <strong>📊 Puntaje:</strong> ${assignment.max_score} pts
                            </p>
                        </div>
                    </div>
                    
                    ${canEdit ? `
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <button class="btn btn-sm btn-primary" onclick="editAssignment(${assignment.id})">
                                ✏️ Editar
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteAssignment(${assignment.id}, '${escapeHtml(assignment.title)}')">
                                🗑️ Eliminar
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Agregar paginación
    if (pagination && pagination.pages > 1) {
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
        html += `<button class="btn btn-secondary btn-sm" onclick="loadAllAssignments(${pagination.page - 1})">← Anterior</button> `;
    }
    
    html += `<span style="margin: 0 15px;">Página ${pagination.page} de ${pagination.pages}</span>`;
    
    if (pagination.page < pagination.pages) {
        html += ` <button class="btn btn-secondary btn-sm" onclick="loadAllAssignments(${pagination.page + 1})">Siguiente →</button>`;
    }
    
    html += '</div>';
    return html;
}

/**
 * Muestra el modal para crear asignación
 */
async function showCreateModal() {
    isEditMode = false;
    document.getElementById('modalTitle').textContent = 'Nueva Asignación';
    document.getElementById('assignmentForm').reset();
    document.getElementById('assignmentId').value = '';
    document.getElementById('maxScore').value = '100';
    document.getElementById('formMessage').innerHTML = '';
    
    // Cargar cursos disponibles
    await loadCoursesForSelect();
    
    // Si viene filtrado por curso, pre-seleccionar y ocultar selector
    if (courseIdFilter) {
        document.getElementById('courseSelect').value = courseIdFilter;
        document.getElementById('courseSelectGroup').style.display = 'none';
    } else {
        document.getElementById('courseSelectGroup').style.display = 'block';
    }
    
    document.getElementById('assignmentModal').classList.add('show');
}

/**
 * Carga los cursos para el selector
 */
async function loadCoursesForSelect() {
    try {
        const response = await apiRequest('/courses?limit=100');
        
        if (response && response.ok && response.data.success) {
            const courses = response.data.data.courses;
            const select = document.getElementById('courseSelect');
            
            select.innerHTML = '<option value="">Selecciona un curso...</option>';
            
            courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.id;
                option.textContent = `${course.name} (${course.code})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error al cargar cursos:', error);
    }
}

/**
 * Edita una asignación
 */
async function editAssignment(assignmentId) {
    try {
        const response = await apiRequest(`/assignments/${assignmentId}`);
        
        if (response && response.ok && response.data.success) {
            const assignment = response.data.data;
            
            isEditMode = true;
            document.getElementById('modalTitle').textContent = 'Editar Asignación';
            document.getElementById('assignmentId').value = assignment.id;
            document.getElementById('title').value = assignment.title;
            document.getElementById('description').value = assignment.description || '';
            document.getElementById('maxScore').value = assignment.max_score;
            
            // Formatear fecha para datetime-local
            if (assignment.due_date) {
                const date = new Date(assignment.due_date);
                const formatted = date.toISOString().slice(0, 16);
                document.getElementById('dueDate').value = formatted;
            }
            
            // Cargar cursos y ocultar selector (no se puede cambiar curso al editar)
            await loadCoursesForSelect();
            document.getElementById('courseSelect').value = assignment.course_id;
            document.getElementById('courseSelectGroup').style.display = 'none';
            
            document.getElementById('formMessage').innerHTML = '';
            document.getElementById('assignmentModal').classList.add('show');
        } else {
            showMessage('messageContainer', 'Error al cargar asignación', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('messageContainer', 'Error de conexión', 'error');
    }
}

/**
 * Guarda la asignación (crear o editar)
 */
async function saveAssignment() {
    const assignmentId = document.getElementById('assignmentId').value;
    const title = document.getElementById('title').value.trim();
    const description = document.getElementById('description').value.trim();
    const dueDate = document.getElementById('dueDate').value;
    const maxScore = parseFloat(document.getElementById('maxScore').value);
    
    let courseId;
    if (isEditMode || courseIdFilter) {
        courseId = courseIdFilter || document.getElementById('courseSelect').value;
    } else {
        courseId = document.getElementById('courseSelect').value;
    }
    
    // Validaciones
    if (!title) {
        document.getElementById('formMessage').innerHTML = 
            '<div class="error-message">El título es requerido</div>';
        return;
    }
    
    if (!isEditMode && !courseId) {
        document.getElementById('formMessage').innerHTML = 
            '<div class="error-message">Debes seleccionar un curso</div>';
        return;
    }
    
    const data = { title, description, max_score: maxScore };
    
    if (!isEditMode) {
        data.course_id = parseInt(courseId);
    }
    
    if (dueDate) {
        // Convertir a formato MySQL
        data.due_date = new Date(dueDate).toISOString().slice(0, 19).replace('T', ' ');
    }
    
    try {
        let response;
        if (isEditMode) {
            response = await apiRequest(`/assignments/${assignmentId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        } else {
            response = await apiRequest('/assignments', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
        
        if (response && response.ok && response.data.success) {
            closeModal();
            showMessage('messageContainer', response.data.message, 'success');
            
            if (courseIdFilter) {
                loadCourseAssignments(courseIdFilter);
            } else {
                loadAllAssignments(currentPage);
            }
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
 * Elimina una asignación
 */
async function deleteAssignment(assignmentId, title) {
    if (!confirm(`¿Estás seguro de eliminar la asignación "${title}"?`)) {
        return;
    }
    
    try {
        const response = await apiRequest(`/assignments/${assignmentId}`, {
            method: 'DELETE'
        });
        
        if (response && response.ok && response.data.success) {
            showMessage('messageContainer', 'Asignación eliminada exitosamente', 'success');
            
            if (courseIdFilter) {
                loadCourseAssignments(courseIdFilter);
            } else {
                loadAllAssignments(currentPage);
            }
        } else {
            showMessage('messageContainer', response.data.message, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('messageContainer', 'Error al eliminar asignación', 'error');
    }
}

/**
 * Cierra el modal
 */
function closeModal() {
    document.getElementById('assignmentModal').classList.remove('show');
}

/**
 * Formatea una fecha y hora
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
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
    const modal = document.getElementById('assignmentModal');
    if (event.target === modal) {
        closeModal();
    }
}