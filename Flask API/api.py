from flask import Flask, request, jsonify
from tensorflow.keras import models, preprocessing
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import io


# Initialize Flask app
app = Flask(__name__)

# Load the pre-trained model
MODEL_PATH = r'C:\Users\rebeccca\skin_cancer_env\Dataset\skin_disease_model.h5'
model = load_model(MODEL_PATH)

# Class labels (update according to your model’s output)
LABELS = ['Acne and Rosacea', 'Actinic Keratosis', 'Melanoma']

# Define the image size expected by the model
IMG_SIZE = (224, 224)

@app.route('/predict', methods=['POST'])
def predict():
    # Ensure an image file is in the request
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']

    try:
        # Read the image and preprocess it
        img = Image.open(io.BytesIO(file.read()))
        img = img.resize(IMG_SIZE)
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

        # Make prediction
        predictions = model.predict(img_array)
        predicted_class = LABELS[np.argmax(predictions)]
        confidence = float(np.max(predictions))

        # Return response as JSON
        response = {
            'prediction': predicted_class,
            'confidence': confidence
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
