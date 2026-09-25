"""
Motor de Traducción (NLP) de Español a Lengua de Señas Colombiana (LSC).

Este módulo utiliza spaCy para procesar texto en español (hablado o escrito)
y adaptarlo a la sintaxis y gramática general de la LSC. Posteriormente, 
busca las palabras resultantes en la base de datos (LSCSign) para devolver 
la secuencia exacta de IDs de animaciones 3D.
"""
import spacy
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lsc_sign import LSCSign, LSCSignStatus

# Intentamos cargar el modelo. Si no está instalado, fallará.
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    raise OSError(
        "El modelo 'es_core_news_sm' de spaCy no está instalado. "
        "Ejecuta: python -m spacy download es_core_news_sm"
    )

def translate_to_lsc_syntax(spanish_text: str) -> list[str]:
    """
    Recibe una frase en español y devuelve una lista de palabras "lematizadas" 
    y filtradas que representan la estructura aproximada en LSC.
    """
    doc = nlp(spanish_text)
    lsc_words = []
    
    for token in doc:
        # 1. Ignorar signos de puntuación y espacios
        if token.is_punct or token.is_space:
            continue
            
        # 2. Ignorar "stop words" que no tienen equivalente directo o son redundantes en LSC
        if token.pos_ in ["DET", "ADP", "CCONJ", "SCONJ"]:
            continue
            
        # 3. Lematizar (llevar al verbo infinitivo o sustantivo singular)
        lemma = token.lemma_.upper()
        lsc_words.append(lemma)
        
    return lsc_words


async def translate_text_to_sign_sequence(session: AsyncSession, spanish_text: str) -> list[dict]:
    """
    Flujo completo Fase 6:
    1. Convierte el texto español a sintaxis LSC (lista de palabras clave).
    2. Consulta la base de datos para buscar si existe una seña (`LSCSign`) validada para esa palabra.
    3. Devuelve una lista de diccionarios con la palabra y el ID de su animación.
    """
    lsc_words = translate_to_lsc_syntax(spanish_text)
    sequence = []
    
    for word in lsc_words:
        # Buscamos la seña en la BD ignorando mayúsculas/minúsculas.
        # Exigimos que la seña esté activa y publicada (validada).
        stmt = select(LSCSign).where(
            func.upper(LSCSign.word) == word,
            LSCSign.is_active == True,
            LSCSign.status == LSCSignStatus.PUBLISHED
        )
        result = await session.execute(stmt)
        sign = result.scalars().first()
        
        sequence.append({
            "word": word,
            "sign_id": str(sign.id) if sign else None,
            "found_in_db": sign is not None
        })
        
    return sequence

