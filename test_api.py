import os
import json
import urllib.request
import urllib.parse
from PIL import Image

API_URL = "http://localhost:8000/predict"

def send_image(image_path):
    with open(image_path, "rb") as f:
        file_content = f.read()
    
    # Boundary for multipart/form-data
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    # Build the body
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(image_path)}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(file_content)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body))
    }
    
    req = urllib.request.Request(API_URL, data=bytes(body), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read()
            return json.loads(result.decode("utf-8"))
    except urllib.error.URLError as e:
        print("Error connecting to the API:", e)
        if hasattr(e, 'read'):
            print(e.read().decode("utf-8"))
        return None

def test_single():
    print("--- Testing Single Object ---")
    img_path = "data/raw/plastic/plastic1.jpg"
    res = send_image(img_path)
    print(json.dumps(res, indent=2))
    
def test_multiple():
    print("\n--- Testing Multiple Objects ---")
    # Create a synthetic image by pasting two images side by side
    img1 = Image.open("data/raw/plastic/plastic1.jpg")
    img2 = Image.open("data/raw/paper/paper1.jpg")
    
    # Resize both to 300x300
    img1 = img1.resize((300, 300))
    img2 = img2.resize((300, 300))
    
    # Create new image 600x300
    new_img = Image.new('RGB', (600, 300))
    new_img.paste(img1, (0, 0))
    new_img.paste(img2, (300, 0))
    
    # Save temporarily
    temp_path = "test_multi.jpg"
    new_img.save(temp_path)
    
    res = send_image(temp_path)
    print(json.dumps(res, indent=2))
    
    # Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)

if __name__ == "__main__":
    test_single()
    test_multiple()
