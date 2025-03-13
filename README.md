# NutriVision - Meal Analysis App

NutriVision is a web application that analyzes food images to provide calorie estimates and macronutrient breakdowns. Using advanced AI vision technology, it helps users track their nutrition by simply uploading or capturing photos of their meals.

## Features

- **Image Upload**: Upload images of your meals for analysis
- **Camera Capture**: Use your device's camera to take photos directly in the app
- **Accurate Analysis**: Get detailed nutritional information including:
  - Total calories
  - Protein content (grams)
  - Fat content (grams)
  - Carbohydrate content (grams)
- **Meal Description**: AI-generated description of what's in your meal
- **Modern UI**: Clean, responsive design that works on desktop and mobile devices
- **Real-time Results**: Instant feedback with animated result displays

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT-4 Vision API
- **Image Processing**: Base64 encoding, Canvas API

## Setup & Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- An OpenAI API key with access to GPT-4 Vision

### Installation Steps

1. Clone the repository or download the source code

2. Navigate to the project directory:
   ```
   cd cal_ai
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY="your-api-key-here"
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage

1. Choose between uploading an existing image or taking a new photo
2. For upload: drag and drop an image or click to select a file
3. For camera: click "Start Camera", then "Take Photo" when ready
4. Click "Analyze Meal" to process the image
5. View the detailed nutritional breakdown
6. Click "New Analysis" to analyze another meal

## Error Handling

The application includes comprehensive error handling for:
- Unsupported image formats
- Camera access issues
- API failures
- Invalid responses

## Security Considerations

- The application does not store uploaded images
- API keys are securely stored in environment variables
- Images are processed in-memory and not saved permanently

## Development

To modify or extend the application:

1. Backend logic is in `app.py`
2. HTML templates are in the `templates` directory
3. CSS styles are in `static/css/style.css`
4. JavaScript functionality is in `static/js/script.js`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for providing the GPT-4 Vision API
- Flask for the web framework
- Font Awesome for icons 