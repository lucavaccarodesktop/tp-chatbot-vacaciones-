# -*- coding: utf-8 -*-
"""
config.py
Centraliza toda la configuración del bot. El token NUNCA se hardcodea en el
código: se lee desde un archivo .env (buena práctica para no subir
credenciales a GitHub por error).
"""
import os
from dotenv import load_dotenv

load_dotenv()  # busca un archivo .env en el mismo directorio

TOKEN = os.getenv("TELEGRAM_TOKEN", "")

DB_PATH = os.getenv("DB_PATH", "base_datos.xlsx")

# Reglas de negocio del proceso (parametrizables sin tocar el código)
DIAS_UMBRAL_APROBACION = int(os.getenv("DIAS_UMBRAL_APROBACION", "10"))
DIAS_MAXIMOS_SOLICITUD = int(os.getenv("DIAS_MAXIMOS_SOLICITUD", "60"))
DIAS_ANTICIPACION_MAXIMA = int(os.getenv("DIAS_ANTICIPACION_MAXIMA", "365"))

# Usuarios de Telegram autorizados a aprobar/rechazar solicitudes pendientes
# (simula el rol de "jefe directo"). Se configura como lista separada por comas
# en la variable de entorno, ej: "@mario_lopez,@andrea_ramos"
_jefes_raw = os.getenv("JEFES_AUTORIZADOS", "")
JEFES_AUTORIZADOS = {u.strip().lower() for u in _jefes_raw.split(",") if u.strip()}

LOG_FILE = os.getenv("LOG_FILE", "bot.log")

if not TOKEN:
    # No frenamos la importación (los tests no necesitan token), pero avisamos.
    import warnings
    warnings.warn(
        "TELEGRAM_TOKEN no está definido. Copiá .env.example a .env y completá "
        "el token antes de ejecutar bot.py."
    )
