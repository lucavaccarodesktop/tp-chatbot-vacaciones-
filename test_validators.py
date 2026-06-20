# -*- coding: utf-8 -*-
"""
tests/test_validators.py
Pruebas automáticas de las validaciones de entrada (camino infeliz del BPMN).
Se ejecuta con: python -m unittest tests/test_validators.py -v
"""
import sys
import os
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import validators as val


class TestValidarLegajo(unittest.TestCase):
    def test_legajo_valido(self):
        ok, valor = val.validar_legajo("1001")
        self.assertTrue(ok)
        self.assertEqual(valor, 1001)

    def test_legajo_con_letras(self):
        ok, _ = val.validar_legajo("abc1")
        self.assertFalse(ok)

    def test_legajo_vacio(self):
        ok, _ = val.validar_legajo("")
        self.assertFalse(ok)

    def test_legajo_demasiado_largo(self):
        ok, _ = val.validar_legajo("1234567")
        self.assertFalse(ok)

    def test_legajo_con_espacios(self):
        ok, valor = val.validar_legajo("  1001  ")
        self.assertTrue(ok)
        self.assertEqual(valor, 1001)


class TestFechas(unittest.TestCase):
    def test_parsear_fecha_valida(self):
        self.assertEqual(val.parsear_fecha("15/07/2026"), date(2026, 7, 15))

    def test_parsear_fecha_formato_invalido(self):
        self.assertIsNone(val.parsear_fecha("15-07-2026"))
        self.assertIsNone(val.parsear_fecha("2026/07/15"))
        self.assertIsNone(val.parsear_fecha("hola"))

    def test_fecha_inicio_anterior_a_hoy(self):
        hoy = date(2026, 6, 19)
        ok, _ = val.validar_fecha_inicio("01/01/2026", hoy=hoy)
        self.assertFalse(ok)

    def test_fecha_inicio_valida(self):
        hoy = date(2026, 6, 19)
        ok, valor = val.validar_fecha_inicio("01/07/2026", hoy=hoy)
        self.assertTrue(ok)
        self.assertEqual(valor, date(2026, 7, 1))

    def test_fecha_inicio_demasiado_lejana(self):
        hoy = date(2026, 6, 19)
        ok, _ = val.validar_fecha_inicio("01/01/2030", hoy=hoy)
        self.assertFalse(ok)

    def test_fecha_fin_anterior_a_inicio(self):
        inicio = date(2026, 7, 10)
        ok, _ = val.validar_fecha_fin("05/07/2026", inicio)
        self.assertFalse(ok)

    def test_fecha_fin_igual_a_inicio(self):
        inicio = date(2026, 7, 10)
        ok, _ = val.validar_fecha_fin("10/07/2026", inicio)
        self.assertFalse(ok)

    def test_fecha_fin_valida(self):
        inicio = date(2026, 7, 10)
        ok, valor = val.validar_fecha_fin("20/07/2026", inicio)
        self.assertTrue(ok)
        self.assertEqual(valor, date(2026, 7, 20))

    def test_fecha_fin_supera_dias_maximos(self):
        inicio = date(2026, 7, 1)
        fin = inicio + timedelta(days=90)
        ok, _ = val.validar_fecha_fin(fin.strftime("%d/%m/%Y"), inicio)
        self.assertFalse(ok)


class TestCalculoDias(unittest.TestCase):
    def test_calculo_simple(self):
        inicio = date(2026, 7, 1)
        fin = date(2026, 7, 11)
        self.assertEqual(val.calcular_dias(inicio, fin), 10)


class TestValidarIdSolicitud(unittest.TestCase):
    def test_id_valido(self):
        ok, valor = val.validar_id_solicitud("5")
        self.assertTrue(ok)
        self.assertEqual(valor, 5)

    def test_id_invalido(self):
        ok, _ = val.validar_id_solicitud("abc")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
