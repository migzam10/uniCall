import os
import sys
import glob
import numpy as np

# Asegurar que podemos importar desde el backend local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.ai.lsc.landmark_extractor import VideoLandmarkExtractor

# Rutas
RAW_VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../entrenamiento"))
PROCESSED_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset/processed"))

def main():
    print(f"--- CONSTRUCTOR DE DATASET LSC (ML) ---")
    print(f"Buscando videos en: {RAW_VIDEOS_DIR}\n")

    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)

    # Buscar todos los videos
    video_files = glob.glob(os.path.join(RAW_VIDEOS_DIR, "*.mp4")) + glob.glob(os.path.join(RAW_VIDEOS_DIR, "*.webm"))
    
    if not video_files:
        print("No se encontraron videos en la carpeta ai/entrenamiento/")
        return

    # Usamos nuestro extractor optimizado (Sin rostro, centrado en la nariz)
    # Ajustamos a 10 fps y 60 frames max para LSTM
    extractor = VideoLandmarkExtractor(target_fps=10.0, max_frames=60)
    
    processed_count = 0

    for video_path in video_files:
        filename = os.path.basename(video_path)
        
        # Inferir la clase (seña) a partir del nombre del archivo ("Hola 1.mp4" -> "Hola")
        # Asumimos que el nombre de la seña es la primera palabra antes de un espacio o número
        sign_class = filename.split(" ")[0].split(".")[0].upper()
        
        print(f"Procesando: {filename} -> Clase detectada: [{sign_class}]")
        
        sequence, hand_frames = extractor.extract_from_file(video_path)
        
        if len(sequence) == 0:
            print(f"  ⚠️ Error: No se pudo extraer datos de {filename}")
            continue
            
        if hand_frames == 0:
            print(f"  ⚠️ Advertencia: No se detectaron manos en {filename}. (¿Es solo ruido?)")
            
        # Convertir a numpy array y guardar
        seq_array = np.array(sequence, dtype=np.float32)
        
        # Crear carpeta para la clase si no existe
        class_dir = os.path.join(PROCESSED_DATA_DIR, sign_class)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
            
        # Guardar como .npy
        save_name = filename.replace(".mp4", "").replace(".webm", "") + ".npy"
        save_path = os.path.join(class_dir, save_name)
        
        np.save(save_path, seq_array)
        print(f"  ✅ Guardado en: {sign_class}/{save_name} (Shape: {seq_array.shape})")
        processed_count += 1

    print(f"\nProceso finalizado. {processed_count} archivos exportados exitosamente a matrices matemáticas (.npy).")
    print("El siguiente paso será crear un script de TensorFlow para entrenar el LSTM con estos datos.")

if __name__ == "__main__":
    main()
