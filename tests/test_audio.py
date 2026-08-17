"""
Tests del clasificador local y servicios.
Ejecutar con: python -m pytest tests/ -v
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.clasificador import clasificar_local, clasificar_texto


class TestClasificadorLocal:
    """Tests del clasificador basado en palabras clave (sin API)."""

    def test_clasifica_ventas(self):
        resultado = clasificar_local("Quiero saber el precio del producto y si hay descuento")
        assert resultado['categoria'] == 'VENTAS'
        assert resultado['confianza'] > 0

    def test_clasifica_soporte(self):
        resultado = clasificar_local("Tengo un problema técnico, el sistema no funciona y muestra error")
        assert resultado['categoria'] == 'SOPORTE'

    def test_clasifica_facturacion(self):
        resultado = clasificar_local("Necesito mi factura y el estado de cuenta del mes pasado")
        assert resultado['categoria'] == 'FACTURACIÓN'

    def test_clasifica_garantia(self):
        resultado = clasificar_local("El producto está defectuoso y quiero hacer uso de la garantía")
        assert resultado['categoria'] == 'GARANTÍA'

    def test_clasifica_informacion(self):
        resultado = clasificar_local("¿Cuál es el horario de atención y la dirección de la sucursal?")
        assert resultado['categoria'] == 'INFORMACIÓN'

    def test_clasifica_reclamo(self):
        resultado = clasificar_local("Estoy muy molesto, el servicio es pésimo y quiero poner un reclamo")
        assert resultado['categoria'] == 'RECLAMO'

    def test_texto_sin_intencion(self):
        resultado = clasificar_local("Hola buenas tardes")
        assert resultado['categoria'] == 'OTRO'
        assert resultado['confianza'] <= 50

    def test_estructura_respuesta(self):
        resultado = clasificar_local("Cualquier texto para probar la estructura")
        assert 'categoria' in resultado
        assert 'confianza' in resultado
        assert 'prioridad' in resultado
        assert 'resumen' in resultado

    def test_confianza_en_rango(self):
        resultado = clasificar_local("Quiero comprar un producto nuevo")
        assert 0 <= resultado['confianza'] <= 100

    def test_prioridad_valida(self):
        resultado = clasificar_local("Tengo un problema urgente con el sistema")
        assert resultado['prioridad'] in ['ALTA', 'MEDIA', 'BAJA']


class TestClasificarTexto:
    """Tests de la función principal clasificar_texto."""

    def test_texto_vacio(self):
        resultado = clasificar_texto("")
        assert resultado['categoria'] == 'OTRO'
        assert resultado['confianza'] == 0

    def test_texto_none(self):
        resultado = clasificar_texto(None)
        assert resultado['categoria'] == 'OTRO'

    def test_sin_api_key(self):
        """Sin API key debe usar el clasificador local."""
        resultado = clasificar_texto("Quiero comprar algo", api_key=None)
        assert resultado['categoria'] in [
            'VENTAS', 'SOPORTE', 'FACTURACIÓN', 'GARANTÍA',
            'INFORMACIÓN', 'RECLAMO', 'OTRO'
        ]

    def test_api_key_vacia(self):
        """Con API key vacía debe usar el clasificador local."""
        resultado = clasificar_texto("Necesito soporte técnico", api_key="")
        assert 'categoria' in resultado
