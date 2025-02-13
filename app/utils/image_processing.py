def resize_image(image, target_size):
    from PIL import Image
    image = Image.open(image)
    image = image.resize(target_size, Image.ANTIALIAS)
    return image

def normalize_image(image):
    import numpy as np
    image_array = np.array(image) / 255.0
    return image_array

def preprocess_image(image, target_size=(224, 224)):
    resized_image = resize_image(image, target_size)
    normalized_image = normalize_image(resized_image)
    return normalized_image