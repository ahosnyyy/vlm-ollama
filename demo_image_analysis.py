import os
import glob
from app.services.image_analysis import analyze_clothing
import asyncio
from tqdm import tqdm

async def process_images():
    # Directory containing images
    image_dir = 'C:/Users/ahosny/Documents/Projects/datasets/fashionpedia/val/'
    image_paths = glob.glob(os.path.join(image_dir, '*'))
    # Loop through each image file in the directory with a progress bar
    for image_path in tqdm(image_paths, desc='Processing Images', unit='image'):
        if image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                image_name = os.path.basename(image_path)
                
                # Analyze the clothing in the image
                try:
                    analysis_result = await analyze_clothing(image_data, image_name)
                    print(f'Analysis for {image_name}:', analysis_result)
                except Exception as e:
                    print(f'Error analyzing {image_name}: {str(e)}')

# Call the async function
asyncio.run(process_images())
