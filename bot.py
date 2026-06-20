# -*- coding: utf-8 -*-
"""
bot.py
Chatbot de Telegram que automatiza la "Gestión de Solicitud de Vacaciones".

Resumen de lo implementado (mapeado al diagrama BPMN del informe):
  - Carril Usuario: comandos /solicitar_vacaciones, /mi_saldo, /mis_solicitudes.
  - Carril Sistema/Bot: validación de legajo y fechas, cálculo de días,
    gateways de saldo suficiente y de umbral de aprobación.
  - Camino infeliz: reintentos ante cualquier dato mal ingresado, sin perder
    el progreso de la conversación.
  - Persistencia: base_datos.xlsx (hoja empleados + hoja solicitudes).
  - Máquina de estados: ConversationHandler de python-telegram-bot.
  - Rol de "jefe directo": comandos /pendientes, /aprobar, /rechazar,
    restringidos a usuarios autorizados (config.JEFES_AUTORIZADOS), que
    cierran el ciclo de las solicitudes derivadas por superar el umbral.

Autores: Guadalupe Soraire - Luca Vaccaro
Cátedra: Organización Empresarial - TUP a Distancia (UTN)
"""
import logging
from logging.handlers import RotatingFileHandler

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, ConversationHandler,
    MessageHandler, ContextTypes, filters,
)

import config
import db
import validators as val

# ---------------------------------------------------------------------------
# Logging: a consola y a archivo rotativo (no crece indefinidamente)
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(config.LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# Estados de la máquina de estados
PIDIENDO_LEGAJO, PIDIENDO_FECHA_INICIO, PIDIENDO_FECHA_FIN = range(3)


# ---------------------------------------------------------------------------
# Utilitario: verificar si quien escribe es un "jefe" autorizado
# ---------------------------------------------------------------------------
def es_jefe_autorizado(update: Update) -> bool:
    if not config.JEFES_AUTORIZADOS:
        # Si no se configuró ninguno, por seguridad no se permite aprobar nada.
        return False
    username = (update.effective_user.username or "").lower()
    return f"@{username}" in config.JEFES_AUTORIZADOS or username in config.JEFES_AUTORIZADOS


# ---------------------------------------------------------------------------
# Flujo principal: solicitud de vacaciones
# ---------------------------------------------------------------------------
async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "¡Hola! Soy el bot de Gestión de Vacaciones. 🌴\n"
        "Para comenzar, decime tu número de legajo (solo números).\n"
        "En cualquier momento podés escribir /cancelar.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PIDIENDO_LEGAJO


async def recibir_legajo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, valor = val.validar_legajo(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {valor}")
        return PIDIENDO_LEGAJO

    try:
        empleado = db.buscar_empleado(valor)
    except db.DBError as e:
        logger.error("Error de base de datos: %s", e)
        await update.message.reply_text(
            "🚧 Tuvimos un problema técnico accediendo a la base de datos. "
            "Probá nuevamente en unos segundos."
        )
        return PIDIENDO_LEGAJO

    if empleado is None:
        await update.message.reply_text(
            "❌ No encontré ese legajo en la base de datos.\n"
            "Probá de nuevo o escribí /cancelar para salir."
        )
        return PIDIENDO_LEGAJO

    context.user_data["empleado"] = empleado
    await update.message.reply_text(
        f"Hola {empleado['nombre']} 👋. Tenés {empleado['saldo']} días disponibles.\n"
        f"Ingresá la fecha de INICIO de tus vacaciones (formato DD/MM/AAAA):"
    )
    return PIDIENDO_FECHA_INICIO


async def recibir_fecha_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, valor = val.validar_fecha_inicio(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {valor}")
        return PIDIENDO_FECHA_INICIO

    context.user_data["fecha_inicio"] = valor
    await update.message.reply_text("Perfecto. Ahora ingresá la fecha de FIN (DD/MM/AAAA):")
    return PIDIENDO_FECHA_FIN


async def recibir_fecha_fin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fecha_inicio = context.user_data["fecha_inicio"]
    ok, valor = val.validar_fecha_fin(update.message.text, fecha_inicio)
    if not ok:
        await update.message.reply_text(f"⚠️ {valor}")
        return PIDIENDO_FECHA_FIN

    fecha_fin = valor
    empleado = context.user_data["empleado"]
    legajo = empleado["legajo"]
    saldo = empleado["saldo"]
    jefe = empleado["jefe"]
    dias = val.calcular_dias(fecha_inicio, fecha_fin)

    try:
        # --- Gateway: ¿Saldo suficiente? ---
        if dias > saldo:
            db.registrar_solicitud(legajo, fecha_inicio, fecha_fin, dias, "RECHAZADO_SIN_SALDO")
            await update.message.reply_text(
                f"❌ Solicitud RECHAZADA: pediste {dias} días pero solo tenés "
                f"{saldo} disponibles.\nGracias por usar el bot."
            )
            return ConversationHandler.END

        # --- Gateway: ¿Supera el umbral que exige aprobación del jefe? ---
        if dias > config.DIAS_UMBRAL_APROBACION:
            id_sol = db.registrar_solicitud(legajo, fecha_inicio, fecha_fin, dias,
                                             "PENDIENTE_APROBACION")
            await update.message.reply_text(
                f"📨 Tu solicitud Nº{id_sol} de {dias} días fue registrada como "
                f"PENDIENTE, ya que supera los {config.DIAS_UMBRAL_APROBACION} días y "
                f"requiere aprobación de tu jefe directo ({jefe}).\n"
                f"Te avisamos por este chat en cuanto se resuelva."
            )
            return ConversationHandler.END

        # --- Camino feliz: aprobación automática ---
        nuevo_saldo = saldo - dias
        db.actualizar_saldo(legajo, nuevo_saldo)
        db.registrar_solicitud(legajo, fecha_inicio, fecha_fin, dias, "APROBADO")
        await update.message.reply_text(
            f"✅ Solicitud APROBADA automáticamente.\n"
            f"Días tomados: {dias}. Saldo restante: {nuevo_saldo} días.\n"
            f"¡Disfrutá tus vacaciones!"
        )
        return ConversationHandler.END

    except db.DBError as e:
        logger.error("Error de base de datos: %s", e)
        await update.message.reply_text(
            "🚧 Tuvimos un problema técnico guardando tu solicitud. "
            "Por favor, intentá nuevamente en unos minutos."
        )
        return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Operación cancelada. Cuando quieras, volvé a escribir /solicitar_vacaciones.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Comandos de consulta para el empleado
# ---------------------------------------------------------------------------
async def mi_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /mi_saldo <legajo>")
        return
    legajo = int(context.args[0])
    try:
        empleado = db.buscar_empleado(legajo)
    except db.DBError as e:
        await update.message.reply_text(f"🚧 Error accediendo a la base de datos: {e}")
        return
    if empleado is None:
        await update.message.reply_text("❌ No encontré ese legajo.")
        return
    await update.message.reply_text(
        f"{empleado['nombre']}: tenés {empleado['saldo']} días disponibles."
    )


async def mis_solicitudes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /mis_solicitudes <legajo>")
        return
    legajo = int(context.args[0])
    try:
        historial = db.historial_por_legajo(legajo)
    except db.DBError as e:
        await update.message.reply_text(f"🚧 Error accediendo a la base de datos: {e}")
        return
    if not historial:
        await update.message.reply_text("No tenés solicitudes registradas.")
        return
    lineas = [
        f"Nº{s['id']} | {s['fecha_inicio']} → {s['fecha_fin']} | {s['dias']} días | {s['estado']}"
        for s in historial
    ]
    await update.message.reply_text("\n".join(lineas))


# ---------------------------------------------------------------------------
# Comandos restringidos al rol "jefe directo"
# ---------------------------------------------------------------------------
async def pendientes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not es_jefe_autorizado(update):
        await update.message.reply_text("⛔ Este comando es solo para jefes autorizados.")
        return
    try:
        lista = db.solicitudes_pendientes()
    except db.DBError as e:
        await update.message.reply_text(f"🚧 Error accediendo a la base de datos: {e}")
        return
    if not lista:
        await update.message.reply_text("No hay solicitudes pendientes de aprobación. ✅")
        return
    lineas = [
        f"Nº{s['id']} | Legajo {s['legajo']} | {s['fecha_inicio']} → {s['fecha_fin']} "
        f"| {s['dias']} días"
        for s in lista
    ]
    await update.message.reply_text(
        "Solicitudes pendientes:\n" + "\n".join(lineas) +
        "\n\nUsá /aprobar <Nº> o /rechazar <Nº> para resolverlas."
    )


async def _resolver_pendiente(update: Update, context: ContextTypes.DEFAULT_TYPE, aprobar: bool) -> None:
    if not es_jefe_autorizado(update):
        await update.message.reply_text("⛔ Este comando es solo para jefes autorizados.")
        return
    if not context.args:
        comando = "/aprobar" if aprobar else "/rechazar"
        await update.message.reply_text(f"Uso: {comando} <número de solicitud>")
        return

    ok, id_sol = val.validar_id_solicitud(context.args[0])
    if not ok:
        await update.message.reply_text(f"⚠️ {id_sol}")
        return

    try:
        solicitud = db.obtener_solicitud(id_sol)
        if solicitud is None:
            await update.message.reply_text("❌ No existe una solicitud con ese número.")
            return
        if solicitud["estado"] != "PENDIENTE_APROBACION":
            await update.message.reply_text(
                f"Esa solicitud ya fue resuelta (estado actual: {solicitud['estado']})."
            )
            return

        resuelto_por = f"@{update.effective_user.username}" if update.effective_user.username else "jefe"
        nuevo_estado = "APROBADO" if aprobar else "RECHAZADO_POR_JEFE"
        legajo, dias = db.actualizar_estado_solicitud(id_sol, nuevo_estado, resuelto_por)

        if aprobar:
            empleado = db.buscar_empleado(legajo)
            db.actualizar_saldo(legajo, empleado["saldo"] - dias)

        await update.message.reply_text(
            f"{'✅ Aprobada' if aprobar else '❌ Rechazada'} la solicitud Nº{id_sol}."
        )
    except db.DBError as e:
        await update.message.reply_text(f"🚧 Error accediendo a la base de datos: {e}")


async def aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _resolver_pendiente(update, context, aprobar=True)


async def rechazar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _resolver_pendiente(update, context, aprobar=False)


# ---------------------------------------------------------------------------
# Ayuda y fallback
# ---------------------------------------------------------------------------
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/solicitar_vacaciones - Inicia una solicitud nueva\n"
        "/mi_saldo <legajo> - Consulta tu saldo de días\n"
        "/mis_solicitudes <legajo> - Ver historial de solicitudes\n"
        "/cancelar - Cancela la solicitud en curso\n"
        "\nPara jefes autorizados:\n"
        "/pendientes - Lista solicitudes pendientes de aprobación\n"
        "/aprobar <Nº> - Aprueba una solicitud pendiente\n"
        "/rechazar <Nº> - Rechaza una solicitud pendiente"
    )


async def mensaje_fuera_de_contexto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "No entendí ese mensaje. Escribí /solicitar_vacaciones para iniciar "
        "una solicitud o /ayuda para ver los comandos disponibles."
    )


async def manejador_de_errores(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Captura cualquier excepción no prevista para que el bot nunca se caiga."""
    logger.error("Excepción no manejada: %s", context.error, exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "🚧 Ocurrió un error inesperado. Por favor, escribí /cancelar y volvé a intentar."
        )


def main():
    if not config.TOKEN:
        raise SystemExit(
            "Falta TELEGRAM_TOKEN. Copiá .env.example a .env y completá el token "
            "obtenido de @BotFather antes de ejecutar el bot."
        )

    app = Application.builder().token(config.TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("solicitar_vacaciones", iniciar)],
        states={
            PIDIENDO_LEGAJO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_legajo)],
            PIDIENDO_FECHA_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_fecha_inicio)],
            PIDIENDO_FECHA_FIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_fecha_fin)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("mi_saldo", mi_saldo))
    app.add_handler(CommandHandler("mis_solicitudes", mis_solicitudes))
    app.add_handler(CommandHandler("pendientes", pendientes))
    app.add_handler(CommandHandler("aprobar", aprobar))
    app.add_handler(CommandHandler("rechazar", rechazar))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_fuera_de_contexto))
    app.add_error_handler(manejador_de_errores)

    logger.info("Bot iniciado. Esperando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    main()
