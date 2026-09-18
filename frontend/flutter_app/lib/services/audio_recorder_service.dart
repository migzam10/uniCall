import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';

/// Grabación de audio para enviar a transcripción (STT).
///
/// Independiente del stream de WebRTC de la llamada: esta es una grabación
/// corta y puntual (el usuario mantiene presionado un botón, habla, y al
/// soltar se envía a transcribir), no un stream continuo.
class AudioRecorderService {
  final AudioRecorder _recorder = AudioRecorder();
  String? _currentPath;

  Future<bool> hasPermission() => _recorder.hasPermission();

  Future<void> start() async {
    final dir = await getTemporaryDirectory();
    final path = '${dir.path}/lsc_recording_${DateTime.now().millisecondsSinceEpoch}.wav';
    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 16000, numChannels: 1),
      path: path,
    );
    _currentPath = path;
  }

  /// Detiene la grabación y devuelve la ruta del archivo WAV, o `null` si
  /// no había una grabación en curso.
  Future<String?> stop() async {
    final path = await _recorder.stop();
    return path ?? _currentPath;
  }

  Future<bool> isRecording() => _recorder.isRecording();

  Future<void> dispose() async {
    await _recorder.dispose();
  }
}
