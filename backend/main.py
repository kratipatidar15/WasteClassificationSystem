import io
import os
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image
from ultralytics import YOLO

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

# Load Classification Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'waste_classifier.h5')
CLASSES_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'classes.txt')

model = None
class_names = []

if os.path.exists(MODEL_PATH):
    print("Loading Classification Model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    if os.path.exists(CLASSES_PATH):
        with open(CLASSES_PATH, 'r') as f:
            class_names = [line.strip() for line in f.readlines()]
    else:
        # Fallback if classes.txt is not found
        class_names = ["battery", "biological", "brown-glass", "cardboard", "clothes", 
                       "green-glass", "metal", "paper", "plastic", "shoes", "trash", "white-glass"]
else:
    print(f"Warning: Model not found at {MODEL_PATH}")

# Load YOLO Model
try:
    print("Loading YOLOv8 Model...")
    yolo_model = YOLO("yolov8n.pt")  # Downloads if not present
except Exception as e:
    print(f"Failed to load YOLO model: {e}")
    yolo_model = None



@app.post("/predict")
async def predict_waste(file: UploadFile = File(...)):
    if model is None:
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
        
        # Predict
        predictions = model.predict(img_array)[0]
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
