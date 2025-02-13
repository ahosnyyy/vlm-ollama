# My FastAPI Clothing Recognition App

This project is a FastAPI application that utilizes a vision language model (VLM) to analyze images of drivers inside car cabins and provide information about their clothing.

## Project Structure

```
my-fastapi-app
├── app
│   ├── main.py                # Entry point of the FastAPI application
│   ├── api
│   │   └── v1
│   │       └── endpoints
│   │           └── clothing_info.py  # API endpoint for clothing information
│   ├── core
│   │   └── config.py          # Configuration settings for the application
│   ├── models
│   │   └── clothing.py        # Contains Pydantic models for analyzing images, including `Object` and `ImageDescription`, which describe detected objects, scene, colors, and other attributes.
│   ├── schemas
│   │   └── clothing.py        # Pydantic schemas for validating clothing data
│   ├── services
│   │   └── clothing_recognition.py  # Logic for recognizing clothing from images
│   └── utils
│       └── image_processing.py # Utility functions for image processing
├── requirements.txt            # Project dependencies
├── Dockerfile                  # Instructions for building a Docker image
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/my-fastapi-app.git
   cd my-fastapi-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## Usage

To use the clothing recognition feature, send a POST request to the `/api/v1/clothing-info` endpoint with an image file. The response will include details about the clothing detected in the image.

## API Documentation

- **POST /api/v1/clothing-info**
  - Request: An image file
  - Response: JSON object containing clothing details (type, color, pattern, etc.)

## License

This project is licensed under the MIT License. See the LICENSE file for details.