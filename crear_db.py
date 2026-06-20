# -*- coding: utf-8 -*-
"""
crear_db.py
Inicializa base_datos.xlsx con datos de ejemplo. Ejecutar una sola vez,
o cada vez que se quiera resetear la base de datos a su estado inicial.

Uso: python crear_db.py
"""
import os
from config import DB_PATH
import db

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        respuesta = input(f"'{DB_PATH}' ya existe. ¿Reescribir y perder los datos "
                           f"actuales? (s/n): ")
        if respuesta.strip().lower() != "s":
            print("Operación cancelada.")
            raise SystemExit
    db.crear_base()
    print(f"'{DB_PATH}' creado con éxito con datos de ejemplo.")
