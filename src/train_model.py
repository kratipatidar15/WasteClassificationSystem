import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import classification_report, confusion_matrix

def create_model(num_classes):
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Freeze the base model layers
    for layer in base_model.layers:
        layer.trainable = False
        
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])
    return model

def print_confusion_matrix(model, val_generator):
    # Get predictions
    val_generator.reset()
    Y_pred = model.predict(val_generator, steps=val_generator.samples // val_generator.batch_size + 1)
    y_pred = np.argmax(Y_pred, axis=1)
    
    # Get true labels
    y_true = val_generator.classes
    
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print("Confusion Matrix:")
    print(cm)
    
    # Print classification report
    print('Classification Report')
    print(classification_report(y_true, y_pred, target_names=val_generator.class_indices.keys()))

def main():
    base_dir = r"C:\Users\krati\OneDrive\Desktop\WasteSystem\data\processed"
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'val')
    test_dir = os.path.join(base_dir, 'test')
    
    if not os.path.exists(train_dir):
        print(f"Data directory {train_dir} not found. Please run data_prep.py first.")
        return
        
    img_size = (224, 224)
    batch_size = 32
    
    # Data Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    val_test_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical'
    )
    
    val_generator = val_test_datagen.flow_from_directory(
        val_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    # Get class names and save mapping
    class_names = list(train_generator.class_indices.keys())
    print(f"Found {len(class_names)} classes: {class_names}")
    
    # Write classes mapping to file for backend
    os.makedirs('models', exist_ok=True)
    with open('models/classes.txt', 'w') as f:
        for c in class_names:
            f.write(f"{c}\n")
            
    num_classes = len(class_names)
    
    model = create_model(num_classes)
    
    # Callbacks
    checkpoint = ModelCheckpoint('models/waste_classifier.h5', monitor='val_accuracy', save_best_only=True, mode='max', verbose=1)
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=1e-5, verbose=1)
    
    print("Starting training...")
    epochs = 5  # Adjust based on time and accuracy
    history = model.fit(
        train_generator,
        steps_per_epoch=20, # Reduced for quick execution
        validation_data=val_generator,
        validation_steps=10, # Reduced for quick execution
        epochs=epochs,
        callbacks=[checkpoint, early_stop, reduce_lr]
    )
    
    print("Training complete. Evaluating metrics...")
    print_confusion_matrix(model, val_generator)
    
    print("Base training complete. Model saved.")

if __name__ == "__main__":
    main()
