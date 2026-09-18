import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';

import '../models/call_info.dart';
import 'signaling_client.dart';

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
    required List<IceServerConfig> iceServers,
  }) : _iceServers = iceServers;

  final SignalingClient signaling;
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
        break;
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
