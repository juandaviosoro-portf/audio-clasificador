"""
Tests de la API del sistema de clasificación.
Ejecutar con: python -m pytest tests/ -v
"""
import json
import os
import sys
import pytest

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models.consulta import Consulta


@pytest.fixture
def client():
    """Crea un cliente de prueba con BD en memoria."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def datos_prueba():
    """Carga los datos de prueba desde el JSON."""
    ruta = os.path.join(os.path.dirname(__file__), 'datos_prueba.json')
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestAnalizarTexto:
    """Tests para el endpoint POST /api/analizar-texto"""

    def test_texto_valido(self, client, datos_prueba):
        """Debería clasificar correctamente un texto de ventas."""
        caso = datos_prueba[0]  # Caso de VENTAS
        resp = client.post('/api/analizar-texto',
                           json={'texto': caso['texto']},
                           content_type='application/json')

        assert resp.status_code == 200
        datos = resp.get_json()

        assert 'categoria' in datos
        assert 'confianza' in datos
        assert 'prioridad' in datos
        assert 'resumen' in datos
        assert datos['categoria'] in [
            'VENTAS', 'SOPORTE', 'FACTURACIÓN', 'GARANTÍA',
            'INFORMACIÓN', 'RECLAMO', 'OTRO'
        ]
        assert 0 <= datos['confianza'] <= 100
        assert datos['prioridad'] in ['ALTA', 'MEDIA', 'BAJA']

    def test_texto_vacio(self, client):
        """Debería rechazar texto vacío."""
        resp = client.post('/api/analizar-texto',
                           json={'texto': ''},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_sin_texto(self, client):
        """Debería rechazar request sin campo texto."""
        resp = client.post('/api/analizar-texto',
                           json={},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_texto_largo(self, client):
        """Debería rechazar texto demasiado largo."""
        texto_largo = 'a' * 5001
        resp = client.post('/api/analizar-texto',
                           json={'texto': texto_largo},
                           content_type='application/json')
        assert resp.status_code == 400

    def test_clasificacion_todos_los_casos(self, client, datos_prueba):
        """Debería clasificar todos los casos de prueba sin errores."""
        for caso in datos_prueba:
            resp = client.post('/api/analizar-texto',
                               json={'texto': caso['texto']},
                               content_type='application/json')
            assert resp.status_code == 200, f"Falló para: {caso['descripcion']}"


class TestHistorial:
    """Tests para el endpoint GET /api/historial"""

    def test_historial_vacio(self, client):
        """Debería devolver lista vacía si no hay consultas."""
        resp = client.get('/api/historial')
        assert resp.status_code == 200
        datos = resp.get_json()
        assert datos['total'] == 0
        assert datos['consultas'] == []

    def test_historial_con_datos(self, client):
        """Debería devolver consultas después de analizar texto."""
        # Crear una consulta
        client.post('/api/analizar-texto',
                     json={'texto': 'Quiero comprar un producto'},
                     content_type='application/json')

        resp = client.get('/api/historial')
        datos = resp.get_json()
        assert datos['total'] >= 1

    def test_filtro_categoria(self, client):
        """Debería filtrar por categoría."""
        resp = client.get('/api/historial?categoria=VENTAS')
        assert resp.status_code == 200


class TestDashboard:
    """Tests para el endpoint GET /api/dashboard"""

    def test_dashboard_vacio(self, client):
        """Debería funcionar con BD vacía."""
        resp = client.get('/api/dashboard')
        assert resp.status_code == 200
        datos = resp.get_json()
        assert datos['total_consultas'] == 0

    def test_dashboard_con_datos(self, client):
        """Debería calcular estadísticas correctas."""
        # Crear algunas consultas
        textos = [
            'Quiero comprar algo',
            'Mi sistema no funciona',
            'Envíenme la factura'
        ]
        for t in textos:
            client.post('/api/analizar-texto',
                         json={'texto': t},
                         content_type='application/json')

        resp = client.get('/api/dashboard')
        datos = resp.get_json()
        assert datos['total_consultas'] == 3


class TestExportar:
    """Tests para el endpoint GET /api/exportar"""

    def test_exportar_vacio(self, client):
        """Debería generar Excel vacío sin errores."""
        resp = client.get('/api/exportar')
        assert resp.status_code == 200
        assert 'spreadsheetml' in resp.content_type

    def test_exportar_con_datos(self, client):
        """Debería generar Excel con datos."""
        client.post('/api/analizar-texto',
                     json={'texto': 'Quiero información sobre el producto'},
                     content_type='application/json')

        resp = client.get('/api/exportar')
        assert resp.status_code == 200
        assert len(resp.data) > 0


class TestPaginas:
    """Tests para las páginas HTML"""

    def test_index(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_dashboard(self, client):
        resp = client.get('/dashboard')
        assert resp.status_code == 200

    def test_historial(self, client):
        resp = client.get('/historial')
        assert resp.status_code == 200
