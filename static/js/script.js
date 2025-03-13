document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadTab = document.getElementById('upload-tab');
    const cameraTab = document.getElementById('camera-tab');
    const uploadContent = document.getElementById('upload-content');
    const cameraContent = document.getElementById('camera-content');
    const uploadForm = document.getElementById('upload-form');
    const fileUpload = document.getElementById('file-upload');
    const filePreviewContainer = document.getElementById('file-preview-container');
    const filePreview = document.getElementById('file-preview');
    const removePreview = document.getElementById('remove-preview');
    const cameraFeed = document.getElementById('camera-feed');
    const cameraCanvas = document.getElementById('camera-canvas');
    const cameraPreviewContainer = document.getElementById('camera-preview-container');
    const cameraPreview = document.getElementById('camera-preview');
    const retakePhoto = document.getElementById('retake-photo');
    const btnStartCamera = document.getElementById('btn-start-camera');
    const btnTakePhoto = document.getElementById('btn-take-photo');
    const btnAnalyzePhoto = document.getElementById('btn-analyze-photo');
    const resultContainer = document.getElementById('result-container');
    const loader = document.getElementById('loader');
    const resultsContent = document.getElementById('results-content');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const btnNewAnalysis = document.getElementById('btn-new-analysis');
    const btnTryAgain = document.getElementById('btn-try-again');
    const mealDescription = document.getElementById('meal-description');
    const calorieCount = document.getElementById('calorie-count');
    const proteinCount = document.getElementById('protein-count');
    const fatCount = document.getElementById('fat-count');
    const carbCount = document.getElementById('carb-count');
    
    // Variables for camera functionality
    let stream = null;
    let capturedImage = null;
    
    // Tab switching
    uploadTab.addEventListener('click', function() {
        uploadTab.classList.add('active');
        cameraTab.classList.remove('active');
        uploadContent.classList.remove('hidden');
        cameraContent.classList.add('hidden');
        
        // Stop camera stream if active
        stopCameraStream();
    });
    
    cameraTab.addEventListener('click', function() {
        cameraTab.classList.add('active');
        uploadTab.classList.remove('active');
        cameraContent.classList.remove('hidden');
        uploadContent.classList.add('hidden');
    });
    
    // File upload and preview
    fileUpload.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check file type
            if (!file.type.match('image.*')) {
                showError('Please select an image file (JPEG, PNG, etc.)');
                return;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                filePreview.src = e.target.result;
                filePreviewContainer.classList.remove('hidden');
            };
            
            reader.readAsDataURL(file);
        }
    });
    
    // Remove file preview
    removePreview.addEventListener('click', function() {
        filePreview.src = '';
        filePreviewContainer.classList.add('hidden');
        fileUpload.value = '';
    });
    
    // Camera functions
    btnStartCamera.addEventListener('click', function() {
        startCamera();
    });
    
    btnTakePhoto.addEventListener('click', function() {
        capturePhoto();
    });
    
    retakePhoto.addEventListener('click', function() {
        // Hide preview and show camera feed again
        cameraPreviewContainer.classList.add('hidden');
        cameraFeed.classList.remove('hidden');
        btnTakePhoto.classList.remove('hidden');
        btnAnalyzePhoto.classList.add('hidden');
        
        // Clear captured image
        capturedImage = null;
    });
    
    // Start camera stream
    function startCamera() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(mediaStream) {
                    stream = mediaStream;
                    cameraFeed.srcObject = mediaStream;
                    cameraFeed.play();
                    
                    // Show camera controls
                    btnStartCamera.classList.add('hidden');
                    btnTakePhoto.classList.remove('hidden');
                    cameraFeed.classList.remove('hidden');
                })
                .catch(function(error) {
                    console.error('Error accessing camera:', error);
                    showError('Could not access camera. Please check permissions or try using image upload instead.');
                });
        } else {
            showError('Your browser does not support camera access. Please try using image upload instead.');
        }
    }
    
    // Stop camera stream
    function stopCameraStream() {
        if (stream) {
            stream.getTracks().forEach(track => {
                track.stop();
            });
            stream = null;
            
            // Reset camera UI
            cameraFeed.srcObject = null;
            cameraFeed.classList.add('hidden');
            cameraPreviewContainer.classList.add('hidden');
            btnStartCamera.classList.remove('hidden');
            btnTakePhoto.classList.add('hidden');
            btnAnalyzePhoto.classList.add('hidden');
        }
    }
    
    // Capture photo from camera
    function capturePhoto() {
        const context = cameraCanvas.getContext('2d');
        
        // Set canvas dimensions to match video
        cameraCanvas.width = cameraFeed.videoWidth;
        cameraCanvas.height = cameraFeed.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(cameraFeed, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        // Get image data as base64
        capturedImage = cameraCanvas.toDataURL('image/jpeg');
        
        // Show preview
        cameraPreview.src = capturedImage;
        cameraPreviewContainer.classList.remove('hidden');
        cameraFeed.classList.add('hidden');
        
        // Update buttons
        btnTakePhoto.classList.add('hidden');
        btnAnalyzePhoto.classList.remove('hidden');
    }
    
    // Form submission for file upload
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if file is selected
        if (!fileUpload.files || !fileUpload.files[0]) {
            showError('Please select an image file');
            return;
        }
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', fileUpload.files[0]);
        
        // Send request to API
        analyzeImage(formData);
    });
    
    // Analyze photo from camera
    btnAnalyzePhoto.addEventListener('click', function() {
        if (!capturedImage) {
            showError('Please capture a photo first');
            return;
        }
        
        // Prepare form data with base64 image
        const formData = new FormData();
        formData.append('image_data', capturedImage.split(',')[1]);
        
        // Send request to API
        analyzeImage(formData);
    });
    
    // Function to send image to API and handle response
    function analyzeImage(formData) {
        // Show loader
        resultContainer.classList.remove('hidden');
        loader.classList.remove('hidden');
        resultsContent.classList.add('hidden');
        errorMessage.classList.add('hidden');
        
        // Send AJAX request to server
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            loader.classList.add('hidden');
            
            if (data.success) {
                // Display results
                displayResults(data.data);
                resultsContent.classList.remove('hidden');
            } else {
                // Show error
                showError(data.error || 'An error occurred during analysis');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loader.classList.add('hidden');
            showError('Network error. Please try again.');
        });
    }
    
    // Display analysis results
    function displayResults(data) {
        // Check if we have the data in the expected format
        if (data) {
            // Update meal description
            if (data.description) {
                mealDescription.textContent = data.description;
            } else {
                mealDescription.textContent = 'A nutritious meal';
            }
            
            // Update nutrition counters with animation
            animateCounter(calorieCount, 0, Math.round(data.calories || 0));
            animateCounter(proteinCount, 0, Math.round(data.proteins || 0));
            animateCounter(fatCount, 0, Math.round(data.fats || 0));
            animateCounter(carbCount, 0, Math.round(data.carbs || 0));
        } else {
            // If data format is unexpected
            showError('Invalid response format from the server');
        }
    }
    
    // Animate counter from start to end value
    function animateCounter(element, start, end) {
        if (start === end) {
            element.textContent = end;
            return;
        }
        
        let current = start;
        const increment = end > start ? 1 : -1;
        const stepTime = Math.abs(Math.floor(500 / (end - start)));
        
        const timer = setInterval(function() {
            current += increment;
            element.textContent = current;
            
            if (current === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }
    
    // Show error message
    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        resultsContent.classList.add('hidden');
        loader.classList.add('hidden');
    }
    
    // New analysis button
    btnNewAnalysis.addEventListener('click', function() {
        resetUI();
    });
    
    // Try again button
    btnTryAgain.addEventListener('click', function() {
        resetUI();
    });
    
    // Reset UI to initial state
    function resetUI() {
        // Hide results
        resultContainer.classList.add('hidden');
        
        // Reset file upload
        fileUpload.value = '';
        filePreview.src = '';
        filePreviewContainer.classList.add('hidden');
        
        // Reset camera
        capturedImage = null;
        cameraPreviewContainer.classList.add('hidden');
        
        if (stream) {
            cameraFeed.classList.remove('hidden');
            btnTakePhoto.classList.remove('hidden');
            btnAnalyzePhoto.classList.add('hidden');
        } else {
            btnStartCamera.classList.remove('hidden');
            btnTakePhoto.classList.add('hidden');
            btnAnalyzePhoto.classList.add('hidden');
        }
    }
    
    // Drag and drop functionality for file upload
    const dropZone = document.querySelector('.file-upload-container');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropZone.classList.add('highlight');
    }
    
    function unhighlight() {
        dropZone.classList.remove('highlight');
    }
    
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files && files[0]) {
            fileUpload.files = files;
            
            // Trigger change event
            const event = new Event('change');
            fileUpload.dispatchEvent(event);
        }
    }
}); 