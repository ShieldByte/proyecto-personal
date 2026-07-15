"""
Tests unitarios para el servicio de cálculo OEE.
Ejecutar con: python -m pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from app.services.oee import calcular_oee, clasificar_oee


class TestCalcularOEE:

    def test_oee_clase_mundial(self):
        """OEE >= 85% debe clasificarse como Clase Mundial."""
        resultado = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=10,
            unidades_objetivo=100,
            unidades_producidas=98,
            unidades_defectuosas=1
        )
        assert resultado["oee"] > 80
        assert resultado["disponibilidad"] > 90
        assert resultado["calidad"] > 95

    def test_oee_sin_produccion(self):
        """Con cero unidades producidas, OEE debe ser 0."""
        resultado = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=0,
            unidades_objetivo=100,
            unidades_producidas=0,
            unidades_defectuosas=0
        )
        assert resultado["oee"] == 0
        assert resultado["calidad"] == 0

    def test_oee_sin_defectos(self):
        """Sin defectos la calidad debe ser 100%."""
        resultado = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=0,
            unidades_objetivo=100,
            unidades_producidas=100,
            unidades_defectuosas=0
        )
        assert resultado["calidad"] == 100.0

    def test_rendimiento_no_supera_100(self):
        """Rendimiento no puede superar 100% aunque se produzca de más."""
        resultado = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=0,
            unidades_objetivo=100,
            unidades_producidas=150,  # Sobreproducción
            unidades_defectuosas=0
        )
        assert resultado["rendimiento"] == 100.0

    def test_disponibilidad_con_paro_total(self):
        """Si el tiempo de paro iguala al disponible, disponibilidad es 0."""
        resultado = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=480,
            unidades_objetivo=100,
            unidades_producidas=0,
            unidades_defectuosas=0
        )
        assert resultado["disponibilidad"] == 0.0

    def test_tiempo_disponible_cero(self):
        """Tiempo disponible = 0 no debe generar división por cero."""
        resultado = calcular_oee(
            tiempo_disponible_min=0,
            tiempo_paro_min=0,
            unidades_objetivo=100,
            unidades_producidas=50,
            unidades_defectuosas=5
        )
        assert resultado["disponibilidad"] == 0

    def test_formula_oee_correcta(self):
        """Verifica que OEE = Disponibilidad × Rendimiento × Calidad."""
        resultado = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=48,   # 90% disponibilidad
            unidades_objetivo=100,
            unidades_producidas=90,  # 90% rendimiento
            unidades_defectuosas=9   # 90% calidad
        )
        esperado = round(0.9 * 0.9 * 0.9 * 100, 2)
        assert abs(resultado["oee"] - esperado) < 0.1


class TestClasificarOEE:

    def test_clase_mundial(self):
        assert clasificar_oee(90) == "Clase Mundial"
        assert clasificar_oee(85) == "Clase Mundial"

    def test_aceptable(self):
        assert clasificar_oee(75) == "Aceptable"
        assert clasificar_oee(65) == "Aceptable"

    def test_regular(self):
        assert clasificar_oee(55) == "Regular"
        assert clasificar_oee(45) == "Regular"

    def test_critico(self):
        assert clasificar_oee(44) == "Crítico"
        assert clasificar_oee(0) == "Crítico"