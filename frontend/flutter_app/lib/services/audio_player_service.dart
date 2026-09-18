import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';

/// Reproducción de audio sintetizado (TTS) a partir de bytes en memoria,
/// sin necesidad de escribir a disco.
class AudioPlayerService {
  final AudioPlayer _player = AudioPlayer();

  Future<void> playBytes(Uint8List audioBytes) async {
    await _player.play(BytesSource(audioBytes));
  }

  Future<void> stop() => _player.stop();

  Future<void> dispose() => _player.dispose();
}
