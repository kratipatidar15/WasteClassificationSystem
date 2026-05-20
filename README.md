# Waste Classification and Recycling Suggestion Web App

This is a complete Smart Waste Management system that uses Deep Learning to classify waste into 12 categories and provides actionable recycling suggestions. It also includes an advanced multi-object detection mode using YOLOv8.

## Features
- **Single Image Classification:** Upload an image to classify the waste type, view the confidence score, and get specific recycling instructions.
- **Multiple Object Detection:** Upload an image to detect multiple waste objects using a pre-trained YOLOv8 model, complete with bounding box visualization.
- **Beautiful UI:** A modern, dark-mode, glassmorphism UI with animations and responsive design.

## Project Structure
- `data/` : Contains the raw and split datasets.
- `src/` : Contains data preparation and model training scripts.
- `models/` : Contains the trained MobileNetV2 model (`waste_classifier.h5`) and class mappings.
- `backend/` : Contains the FastAPI backend and rule-based logic.
- `frontend/` : Contains the HTML, CSS, and JS files for the UI.

## How to Run the Application

### Prerequisites
Make sure you have Python installed. You can install all dependencies via:
```bash
pip install -r requirements.txt
```

### 1. Start the Backend Server
Navigate to the root directory (`WasteSystem`) and start the FastAPI server using Uvicorn:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`. You can also visit `http://localhost:8000/docs` to test the API directly using Swagger UI.

### 2. Start the Frontend
Since it's a static web page, you can either:
- Open `frontend/index.html` directly in your browser.
- Or use a simple Python HTTP server:
  ```bash
  cd frontend
  python -m http.server 5500
  ```
  Then visit `http://localhost:5500` in your browser.

## Note on Training
If you wish to retrain the model on new data:
1. Place the dataset in `data/raw`.
2. Run `python src/data_prep.py` to organize the dataset.
3. Run `python src/train_model.py` to train the CNN and generate the `.h5` model file.
