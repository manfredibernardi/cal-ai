import os
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
import traceback
from openai import OpenAI
import json

# Try to import Pillow, but handle failure gracefully
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    print("Warning: Pillow (PIL) is not available. Image conversion features will be limited.")
    PILLOW_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging for Vercel
if os.environ.get('VERCEL_ENV'):
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Running in Vercel environment")

# Ensure required environment variables are set
required_env_vars = ["OPENAI_API_KEY", "USDA_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    if os.environ.get('VERCEL_ENV'):
        print(error_msg)  # Print to Vercel logs
    else:
        raise ValueError(error_msg)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error serving index: {str(e)}")
        traceback.print_exc()
        return app.send_static_file('index.html')

@app.errorhandler(500)
def server_error(e):
    error_msg = str(e)
    print(f"Server error: {error_msg}")
    traceback.print_exc()
    return jsonify(error=error_msg), 500

# Set upload folder based on environment
app.config['UPLOAD_FOLDER'] = '/tmp' if os.environ.get('VERCEL_ENV') else 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
print(f"Allowed extensions set to: {app.config['ALLOWED_EXTENSIONS']}")
print(f"Upload folder set to: {app.config['UPLOAD_FOLDER']}")

# Create uploads folder if it doesn't exist and we're not in Vercel
if not os.environ.get('VERCEL_ENV'):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if file has an allowed extension"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    # Print all allowed extensions for debugging
    print(f"Checking extension: '{ext}' against allowed extensions: {app.config['ALLOWED_EXTENSIONS']}")
    is_allowed = ext in app.config['ALLOWED_EXTENSIONS']
    # Add special case for webp since it might be problematic
    if ext == 'webp' and not is_allowed:
        print("WebP file detected but not in allowed extensions!")
    return is_allowed

def analyze_image_with_gpt_vision(image_data):
    """
    Send the image to GPT Vision API and get nutritional analysis
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # Convert image data to base64
        if isinstance(image_data, str):  # If it's a file path
            print(f"Processing image from file path: {image_data}")
            try:
                with open(image_data, "rb") as image_file:
                    image_content = image_file.read()
                    print(f"Successfully read image file: {len(image_content)} bytes")
                    encoded_image = base64.b64encode(image_content).decode('utf-8')
            except Exception as file_error:
                print(f"Error reading image file: {str(file_error)}")
                raise
        else:  # If it's already binary data
            print(f"Processing binary image data: {len(image_data)} bytes")
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
        print(f"Successfully encoded image to base64: {len(encoded_image)} chars")
        
        # Prepare the prompt for GPT Vision with step-by-step instructions
        prompt = """
        You are an expert nutritionist and food analyst with access to detailed food databases. I need you to analyze this food image methodically:
        
        STEP 1: IDENTIFY ALL FOODS
        - List each distinct food item visible in the image
        - Be specific about varieties, cooking methods, and visible ingredients
        - Note visible condiments, sauces, or toppings

        STEP 2: ESTIMATE PORTION SIZES
        - First, estimate the approximate diameter of the plate/container in inches
        - For each food identified in Step 1, estimate:
          * The volume (in cups, tablespoons) or weight (in ounces) as appropriate
          * Use the plate size as a reference
          * Consider portion depth for foods like rice, pasta, etc.

        STEP 3: DETAILED FOOD DESCRIPTIONS
        - For each food, create a standardized description that includes:
          * The specific food name (e.g., "brown rice" not just "rice")
          * Preparation method if visible (baked, fried, grilled, etc.)
          * Visual cues about ingredients (seasonings, oils, etc.)
        
        Format your response as a structured JSON object:
        {
          "plate_size": "estimated diameter in inches",
          "food_items": [
            {
              "name": "specific food name",
              "description": "detailed description",
              "preparation": "cooking method if identifiable",
              "quantity": "numerical value",
              "unit": "oz, cups, tbsp, etc.",
              "confidence": "high/medium/low"
            },
            // repeat for each food item
          ],
          "meal_description": "brief overall description of the meal"
        }

        Be as precise and detailed as possible in your identification and measurements.
        """
        
        print("Sending request to OpenAI API...")
        
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        print("Received response from OpenAI API")
        
        # Extract and parse JSON from the response
        response_text = response.choices[0].message.content
        print(f"Response text length: {len(response_text)} characters")
        
        # Try to find JSON in the response
        try:
            # First try: look for JSON block delimiters
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start >= 0 and json_end >= 0:
                json_str = response_text[json_start:json_end+1]
                print(f"Extracted JSON string: {len(json_str)} characters")
                food_analysis = json.loads(json_str)
            else:
                # Second try: assume the entire response is valid JSON
                food_analysis = json.loads(response_text)
            
            # Get nutrition information for each food item
            print("Successfully parsed JSON response, getting nutrition data...")
            result = get_nutrition_data(food_analysis)
            return {
                "success": True,
                "data": result
            }
                
        except json.JSONDecodeError as json_error:
            # If JSON parsing fails, return the raw response
            print(f"Failed to parse JSON: {str(json_error)}")
            print(f"Raw response text: {response_text}")
            return {
                "success": False,
                "error": f"Failed to parse GPT Vision response: {str(json_error)}",
                "raw_response": response_text
            }
    
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

def get_nutrition_data(food_analysis):
    """
    Get nutrition data for each food item using USDA FoodData Central API
    """
    # Initialize nutrition totals
    total_nutrition = {
        "calories": 0,
        "proteins": 0,
        "fats": 0,
        "carbs": 0
    }
    
    # Get API key from environment
    api_key = os.getenv("USDA_API_KEY")
    
    if not api_key:
        # If no API key, make an estimate based on the food items
        return estimate_nutrition(food_analysis)
    
    food_details = []
    
    # Process each food item
    for food_item in food_analysis.get("food_items", []):
        # Prepare search term
        food_name = food_item.get("name", "")
        
        # Search for food in USDA FoodData Central
        search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "api_key": api_key,
            "query": food_name,
            "dataType": ["Foundation", "SR Legacy"],
            "pageSize": 1
        }
        
        try:
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get("foods") and len(data["foods"]) > 0:
                    food_data = data["foods"][0]
                    
                    # Get nutrient values
                    nutrients = food_data.get("foodNutrients", [])
                    calories = next((n["value"] for n in nutrients if n.get("nutrientName") == "Energy" and n.get("unitName") == "KCAL"), 0)
                    proteins = next((n["value"] for n in nutrients if n.get("nutrientName") == "Protein"), 0)
                    fats = next((n["value"] for n in nutrients if n.get("nutrientName") == "Total lipid (fat)"), 0)
                    carbs = next((n["value"] for n in nutrients if n.get("nutrientName") == "Carbohydrate, by difference"), 0)
                    
                    # Scale nutrients based on portion size
                    quantity = float(food_item.get("quantity", 1))
                    unit = food_item.get("unit", "oz")
                    
                    # Convert to grams based on unit
                    grams = convert_to_grams(quantity, unit)
                    
                    # Standard USDA reference amount is per 100g
                    scale_factor = grams / 100.0
                    
                    # Calculate scaled nutrients
                    item_nutrition = {
                        "name": food_name,
                        "description": food_item.get("description", ""),
                        "calories": calories * scale_factor,
                        "proteins": proteins * scale_factor,
                        "fats": fats * scale_factor,
                        "carbs": carbs * scale_factor,
                        "quantity": quantity,
                        "unit": unit
                    }
                    
                    # Add to total nutrition
                    total_nutrition["calories"] += item_nutrition["calories"]
                    total_nutrition["proteins"] += item_nutrition["proteins"]
                    total_nutrition["fats"] += item_nutrition["fats"]
                    total_nutrition["carbs"] += item_nutrition["carbs"]
                    
                    food_details.append(item_nutrition)
                else:
                    # If food not found, estimate
                    estimated = estimate_food_item(food_item)
                    food_details.append(estimated)
                    
                    # Add to total nutrition
                    total_nutrition["calories"] += estimated["calories"]
                    total_nutrition["proteins"] += estimated["proteins"]
                    total_nutrition["fats"] += estimated["fats"]
                    total_nutrition["carbs"] += estimated["carbs"]
            else:
                # API error, estimate nutrients
                estimated = estimate_food_item(food_item)
                food_details.append(estimated)
                
                # Add to total nutrition
                total_nutrition["calories"] += estimated["calories"]
                total_nutrition["proteins"] += estimated["proteins"]
                total_nutrition["fats"] += estimated["fats"]
                total_nutrition["carbs"] += estimated["carbs"]
                
        except Exception as e:
            print(f"Error getting nutrition data for {food_name}: {str(e)}")
            # On error, estimate nutrients
            estimated = estimate_food_item(food_item)
            food_details.append(estimated)
            
            # Add to total nutrition
            total_nutrition["calories"] += estimated["calories"]
            total_nutrition["proteins"] += estimated["proteins"]
            total_nutrition["fats"] += estimated["fats"]
            total_nutrition["carbs"] += estimated["carbs"]
    
    # Prepare final result
    result = {
        "meal_description": food_analysis.get("meal_description", ""),
        "plate_size": food_analysis.get("plate_size", ""),
        "total_nutrition": total_nutrition,
        "food_items": food_details
    }
    
    return result

def convert_to_grams(quantity, unit):
    """Convert various units to grams"""
    unit = unit.lower()
    if unit in ["g", "grams"]:
        return quantity
    elif unit in ["oz", "ounce", "ounces"]:
        return quantity * 28.35  # 1 oz = 28.35g
    elif unit in ["cup", "cups"]:
        return quantity * 240  # Approximately 240g per cup (varies by food)
    elif unit in ["tbsp", "tablespoon", "tablespoons"]:
        return quantity * 15  # Approximately 15g
    elif unit in ["tsp", "teaspoon", "teaspoons"]:
        return quantity * 5  # Approximately 5g
    else:
        # Default to oz if unit not recognized
        return quantity * 28.35

def estimate_food_item(food_item):
    """
    Make a rough estimate of nutrition for a food item when API data is unavailable
    """
    # Basic estimates for common food categories (per 100g)
    food_estimates = {
        "default": {"calories": 150, "proteins": 5, "fats": 5, "carbs": 20},
        "vegetable": {"calories": 50, "proteins": 2, "fats": 0.5, "carbs": 10},
        "fruit": {"calories": 70, "proteins": 1, "fats": 0.3, "carbs": 15},
        "meat": {"calories": 200, "proteins": 25, "fats": 12, "carbs": 0},
        "fish": {"calories": 150, "proteins": 20, "fats": 8, "carbs": 0},
        "grain": {"calories": 350, "proteins": 10, "fats": 2, "carbs": 70},
        "dairy": {"calories": 150, "proteins": 10, "fats": 8, "carbs": 12},
        "dessert": {"calories": 400, "proteins": 5, "fats": 15, "carbs": 60}
    }
    
    # Try to categorize the food item
    name = food_item.get("name", "").lower()
    description = food_item.get("description", "").lower()
    text = name + " " + description
    
    category = "default"
    for key in food_estimates:
        if key in text and key != "default":
            category = key
            break
    
    # Get base estimates for the category
    base_nutrition = food_estimates[category]
    
    # Scale based on portion size
    quantity = float(food_item.get("quantity", 1))
    unit = food_item.get("unit", "oz")
    
    # Convert to grams
    grams = convert_to_grams(quantity, unit)
    
    # Scale nutrition values (base values are per 100g)
    scale_factor = grams / 100.0
    
    return {
        "name": food_item.get("name", ""),
        "description": food_item.get("description", ""),
        "calories": round(base_nutrition["calories"] * scale_factor, 1),
        "proteins": round(base_nutrition["proteins"] * scale_factor, 1),
        "fats": round(base_nutrition["fats"] * scale_factor, 1),
        "carbs": round(base_nutrition["carbs"] * scale_factor, 1),
        "quantity": quantity,
        "unit": unit,
        "estimated": True  # Flag to indicate this is an estimate
    }

def estimate_nutrition(food_analysis):
    """
    Estimate nutrition when API is unavailable
    """
    # Initialize nutrition totals
    total_nutrition = {
        "calories": 0,
        "proteins": 0,
        "fats": 0,
        "carbs": 0
    }
    
    food_details = []
    
    # Process each food item
    for food_item in food_analysis.get("food_items", []):
        estimated = estimate_food_item(food_item)
        food_details.append(estimated)
        
        # Add to total nutrition
        total_nutrition["calories"] += estimated["calories"]
        total_nutrition["proteins"] += estimated["proteins"]
        total_nutrition["fats"] += estimated["fats"]
        total_nutrition["carbs"] += estimated["carbs"]
    
    # Prepare final result
    result = {
        "meal_description": food_analysis.get("meal_description", ""),
        "plate_size": food_analysis.get("plate_size", ""),
        "total_nutrition": total_nutrition,
        "food_items": food_details,
        "note": "Nutrition values are estimates based on visual analysis and may not be accurate."
    }
    
    return result

def extract_number(text, *keywords):
    """Extract numerical values associated with keywords from text"""
    for line in text.split('\n'):
        for keyword in keywords:
            if keyword.lower() in line.lower():
                # Find all numbers in the line
                import re
                numbers = re.findall(r'\d+(?:\.\d+)?', line)
                if numbers:
                    return float(numbers[0])
    return 0  # Default if no number found

def convert_image_format(input_path, output_path, format='JPEG'):
    """Convert image to another format if Pillow is available"""
    if not PILLOW_AVAILABLE:
        print("Warning: Cannot convert image format because Pillow is not available")
        # Just copy the file as a fallback
        with open(input_path, 'rb') as src, open(output_path, 'wb') as dst:
            dst.write(src.read())
        return False
    
    try:
        with Image.open(input_path) as img:
            # Handle transparency if needed
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(output_path, format, quality=90)
        return True
    except Exception as e:
        print(f"Error converting image: {str(e)}")
        return False

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files and 'image_data' not in request.form:
        print("Error: No image provided")
        return jsonify({"success": False, "error": "No image provided"})
    
    try:
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                print("Error: No file selected")
                return jsonify({"success": False, "error": "No file selected"})
            
            print(f"File received: {file.filename}, Content type: {file.content_type}")
            
            # Save the uploaded file temporarily
            filename = secure_filename(file.filename)
            original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "original_" + filename)
            file.save(original_filepath)
            print(f"Original file saved to: {original_filepath}")
            
            # For WebP files, convert to JPEG if Pillow is available
            if filename.lower().endswith('.webp'):
                print("Converting WebP to JPEG...")
                processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], "processed_" + filename.rsplit('.', 1)[0] + ".jpg")
                
                if convert_image_format(original_filepath, processed_filepath):
                    print(f"Converted image saved to: {processed_filepath}")
                    filepath_to_analyze = processed_filepath
                else:
                    print("Could not convert WebP, using original file")
                    filepath_to_analyze = original_filepath
                    
                # Use the processed or original image for analysis
                try:
                    result = analyze_image_with_gpt_vision(filepath_to_analyze)
                    # Clean up files after analysis
                    if os.path.exists(original_filepath):
                        os.remove(original_filepath)
                    if os.path.exists(processed_filepath) and original_filepath != processed_filepath:
                        os.remove(processed_filepath)
                    return jsonify(result)
                except Exception as analysis_error:
                    print(f"Error analyzing image: {str(analysis_error)}")
                    # Clean up files
                    if os.path.exists(original_filepath):
                        os.remove(original_filepath)
                    if os.path.exists(processed_filepath) and original_filepath != processed_filepath:
                        os.remove(processed_filepath)
                    raise
            
            # For non-WebP files
            else:
                # Check file extension
                if not allowed_file(filename):
                    print(f"Error: Invalid file format. File: {filename}")
                    os.remove(original_filepath)
                    return jsonify({"success": False, "error": f"Invalid file format. Allowed formats: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"})
                
                try:
                    result = analyze_image_with_gpt_vision(original_filepath)
                    # Clean up the file after analysis
                    os.remove(original_filepath)
                    return jsonify(result)
                except Exception as analysis_error:
                    print(f"Error analyzing image: {str(analysis_error)}")
                    if os.path.exists(original_filepath):
                        os.remove(original_filepath)
                    return jsonify({"success": False, "error": f"Error analyzing image: {str(analysis_error)}"})
        
        # Handle base64 image data from webcam
        elif 'image_data' in request.form:
            image_data = request.form['image_data']
            # Check if the data is valid
            if not image_data:
                print("Error: Empty image data")
                return jsonify({"success": False, "error": "Empty image data"})
                
            # Extract content type and raw base64 data
            content_type = None
            if image_data.startswith('data:image'):
                content_parts = image_data.split(';')
                if len(content_parts) > 0:
                    content_type = content_parts[0].split(':')[1]
                print(f"Base64 image content type: {content_type}")
                image_data = image_data.split(',')[1]
            
            try:
                # Decode base64 to binary
                image_binary = base64.b64decode(image_data)
                
                # If it's a WebP image, convert it to JPEG if Pillow is available
                if content_type == 'image/webp':
                    print("Converting WebP base64 image to JPEG...")
                    temp_webp_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_webcam.webp")
                    temp_jpg_path = os.path.join(app.config['UPLOAD_FOLDER'], "temp_webcam.jpg")
                    
                    # Save the original WebP image
                    with open(temp_webp_path, 'wb') as f:
                        f.write(image_binary)
                    
                    if convert_image_format(temp_webp_path, temp_jpg_path):
                        print(f"Converted base64 image saved to: {temp_jpg_path}")
                        filepath_to_analyze = temp_jpg_path
                    else:
                        print("Could not convert WebP, using original file")
                        filepath_to_analyze = temp_webp_path
                    
                    # Analyze the image
                    try:
                        result = analyze_image_with_gpt_vision(filepath_to_analyze)
                        
                        # Clean up temporary files
                        if os.path.exists(temp_webp_path):
                            os.remove(temp_webp_path)
                        if os.path.exists(temp_jpg_path) and temp_webp_path != temp_jpg_path:
                            os.remove(temp_jpg_path)
                        
                        return jsonify(result)
                    
                    except Exception as analysis_error:
                        print(f"Error analyzing WebP base64 image: {str(analysis_error)}")
                        # Clean up any temporary files
                        if os.path.exists(temp_webp_path):
                            os.remove(temp_webp_path)
                        if os.path.exists(temp_jpg_path) and temp_webp_path != temp_jpg_path:
                            os.remove(temp_jpg_path)
                        return jsonify({"success": False, "error": f"Error analyzing WebP image: {str(analysis_error)}"})
                
                # For other image types, process directly
                else:
                    result = analyze_image_with_gpt_vision(image_binary)
                    return jsonify(result)
                
            except Exception as decode_error:
                print(f"Error decoding image data: {str(decode_error)}")
                return jsonify({"success": False, "error": f"Error decoding image data: {str(decode_error)}"})
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0') 