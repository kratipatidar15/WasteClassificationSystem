import io
import os
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image

# Import recycling rules
try:
    from backend.rules import get_recycling_info
except ImportError:
    from rules import get_recycling_info

app = FastAPI(title="Waste Classification API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define model paths
TFLITE_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'waste_classifier.tflite')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'waste_classifier.h5')
CLASSES_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'classes.txt')

# Global variables for lazy loading
tflite_interpreter = None
tflite_input_details = None
tflite_output_details = None
tf_model = None
yolo_model = None
class_names = []
models_loaded = False

def load_models():
    global tflite_interpreter, tflite_input_details, tflite_output_details, tf_model, yolo_model, class_names, models_loaded
    if models_loaded:
        return
        
    print("Lazy loading models...")
    
    # Load Class Names
    if os.path.exists(CLASSES_PATH):
        with open(CLASSES_PATH, 'r') as f:
            class_names = [line.strip() for line in f.readlines()]
    else:
        class_names = ["battery", "biological", "brown-glass", "cardboard", "clothes", 
                       "green-glass", "metal", "paper", "plastic", "shoes", "trash", "white-glass"]
                       
    # 1. Try loading TFLite Model
    if os.path.exists(TFLITE_PATH):
        try:
            print("Attempting to load TFLite Model using tflite_runtime...")
            try:
                import tflite_runtime.interpreter as tflite
            except ImportError:
                print("tflite_runtime not found. Trying to import from tensorflow...")
                from tensorflow import lite as tflite
                
            tflite_interpreter = tflite.Interpreter(model_path=TFLITE_PATH)
            tflite_interpreter.allocate_tensors()
            tflite_input_details = tflite_interpreter.get_input_details()
            tflite_output_details = tflite_interpreter.get_output_details()
            print("TFLite Model loaded successfully!")
        except Exception as e:
            print(f"Failed to load TFLite model: {e}")
            tflite_interpreter = None
            
    # 2. Fallback to original H5 Model (only if TFLite failed or doesn't exist)
    if tflite_interpreter is None:
        if os.path.exists(MODEL_PATH):
            try:
                print("Fallback: Loading original Keras Classification Model (.h5)...")
                import tensorflow as tf
                tf_model = tf.keras.models.load_model(MODEL_PATH)
                print("Keras Model loaded successfully!")
            except Exception as e:
                print(f"Failed to load fallback Keras model: {e}")
                tf_model = None
        else:
            print(f"Warning: Model not found at {MODEL_PATH}")

    # 3. Load YOLO Model
    try:
        print("Loading YOLOv8 Model...")
        from ultralytics import YOLO
        yolo_model = YOLO("yolov8n.pt")
        print("YOLOv8 Model loaded successfully!")
    except Exception as e:
        print(f"Failed to load YOLO model: {e}")
        yolo_model = None
        
    models_loaded = True

@app.post("/predict")
async def predict_waste(file: UploadFile = File(...)):
    load_models()
    if tflite_interpreter is None and tf_model is None:
        return {"error": "Classification model is not loaded"}
        
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # --- Smart Logic ---
        valid_detections = []
        if yolo_model is not None:
            # Predict using YOLOv8 with confidence threshold and NMS
            results = yolo_model(image, conf=0.5, iou=0.45)
            for r in results:
                for box in r.boxes:
                    conf = float(box.conf)
                    if conf >= 0.5:
                        b = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                        c = int(box.cls)
                        name = yolo_model.names[c]
                        
                        rule = get_recycling_info(name)
                        
                        valid_detections.append({
                            "box": b,
                            "class": name,
                            "confidence": conf,
                            "category": rule["category"],
                            "suggestion": rule["suggestion"]
                        })
        
        # Check if multiple valid objects are detected
        if len(valid_detections) > 1:
            return {
                "type": "multiple",
                "detections": valid_detections
            }
        
        # --- Fallback to Single Object Classification ---
        # Preprocess image
        image_resized = image.resize((224, 224))
        img_array = np.array(image_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # Predict using TFLite or Keras fallback
        if tflite_interpreter is not None:
            img_array = img_array.astype(np.float32)
            tflite_interpreter.set_tensor(tflite_input_details[0]['index'], img_array)
            tflite_interpreter.invoke()
            predictions = tflite_interpreter.get_tensor(tflite_output_details[0]['index'])[0]
        else:
            predictions = tf_model.predict(img_array)[0]
            
        max_idx = np.argmax(predictions)
        predicted_class = class_names[max_idx]
        confidence = float(predictions[max_idx])
        
        # Get Rules
        rules = get_recycling_info(predicted_class)
        
        return {
            "type": "single",
            "predicted_class": predicted_class,
            "confidence": confidence,
            "category": rules["category"],
            "suggestion": rules["suggestion"]
        }
    except Exception as e:
        return {"error": str(e)}

# Serve frontend statically
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
