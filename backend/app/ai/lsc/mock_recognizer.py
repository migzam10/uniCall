from app.ai.lsc.base import LSCRecognitionResult, LSCRecognizer


class MockLSCRecognizer(LSCRecognizer):
    async def recognize(self, video_bytes: bytes) -> LSCRecognitionResult:
        if not video_bytes:
            return LSCRecognitionResult(matched=False, message="No se recibió video.")
        return LSCRecognitionResult(
            matched=True,
            sign_id="00000000-0000-0000-0000-000000000000",
            word="[reconocimiento simulado]",
            meaning="Resultado de prueba",
            confidence=1.0,
        )
