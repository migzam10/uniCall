"""
Importa todos los modelos ORM para que:
1. Alembic pueda detectarlos automáticamente al generar migraciones.
2. Las relaciones entre modelos se resuelvan correctamente.

A medida que se agreguen nuevas entidades (Contacts, Calls, LSCSigns, etc.
según la sección 20), deben importarse aquí también.
"""
from app.models.profile import Profile  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401
from app.models.user_preferences import UserPreferences, VoicePreference  # noqa: F401
from app.models.contact import Contact  # noqa: F401
from app.models.contact_request import ContactRequest, ContactRequestStatus  # noqa: F401
from app.models.call import Call, CallStatus, generate_call_code  # noqa: F401
from app.models.call_participant import CallParticipant  # noqa: F401
from app.models.call_invitation import CallInvitation, CallInvitationStatus  # noqa: F401
from app.models.lsc_category import LSCCategory  # noqa: F401
from app.models.lsc_sign import LSCSign, LSCSignStatus  # noqa: F401
from app.models.lsc_video import LSCVideo  # noqa: F401
from app.models.lsc_phrase import LSCPhrase, LSCPhraseSign  # noqa: F401
from app.models.lsc_sign_template import LSCSignTemplate  # noqa: F401
