import os
import glob
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout # type: ignore
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint # type: ignore

PROCESSED_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "dataset/processed"))
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))

MAX_FRAMES = 60 # Longitud de secuencia fija
VECTOR_SIZE = 258 # 33*4 + 21*3*2

def pad_sequence(seq, max_len=MAX_FRAMES):
    """Rellena o recorta la secuencia de frames a un tamaño fijo."""
    if len(seq) > max_len:
        return seq[:max_len] # Recorta
    else:
        # Rellena con ceros al final
        padding = np.zeros((max_len - len(seq), VECTOR_SIZE))
        return np.vstack((seq, padding))

def main():
    print("--- ENTRENAMIENTO DE RED NEURONAL LSC (LSTM) ---")
    
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)

    # 1. Cargar el Dataset
    classes = sorted(os.listdir(PROCESSED_DATA_DIR))
    # Filtrar archivos ocultos como .DS_Store
    classes = [c for c in classes if os.path.isdir(os.path.join(PROCESSED_DATA_DIR, c))]
    
    if not classes:
        print("No se encontraron clases en el dataset.")
        return
        
    print(f"Clases detectadas ({len(classes)}): {classes}")

    label_map = {label: num for num, label in enumerate(classes)}
    
    X, y = [], []
    
    for sign_class in classes:
        class_dir = os.path.join(PROCESSED_DATA_DIR, sign_class)
        for npy_file in glob.glob(os.path.join(class_dir, "*.npy")):
            res = np.load(npy_file)
            res = pad_sequence(res)
            X.append(res)
            y.append(label_map[sign_class])

    X = np.array(X)
    y = to_categorical(y, num_classes=len(classes))
    
    print(f"Dataset final X shape: {X.shape}")
    print(f"Dataset final Y shape: {y.shape}")
    
    if len(X) < 2:
        print("Error: Se necesitan al menos 2 videos en total para entrenar.")
        return

    # 2. Dividir en Entrenamiento y Prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3. Construir Arquitectura LSTM
    model = Sequential([
        LSTM(64, return_sequences=True, activation='relu', input_shape=(MAX_FRAMES, VECTOR_SIZE)),
        Dropout(0.2),
        LSTM(128, return_sequences=True, activation='relu'),
        Dropout(0.2),
        LSTM(64, return_sequences=False, activation='relu'),
        Dense(64, activation='relu'),
        Dense(len(classes), activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    # 4. Entrenar el Modelo
    print("\nIniciando entrenamiento...")
    callbacks = [
        EarlyStopping(patience=20, restore_best_weights=True),
        ModelCheckpoint(os.path.join(MODELS_DIR, 'lsc_lstm_model.h5'), save_best_only=True)
    ]
    
    history = model.fit(
        X_train, y_train, 
        epochs=100, 
        batch_size=8, 
        validation_data=(X_test, y_test),
        callbacks=callbacks
    )

    # 5. Guardar el diccionario de clases
    classes_path = os.path.join(MODELS_DIR, 'classes.txt')
    with open(classes_path, 'w') as f:
        for c in classes:
            f.write(f"{c}\n")

    print(f"\n✅ Entrenamiento completado. Modelo guardado en {MODELS_DIR}/lsc_lstm_model.h5")
    print(f"Precisión final de validación: {history.history.get('val_accuracy', [-1])[-1]:.2f}")

if __name__ == "__main__":
    main()
