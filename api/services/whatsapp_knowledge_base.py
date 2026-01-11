"""
Base de conocimiento con ejemplos de intenciones para clasificación.
Contiene patrones y ejemplos de cómo los usuarios pueden expresar diferentes intenciones.
"""
from typing import Dict, List


# Base de conocimiento de intenciones
INTENTIONS_KNOWLEDGE_BASE: Dict[str, List[str]] = {
    'crear_trabajo': [
        'crear trabajo',
        'nuevo trabajo',
        'trabajo de siembra',
        'trabajo de siembra de soja',
        'crear trabajo de siembra',
        'crear trabajo de siembra de soja',
        'trabajo de siembra en campo',
        'crear trabajo de siembra en campo',
        'trabajo de cosecha',
        'trabajo de pulverización',
        'trabajo de labranza',
        'registrar trabajo',
        'agregar trabajo',
        'trabajo nuevo',
        'iniciar trabajo',
        'comenzar trabajo',
        'hacer trabajo',
        'realizar trabajo',
        'trabajo en campo',
        'siembra en campo',
        'siembra de soja en campo',
        'cosecha en',
        'pulverizar en',
        'trabajo el',
        'trabajo para el',
        'trabajo fecha',
    ],
    'crear_costo': [
        'crear costo',
        'nuevo costo',
        'registrar costo',
        'agregar costo',
        'costo de',
        'gasto de',
        'pago de',
        'gasto',
        'costo',
        'pago',
        'desembolso',
        'egreso',
        'gasté',
        'pagué',
        'compré',
    ],
    'crear_campo': [
        'crear campo',
        'nuevo campo',
        'registrar campo',
        'agregar campo',
        'campo llamado',
        'campo nuevo',
        'campo con nombre',
        'campo de',
        'nuevo campo llamado',
    ],
    'crear_cliente': [
        'crear cliente',
        'nuevo cliente',
        'registrar cliente',
        'agregar cliente',
        'cliente llamado',
        'cliente nuevo',
        'cliente con nombre',
        'cliente de',
        'nuevo cliente llamado',
    ],
}


def get_intentions() -> Dict[str, List[str]]:
    """
    Retorna la base de conocimiento de intenciones.
    
    Returns:
        Diccionario con intenciones y sus ejemplos
    """
    return INTENTIONS_KNOWLEDGE_BASE


def get_all_examples() -> List[str]:
    """
    Retorna todos los ejemplos de todas las intenciones en una lista plana.
    
    Returns:
        Lista de todos los ejemplos
    """
    examples = []
    for intent_examples in INTENTIONS_KNOWLEDGE_BASE.values():
        examples.extend(intent_examples)
    return examples


def get_intentions_list() -> List[str]:
    """
    Retorna la lista de todas las intenciones disponibles.
    
    Returns:
        Lista de nombres de intenciones
    """
    return list(INTENTIONS_KNOWLEDGE_BASE.keys())
