# Diccionario de Datos

## Hoja "empleados" (base_datos.xlsx)

| Campo | Tipo | Descripción |
|---|---|---|
| legajo | Entero | Identificador único del empleado |
| nombre | Texto | Nombre y apellido del empleado |
| saldo_dias | Entero | Días de vacaciones disponibles actualmente |
| jefe_directo | Texto | Nombre del responsable que aprueba solicitudes extendidas |

## Hoja "solicitudes" (base_datos.xlsx)

| Campo | Tipo | Descripción |
|---|---|---|
| id_solicitud | Entero | Identificador correlativo de cada pedido |
| legajo | Entero | Legajo del empleado solicitante |
| fecha_inicio | Fecha (DD/MM/AAAA) | Primer día de las vacaciones solicitadas |
| fecha_fin | Fecha (DD/MM/AAAA) | Último día de las vacaciones solicitadas |
| dias_solicitados | Entero | Cantidad de días calculados entre ambas fechas |
| estado | Texto | APROBADO / RECHAZADO_SIN_SALDO / PENDIENTE_APROBACION / RECHAZADO_POR_JEFE |
| fecha_registro | Fecha y hora | Momento en que se registró la solicitud |
| resuelto_por | Texto | Usuario de Telegram del jefe que aprobó/rechazó (si aplica) |

## Variables de la máquina de estados (en memoria, por usuario)

| Variable | Dónde vive | Descripción |
|---|---|---|
| context.user_data["empleado"] | RAM (por chat) | Datos del empleado ya validado en la conversación actual |
| context.user_data["fecha_inicio"] | RAM (por chat) | Fecha de inicio ya validada, antes de pedir la fecha de fin |
| Estado del ConversationHandler | RAM (por chat) | PIDIENDO_LEGAJO / PIDIENDO_FECHA_INICIO / PIDIENDO_FECHA_FIN |
