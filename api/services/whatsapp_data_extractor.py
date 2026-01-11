"""
Extractor de datos de mensajes de texto.
Extrae fechas, montos, nombres y otras entidades de los mensajes.
"""
import re
import dateparser
from datetime import datetime, date
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


def extract_dates(text: str) -> List[Dict[str, any]]:
    """
    Extrae fechas del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Lista de diccionarios con {'text': texto encontrado, 'date': objeto date}
    """
    dates = []
    
    # Patrones comunes de fechas
    patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 15/03/2024, 15-03-24
        r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}',  # 15 de marzo de 2024
        r'\d{1,2}\s+de\s+\w+',  # 15 de marzo (asume año actual)
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_text = match.group()
            parsed_date = dateparser.parse(date_text, languages=['es'])
            if parsed_date:
                dates.append({
                    'text': date_text,
                    'date': parsed_date.date(),
                    'start': match.start(),
                    'end': match.end()
                })
    
    # Palabras clave de tiempo relativo
    relative_keywords = {
        'hoy': date.today(),
        'mañana': date.today().replace(day=date.today().day + 1) if date.today().day < 28 else None,
        'ayer': date.today().replace(day=date.today().day - 1) if date.today().day > 1 else None,
    }
    
    text_lower = text.lower()
    for keyword, date_obj in relative_keywords.items():
        if keyword in text_lower and date_obj:
            dates.append({
                'text': keyword,
                'date': date_obj,
                'start': text_lower.find(keyword),
                'end': text_lower.find(keyword) + len(keyword)
            })
    
    return dates


def extract_amounts(text: str) -> List[Dict[str, any]]:
    """
    Extrae montos/números monetarios del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Lista de diccionarios con {'text': texto encontrado, 'amount': float}
    """
    amounts = []
    
    # Patrones para montos (ordenados: más específicos primero)
    # IMPORTANTE: El patrón simple $10000 debe ir ANTES del que espera separadores
    patterns = [
        (r'\$\s*(\d+)', True),  # $10000 (sin separadores) - usar grupo directamente
        (r'\$\s*(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{2})?)', False),  # $50.000, $50,000.00 (con separadores)
        (r'(\d+)\s*(?:mil|millones)', True),  # 10 mil, 5 millones - usar grupo directamente
        (r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:pesos|dólares|usd|ars)', False),  # 50000 pesos
        (r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:mil|millones)', False),  # 50 mil
    ]
    
    for pattern, use_group_directly in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_text = match.group()
            
            # Si el patrón captura directamente el número, usarlo
            if use_group_directly:
                number_str = match.group(1)
            else:
                # Para otros patrones, extraer el número del texto completo
                number_match = re.search(r'(\d+(?:[.,]\d+)?)', amount_text)
                if not number_match:
                    continue
                number_str = number_match.group(1)
                # Si tiene punto o coma, determinar si es separador de miles o decimales
                if '.' in number_str and ',' in number_str:
                    # Formato: 50.000,50 (punto para miles, coma para decimales)
                    number_str = number_str.replace('.', '').replace(',', '.')
                elif ',' in number_str and len(number_str.split(',')[1]) <= 2:
                    # Formato: 50000,50 (coma para decimales)
                    number_str = number_str.replace(',', '.')
                else:
                    # Formato: 50000 o 50.000 (punto para miles o sin separador)
                    number_str = number_str.replace('.', '').replace(',', '')
            
            try:
                amount = float(number_str)
                # Si dice "mil", multiplicar por 1000
                if 'mil' in amount_text.lower():
                    amount *= 1000
                elif 'millones' in amount_text.lower() or 'millón' in amount_text.lower():
                    amount *= 1000000
                amounts.append({
                    'text': amount_text,
                    'amount': amount,
                    'start': match.start(),
                    'end': match.end()
                })
                logger.debug(f"Monto extraído: {amount} de '{amount_text}'")
            except ValueError:
                pass
    
    return amounts


def extract_names(text: str, keywords: List[str]) -> List[str]:
    """
    Extrae nombres después de palabras clave.
    
    Args:
        text: Texto a analizar
        keywords: Lista de palabras clave (ej: ['campo', 'cliente', 'cultivo'])
        
    Returns:
        Lista de nombres encontrados
    """
    names = []
    text_lower = text.lower()
    
    # Palabras que indican fin del nombre (artículos, preposiciones comunes antes de fechas/números)
    stop_words = ['el', 'la', 'los', 'las', 'del', 'de', 'para', 'con', 'en', 'a', 'por']
    
    for keyword in keywords:
        # Buscar patrón: keyword + " " + nombre
        # Mejorado para manejar "en campo X" y detenerse antes de artículos seguidos de fechas
        pattern = rf'{re.escape(keyword)}\s+([^,.\n]+?)(?:\s+(?:el|la|los|las|del|de|para|con|en|a|por)\s+\d|[,.\n]|$)'
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            name = match.group(1).strip()
            # Limpiar el nombre: eliminar palabras stop al final
            name_parts = name.split()
            # Si la última palabra es un stop word, eliminarla
            if name_parts and name_parts[-1] in stop_words:
                name = ' '.join(name_parts[:-1])
            # Filtrar nombres muy cortos o que sean solo números
            if len(name) > 2 and not name.isdigit():
                names.append(name)
                logger.debug(f"Nombre extraído con keyword '{keyword}': {name}")
    
    # También buscar entre comillas
    quoted = re.findall(r'["\']([^"\']+)["\']', text)
    names.extend(quoted)
    
    # Si no se encontraron nombres con keywords, intentar patrón más flexible para "campo"
    if 'campo' in keywords and not names:
        # Buscar "campo X" o "en campo X" de forma más flexible
        pattern = r'(?:en\s+)?campo\s+([A-Za-záéíóúñÁÉÍÓÚÑ]+)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            name = match.group(1).strip()
            if len(name) > 2:
                names.append(name)
                logger.debug(f"Nombre de campo extraído (patrón flexible): {name}")
    
    return names


def extract_descriptions(text: str) -> List[str]:
    """
    Extrae descripciones/destinatarios del texto.
    Busca después de palabras clave como "gasto de", "costo de", "para", etc.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Lista de descripciones encontradas
    """
    descriptions = []
    text_lower = text.lower()
    
    # Patrones para descripciones/destinatarios (más específicos)
    patterns = [
        # "gasto de combustible el dia" -> "combustible"
        r'(?:gasto|costo|pago|desembolso)\s+de\s+([a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)?)\s+(?:el\s+(?:día|dia)|para|con|,|\.|$)',
        # "gasto de combustible" -> "combustible"
        r'(?:gasto|costo|pago|desembolso)\s+de\s+([a-záéíóúñ]+)',
        # "para combustible" -> "combustible"
        r'para\s+([a-záéíóúñ]+(?:\s+[a-záéíóúñ]+)?)(?:\s+(?:el|de|para|con|,|\.|$))',
        # "descripción: combustible"
        r'descripci[óo]n\s*:?\s*([a-záéíóúñ\s]+?)(?:,|\.|$)',
        # "detalle: combustible"
        r'detalle\s*:?\s*([a-záéíóúñ\s]+?)(?:,|\.|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            desc = match.group(1).strip()
            # Filtrar descripciones muy cortas, números, o palabras comunes
            if len(desc) > 2 and not desc.isdigit() and desc not in ['el', 'la', 'los', 'las', 'de', 'para']:
                # Limpiar palabras comunes al final
                desc = re.sub(r'\s+(el|la|los|las|de|para|con|en|a|por|día|dia)$', '', desc)
                if len(desc) > 2:
                    descriptions.append(desc)
                    logger.debug(f"Descripción extraída: {desc}")
    
    # También buscar entre comillas
    quoted = re.findall(r'["\']([^"\']+)["\']', text)
    descriptions.extend(quoted)
    
    return descriptions


def extract_work_type(text: str) -> Optional[str]:
    """
    Extrae tipo de trabajo mencionado en el texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Nombre del tipo de trabajo o None
    """
    work_types = ['siembra', 'cosecha', 'pulverización', 'pulverizar', 'labranza', 'arado', 'fertilización', 'fertilizar']
    text_lower = text.lower()
    
    for work_type in work_types:
        if work_type in text_lower:
            logger.debug(f"   Tipo de trabajo encontrado: {work_type}")
            return work_type
    
    # Si no encuentra directamente, buscar patrones como "trabajo de X"
    pattern = r'trabajo\s+de\s+([a-záéíóúñ]+)'
    match = re.search(pattern, text_lower)
    if match:
        work_type = match.group(1)
        logger.debug(f"   Tipo de trabajo encontrado por patrón: {work_type}")
        return work_type
    
    return None


def extract_crop(text: str) -> Optional[str]:
    """
    Extrae cultivo mencionado en el texto.
    Solo busca cultivos conocidos, no palabras genéricas.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Nombre del cultivo o None
    """
    crops = ['soja', 'maíz', 'trigo', 'girasol', 'sorgo', 'cebada', 'avena']
    text_lower = text.lower()
    
    for crop in crops:
        if crop in text_lower:
            # Verificar que no sea parte de otra palabra (ej: "combustible" no debe ser cultivo)
            pattern = rf'\b{crop}\b'
            if re.search(pattern, text_lower):
                return crop
    
    # Buscar después de "cultivo" específicamente (no solo "de")
    pattern = r'cultivo\s+(?:de\s+)?([a-záéíóúñ]+)'
    match = re.search(pattern, text_lower)
    if match:
        crop_candidate = match.group(1)
        # Verificar que sea un cultivo conocido
        if crop_candidate in crops:
            return crop_candidate
    
    return None


def extract_all_data(text: str) -> Dict[str, any]:
    """
    Extrae todos los datos posibles del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Diccionario con todos los datos extraídos
    """
    logger.debug(f"   Extrayendo datos de: '{text}'")
    
    dates = extract_dates(text)
    amounts = extract_amounts(text)
    work_type = extract_work_type(text)
    crop = extract_crop(text)
    field_names = extract_names(text, ['campo', 'en campo'])
    client_names = extract_names(text, ['cliente', 'para cliente'])
    descriptions = extract_descriptions(text)
    
    logger.debug(f"   Fechas extraídas: {len(dates)}")
    logger.debug(f"   Montos extraídos: {len(amounts)}")
    logger.debug(f"   Tipo trabajo: {work_type}")
    logger.debug(f"   Cultivo: {crop}")
    logger.debug(f"   Campos: {field_names}")
    logger.debug(f"   Clientes: {client_names}")
    logger.debug(f"   Descripciones: {descriptions}")
    
    return {
        'dates': dates,
        'amounts': amounts,
        'work_type': work_type,
        'crop': crop,
        'field_names': field_names,
        'client_names': client_names,
        'descriptions': descriptions,
    }
