"""
Tests para el módulo de usuarios (CRUD)
"""

import json
import pytest

class TestUsers:
    """Suite de tests para gestión de usuarios"""
    
    def test_get_users_without_auth(self, client):
        """Test: Obtener usuarios sin autenticación"""
        response = client.get('/api/users')
        assert response.status_code == 401
    
    def test_get_users_with_auth(self, client, auth_headers):
        """Test: Obtener lista de usuarios con autenticación"""
        response = client.get('/api/users', headers=auth_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'users' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_user_by_id(self, client, auth_headers):
        """Test: Obtener usuario específico por ID"""
        # Primero obtener lista para tener un ID válido
        response = client.get('/api/users', headers=auth_headers)
        data = json.loads(response.data)
        
        if len(data['data']['users']) > 0:
            user_id = data['data']['users'][0]['id']
            
            response = client.get(f'/api/users/{user_id}', headers=auth_headers)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['id'] == user_id
    
    def test_get_nonexistent_user(self, client, auth_headers):
        """Test: Obtener usuario que no existe"""
        response = client.get('/api/users/99999', headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_user(self, client, auth_headers):
        """Test: Crear nuevo usuario"""
        response = client.post('/api/users',
            headers=auth_headers,
            data=json.dumps({
                'username': 'testcreate',
                'email': 'testcreate@test.com',
                'password': 'TestCreate123!',
                'role': 'student'
            })
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['username'] == 'testcreate'
    
    def test_create_user_missing_fields(self, client, auth_headers):
        """Test: Crear usuario sin campos requeridos"""
        response = client.post('/api/users',
            headers=auth_headers,
            data=json.dumps({
                'username': 'incomplete'
            })
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_user(self, client, auth_headers):
        """Test: Actualizar usuario existente"""
        # Crear usuario primero
        create_response = client.post('/api/users',
            headers=auth_headers,
            data=json.dumps({
                'username': 'toupdate',
                'email': 'toupdate@test.com',
                'password': 'ToUpdate123!',
                'role': 'student'
            })
        )
        
        user_id = json.loads(create_response.data)['data']['id']
        
        # Actualizar usuario
        update_response = client.put(f'/api/users/{user_id}',
            headers=auth_headers,
            data=json.dumps({
                'email': 'updated@test.com'
            })
        )
        
        assert update_response.status_code == 200
        data = json.loads(update_response.data)
        assert data['success'] is True
        assert data['data']['email'] == 'updated@test.com'
    
    def test_delete_user(self, client, auth_headers):
        """Test: Eliminar usuario"""
        # Crear usuario primero
        create_response = client.post('/api/users',
            headers=auth_headers,
            data=json.dumps({
                'username': 'todelete',
                'email': 'todelete@test.com',
                'password': 'ToDelete123!',
                'role': 'student'
            })
        )
        
        user_id = json.loads(create_response.data)['data']['id']
        
        # Eliminar usuario
        delete_response = client.delete(f'/api/users/{user_id}', 
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200
        data = json.loads(delete_response.data)
        assert data['success'] is True
    
    def test_pagination(self, client, auth_headers):
        """Test: Paginación de usuarios"""
        response = client.get('/api/users?page=1&limit=5', 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['limit'] == 5