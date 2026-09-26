import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_exception.dart';
import '../../core/providers.dart';
import '../../models/lsc_data.dart';
import 'lsc_admin_controller.dart';

class LscSignDetailScreen extends ConsumerStatefulWidget {
  const LscSignDetailScreen({super.key, required this.signId});
  final String signId;

  @override
  ConsumerState<LscSignDetailScreen> createState() => _LscSignDetailScreenState();
}

class _LscSignDetailScreenState extends ConsumerState<LscSignDetailScreen> {
  bool _uploading = false;
  bool _uploadingAnimation = false;

  Future<void> _uploadVideo() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.video,
      withData: false,
    );
    if (result == null || result.files.single.path == null) return;

    final file = result.files.single;
    setState(() => _uploading = true);
    try {
      await ref.read(lscAdminRepositoryProvider).uploadVideo(widget.signId, file.path!, file.name);
      ref.invalidate(lscSignDetailProvider(widget.signId));
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  Future<void> _uploadAnimation() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['glb', 'gltf'],
      withData: false,
    );
    if (result == null || result.files.single.path == null) return;

    final file = result.files.single;
    setState(() => _uploadingAnimation = true);
    try {
      await ref.read(lscAdminRepositoryProvider).uploadAnimation(widget.signId, file.path!, file.name);
      ref.invalidate(lscSignDetailProvider(widget.signId));
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message), backgroundColor: Theme.of(context).colorScheme.error));
      }
    } finally {
      if (mounted) setState(() => _uploadingAnimation = false);
    }
  }

  Future<void> _changeStatus(LscSignStatus status) async {
    await ref.read(lscAdminRepositoryProvider).updateSignStatus(widget.signId, status: status);
    ref.invalidate(lscSignDetailProvider(widget.signId));
  }

  Future<void> _bumpVersion() async {
    await ref.read(lscAdminRepositoryProvider).updateSignStatus(widget.signId, bumpVersion: true);
    ref.invalidate(lscSignDetailProvider(widget.signId));
  }

  @override
  Widget build(BuildContext context) {
    final signAsync = ref.watch(lscSignDetailProvider(widget.signId));

    return Scaffold(
      appBar: AppBar(title: const Text('Detalle de la seña')),
      body: signAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Error: $err')),
        data: (sign) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Text(sign.word, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(sign.meaning, style: Theme.of(context).textTheme.bodyLarge),
            if (sign.tags != null) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 6,
                children: sign.tags!
                    .split(',')
                    .map((t) => Chip(label: Text(t.trim()), visualDensity: VisualDensity.compact))
                    .toList(),
              ),
            ],
            const SizedBox(height: 20),
            Text('Estado y versión', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                for (final status in LscSignStatus.values)
                  ChoiceChip(
                    label: Text(status.label),
                    selected: sign.status == status,
                    onSelected: (_) => _changeStatus(status),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Text('Versión actual: ${sign.version}', style: Theme.of(context).textTheme.bodyMedium),
                const Spacer(),
                OutlinedButton.icon(
                  onPressed: _bumpVersion,
                  icon: const Icon(Icons.upgrade),
                  label: const Text('Nueva versión'),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Text('Videos de referencia', style: Theme.of(context).textTheme.titleMedium),
                const Spacer(),
                FilledButton.icon(
                  onPressed: _uploading ? null : _uploadVideo,
                  icon: _uploading
                      ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.upload_file),
                  label: Text(_uploading ? 'Subiendo...' : 'Cargar video'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (sign.videos.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text('Todavía no hay videos de referencia para esta seña.'),
              )
            else
              ...sign.videos.map((video) => _VideoTile(video: video, signId: widget.signId)),
            const SizedBox(height: 24),
            Row(
              children: [
                Text('Animaciones 3D del avatar', style: Theme.of(context).textTheme.titleMedium),
                const Spacer(),
                FilledButton.icon(
                  onPressed: _uploadingAnimation ? null : _uploadAnimation,
                  icon: _uploadingAnimation
                      ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.view_in_ar_outlined),
                  label: Text(_uploadingAnimation ? 'Subiendo...' : 'Cargar animación'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (sign.animations.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text('Todavía no hay animaciones del avatar para esta seña.'),
              )
            else
              ...sign.animations.map((animation) => _AnimationTile(animation: animation, signId: widget.signId)),
          ],
        ),
      ),
    );
  }
}

class _VideoTile extends ConsumerStatefulWidget {
  const _VideoTile({required this.video, required this.signId});
  final LscVideo video;
  final String signId;

  @override
  ConsumerState<_VideoTile> createState() => _VideoTileState();
}

class _VideoTileState extends ConsumerState<_VideoTile> {
  bool _processing = false;
  String? _processError;

  Future<void> _process() async {
    setState(() {
      _processing = true;
      _processError = null;
    });
    try {
      await ref.read(lscAdminRepositoryProvider).processVideo(widget.video.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Video procesado: listo para el reconocimiento de LSC.')),
        );
      }
    } on ApiException catch (e) {
      setState(() => _processError = e.message);
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE1E5EA)),
      ),
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.videocam_outlined, color: Color(0xFF1755C7)),
            title: Text(widget.video.originalFilename),
            subtitle: Text('${(widget.video.sizeBytes / 1024 / 1024).toStringAsFixed(1)} MB'),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  tooltip: 'Procesar para reconocimiento',
                  icon: _processing
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.auto_awesome, color: Color(0xFF00897B)),
                  onPressed: _processing ? null : _process,
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: Color(0xFFC62828)),
                  onPressed: () async {
                    await ref.read(lscAdminRepositoryProvider).deleteVideo(widget.video.id);
                    ref.invalidate(lscSignDetailProvider(widget.signId));
                  },
                ),
              ],
            ),
          ),
          if (_processError != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              child: Text(_processError!, style: const TextStyle(color: Color(0xFFC62828), fontSize: 13)),
            ),
        ],
      ),
    );
  }
}

class _AnimationTile extends ConsumerWidget {
  const _AnimationTile({required this.animation, required this.signId});
  final LscAnimation animation;
  final String signId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE1E5EA)),
      ),
      child: ListTile(
        leading: const Icon(Icons.view_in_ar_outlined, color: Color(0xFF1755C7)),
        title: Text(animation.originalFilename),
        subtitle: Text('${(animation.sizeBytes / 1024).toStringAsFixed(0)} KB'),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, color: Color(0xFFC62828)),
          onPressed: () async {
            await ref.read(lscAdminRepositoryProvider).deleteAnimation(animation.id);
            ref.invalidate(lscSignDetailProvider(signId));
          },
        ),
      ),
    );
  }
}
