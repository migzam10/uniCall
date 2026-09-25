import asyncio
import os
import sys

# Ajustar PYTHONPATH para que encuentre la carpeta app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.ai.translation.nlp_engine import translate_text_to_sign_sequence

async def test_translation():
    # Inicializamos la DB para que no falle la conexión asíncrona
    from app.core.database import engine
    from app.core.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with SessionLocal() as db:
        sentence = "Hola, yo quiero comer una manzana roja."
        print(f"Probando: '{sentence}'")
        res = await translate_text_to_sign_sequence(db, sentence)
        for item in res:
            print(item)

if __name__ == "__main__":
    asyncio.run(test_translation())
