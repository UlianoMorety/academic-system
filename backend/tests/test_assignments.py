"""
Tests para el módulo de asignaciones (CRUD)
"""

import json
import pytest
from datetime import datetime, timedelta

class TestAssignments:
    """Suite de tests para gestión de asignaciones"""
    
    def test_get_assignments_without_auth(self, client):
        """Test: Obtener asignaciones sin autenticación"""
        response = client.get('/api/assignments')
        assert response.status_code == 401
    
    def test_get_assignments_with_auth(self, client, auth_headers):
        """Test: Obtener lista de asignaciones con autenticación"""
        response = client.get('/api/assignments', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'assignments' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_assignment_by_id(self, client, auth_headers):
        """Test: Obtener asignación específica por ID"""
        # Primero obtener lista para tener un ID válido
        response = client.get('/api/assignments', headers=auth_headers)
        data = json.loads(response.data)
        
        if len(data['data']['assignments']) > 0:
            assignment_id = data['data']['assignments'][0]['id']
            
            response = client.get(f'/api/assignments/{assignment_id}', 
                headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['id'] == assignment_id
    
    def test_create_assignment(self, client, auth_headers):
        """Test: Crear nueva asignación"""
        # Primero crear un curso
        course_response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Test Course for Assignment',
                'code': 'TCFA101',
                'description': 'Test'
            })
        )
        course_id = json.loads(course_response.data)['data']['id']
        
        # Crear asignación
        due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        
        response = client.post('/api/assignments',
            headers=auth_headers,
            data=json.dumps({
                'title': 'Test Assignment',
                'course_id': course_id,
                'description': 'Test description',
                'due_date': due_date,
                'max_score': 100.0
            })
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'Test Assignment'
    
    def test_create_assignment_missing_fields(self, client, auth_headers):
        """Test: Crear asignación sin campos requeridos"""
        response = client.post('/api/assignments',
            headers=auth_headers,
            data=json.dumps({
                'title': 'Incomplete Assignment'
            })
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_assignment(self, client, auth_headers):
        """Test: Actualizar asignación existente"""
        # Crear curso
        course_response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Course for Update Test',
                'code': 'CFUT101',
                'description': 'Test'
            })
        )
        course_id = json.loads(course_response.data)['data']['id']
        
        # Crear asignación
        create_response = client.post('/api/assignments',
            headers=auth_headers,
            data=json.dumps({
                'title': 'To Update',
                'course_id': course_id,
                'description': 'Original',
                'max_score': 80.0
            })
        )
        
        assignment_id = json.loads(create_response.data)['data']['id']
        
        # Actualizar asignación
        update_response = client.put(f'/api/assignments/{assignment_id}',
            headers=auth_headers,
            data=json.dumps({
                'title': 'Updated Assignment',
                'max_score': 120.0
            })
        )
        
        assert update_response.status_code == 200
        data = json.loads(update_response.data)
        assert data['success'] is True
        assert data['data']['title'] == 'Updated Assignment'
        assert float(data['data']['max_score']) == 120.0
    
    def test_delete_assignment(self, client, auth_headers):
        """Test: Eliminar asignación"""
        # Crear curso
        course_response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Course for Delete Test',
                'code': 'CFDT101',
                'description': 'Test'
            })
        )
        course_id = json.loads(course_response.data)['data']['id']
        
        # Crear asignación
        create_response = client.post('/api/assignments',
            headers=auth_headers,
            data=json.dumps({
                'title': 'To Delete',
                'course_id': course_id,
                'description': 'Will be deleted'
            })
        )
        
        assignment_id = json.loads(create_response.data)['data']['id']
        
        # Eliminar asignación
        delete_response = client.delete(f'/api/assignments/{assignment_id}', 
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200
        data = json.loads(delete_response.data)
        assert data['success'] is True
    
    def test_get_course_assignments(self, client, auth_headers):
        """Test: Obtener asignaciones de un curso específico"""
        # Crear curso
        course_response = client.post('/api/courses',
            headers=auth_headers,
            data=json.dumps({
                'name': 'Course with Assignments',
                'code': 'CWA101',
                'description': 'Test'
            })
        )
        course_id = json.loads(course_response.data)['data']['id']
        
        # Crear asignaciones
        client.post('/api/assignments',
            headers=auth_headers,
            data=json.dumps({
                'title': 'Assignment 1',
                'course_id': course_id
            })
        )
        
        client.post('/api/assignments',
            headers=auth_headers,
            data=json.dumps({
                'title': 'Assignment 2',
                'course_id': course_id
            })
        )
        
        # Obtener asignaciones del curso
        response = client.get(f'/api/courses/{course_id}/assignments',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'assignments' in data['data']
        assert len(data['data']['assignments']) >= 2