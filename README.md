# Bot de Gestión de Solicitud de Vacaciones Empresa Solutech S.A.

Trabajo Práctico Integrador — Organización Empresarial
TUP a Distancia (UTN) — Cohorte Marzo 2026

**Integrantes:** Rosario Guadaluype Mallón — Luca Vaccaro

## Descripción

Chatbot de Telegram que automatiza el proceso administrativo de solicitud de
vacaciones de un empleado, siguiendo el modelo BPMN 2.0 incluido en
`docs/bpmn_vacaciones.png`. Incluye:

- Máquina de estados real (`ConversationHandler`) para el flujo del empleado.
- Persistencia en una base de datos simulada en Excel (`base_datos.xlsx`).
- Rol de **jefe directo**, que puede aprobar o rechazar solicitudes derivadas
  por superar el umbral de días, desde el propio chat de Telegram.
- Manejo robusto de errores: reintentos ante archivo bloqueado, validaciones
  desacopladas y testeadas, manejador global de excepciones para que el bot
  nunca se caiga ante un error inesperado.
- Logging a archivo rotativo (`bot.log`) además de consola.
- 17 tests automáticos sobre las validaciones (camino infeliz).

## Estructura del repositorio

```
.
├── bot.py                   # Lógica de conversación y comandos de Telegram
├── db.py                    # Acceso a la base de datos simulada (Excel)
├── validators.py            # Validaciones puras (testeables sin Telegram)
├── config.py                # Configuración vía variables de entorno
├── crear_db.py               # Inicializa base_datos.xlsx
├── base_datos.xlsx           # Persistencia: empleados y solicitudes
├── requirements.txt
├── .env.example               # Plantilla de variables de entorno
├── .gitignore
├── tests/
│   └── test_validators.py    # 17 pruebas automáticas
└── docs/
    ├── bpmn_vacaciones.png
    ├── diccionario_datos.md
    └── manual_usuario.md
```

## Requisitos

- Python 3.10+
- Un bot creado en Telegram hablando con **@BotFather** (te da el token).

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

1. Copiar `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
2. Completar `TELEGRAM_TOKEN` con el token de @BotFather.
3. (Opcional) Completar `JEFES_AUTORIZADOS` con los usuarios de Telegram que
   van a poder usar `/aprobar` y `/rechazar`, ej:
   `JEFES_AUTORIZADOS=@mario_lopez,@andrea_ramos`
4. Generar la base de datos simulada (solo la primera vez):
   ```bash
   python crear_db.py
   ```

## Ejecución

```bash
python bot.py
```

## Correr los tests

```bash
python -m unittest tests/test_validators.py -v
```

## Comandos del bot

### Empleados
| Comando | Función |
|---|---|
| `/solicitar_vacaciones` | Inicia el proceso de solicitud |
| `/mi_saldo <legajo>` | Consulta el saldo de días disponibles |
| `/mis_solicitudes <legajo>` | Ver historial de solicitudes y su estado |
| `/cancelar` | Cancela la solicitud en curso en cualquier paso |
| `/ayuda` | Muestra los comandos disponibles |

### Jefes autorizados
| Comando | Función |
|---|---|
| `/pendientes` | Lista solicitudes pendientes de aprobación |
| `/aprobar <Nº>` | Aprueba una solicitud pendiente y actualiza el saldo |
| `/rechazar <Nº>` | Rechaza una solicitud pendiente |

## Datos de prueba precargados

| Legajo | Nombre | Saldo inicial |
|---|---|---|
| 1001 | Guadalupe Soraire | 14 días |
| 1002 | Luca Vaccaro | 8 días |
| 1003 | Rosario Mallón | 20 días |
| 1004 | Mauro Rodríguez | 3 días |

Usalos para probar los distintos caminos: aprobación automática (pocos días),
rechazo por falta de saldo (legajo 1004 pidiendo muchos días), y derivación a
aprobación del jefe (pedir más de 10 días con saldo suficiente, ej. legajo 1003).
