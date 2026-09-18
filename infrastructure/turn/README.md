# Servidor TURN/STUN (Fase 2)

Aquí se configurará el servidor TURN (p. ej. coturn) para usuarios detrás de
NAT/firewalls estrictos que no puedan conectar directamente vía WebRTC.
Mientras tanto, el backend expone `STUN_SERVER`/`TURN_SERVER` como variables
de entorno (ver `backend/.env.example`) para que el frontend los consuma al
configurar la conexión WebRTC.
