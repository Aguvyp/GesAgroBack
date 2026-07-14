"""Procesamiento principal del bot de Telegram + OpenCode."""
import json
import logging
from typing import Any, Dict

from django.core.cache import cache

from .phone_auth import normalize_phone_number, get_user_by_phone
from .nlu_provider import LLMInterpreter
from .opencode_agent import call_function

logger = logging.getLogger(__name__)
PHONE_CACHE_TTL = 60 * 60 * 24


def _cache_phone(chat_id: int, phone: str) -> None:
    if not phone:
        return
    normalized = normalize_phone_number(phone)
    cache.set(f'telegram_phone_{chat_id}', normalized, timeout=PHONE_CACHE_TTL)


def _get_cached_phone(chat_id: int) -> str | None:
    return cache.get(f'telegram_phone_{chat_id}')


def _get_phone_for_chat(chat_id: int, contact_phone: str | None = None) -> str | None:
    cached = _get_cached_phone(chat_id)
    if cached:
        return cached
    if contact_phone:
        _cache_phone(chat_id, contact_phone)
        return normalize_phone_number(contact_phone)
    return None


def _build_contact_prompt() -> str:
    return (
        "Necesito verificar tu número de teléfono para identificar tu cuenta. "
        "Por favor comparte tu contacto desde Telegram o escribe tu número con + y código de país."
    )


def process_telegram_message(chat_id: int, text: str | None, contact_phone: str | None = None) -> Dict[str, Any]:
    if not text and not contact_phone:
        return {
            'success': False,
            'reply': 'Envíame un texto o comparte tu contacto desde el botón de Telegram.'
        }

    phone = _get_phone_for_chat(chat_id, contact_phone)
    if not phone:
        if contact_phone:
            phone = normalize_phone_number(contact_phone)
            _cache_phone(chat_id, phone)
        else:
            return {'success': False, 'reply': _build_contact_prompt()}

    user = get_user_by_phone(phone)
    if not user:
        return {
            'success': False,
            'reply': (
                'No encuentro una cuenta vinculada a ese número. Asegurate de usar el mismo teléfono que usás en la app.'
            )
        }

    interpreter = LLMInterpreter()
    interpretation = interpreter.interpret(text or '', usuario_id=user.id)

    if not interpretation.get('success'):
        return {'success': False, 'reply': interpretation.get('error', 'Error interpretando el mensaje.')}

    function_name = interpretation.get('function')
    arguments = interpretation.get('arguments', {}) or {}

    tool_result = call_function(function_name, arguments, usuario_id=user.id)

    if not tool_result.get('success'):
        error = tool_result.get('error', 'No se pudo ejecutar la acción solicitada.')
        return {'success': False, 'reply': error}

    message_parts = []
    if tool_result.get('message'):
        message_parts.append(tool_result['message'])
    if tool_result.get('data'):
        try:
            extra = json.dumps(tool_result['data'], ensure_ascii=False, default=str)
            message_parts.append(f"Datos: {extra}")
        except Exception:
            message_parts.append(str(tool_result['data']))

    reply = '\n'.join(message_parts) or 'Acción completada.'
    return {'success': True, 'reply': reply}
