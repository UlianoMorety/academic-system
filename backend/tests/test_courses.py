"""
Tests para el módulo de cursos (CRUD)
"""

import json
import pytest

class TestCourses:
    """Suite de tests para gestión de cursos"""
    
    def test_get_courses_without_auth(self, client):
        """Test: Obtener cursos sin autenticación"""
        response = client.get('/api/courses')
        assert response.status_code == 401
    
    def test_get_courses_with_auth(self, client, auth_headers):
        """Test: Obtener lista de cursos con autenticación"""
        response = client.get('/api/courses', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'courses' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_course_by_id(self, client, auth_headers):
        """Test: Obtener curso específico por ID"""
        # Primero obtener lista para tener un ID válido
        response = client.get('/api/courses', headers=auth_headers)
        data = json.loads(response.data)
        
        if len(data['data']['courses']) > 0:
            course_id = data['data']['courses'][0]['id']
            
            response = client.get(f'/api/courses/{course_id}', headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['id'] == course_id
    
    def test_get_nonexistent_course(self, client, auth_headers):
        """Test: Obtener curso que no existe"""
        response = client.get('/api/courses/99999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_course(self, client, auth_headers):
        """Test: Crear nuevo curso"""
        response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Test Course',
                'code': 'TEST101',
                'description': 'Course for testing'
            })
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'Test Course'
        assert data['data']['code'] == 'TEST101'
    
    def test_create_course_missing_fields(self, client, auth_headers):
        """Test: Crear curso sin campos requeridos"""
        response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Incomplete Course'
            })
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_create_course_duplicate_code(self, client, auth_headers):
        """Test: Crear curso con código duplicado"""
        # Crear primer curso
        client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'First Course',
                'code': 'DUP101',
                'description': 'First'
            })
        )
        
        # Intentar crear con mismo código
        response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Second Course',
                'code': 'DUP101',
                'description': 'Second'
            })
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_course(self, client, auth_headers):
        """Test: Actualizar curso existente"""
        # Crear curso primero
        create_response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'To Update',
                'code': 'UPD101',
                'description': 'Original'
            })
        )
        
        course_id = json.loads(create_response.data)['data']['id']
        
        # Actualizar curso
        update_response = client.put(f'/api/courses/{course_id}',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Updated Course',
                'description': 'Updated description'
            })
        )
        
        assert update_response.status_code == 200
        data = json.loads(update_response.data)
        assert data['success'] is True
        assert data['data']['name'] == 'Updated Course'
    
    def test_delete_course(self, client, auth_headers):
        """Test: Eliminar curso"""
        # Crear curso primero
        create_response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'To Delete',
                'code': 'DEL101',
                'description': 'Will be deleted'
            })
        )
        
        course_id = json.loads(create_response.data)['data']['id']
        
        # Eliminar curso
        delete_response = client.delete(f'/api/courses/{course_id}', 
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200
        data = json.loads(delete_response.data)
        assert data['success'] is True
    
    def test_pagination(self, client, auth_headers):
        """Test: Paginación de cursos"""
        response = client.get('/api/courses?page=1&limit=5', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['limit'] == 5