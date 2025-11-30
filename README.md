# Sistema de Gestión Académica

## 📋 Descripción
Sistema web para gestión académica con autenticación JWT, control de roles y operaciones CRUD completas sobre cursos y asignaciones.

## 🛠️ Tecnologías Usadas
- **Backend**: Python 3.10+, Flask 3.0+
- **Base de Datos**: MySQL 8.0+
- **Autenticación**: PyJWT
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Testing**: pytest, pytest-flask

## 📦 Requisitos Previos
- Python 3.10 o superior
- MySQL 8.0 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar/Descargar el Proyecto
```bash
# Descargar y extraer el proyecto
cd academic-system
```

### Paso 2: Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
cd backend
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos MySQL

1. Acceder a MySQL:
```bash
mysql -u root -p
```

2. Crear la base de datos:
```sql
CREATE DATABASE academic_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'academic_user'@'localhost' IDENTIFIED BY 'Academic123!';
GRANT ALL PRIVILEGES ON academic_system.* TO 'academic_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Paso 5: Configurar Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Editar `.env` con tus credenciales:
```env
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=academic_user
DATABASE_PASSWORD=Academic123!
DATABASE_NAME=academic_system
JWT_SECRET_KEY=tu-jwt-secret-key-cambiar-en-produccion
JWT_ACCESS_TOKEN_EXPIRES=1800
```

### Paso 6: Inicializar Base de Datos
```bash
# Ejecutar script de creación de tablas
python scripts/init_db.py

# Cargar datos de prueba
python scripts/seed_data.py
```

### Paso 7: Ejecutar Aplicación
```bash
# Desde la carpeta backend
flask run
# O
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🔐 Credenciales de Prueba

| Rol | Usuario | Contraseña | Email |
|-----|---------|------------|-------|
| Admin | admin | Admin123! | admin@academic.com |
| Teacher | teacher1 | Teacher123! | teacher1@academic.com |
| Student | student1 | Student123! | student1@academic.com |
| Administrative | admin_staff | Admin123! | admin.staff@academic.com |

## 📁 Estructura del Proyecto

```
academic-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Inicialización de Flask
│   │   ├── config.py            # Configuración
│   │   ├── database.py          # Conexión a BD
│   │   ├── models.py            # Modelos de datos
│   │   ├── auth.py              # Decoradores de autenticación
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py   # Rutas de autenticación
│   │   │   ├── user_routes.py   # CRUD usuarios
│   │   │   ├── course_routes.py # CRUD cursos
│   │   │   └── assignment_routes.py # CRUD asignaciones
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Lógica de autenticación
│   │   │   ├── user_service.py  # Lógica usuarios
│   │   │   ├── course_service.py # Lógica cursos
│   │   │   └── assignment_service.py # Lógica asignaciones
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py    # Validaciones
│   │       └── responses.py     # Respuestas estandarizadas
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Configuración de tests
│   │   ├── test_auth.py         # Tests autenticación
│   │   ├── test_users.py        # Tests usuarios
│   │   ├── test_courses.py      # Tests cursos
│   │   └── test_assignments.py  # Tests asignaciones
│   ├── scripts/
│   │   ├── init_db.py           # Script crear tablas
│   │   └── seed_data.py         # Script datos de prueba
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── index.html               # Página principal
│   ├── login.html               # Login
│   ├── dashboard.html           # Dashboard
│   ├── users.html               # Gestión usuarios
│   ├── courses.html             # Gestión cursos
│   ├── assignments.html         # Gestión asignaciones
│   ├── css/
│   │   └── style.css            # Estilos globales
│   └── js/
│       ├── config.js            # Configuración API
│       ├── auth.js              # Funciones autenticación
│       ├── api.js               # Cliente API
│       ├── users.js             # Lógica usuarios
│       ├── courses.js           # Lógica cursos
│       └── assignments.js       # Lógica asignaciones
├── docs/
│   ├── database_diagram.png     # Diagrama ER
│   └── manual_usuario.pdf       # Manual de usuario
├── .env.example
├── .gitignore
└── README.md
```

## 🗄️ Estructura de Base de Datos

### Diagrama Entidad-Relación
Ver archivo: `docs/database_diagram.png`

### Tablas

#### roles
- `id` (INT, PK, AUTO_INCREMENT)
- `name` (VARCHAR(50), UNIQUE, NOT NULL)
- `description` (TEXT)
- `created_at` (TIMESTAMP)

#### users
- `id` (INT, PK, AUTO_INCREMENT)
- `username` (VARCHAR(50), UNIQUE, NOT NULL)
- `email` (VARCHAR(100), UNIQUE, NOT NULL)
- `password_hash` (VARCHAR(255), NOT NULL)
- `role_id` (INT, FK → roles.id)
- `is_active` (BOOLEAN, DEFAULT TRUE)
- `created_at` (TIMESTAMP)

#### courses
- `id` (INT, PK, AUTO_INCREMENT)
- `name` (VARCHAR(100), NOT NULL)
- `description` (TEXT)
- `code` (VARCHAR(20), UNIQUE, NOT NULL)
- `teacher_id` (INT, FK → users.id)
- `created_at` (TIMESTAMP)

#### assignments
- `id` (INT, PK, AUTO_INCREMENT)
- `title` (VARCHAR(200), NOT NULL)
- `description` (TEXT)
- `course_id` (INT, FK → courses.id)
- `due_date` (DATETIME)
- `max_score` (DECIMAL(5,2))
- `created_at` (TIMESTAMP)

#### enrollments
- `id` (INT, PK, AUTO_INCREMENT)
- `student_id` (INT, FK → users.id)
- `course_id` (INT, FK → courses.id)
- `enrolled_at` (TIMESTAMP)
- UNIQUE(student_id, course_id)

### Relaciones
- Role 1:N Users
- User(Teacher) 1:N Courses
- Course 1:N Assignments
- User(Student) N:M Courses (through enrollments)

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión (retorna JWT)

### Usuarios (Admin only)
- `GET /api/users` - Listar todos los usuarios
- `GET /api/users/<id>` - Obtener usuario específico
- `POST /api/users` - Crear usuario
- `PUT /api/users/<id>` - Actualizar usuario
- `DELETE /api/users/<id>` - Eliminar usuario

### Cursos
- `GET /api/courses` - Listar cursos (filtrado por rol)
- `GET /api/courses/<id>` - Obtener curso específico
- `POST /api/courses` - Crear curso (Admin/Teacher)
- `PUT /api/courses/<id>` - Actualizar curso (Owner/Admin)
- `DELETE /api/courses/<id>` - Eliminar curso (Owner/Admin)
- `POST /api/courses/<id>/enroll` - Inscribir estudiante

### Asignaciones
- `GET /api/courses/<course_id>/assignments` - Listar asignaciones del curso
- `GET /api/assignments/<id>` - Obtener asignación específica
- `POST /api/assignments` - Crear asignación (Teacher/Admin)
- `PUT /api/assignments/<id>` - Actualizar asignación
- `DELETE /api/assignments/<id>` - Eliminar asignación

## 🧪 Ejecutar Tests

```bash
# Desde la carpeta backend
pytest

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_auth.py
pytest tests/test_users.py -v
```

## 🔒 Seguridad Implementada

1. **Autenticación JWT**: Tokens con expiración de 30 minutos
2. **Hash de Contraseñas**: bcrypt con 12 rounds
3. **Validaciones**: Servidor y cliente
4. **Consultas Parametrizadas**: Prevención de SQL injection
5. **CORS Configurado**: Orígenes permitidos específicos
6. **Autorización por Roles**: Decoradores para proteger rutas
7. **Variables de Entorno**: Credenciales nunca en código
8. **Validación de Entrada**: Sanitización y validación de datos

## 📸 Capturas de Pantalla

Las capturas deben incluir:
1. Login exitoso con diferentes roles
2. Dashboard según rol
3. CRUD de usuarios (crear, listar, editar, eliminar)
4. CRUD de cursos
5. CRUD de asignaciones
6. Validaciones y mensajes de error
7. Autorización (acceso denegado)

## 🐛 Solución de Problemas

### Error de conexión a MySQL
```bash
# Verificar que MySQL esté corriendo
mysql -u root -p

# Verificar credenciales en .env
```

### Error de módulos no encontrados
```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error de CORS
```bash
# Verificar que el frontend se sirva desde el origen configurado
# O ajustar CORS_ORIGINS en config.py
```

## 📚 Notas Adicionales

- **Desarrollo**: Usar `FLASK_ENV=development` para debugging
- **Producción**: Cambiar todas las claves secretas y usar HTTPS
- **Backup**: Crear respaldos regulares de la base de datos
- **Logs**: Revisar logs en consola para debugging

## 👨‍💻 Autor
[Tu Nombre]
[Tu Email]

## 📄 Licencia
Este proyecto es para fines educativos.

---
**Fecha de creación**: Noviembre 2025
**Versión**: 1.0.0