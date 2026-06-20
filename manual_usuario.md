# Manual de Usuario — Bot de Gestión de Vacaciones

## Para empleados

| Comando | Qué hace |
|---|---|
| `/solicitar_vacaciones` | Inicia una solicitud nueva. El bot pide legajo, fecha de inicio y fecha de fin. |
| `/mi_saldo <legajo>` | Consulta cuántos días de vacaciones tenés disponibles. |
| `/mis_solicitudes <legajo>` | Muestra el historial de todas tus solicitudes y su estado. |
| `/cancelar` | Cancela la solicitud que estás completando en ese momento. |
| `/ayuda` | Muestra la lista de comandos disponibles. |

### Flujo típico de una solicitud

1. Escribís `/solicitar_vacaciones`.
2. El bot te pide tu legajo → lo ingresás (solo números).
3. El bot te muestra tu saldo y te pide la fecha de inicio (DD/MM/AAAA).
4. Te pide la fecha de fin (DD/MM/AAAA).
5. El bot responde automáticamente con una de estas tres resoluciones:
   - ✅ **Aprobado**: si hay saldo suficiente y los días no superan el umbral de aprobación.
   - ❌ **Rechazado**: si no tenés saldo suficiente.
   - 📨 **Pendiente**: si los días solicitados superan el umbral (10 días por defecto) y se deriva a tu jefe directo.

### Si te equivocás al escribir algo

El bot nunca pierde tu progreso: si ingresás un legajo inexistente o una fecha en
formato incorrecto, te lo va a indicar y te va a pedir que lo vuelvas a escribir,
sin necesidad de empezar de nuevo.

## Para jefes/aprobadores

Estos comandos solo funcionan si tu usuario de Telegram (@usuario) está incluido
en la variable `JEFES_AUTORIZADOS` del archivo `.env`.

| Comando | Qué hace |
|---|---|
| `/pendientes` | Lista todas las solicitudes que están esperando tu aprobación. |
| `/aprobar <Nº>` | Aprueba la solicitud con ese número y descuenta el saldo del empleado. |
| `/rechazar <Nº>` | Rechaza la solicitud con ese número. |
