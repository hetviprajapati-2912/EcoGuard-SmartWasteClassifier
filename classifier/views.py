import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
from .forms import ImageUploadForm
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import matplotlib
from django.core.files.storage import FileSystemStorage
import io
import base64
from .models import WasteImage

matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import uuid

# Load the trained CNN model
BASE_DIR = settings.BASE_DIR
MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'waste_cnn.h5')
model = load_model(MODEL_PATH)

# Model's original classes (exact order)
specific_classes = [
    'battery',       # 0
    'biological',    # 1
    'brown-glass',   # 2
    'cardboard',     # 3
    'clothes',       # 4
    'green-glass',   # 5
    'metal',         # 6
    'paper',         # 7
    'plastic',       # 8
    'shoes',         # 9
    'trash',         # 10
    'white-glass'    # 11
]

# Index to label mapping
class_indices = {i: label for i, label in enumerate(specific_classes)}

# Label to category mapping
label_to_category = {
    'battery': 'Hazardous',
    'biological': 'Organic',
    'brown-glass': 'Recyclable',
    'cardboard': 'Recyclable',
    'clothes': 'Hazardous',
    'green-glass': 'Recyclable',
    'metal': 'Recyclable',
    'paper': 'Recyclable',
    'plastic': 'Recyclable',
    'shoes': 'Hazardous',
    'trash': 'Hazardous',
    'white-glass': 'Recyclable'
}
def preprocess_image(path):
    """
    Loads and preprocesses an image for model prediction.
    - Resizes to 224x224 (or whatever your model was trained on)
    - Converts to array and normalizes pixel values
    """
    img = image.load_img(path, target_size=(224, 224)) 
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) 
    img_array = img_array / 255.0
    return img_array

def classify_image(image_path):
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array)[0]

    top_indices = predictions.argsort()[-3:][::-1]  # top 3 predictions
    labels = [specific_classes[i] for i in top_indices]
    confidences = [float(predictions[i]) * 100 for i in top_indices]
    categories = [label_to_category[label] for label in labels]

    # Color mapping based on category
    color_map = {
        'Recyclable': 'gold',
        'Organic': 'green',
        'Hazardous': 'red'
    }
    colors = [color_map.get(category, 'blue') for category in categories]

    # Plotting
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, confidences, color=colors)
    plt.ylim(0, 100)
    plt.title("Top 3 Waste Predictions", fontsize=14)
    plt.xlabel("Waste Type", fontsize=12)
    plt.ylabel("Confidence (%)", fontsize=12)

    # Annotate bars with confidence and category
    for i, (bar, conf, cat) in enumerate(zip(bars, confidences, categories)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, f"{conf:.1f}%", 
                 ha='center', fontsize=10, color='black')
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 10, f"{cat}", 
                 ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')

    plt.tight_layout()

    # Convert chart to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    chart_url = 'data:image/png;base64,' + image_base64

    plt.close()

    return labels[0], categories[0], confidences[0], chart_url


def upload_image(request):
    """
    Handles the image upload and renders prediction results.
    """
    form = ImageUploadForm()
    specific_label = None
    category_label = None
    confidence = None
    img_url = None
    chart_url = None

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            file_path = fs.path(filename)
            img_url = fs.url(filename)

            # classify and get updated bar chart path
            specific_label, category_label, confidence, chart_url = classify_image(file_path)

    return render(request, 'classifier/upload.html', {
        'form': form,
        'specific_label': specific_label,
        'category_label': category_label,
        'confidence': round(confidence, 2) if confidence else None,
        'uploaded_image': img_url,
        'chart_url': chart_url  
    })
