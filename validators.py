# -*- coding: utf-8 -*-
"""
validators.py
Funciones puras de validación de entradas del usuario. Se separan de bot.py
a propósito para poder testearlas con unittest sin necesitar una conexión
real a Telegram (ver tests/test_validators.py).
"""
from datetime import datetime, date
from config import DIAS_MAXIMOS_SOLICITUD, DIAS_ANTICIPACION_MAXIMA


def validar_legajo(texto: str):
    """Devuelve (ok: bool, valor_o_error)."""
    texto = texto.strip()
    if not texto.isdigit():
        return False, "El legajo debe contener solo números."
    if len(texto) > 6:
        return False, "El legajo ingresado es demasiado largo."
    return True, int(texto)


def parsear_fecha(texto: str):
    """Devuelve un date o None si el formato DD/MM/AAAA es inválido."""
    texto = texto.strip()
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None


def validar_fecha_inicio(texto: str, hoy: date = None):
    hoy = hoy or date.today()
    fecha = parsear_fecha(texto)
    if fecha is None:
        return False, "Formato inválido. Usá DD/MM/AAAA (ej: 15/07/2026)."
    if fecha < hoy:
        return False, "La fecha de inicio no puede ser anterior a hoy."
    if (fecha - hoy).days > DIAS_ANTICIPACION_MAXIMA:
        return False, f"No se pueden solicitar vacaciones con más de " \
                       f"{DIAS_ANTICIPACION_MAXIMA} días de anticipación."
    return True, fecha


def validar_fecha_fin(texto: str, fecha_inicio: date):
    fecha_fin = parsear_fecha(texto)
    if fecha_fin is None:
        return False, "Formato inválido. Usá DD/MM/AAAA (ej: 20/07/2026)."
    if fecha_fin <= fecha_inicio:
        return False, "La fecha de fin debe ser posterior a la de inicio."
    dias = (fecha_fin - fecha_inicio).days
    if dias > DIAS_MAXIMOS_SOLICITUD:
        return False, f"No se pueden solicitar más de {DIAS_MAXIMOS_SOLICITUD} " \
                       f"días en una sola solicitud."
    return True, fecha_fin


def calcular_dias(fecha_inicio: date, fecha_fin: date) -> int:
    return (fecha_fin - fecha_inicio).days


def validar_id_solicitud(texto: str):
    texto = texto.strip()
    if not texto.isdigit():
        return False, "El ID de solicitud debe ser un número."
    return True, int(texto)
