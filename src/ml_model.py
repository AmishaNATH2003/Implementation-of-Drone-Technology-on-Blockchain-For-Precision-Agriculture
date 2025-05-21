'''import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import cv2

# Define CNN model for segmentation
def create_cnn_model(input_shape=(128, 128, 3), num_classes=2):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        MaxPooling2D((2, 2)),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Conv2D(128, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Load and preprocess data for training
def load_and_preprocess_data(train_data_dir, val_data_dir, batch_size=32, target_size=(128, 128)):
    train_datagen = ImageDataGenerator(rescale=1./255)
    train_generator = train_datagen.flow_from_directory(
        train_data_dir, target_size=target_size, batch_size=batch_size, class_mode='sparse')

    val_datagen = ImageDataGenerator(rescale=1./255)
    val_generator = val_datagen.flow_from_directory(
        val_data_dir, target_size=target_size, batch_size=batch_size, class_mode='sparse')

    return train_generator, val_generator

# Segment the image and save the result
def segment_and_save_image(model, input_image_path, output_image_path):
    # Load the input image
    image = cv2.imread(input_image_path)
    image_resized = cv2.resize(image, (128, 128))  # Resize to match model input
    image_resized = image_resized / 255.0  # Normalize the image
    image_resized = np.expand_dims(image_resized, axis=0)  # Add batch dimension

    # Predict the segmentation mask
    segmented_image = model.predict(image_resized)

    # Convert the prediction back to image format
    segmented_image = np.argmax(segmented_image, axis=-1)  # Get the class with the highest probability
    segmented_image = np.squeeze(segmented_image)  # Remove batch dimension

    # Save the segmented image
    cv2.imwrite(output_image_path, segmented_image * 255)  # Save as 8-bit image (multiply by 255)

    print(f"Segmented image saved at {output_image_path}")

# Main function to train the model and segment an image
def main():
    # Define paths for your data (modify these with actual paths)
    train_data_dir = r'F:\Final_Year_project\Blockchain_Agri\src\data\train'
    val_data_dir = r'F:\Final_Year_project\Blockchain_Agri\src\data\val'

    # Load the data
    train_generator, val_generator = load_and_preprocess_data(train_data_dir, val_data_dir)

    # Create and train the model
    model = create_cnn_model()
    model.fit(train_generator, validation_data=val_generator, epochs=10)

    # Save the trained model as an .h5 file
    model.save('crop_weed_detector.h5')
    print("Model saved as crop_weed_detector.h5")

    # Segment a test image
    input_image_path = r'F:\Final_Year_project\Blockchain_Agri\src\data\train\crop\1.JPG'
    output_image_path = 'segmented_image.jpg'  # Output segmented image path
    segment_and_save_image(model, input_image_path, output_image_path)

if __name__ == "__main__":
    main()
'''
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import cv2
import numpy as np
import os

# Set seed for reproducibility
tf.random.set_seed(42)

# Dataset paths
train_dir = r"F:\PROJECT\Final_Year_project\Blockchain_Agri\src\data\train"
val_dir = r"F:\PROJECT\Final_Year_project\Blockchain_Agri\src\data\val"

# Image parameters
img_height = 128
img_width = 128
batch_size = 32

# Data preprocessing and augmentation
train_datagen = ImageDataGenerator(rescale=1./255, zoom_range=0.2, horizontal_flip=True)
val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical'
)

val_gen = val_datagen.flow_from_directory(
    val_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical'
)

# CNN model (AlexNet-like)
model = Sequential([
    Conv2D(96, (11,11), strides=(4,4), activation='relu', input_shape=(img_height, img_width, 3)),
    MaxPooling2D(pool_size=(3,3), strides=(2,2)),

    Conv2D(256, (5,5), padding='same', activation='relu'),
    MaxPooling2D(pool_size=(3,3), strides=(2,2)),

    Conv2D(384, (3,3), padding='same', activation='relu'),
    Conv2D(384, (3,3), padding='same', activation='relu'),
    Conv2D(256, (3,3), padding='same', activation='relu'),
    MaxPooling2D(pool_size=(3,3), strides=(2,2)),

    Flatten(),
    Dense(4096, activation='relu'),
    Dropout(0.5),
    Dense(4096, activation='relu'),
    Dropout(0.5),
    Dense(2, activation='softmax')  # 2 classes: crop and weed
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Model summary
model.summary()

# Train the model
history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=10
)

# Save the trained model
model.save(r"F:\PROJECT\Final_Year_project\Blockchain_Agri\src\crop_weed_detector.h5")

# Reload the trained model
model = load_model(r"F:\PROJECT\Final_Year_project\Blockchain_Agri\src\crop_weed_detector.h5")

def segment_image_and_detect_weeds(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Check if the image is loaded correctly
    if image is None:
        raise ValueError(f"[ERROR] Failed to load image from: {image_path}")

    # Resize the image to fit the model input size
    image_resized = cv2.resize(image, (128, 128))
    image_input = np.expand_dims(image_resized / 255.0, axis=0)

    # Predict the class using the model
    prediction = model.predict(image_input)
    class_id = np.argmax(prediction)

    # Generate the output path for the segmented image
    output_path = image_path.replace("target", "segmented")
    
    # Ensure the directory exists for saving the segmented image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the segmented image (class-id based output)
    cv2.imwrite(output_path, (class_id * 255) * np.ones_like(image_resized))

    print(f"Segmentation done. Weeds detected: {'Yes' if class_id == 1 else 'No'}")
    return output_path, class_id == 1

# Example of usage
image_path = r"F:\PROJECT\Final_Year_project\Blockchain_Agri\src\data\val\crop\target_5.png"
segmented_image_path, weed_detected = segment_image_and_detect_weeds(image_path)
print(f"Segmented image saved at: {segmented_image_path}")
print(f"Weed Detected: {'Yes' if weed_detected else 'No'}")
