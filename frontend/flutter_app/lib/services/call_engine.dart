import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';

import '../models/call_info.dart';
import '../models/lsc_translation.dart';
import '../repositories/lsc_translation_repository.dart';
import 'signaling_client.dart';

/// Cuánto tiempo se muestra cada palabra/animación de una secuencia
/// traducida antes de avanzar a la siguiente. Corte seco, sin
/// interpolación entre animaciones (decisión documentada en README §5.1:
/// el blending queda como TODO explícito para una fase posterior).
const _avatarSequenceStepDuration = Duration(milliseconds: 2500);

enum CallEngineStatus { connecting, waitingForPeer, negotiating, connected, ended, error }

/// Motor de videollamada 1:1.
///
/// Coordina:
/// - Captura de audio/video local (getUserMedia).
/// - Creación del RTCPeerConnection con los servidores ICE del backend.
/// - Intercambio de offer/answer/ICE candidates a través de [SignalingClient].
///
/// El audio/video viaja directo entre los dos peers vía WebRTC; el
/// servidor solo transporta los mensajes de señalización (sección 2).
class CallEngine extends ChangeNotifier {
  CallEngine({
    required this.signaling,
    required this.translationRepository,
    required List<IceServerConfig> iceServers,
  }) : _iceServers = iceServers;

  final SignalingClient signaling;
  final LscTranslationRepository translationRepository;
  final List<IceServerConfig> _iceServers;

  RTCPeerConnection? _peerConnection;
  MediaStream? localStream;
  MediaStream? remoteStream;

  CallEngineStatus status = CallEngineStatus.connecting;
  bool isMicEnabled = true;
  bool isCameraEnabled = true;
  String? errorMessage;

  /// Último texto de apoyo propio enviado y el recibido del otro
  /// participante (sección 17: texto en la videollamada).
  String? localCaption;
  String? remoteCaption;

  /// Traducción a LSC del último `remoteCaption` recibido, y qué item de la
  /// secuencia se está mostrando ahora mismo en el avatar (Fase 6).
  LscTranslationResult? currentTranslation;
  int currentSequenceIndex = 0;
  Timer? _sequenceTimer;

  LscTranslationItem? get currentTranslationItem {
    final translation = currentTranslation;
    if (translation == null || translation.sequence.isEmpty) return null;
    if (currentSequenceIndex >= translation.sequence.length) return null;
    return translation.sequence[currentSequenceIndex];
  }

  StreamSubscription? _signalingSubscription;
  String? _remotePeerId;
  String? get remotePeerId => _remotePeerId;

  Future<void> initialize() async {
    try {
      await _openLocalMedia();
      await _createPeerConnection();

      _signalingSubscription = signaling.messages.listen(_handleSignalingMessage);
      await signaling.connect();

      status = CallEngineStatus.waitingForPeer;
      notifyListeners();
    } catch (e) {
      status = CallEngineStatus.error;
      errorMessage = 'No se pudo acceder a la cámara o el micrófono.';
      notifyListeners();
    }
  }

  Future<void> _openLocalMedia() async {
    localStream = await navigator.mediaDevices.getUserMedia({
      'audio': true,
      'video': {
        'facingMode': 'user',
        'width': {'ideal': 1280},
        'height': {'ideal': 720},
      },
    });
  }

  Future<void> _createPeerConnection() async {
    final config = {
      'iceServers': _iceServers.map((s) => s.toWebRTCConfig()).toList(),
      'sdpSemantics': 'unified-plan',
    };

    _peerConnection = await createPeerConnection(config);

    for (final track in localStream!.getTracks()) {
      await _peerConnection!.addTrack(track, localStream!);
    }

    _peerConnection!.onTrack = (RTCTrackEvent event) {
      if (event.streams.isNotEmpty) {
        remoteStream = event.streams.first;
        status = CallEngineStatus.connected;
        notifyListeners();
      }
    };

    _peerConnection!.onIceCandidate = (RTCIceCandidate candidate) {
      if (candidate.candidate == null) return;
      signaling.sendIceCandidate({
        'candidate': candidate.candidate,
        'sdpMid': candidate.sdpMid,
        'sdpMLineIndex': candidate.sdpMLineIndex,
      });
    };

    _peerConnection!.onConnectionState = (RTCPeerConnectionState state) {
      if (state == RTCPeerConnectionState.RTCPeerConnectionStateDisconnected ||
          state == RTCPeerConnectionState.RTCPeerConnectionStateFailed ||
          state == RTCPeerConnectionState.RTCPeerConnectionStateClosed) {
        status = CallEngineStatus.ended;
        notifyListeners();
      }
    };
  }

  Future<void> _handleSignalingMessage(Map<String, dynamic> message) async {
    final type = message['type'] as String?;

    switch (type) {
      case 'peer-joined':
        // El participante que YA estaba en la sala inicia la oferta hacia
        // el que acaba de unirse (evita que ambos lados ofrezcan a la vez).
        _remotePeerId = message['user_id'] as String?;
        status = CallEngineStatus.negotiating;
        notifyListeners();
        await _createAndSendOffer();
        break;

      case 'offer':
        _remotePeerId = message['from_user_id'] as String?;
        await _peerConnection!.setRemoteDescription(RTCSessionDescription(message['sdp'] as String, 'offer'));
        final answer = await _peerConnection!.createAnswer();
        await _peerConnection!.setLocalDescription(answer);
        signaling.sendAnswer(answer.sdp!);
        break;

      case 'answer':
        await _peerConnection!.setRemoteDescription(RTCSessionDescription(message['sdp'] as String, 'answer'));
        break;

      case 'ice-candidate':
        final candidateData = message['candidate'] as Map<String, dynamic>;
        await _peerConnection!.addCandidate(RTCIceCandidate(
          candidateData['candidate'] as String?,
          candidateData['sdpMid'] as String?,
          candidateData['sdpMLineIndex'] as int?,
        ));
        break;

      case 'peer-left':
        status = CallEngineStatus.ended;
        notifyListeners();
        break;

      case 'caption':
        remoteCaption = message['text'] as String?;
        notifyListeners();
        if (remoteCaption != null && remoteCaption!.trim().isNotEmpty) {
          unawaited(_translateAndPlay(remoteCaption!));
        }
        break;
    }
  }

  /// Traduce el subtítulo recibido a LSC y reproduce la secuencia en el
  /// avatar (Fase 6), un item a la vez con corte seco. Si la traducción
  /// falla (backend caído, red, etc.), se deja de mostrar el avatar y el
  /// usuario sigue viendo el subtítulo de texto normal — nunca se bloquea
  /// la llamada por esto.
  Future<void> _translateAndPlay(String text) async {
    _sequenceTimer?.cancel();
    try {
      final result = await translationRepository.translate(text);
      currentTranslation = result;
      currentSequenceIndex = 0;
      notifyListeners();

      if (result.sequence.length > 1) {
        _sequenceTimer = Timer.periodic(_avatarSequenceStepDuration, (timer) {
          if (currentSequenceIndex >= result.sequence.length - 1) {
            timer.cancel();
            return;
          }
          currentSequenceIndex++;
          notifyListeners();
        });
      }
    } catch (_) {
      currentTranslation = null;
      currentSequenceIndex = 0;
      notifyListeners();
    }
  }

  /// Envía un texto de apoyo al otro participante y lo guarda localmente
  /// para mostrarlo también en la propia pantalla.
  void sendCaption(String text) {
    localCaption = text;
    signaling.sendCaption(text);
    notifyListeners();
  }

  Future<void> _createAndSendOffer() async {
    final offer = await _peerConnection!.createOffer();
    await _peerConnection!.setLocalDescription(offer);
    signaling.sendOffer(offer.sdp!);
  }

  void toggleMic() {
    isMicEnabled = !isMicEnabled;
    localStream?.getAudioTracks().forEach((track) => track.enabled = isMicEnabled);
    notifyListeners();
  }

  void toggleCamera() {
    isCameraEnabled = !isCameraEnabled;
    localStream?.getVideoTracks().forEach((track) => track.enabled = isCameraEnabled);
    notifyListeners();
  }

  Future<void> switchCamera() async {
    final videoTrack = localStream?.getVideoTracks().firstOrNull;
    if (videoTrack != null) {
      await Helper.switchCamera(videoTrack);
    }
  }

  Future<void> hangUp() async {
    signaling.sendLeave();
    await _cleanup();
    status = CallEngineStatus.ended;
    notifyListeners();
  }

  Future<void> _cleanup() async {
    _sequenceTimer?.cancel();
    await _signalingSubscription?.cancel();
    await signaling.dispose();
    for (final track in localStream?.getTracks() ?? <MediaStreamTrack>[]) {
      await track.stop();
    }
    await localStream?.dispose();
    await _peerConnection?.close();
    await _peerConnection?.dispose();
  }

  @override
  void dispose() {
    _cleanup();
    super.dispose();
  }
}

extension _FirstOrNull<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
