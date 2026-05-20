import os
import shutil
import random

def split_dataset(src_dir, dest_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    os.makedirs(dest_dir, exist_ok=True)
    
    for split in ['train', 'val', 'test']:
        split_dir = os.path.join(dest_dir, split)
        os.makedirs(split_dir, exist_ok=True)
        
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    classes = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    
    for class_name in classes:
        class_path = os.path.join(src_dir, class_name)
        
        # Get all valid images
        images = []
        for f in os.listdir(class_path):
            ext = os.path.splitext(f)[1].lower()
            if ext in valid_extensions:
                images.append(f)
            else:
                # Remove unnecessary files to clean dataset
                try:
                    file_to_remove = os.path.join(class_path, f)
                    if os.path.isfile(file_to_remove):
                        os.remove(file_to_remove)
                        print(f"Removed non-image file: {file_to_remove}")
                except Exception as e:
                    print(f"Could not remove {f}: {e}")
                
        # Shuffle with a fixed seed for reproducibility if needed, but random is fine
        random.seed(42)
        random.shuffle(images)
        
        # Split
        total = len(images)
        if total == 0:
            print(f"Warning: No valid images found in {class_name}")
            continue
            
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        train_imgs = images[:train_end]
        val_imgs = images[train_end:val_end]
        test_imgs = images[val_end:]
        
        # Helper to copy
        def copy_imgs(img_list, split_name):
            target_dir = os.path.join(dest_dir, split_name, class_name)
            os.makedirs(target_dir, exist_ok=True)
            for img in img_list:
                shutil.copy2(os.path.join(class_path, img), os.path.join(target_dir, img))
                
        copy_imgs(train_imgs, 'train')
        copy_imgs(val_imgs, 'val')
        copy_imgs(test_imgs, 'test')
        print(f"Class '{class_name}': {len(train_imgs)} train, {len(val_imgs)} val, {len(test_imgs)} test.")

if __name__ == "__main__":
    src_directory = r"C:\Users\krati\OneDrive\Desktop\WasteSystem\data\raw"
    dest_directory = r"C:\Users\krati\OneDrive\Desktop\WasteSystem\data\processed"
    
    if os.path.exists(src_directory):
        print("Splitting dataset into train, val, and test...")
        split_dataset(src_directory, dest_directory)
        print("Dataset preparation complete!")
    else:
        print("Source directory not found!")
