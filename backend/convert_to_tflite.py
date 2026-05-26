import tensorflow as tf
import os

def main():
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'waste_classifier.h5')
    tflite_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'waste_classifier.tflite')

    if not os.path.exists(model_path):
        print(f"Error: Keras model not found at {model_path}")
        return

    print(f"Loading Keras model from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    print("Converting to TFLite with optimizations...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()

    print(f"Saving TFLite model to {tflite_path}...")
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)

    print("Conversion complete!")

if __name__ == "__main__":
    main()
