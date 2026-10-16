import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/app_config.dart';

/// Cliente del canal de señalización WebRTC de una llamada.
///
/// Traduce el WebSocket crudo (`/ws/calls/{callId}`) a un stream de eventos
/// tipados que el motor de la llamada puede consumir sin conocer detalles
/// de transporte.
class SignalingClient {
  SignalingClient({required this.callId, required this.accessToken});

  final String callId;
  final String accessToken;

  WebSocketChannel? _channel;
  final _controller = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get messages => _controller.stream;

  Future<void> connect() async {
    final uri = Uri.parse('${AppConfig.wsBaseUrl}/ws/calls/$callId?token=$accessToken');
    _channel = WebSocketChannel.connect(uri);
    _channel!.stream.listen(
      (raw) {
        try {
          final decoded = jsonDecode(raw as String) as Map<String, dynamic>;
          _controller.add(decoded);
        } catch (_) {
          // Mensaje no-JSON inesperado: se ignora.
        }
      },
      onDone: () => _controller.close(),
      onError: (_) => _controller.close(),
    );
  }

  void send(Map<String, dynamic> message) {
    _channel?.sink.add(jsonEncode(message));
  }

  void sendOffer(String sdp) => send({'type': 'offer', 'sdp': sdp});

  void sendAnswer(String sdp) => send({'type': 'answer', 'sdp': sdp});

  void sendIceCandidate(Map<String, dynamic> candidate) => send({'type': 'ice-candidate', 'candidate': candidate});

  void sendCaption(String text) => send({'type': 'caption', 'text': text});

  /// Reconocimiento de señas en vivo (Fase 7): "mantener presionado para
  /// señas" dispara sendSignStart, manda frames sueltos con sendSignFrame
  /// mientras está presionado, y sendSignStop al soltar.
  void sendSignStart() => send({'type': 'sign-start'});

  void sendSignFrame(String base64Data) => send({'type': 'sign-frame', 'data': base64Data});

  void sendSignStop() => send({'type': 'sign-stop'});

  void sendLeave() => send({'type': 'leave'});

  Future<void> dispose() async {
    await _channel?.sink.close();
    await _controller.close();
  }
}
