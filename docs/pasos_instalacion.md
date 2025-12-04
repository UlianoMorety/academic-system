# 🚀 Guía de Instalación Paso a Paso

Esta guía te llevará desde cero hasta tener el sistema funcionando completamente.

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.10 o superior**
   - Descargar de: https://www.python.org/downloads/
   - Verificar instalación: `python --version`

2. **MySQL 8.0 o superior**
   - Descargar de: https://dev.mysql.com/downloads/mysql/
   - Verificar instalación: `mysql --version`

3. **pip** (viene con Python)
   - Verificar: `pip --version`

---

## 📁 Paso 1: Preparar el Proyecto

### 1.1 Descargar/Clonar el Proyecto

```bash
# Si usas git
git clone [url-del-repositorio]
cd academic-system

# O simplemente descargar y extraer el ZIP
```

### 1.2 Verificar la Estructura

Tu proyecto debe tener esta estructura:

```
academic-system/
├── backend/
│   ├── app/
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── css/
│   ├── js/
│   └── *.html
├── .env.example
└── README.md
```

---

## 🐍 Paso 2: Configurar Python

### 2.1 Crear Entorno Virtual

**En Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
cd backend
python3 -m venv env
source venv/bin/activate
```

Tu terminal debe mostrar `(env)` al inicio, indicando que el entorno está activo.

### 2.2 Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- Flask (framework web)
- Flask-CORS (manejo de CORS)
- PyJWT (tokens JWT)
- bcrypt (hash de contraseñas)
- PyMySQL (conexión a MySQL)
- python-dotenv (variables de entorno)
- pytest (testing)

### 2.3 Verificar Instalación

```bash
pip list
```

Deberías ver todas las librerías instaladas con sus versiones.

---

## 🗄️ Paso 3: Configurar MySQL

### 3.1 Iniciar MySQL

**Windows:**
- Buscar "MySQL Command Line Client" en el menú inicio
- O abrir CMD y escribir: `mysql -u root -p`

**Linux/Mac:**
```bash
mysql -u root -p
```

Te pedirá la contraseña de root que configuraste al instalar MySQL.

### 3.2 Crear Base de Datos y Usuario

Copia y pega estos comandos en la consola de MySQL:

```sql
-- Crear base de datos
CREATE DATABASE academic_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Crear usuario específico
CREATE USER 'academic_user'@'localhost' 
IDENTIFIED BY 'Academic123!';

-- Dar permisos
GRANT ALL PRIVILEGES ON academic_system.* 
TO 'academic_user'@'localhost';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Verificar base de datos
SHOW DATABASES;

-- Salir
EXIT;
```

### 3.3 Verificar Conexión

Intenta conectarte con el nuevo usuario:

```bash
mysql -u academic_user -p academic_system
# Contraseña: Academic123!
```

Si funciona, escribe `EXIT;` y continúa.

---

## ⚙️ Paso 4: Configurar Variables de Entorno

### 4.1 Copiar Archivo de Ejemplo

**Desde la carpeta raíz del proyecto:**

**Windows:**
```bash
copy .env.example backend\.env
```

**Linux/Mac:**
```bash
cp .env.example backend/.env
```

### 4.2 Editar el Archivo .env

Abre `backend/.env` con cualquier editor de texto y verifica/modifica:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=mi-clave-secreta-super-segura-12345

# Base de Datos
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=academic_user
DATABASE_PASSWORD=Academic123!
DATABASE_NAME=academic_system

# JWT
JWT_SECRET_KEY=mi-jwt-secret-key-98765
JWT_ACCESS_TOKEN_EXPIRES=1800

# CORS
CORS_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```

**IMPORTANTE:** 
- Cambia `SECRET_KEY` y `JWT_SECRET_KEY` por valores únicos
- Si cambiaste la contraseña de MySQL, actualízala aquí
- Si tu MySQL usa otro puerto, cámbialo

---

## 🏗️ Paso 5: Inicializar Base de Datos

Asegúrate de estar en la carpeta `backend` con el entorno virtual activado.

### 5.1 Crear Tablas

```bash
python scripts/init_db.py
```

Deberías ver:
```
==================================================
  Inicialización de Base de Datos
==================================================
🗄️  Creando tablas...
✅ Tabla 'roles' creada
✅ Tabla 'users' creada
✅ Tabla 'courses' creada
✅ Tabla 'assignments' creada
✅ Tabla 'enrollments' creada

✨ ¡Base de datos inicializada exitosamente!
```

### 5.2 Cargar Datos de Prueba

```bash
python scripts/seed_data.py
```

Deberías ver:
```
==================================================
  Carga de Datos de Prueba
==================================================
🌱 Insertando datos de prueba...

📋 Insertando roles...
  ✅ 4 roles insertados
👥 Insertando usuarios...
  ✅ 7 usuarios insertados
📚 Insertando cursos...
  ✅ 4 cursos insertados
📝 Insertando asignaciones...
  ✅ 6 asignaciones insertadas
🎓 Insertando inscripciones...
  ✅ 6 inscripciones insertadas

==================================================
✨ ¡Datos de prueba insertados exitosamente!
==================================================

📊 Resumen:
  • 4 roles
  • 7 usuarios
  • 4 cursos
  • 6 asignaciones
  • 6 inscripciones

🔐 Credenciales de prueba:
  Admin:    admin / Admin123!
  Teacher:  teacher1 / Teacher123!
  Student:  student1 / Student123!
  Staff:    admin_staff / Admin123!
```

### 5.3 Verificar en MySQL (Opcional)

```bash
mysql -u academic_user -p academic_system

mysql> SELECT * FROM users;
mysql> SELECT * FROM roles;
mysql> EXIT;
```

---

## 🚀 Paso 6: Ejecutar la Aplicación

### 6.1 Iniciar el Backend

Desde la carpeta `backend` con entorno virtual activado:

```bash
python run.py
```

Deberías ver:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in production.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

**NO CIERRES ESTA VENTANA** - debe quedar corriendo.

### 6.2 Abrir el Frontend

1. Abre una **nueva terminal/ventana**
2. Navega a la carpeta `frontend`
3. Abre `login.html` directamente en tu navegador:

**Opción 1 - Doble clic:**
```
Busca el archivo frontend/login.html y ábrelo con tu navegador
```

**Opción 2 - Servidor simple Python (Recomendado):**
```bash
cd frontend
python -m http.server 8000
```

Luego abre: `http://localhost:8000/login.html`

---

## 🧪 Paso 7: Probar el Sistema

### 7.1 Probar Login

1. En tu navegador, ve a `login.html`
2. Prueba con las credenciales:
   - **Usuario:** admin
   - **Contraseña:** Admin123!
3. Deberías ser redirigido al dashboard

### 7.2 Explorar Funcionalidades

Como **Admin** puedes:
- ✅ Ver todos los usuarios
- ✅ Crear nuevos usuarios
- ✅ Editar usuarios
- ✅ Eliminar usuarios
- ✅ Gestionar cursos
- ✅ Gestionar asignaciones

### 7.3 Probar Diferentes Roles

Cierra sesión y prueba con:

**Teacher (Profesor):**
- Usuario: teacher1
- Contraseña: Teacher123!
- Puede: Gestionar sus cursos y asignaciones

**Student (Estudiante):**
- Usuario: student1
- Contraseña: Student123!
- Puede: Ver sus cursos y asignaciones

---

## 🧪 Paso 8: Ejecutar Tests (Opcional)

### 8.1 Ejecutar Todos los Tests

```bash
cd backend
pytest
```

### 8.2 Ejecutar Tests Específicos

```bash
# Solo tests de autenticación
pytest tests/test_auth.py

# Solo tests de usuarios
pytest tests/test_users.py

# Con información detallada
pytest -v

# Con cobertura
pytest --cov=app tests/
```

---

## 🔧 Solución de Problemas Comunes

### Problema 1: "Module not found"

**Solución:**
```bash
# Verificar que el entorno virtual esté activo
# Reinstalar dependencias
pip install -r requirements.txt
```

### Problema 2: "Can't connect to MySQL"

**Posibles causas:**
1. MySQL no está corriendo
   ```bash
   # Windows: Buscar "Services" y verificar MySQL
   # Linux/Mac:
   sudo service mysql start
   ```

2. Credenciales incorrectas en `.env`
   - Verifica usuario, contraseña y nombre de BD

3. Puerto incorrecto
   - Verifica que MySQL esté en puerto 3306
   ```bash
   mysql -u root -p
   mysql> SHOW VARIABLES LIKE 'port';
   ```

### Problema 3: "CORS Error" en el navegador

**Solución:**
1. Verifica que el backend esté corriendo
2. Actualiza `CORS_ORIGINS` en `.env`:
   ```env
   CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:5000
   ```
3. Reinicia el servidor Flask

### Problema 4: "Token inválido" al hacer peticiones

**Solución:**
1. Cierra sesión y vuelve a iniciar
2. Limpia el localStorage del navegador:
   ```javascript
   // En la consola del navegador (F12)
   localStorage.clear()
   ```
3. Recarga la página

### Problema 5: Base de datos ya existe

**Si necesitas reiniciar desde cero:**
```sql
mysql -u root -p

mysql> DROP DATABASE academic_system;
mysql> CREATE DATABASE academic_system 
       CHARACTER SET utf8mb4 
       COLLATE utf8mb4_unicode_ci;
mysql> EXIT;

# Luego vuelve a ejecutar:
python scripts/init_db.py
python scripts/seed_data.py
```

---

## 📝 Comandos de Referencia Rápida

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear tablas
python scripts/init_db.py

# Cargar datos de prueba
python scripts/seed_data.py

# Ejecutar aplicación
python run.py

# Ejecutar tests
pytest

# Desactivar entorno virtual
deactivate
```

---

## 🎯 Próximos Pasos

Una vez que todo funcione:

1. ✅ **Explora todas las funcionalidades**
2. ✅ **Prueba crear, editar y eliminar registros**
3. ✅ **Verifica las validaciones**
4. ✅ **Revisa la autorización por roles**
5. ✅ **Toma capturas de pantalla para tu documentación**

---

## 📚 Recursos Adicionales

- **Documentación Flask:** https://flask.palletsprojects.com/
- **Documentación MySQL:** https://dev.mysql.com/doc/
- **Documentación PyJWT:** https://pyjwt.readthedocs.io/
- **pytest:** https://docs.pytest.org/

---