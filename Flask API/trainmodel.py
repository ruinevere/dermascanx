import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import seaborn as sns
from PIL import Image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, classification_report

# Define your local dataset paths
BASE_PATH = r'C:\Users\rebeccca\skin_cancer_env\Dataset'
TRAIN_PATH = os.path.join(BASE_PATH, 'train')
TEST_PATH = os.path.join(BASE_PATH, 'test')

# Define subdirectories (categories) within the dataset
our_folders = [
    'Acne and Rosacea Photos',
    'Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions',
    'Melanoma Skin Cancer Nevi and Moles'
]

# Generate full paths for train and test data
def get_image_paths(root_dir, folder):
    folder_path = os.path.join(root_dir, folder)
    if not os.path.exists(folder_path):
        print(f"Warning: Directory {folder_path} does not exist.")
        return []
    return [
        os.path.join(folder_path, img)
        for img in os.listdir(folder_path)
        if img.endswith(('.jpg', '.png', '.jpeg'))
    ]

# Collect train and test image paths
train_data = []
test_data = []

for folder in our_folders:
    train_images = get_image_paths(TRAIN_PATH, folder)
    test_images = get_image_paths(TEST_PATH, folder)
    
    if len(train_images) == 0:
        print(f"No training images found in folder: {folder}")
    if len(test_images) == 0:
        print(f"No testing images found in folder: {folder}")

    train_data.extend([(path, folder) for path in train_images])
    test_data.extend([(path, folder) for path in test_images])

# Create DataFrames for train and test data
train_df = pd.DataFrame(train_data, columns=['Image', 'Label'])
test_df = pd.DataFrame(test_data, columns=['Image', 'Label'])

# Show sample of data
print(train_df.sample(5))
print(f'Train data: {train_df.shape}, Test data: {test_df.shape}')

# Plot distribution of classes
ax = sns.countplot(x=train_df['Label'], order=train_df['Label'].value_counts().index)
ax.bar_label(container=ax.containers[0], labels=train_df['Label'].value_counts().values)
plt.show()

# Image Data Generators for training and testing
train_data_gen = ImageDataGenerator(
    rescale=1 / 255.0,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    validation_split=0.2,
    fill_mode='nearest'
)

test_data_gen = ImageDataGenerator(rescale=1 / 255.0)

# Create data generators
batch_size = 8
train_generator = train_data_gen.flow_from_dataframe(
    dataframe=train_df,
    x_col='Image',
    y_col='Label',
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical',
    subset='training',
    shuffle=True,
    seed=42
)

valid_generator = train_data_gen.flow_from_dataframe(
    dataframe=train_df,
    x_col='Image',
    y_col='Label',
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation',
    shuffle=True,
    seed=42
)

test_generator = test_data_gen.flow_from_dataframe(
    dataframe=test_df,
    x_col='Image',
    y_col='Label',
    target_size=(224, 224),
    batch_size=1,
    class_mode='categorical',
    shuffle=False
)

# Load and customize DenseNet model
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.layers import GlobalAveragePooling2D, BatchNormalization, Dense
from tensorflow.keras.models import Model

# Initialize DenseNet121 with pre-trained ImageNet weights
base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze the base model

# Add custom layers on top
x = GlobalAveragePooling2D()(base_model.output)
x = BatchNormalization()(x)
x = Dense(512, activation='relu')(x)
x = BatchNormalization()(x)
x = Dense(256, activation='relu')(x)
x = BatchNormalization()(x)
output = Dense(len(our_folders), activation='softmax')(x)  # Adapt to number of classes

# Define the final model
model = Model(inputs=base_model.input, outputs=output)

# Compile the model
model.compile(optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['categorical_accuracy'])

# Summary of the model
model.summary()

# Early stopping callback
from tensorflow.keras.callbacks import EarlyStopping

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    min_delta=0.001,
    mode='min'
)

# Train the model
history = model.fit(
    train_generator,
    validation_data=valid_generator,
    epochs=20,
    callbacks=[early_stopping]
)

# Plot training accuracy and loss
plt.plot(history.history['categorical_accuracy'], label='Train Accuracy')
plt.plot(history.history['val_categorical_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Evaluate the model on the test data
test_loss, test_accuracy = model.evaluate(test_generator)
print(f'Test Loss: {test_loss}, Test Accuracy: {test_accuracy}')

# Generate predictions and print classification report and confusion matrix
test_predictions = model.predict(test_generator)
predicted_classes = np.argmax(test_predictions, axis=1)

true_classes = test_generator.classes
class_labels = list(test_generator.class_indices.keys())

print(classification_report(true_classes, predicted_classes, target_names=class_labels))

cm = confusion_matrix(true_classes, predicted_classes)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
fig, ax = plt.subplots(figsize=(10, 10))
disp.plot(ax=ax, cmap=plt.cm.Blues)
plt.show()