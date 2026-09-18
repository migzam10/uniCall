import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:go_router/go_router.dart';

import '../../config/app_theme.dart';
import '../../core/api_exception.dart';
import '../../core/providers.dart';
import '../../models/user_preferences.dart';
import '../../services/audio_player_service.dart';
import '../../services/audio_recorder_service.dart';
import '../../services/call_engine.dart';
import '../../services/signaling_client.dart';
import '../profile/profile_controller.dart';

class CallScreen extends ConsumerStatefulWidget {
  const CallScreen({super.key, required this.callId, required this.callCode});

  final String callId;
  final String callCode;

  @override
  ConsumerState<CallScreen> createState() => _CallScreenState();
}

class _CallScreenState extends ConsumerState<CallScreen> {
  final _localRenderer = RTCVideoRenderer();
  final _remoteRenderer = RTCVideoRenderer();
  final _audioRecorder = AudioRecorderService();
  final _audioPlayer = AudioPlayerService();
  CallEngine? _engine;
  bool _initializing = true;
  String? _initError;
  bool _isRecordingSpeech = false;
  bool _isProcessingSpeech = false;

  @override
  void initState() {
    super.initState();
    _setup();
  }

  Future<void> _setup() async {
    await _localRenderer.initialize();
    await _remoteRenderer.initialize();

    try {
      final token = await ref.read(tokenStorageProvider).getAccessToken();
      if (token == null) throw Exception('Sesión no válida');

      final iceServers = await ref.read(callRepositoryProvider).getIceServers();
      final signaling = SignalingClient(callId: widget.callId, accessToken: token);
      final engine = CallEngine(signaling: signaling, iceServers: iceServers);

      engine.addListener(_onEngineUpdate);
      await engine.initialize();

      setState(() {
        _engine = engine;
        _localRenderer.srcObject = engine.localStream;
        _initializing = false;
      });
    } catch (e) {
      setState(() {
        _initError = 'No se pudo iniciar la llamada. Revisa los permisos de cámara y micrófono.';
        _initializing = false;
      });
    }
  }

  void _onEngineUpdate() {
    if (!mounted || _engine == null) return;
    setState(() {
      _remoteRenderer.srcObject = _engine!.remoteStream;
    });
    if (_engine!.status == CallEngineStatus.ended) {
      _endAndClose();
    }
  }

  Future<void> _endAndClose() async {
    if (!mounted) return;
    if (context.canPop()) {
      context.pop();
    } else {
      context.go('/home');
    }
  }

  /// Español hablado -> texto (sección 8): graba mientras se mantiene
  /// presionado, transcribe al soltar y comparte el texto con el otro
  /// participante como subtítulo.
  Future<void> _startRecordingSpeech() async {
    final hasPermission = await _audioRecorder.hasPermission();
    if (!hasPermission) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Se necesita permiso de micrófono.')));
      }
      return;
    }
    await _audioRecorder.start();
    setState(() => _isRecordingSpeech = true);
  }

  Future<void> _stopRecordingAndTranscribe() async {
    setState(() {
      _isRecordingSpeech = false;
      _isProcessingSpeech = true;
    });

    try {
      final path = await _audioRecorder.stop();
      if (path == null) return;
      final text = await ref.read(speechRepositoryProvider).transcribe(path);
      _engine?.sendCaption(text);
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    } finally {
      if (mounted) setState(() => _isProcessingSpeech = false);
    }
  }

  /// Texto -> voz (sección 9, tramo final): sintetiza y reproduce el texto
  /// recibido como subtítulo remoto. En fases posteriores este texto vendrá
  /// automáticamente del reconocimiento de LSC (Fase 5); por ahora también
  /// se puede reproducir manualmente el último subtítulo recibido.
  Future<void> _speakRemoteCaption() async {
    final text = _engine?.remoteCaption;
    if (text == null || text.trim().isEmpty) return;

    final voicePreference = ref.read(meProvider).valueOrNull?.preferences.voicePreference ?? VoicePreference.femenina;

    try {
      final audioBytes = await ref.read(speechRepositoryProvider).synthesize(text, voicePreference);
      await _audioPlayer.playBytes(audioBytes);
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    }
  }

  @override
  void dispose() {
    _engine?.removeListener(_onEngineUpdate);
    _engine?.hangUp();
    _localRenderer.dispose();
    _remoteRenderer.dispose();
    _audioRecorder.dispose();
    _audioPlayer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_initializing) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(child: CircularProgressIndicator(color: Colors.white)),
      );
    }

    if (_initError != null) {
      return Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, color: Colors.white, size: 48),
                const SizedBox(height: 16),
                Text(_initError!, style: const TextStyle(color: Colors.white), textAlign: TextAlign.center),
                const SizedBox(height: 24),
                ElevatedButton(onPressed: () => context.pop(), child: const Text('Volver')),
              ],
            ),
          ),
        ),
      );
    }

    final engine = _engine!;

    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            // Video remoto a pantalla completa
            Positioned.fill(
              child: engine.status == CallEngineStatus.connected
                  ? RTCVideoView(_remoteRenderer, objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover)
                  : _WaitingIndicator(status: engine.status, code: widget.callCode),
            ),

            // Video local (esquina)
            Positioned(
              top: 16,
              right: 16,
              child: Container(
                width: 120,
                height: 160,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.white24),
                ),
                clipBehavior: Clip.antiAlias,
                child: RTCVideoView(_localRenderer, mirror: true),
              ),
            ),

            // Indicadores visuales de estado (sección 22: no depender solo del color)
            Positioned(
              top: 16,
              left: 16,
              child: Row(
                children: [
                  if (!engine.isMicEnabled) const _StatusChip(icon: Icons.mic_off, label: 'Mic apagado'),
                  if (!engine.isCameraEnabled) const _StatusChip(icon: Icons.videocam_off, label: 'Cámara apagada'),
                ],
              ),
            ),

            // Subtítulos (sección 17: texto de apoyo en la videollamada)
            Positioned(
              left: 16,
              right: 16,
              bottom: 110,
              child: _CaptionsOverlay(engine: engine, onSpeak: _speakRemoteCaption, isSpeaking: _isProcessingSpeech),
            ),

            // Controles
            Positioned(
              left: 0,
              right: 0,
              bottom: 24,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _CallButton(
                    icon: engine.isMicEnabled ? Icons.mic : Icons.mic_off,
                    onTap: engine.toggleMic,
                    backgroundColor: engine.isMicEnabled ? Colors.white24 : StatusColors.micOff,
                  ),
                  const SizedBox(width: 16),
                  _CallButton(
                    icon: engine.isCameraEnabled ? Icons.videocam : Icons.videocam_off,
                    onTap: engine.toggleCamera,
                    backgroundColor: engine.isCameraEnabled ? Colors.white24 : StatusColors.cameraOff,
                  ),
                  const SizedBox(width: 16),
                  _CallButton(icon: Icons.cameraswitch, onTap: engine.switchCamera, backgroundColor: Colors.white24),
                  const SizedBox(width: 16),
                  GestureDetector(
                    onLongPressStart: (_) => _startRecordingSpeech(),
                    onLongPressEnd: (_) => _stopRecordingAndTranscribe(),
                    child: Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        color: _isRecordingSpeech ? StatusColors.translationActive : Colors.white24,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        _isRecordingSpeech ? Icons.graphic_eq : Icons.subtitles_outlined,
                        color: Colors.white,
                        size: 26,
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  _CallButton(
                    icon: Icons.call_end,
                    onTap: () async {
                      await engine.hangUp();
                    },
                    backgroundColor: AppTheme.danger,
                    size: 64,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _WaitingIndicator extends StatelessWidget {
  const _WaitingIndicator({required this.status, required this.code});
  final CallEngineStatus status;
  final String code;

  @override
  Widget build(BuildContext context) {
    final message = switch (status) {
      CallEngineStatus.waitingForPeer => 'Esperando a que la otra persona se una...\nCódigo: $code',
      CallEngineStatus.negotiating => 'Conectando...',
      CallEngineStatus.connecting => 'Iniciando...',
      _ => 'Conectando...',
    };

    return Container(
      color: const Color(0xFF10151A),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(color: Colors.white),
            const SizedBox(height: 16),
            Text(message, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white70, fontSize: 16)),
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.icon, required this.label});
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(20)),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: Colors.white, size: 16),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(color: Colors.white, fontSize: 12)),
        ],
      ),
    );
  }
}

class _CallButton extends StatelessWidget {
  const _CallButton({required this.icon, required this.onTap, required this.backgroundColor, this.size = 56});
  final IconData icon;
  final VoidCallback onTap;
  final Color backgroundColor;
  final double size;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: icon.toString(),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(color: backgroundColor, shape: BoxShape.circle),
          child: Icon(icon, color: Colors.white, size: size * 0.45),
        ),
      ),
    );
  }
}

class _CaptionsOverlay extends ConsumerWidget {
  const _CaptionsOverlay({required this.engine, required this.onSpeak, required this.isSpeaking});

  final CallEngine engine;
  final VoidCallback onSpeak;
  final bool isSpeaking;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final prefs = ref.watch(meProvider).valueOrNull?.preferences;
    final showSubtitles = prefs?.showSubtitles ?? true;
    final voiceOutputEnabled = prefs?.voiceOutputEnabled ?? true;

    if (!showSubtitles) return const SizedBox.shrink();
    if (engine.localCaption == null && engine.remoteCaption == null) return const SizedBox.shrink();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (engine.remoteCaption != null)
          _CaptionBubble(
            label: 'Texto recibido',
            text: engine.remoteCaption!,
            trailing: voiceOutputEnabled
                ? IconButton(
                    tooltip: 'Escuchar en voz alta',
                    icon: Icon(isSpeaking ? Icons.hourglass_top : Icons.volume_up, color: Colors.white),
                    onPressed: isSpeaking ? null : onSpeak,
                  )
                : null,
          ),
        if (engine.localCaption != null) ...[
          const SizedBox(height: 8),
          _CaptionBubble(label: 'Tu texto', text: engine.localCaption!),
        ],
      ],
    );
  }
}

class _CaptionBubble extends StatelessWidget {
  const _CaptionBubble({required this.label, required this.text, this.trailing});
  final String label;
  final String text;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(color: Colors.black87, borderRadius: BorderRadius.circular(12)),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(label, style: const TextStyle(color: Colors.white54, fontSize: 11)),
                Text(text, style: const TextStyle(color: Colors.white, fontSize: 16)),
              ],
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}
