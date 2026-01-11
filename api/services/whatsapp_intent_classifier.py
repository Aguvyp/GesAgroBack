"""
Clasificador de intenciones usando embeddings locales con sentence-transformers.
Detecta qué acción quiere realizar el usuario basándose en similitud semántica.
"""
from sentence_transformers import SentenceTransformer
from typing import Dict, Tuple, Optional
import logging
import numpy as np
from .whatsapp_knowledge_base import get_intentions, get_all_examples, get_intentions_list

logger = logging.getLogger(__name__)

# Cache del modelo
_model = None
_intent_embeddings = None


def get_model():
    """
    Obtiene el modelo de embeddings, cargándolo solo una vez.
    
    Returns:
        Modelo SentenceTransformer
    """
    global _model
    if _model is None:
        logger.info("Cargando modelo de embeddings: paraphrase-multilingual-MiniLM-L12-v2")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("Modelo de embeddings cargado exitosamente")
    return _model


def get_intent_embeddings():
    """
    Obtiene los embeddings de todas las intenciones, calculándolos solo una vez.
    
    Returns:
        Diccionario con intención -> embedding
    """
    global _intent_embeddings
    if _intent_embeddings is None:
        logger.info("Calculando embeddings de intenciones...")
        model = get_model()
        intentions = get_intentions()
        _intent_embeddings = {}
        
        for intent, examples in intentions.items():
            # Calcular embedding promedio de todos los ejemplos
            embeddings = model.encode(examples)
            # Promediar los embeddings
            avg_embedding = np.mean(embeddings, axis=0)
            _intent_embeddings[intent] = avg_embedding
        
        logger.info(f"Embeddings calculados para {len(_intent_embeddings)} intenciones")
    
    return _intent_embeddings


def classify_intent(message: str, threshold: float = 0.5) -> Tuple[Optional[str], float]:
    """
    Clasifica la intención de un mensaje usando similitud de embeddings.
    
    Args:
        message: Mensaje del usuario
        threshold: Umbral mínimo de similitud (0-1)
        
    Returns:
        Tupla (intención, score) o (None, score) si no supera el threshold
    """
    try:
        model = get_model()
        intent_embeddings = get_intent_embeddings()
        
        # Calcular embedding del mensaje
        message_embedding = model.encode([message])[0]
        
        # Calcular similitud con cada intención
        best_intent = None
        best_score = 0.0
        
        for intent, intent_embedding in intent_embeddings.items():
            # Calcular similitud coseno
            cosine_sim = np.dot(message_embedding, intent_embedding) / (
                np.linalg.norm(message_embedding) * np.linalg.norm(intent_embedding)
            )
            
            if cosine_sim > best_score:
                best_score = cosine_sim
                best_intent = intent
        
        # Verificar si supera el threshold
        logger.debug(f"   Comparando con threshold: {threshold}")
        logger.debug(f"   Mejor intención: {best_intent} con score: {best_score:.3f}")
        
        if best_score >= threshold:
            logger.info(f"   ✅ Intención detectada: {best_intent} (score: {best_score:.3f})")
            return best_intent, best_score
        else:
            logger.warning(f"   ⚠️ No se detectó intención clara (mejor score: {best_score:.3f} < threshold: {threshold})")
            return None, best_score
            
    except Exception as e:
        logger.error(f"Error clasificando intención: {str(e)}")
        return None, 0.0
