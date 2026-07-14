"""Cliente ligero para llamar a un LLM gratuito self-hosted y obtener instrucciones de funciones."""
import json
import logging
from typing import Dict, Optional

import requests
from django.conf import settings

from .opencode_agent import FUNCTION_DEFINITIONS

logger = logging.getLogger(__name__)

LLM_INSTRUCTIONS = """
Eres OpenCode, un asistente que gestiona una empresa agrícola. Puedes llamar a funciones CRUD (create, update, delete, get) para trabajos, campos, clientes, costos y personal.
Responde siempre en español. Cuando no estés seguro, pide más datos.
Devuelve SOLO un JSON válido con las claves:
  - "function": nombre de la función que vas a llamar.
  - "arguments": diccionario con los parámetros necesarios.
"""


def _build_prompt(message: str) -> str:
    funciones = "\n".join([f"- {fn['name']}: {fn['description']}" for fn in FUNCTION_DEFINITIONS])
    return (
        f"{LLM_INSTRUCTIONS}\nDisponibles:\n{funciones}\n\nMensaje del usuario:\n{message}\n\nResponde solo con JSON válido."
    )


def _parse_json(text: str) -> Optional[Dict]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                logger.debug('No se pudo parsear JSON del contenido parcial')
        logger.debug('Respuesta no contiene JSON válido')
        return None


class LLMInterpreter:
    def __init__(self):
        self.url = getattr(settings, 'LLM_PROVIDER_URL', '')
        self.api_key = getattr(settings, 'LLM_PROVIDER_KEY', None)

    def is_ready(self) -> bool:
        return bool(self.url)

    def interpret(self, message: str, usuario_id: Optional[int] = None) -> Dict:
        if not self.is_ready():
            return {
                'success': False,
                'error': 'LLM no configurado. Define LLM_PROVIDER_URL para apuntar a un modelo gratuito.',
            }

        prompt = _build_prompt(message)
        payload = {'inputs': prompt, 'parameters': {'max_new_tokens': 250, 'temperature': 0}}
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            body = response.json()
        except Exception as exc:
            logger.error('Error llamando al LLM: %s', exc)
            return {'success': False, 'error': f'Error llamando al modelo: {exc}'}

        if isinstance(body, list) and body:
            text = body[0].get('generated_text') or body[0].get('text')
        elif isinstance(body, dict) and 'generated_text' in body:
            text = body.get('generated_text')
        elif isinstance(body, dict) and 'output' in body:
            text = body.get('output')
        else:
            text = body if isinstance(body, str) else ''

        parsed = _parse_json(text)
        if not parsed:
            return {
                'success': False,
                'error': 'No se pudo interpretar la respuesta del modelo. Asegurate de que devuelva JSON con function y arguments.'
            }

        if 'function' not in parsed:
            return {'success': False, 'error': 'Falta la clave function en la respuesta del modelo.'}

        return {
            'success': True,
            'function': parsed['function'],
            'arguments': parsed.get('arguments', {}),
        }
