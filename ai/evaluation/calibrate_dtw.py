import os
import sys

# Aseguramos que Python encuentre la carpeta 'backend' y sus módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.ai.lsc.landmark_extractor import VideoLandmarkExtractor
from app.ai.lsc.dtw import dtw_distance

def main():
    videos = {
        "Hola_1": "../../ai/entrenamiento/Hola 1.mp4",
        "Hola_2": "../../ai/entrenamiento/Hola 2.mp4",
        "Gracias_1": "../../ai/entrenamiento/Gracias 1.mp4",
        "Gracias_2": "../../ai/entrenamiento/Gracias 2.mp4",
    }
    
    # Resolviendo paths absolutos
    base_dir = os.path.dirname(__file__)
    
    extractor = VideoLandmarkExtractor()
    sequences = {}
    
    print("Extrayendo landmarks (esto puede tomar unos segundos por video)...")
    for name, relative_path in videos.items():
        path = os.path.join(base_dir, relative_path)
        if not os.path.exists(path):
            print(f"Error: No se encontró el video {path}")
            continue
            
        print(f"Procesando {name}...")
        seq, hand_frames = extractor.extract_from_file(path)
        sequences[name] = seq
        print(f"  -> {len(seq)} frames procesados. Frames con manos detectadas: {hand_frames}")

    print("\n--- RESULTADOS MATRIZ DE DISTANCIA DTW ---")
    
    # Intraclase (Misma seña)
    dist_hola = dtw_distance(sequences["Hola_1"], sequences["Hola_2"])
    dist_gracias = dtw_distance(sequences["Gracias_1"], sequences["Gracias_2"])
    
    # Interclase (Distinta seña)
    dist_h1_g1 = dtw_distance(sequences["Hola_1"], sequences["Gracias_1"])
    dist_h1_g2 = dtw_distance(sequences["Hola_1"], sequences["Gracias_2"])
    dist_h2_g1 = dtw_distance(sequences["Hola_2"], sequences["Gracias_1"])
    dist_h2_g2 = dtw_distance(sequences["Hola_2"], sequences["Gracias_2"])
    
    print(f"\n[DISTANCIAS INTRACLASE] (Deberían ser BAJAS - misma seña)")
    print(f"Hola_1    vs Hola_2    : {dist_hola:.2f}")
    print(f"Gracias_1 vs Gracias_2 : {dist_gracias:.2f}")
    
    print(f"\n[DISTANCIAS INTERCLASE] (Deberían ser ALTAS - señas distintas)")
    print(f"Hola_1    vs Gracias_1 : {dist_h1_g1:.2f}")
    print(f"Hola_1    vs Gracias_2 : {dist_h1_g2:.2f}")
    print(f"Hola_2    vs Gracias_1 : {dist_h2_g1:.2f}")
    print(f"Hola_2    vs Gracias_2 : {dist_h2_g2:.2f}")
    
    print("\n--- RECOMENDACIÓN DE CALIBRACIÓN ---")
    max_intra = max(dist_hola, dist_gracias)
    min_inter = min(dist_h1_g1, dist_h1_g2, dist_h2_g1, dist_h2_g2)
    
    if max_intra < min_inter:
        umbral_recomendado = (max_intra + min_inter) / 2
        print(f"✅ Los modelos son distinguibles.")
        print(f"Umbral actual sugerido teóricamente en .env: 15.0")
        print(f"⭐ NUEVO umbral recomendado (LSC_MAX_DTW_DISTANCE): {umbral_recomendado:.2f}")
    else:
        print(f"⚠️ PELIGRO: Hay superposición matemática. Una distancia de misma seña ({max_intra:.2f})")
        print(f"es mayor que la distancia entre señas distintas ({min_inter:.2f}).")
        print("El algoritmo DTW por sí solo podría confundirlas si el ruido en el video es alto.")

if __name__ == "__main__":
    main()
