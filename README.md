

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
- **Vercel Integration**: Deploy and manage your app with Vercel directly from Cursor using MCP

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT-4 Vision API
- **Image Processing**: Base64 encoding, Canvas API
- **Deployment**: Vercel
- **MCP**: Model Context Protocol for Cursor integration

## Setup & Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- An OpenAI API key with access to GPT-4 Vision
- Node.js 16 or higher (for Vercel MCP)
- Vercel account and API token (for Vercel integration)

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

### Setting up Vercel MCP

1. Navigate to the Vercel MCP directory:
   ```
   cd vercel-mcp
   ```

2. Run the setup script:
   ```
   ./setup.sh
   ```

3. Edit the `.env` file and add your Vercel API token:
   ```
   VERCEL_TOKEN="your-vercel-token-here"
   ```

4. Start the MCP server:
   ```
   npm start
   ```

5. Configure Cursor:
   - Open Cursor Settings
   - Navigate to Features > MCP
   - Click "+ Add New MCP Server"
   - Configure the server:
     - Name: Vercel MCP
     - Type: stdio
     - Command: node /path/to/vercel-mcp/dist/index.js
   - Click "Add"

## Usage

1. Choose between uploading an existing image or taking a new photo
2. For upload: drag and drop an image or click to select a file
3. For camera: click "Start Camera", then "Take Photo" when ready
4. Click "Analyze Meal" to process the image
5. View the detailed nutritional breakdown
6. Click "New Analysis" to analyze another meal

### Using Vercel MCP in Cursor

Once the Vercel MCP is set up, you can use it in Cursor's Composer to:

- List your Vercel projects
- Create new projects
- Manage deployments
- Add and remove domains
- Configure environment variables
- And more!

Simply ask the Composer Agent to perform Vercel-related tasks, and it will use the MCP tools automatically.

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
- Vercel API tokens are stored locally and not exposed

## Development

To modify or extend the application:

1. Backend logic is in `app.py`
2. HTML templates are in the `templates` directory
3. CSS styles are in `static/css/style.css`
4. JavaScript functionality is in `static/js/script.js`
5. Vercel MCP implementation is in the `vercel-mcp` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for providing the GPT-4 Vision API
- Flask for the web framework
- Font Awesome for icons
- Vercel for deployment infrastructure
- Cursor for the MCP integration
