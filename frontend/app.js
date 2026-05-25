const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const canvas = document.getElementById('detection-canvas');
const submitBtn = document.getElementById('submit-btn');
const loader = document.getElementById('loader');
const resultsSection = document.getElementById('results-section');

// Result elements
const classificationResults = document.getElementById('classification-results');
const detectionResults = document.getElementById('detection-results');
const multiWarning = document.getElementById('multi-warning');

const predClass = document.getElementById('pred-class');
const predConf = document.getElementById('pred-conf');
const confBar = document.getElementById('conf-bar');
const suggCategory = document.getElementById('sugg-category');
const suggText = document.getElementById('sugg-text');
const detectionList = document.getElementById('detection-list');

let selectedFile = null;

// Backend URL
const API_URL = window.location.protocol === 'file:' ? 'http://127.0.0.1:8000' : window.location.origin;


// File Handling
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
    }
    
    selectedFile = file;
    const reader = new FileReader();
    
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        previewContainer.classList.remove('hidden');
        submitBtn.disabled = false;
        resultsSection.classList.add('hidden');
        canvas.classList.add('hidden');
    };
    
    reader.readAsDataURL(file);
}

// Submit
submitBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    loader.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    try {
        const endpoint = '/predict';
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            displayResults(data);
        }
    } catch (err) {
        alert('Failed to connect to the server. Make sure the backend is running.');
        console.error(err);
    } finally {
        loader.classList.add('hidden');
    }
});

function displayResults(data) {
    resultsSection.classList.remove('hidden');
    
    if (data.type === 'single') {
        classificationResults.classList.remove('hidden');
        detectionResults.classList.add('hidden');
        multiWarning.classList.add('hidden');
        
        predClass.textContent = data.predicted_class;
        const confPercent = Math.round(data.confidence * 100);
        predConf.textContent = `${confPercent}%`;
        
        setTimeout(() => {
            confBar.style.width = `${confPercent}%`;
            // Color based on confidence
            if (confPercent > 80) confBar.style.background = 'linear-gradient(90deg, #3b82f6, #10b981)';
            else if (confPercent > 50) confBar.style.background = 'linear-gradient(90deg, #f59e0b, #eab308)';
            else confBar.style.background = 'linear-gradient(90deg, #ef4444, #f43f5e)';
        }, 100);
        
        suggCategory.textContent = data.category;
        suggText.textContent = data.suggestion;
        
    } else if (data.type === 'multiple') {
        classificationResults.classList.add('hidden');
        detectionResults.classList.remove('hidden');
        canvas.classList.remove('hidden');
        multiWarning.classList.remove('hidden');
        
        drawDetections(data.detections);
    }
}

function drawDetections(detections) {
    // Resize canvas to match image display size
    const rect = imagePreview.getBoundingClientRect();
    
    // Natural image dimensions
    const imgW = imagePreview.naturalWidth;
    const imgH = imagePreview.naturalHeight;
    
    // Scale factors
    const scaleX = rect.width / imgW;
    const scaleY = rect.height / imgH;
    
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    detectionList.innerHTML = '';
    
    if (detections.length === 0) {
        detectionList.innerHTML = '<li class="detection-item">No objects detected</li>';
        return;
    }
    
    detections.forEach((d, i) => {
        // Draw Box
        const [x1, y1, x2, y2] = d.box;
        
        const scaledX = x1 * scaleX;
        const scaledY = y1 * scaleY;
        const scaledW = (x2 - x1) * scaleX;
        const scaledH = (y2 - y1) * scaleY;
        
        // Colors
        const colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444'];
        const color = colors[i % colors.length];
        
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);
        
        // Draw Label
        ctx.fillStyle = color;
        const label = `${d.class} ${Math.round(d.confidence * 100)}%`;
        ctx.font = '14px Outfit';
        const textWidth = ctx.measureText(label).width;
        
        ctx.fillRect(scaledX, scaledY - 25, textWidth + 10, 25);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, scaledX + 5, scaledY - 8);
        
        // Add to List
        const li = document.createElement('li');
        li.className = 'detection-item';
        li.style.borderLeftColor = color;
        li.style.display = 'flex';
        li.style.flexDirection = 'column';
        li.style.gap = '5px';
        li.innerHTML = `
            <div style="display: flex; justify-content: space-between; width: 100%;">
                <span style="text-transform: capitalize; font-weight: 600;">${d.class}</span>
                <span style="color: var(--text-muted)">${Math.round(d.confidence * 100)}%</span>
            </div>
            <div style="font-size: 0.9em; color: var(--text-muted);">
                <strong>${d.category}:</strong> ${d.suggestion}
            </div>
        `;
        detectionList.appendChild(li);
    });
}

// Handle window resize for canvas redrawing
window.addEventListener('resize', () => {
    if (!canvas.classList.contains('hidden') && !resultsSection.classList.contains('hidden') && classificationResults.classList.contains('hidden')) {
        canvas.classList.add('hidden');
    }
});
