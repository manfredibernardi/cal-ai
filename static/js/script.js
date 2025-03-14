document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements - Input section
    const fileUpload = document.getElementById('file-upload');
    const btnTakePhoto = document.getElementById('btn-take-photo');
    
    // DOM Elements - Camera section
    const cameraSection = document.getElementById('camera-section');
    const cameraFeed = document.getElementById('camera-feed');
    const cameraCanvas = document.getElementById('camera-canvas');
    const btnCapture = document.getElementById('btn-capture');
    const btnCancelCamera = document.getElementById('btn-cancel-camera');
    
    // DOM Elements - Preview section
    const previewSection = document.getElementById('preview-section');
    const previewImage = document.getElementById('preview-image');
    const btnAnalyze = document.getElementById('btn-analyze');
    const btnRetry = document.getElementById('btn-retry');
    
    // DOM Elements - Loading section
    const loadingSection = document.getElementById('loading-section');
    
    // DOM Elements - Results section
    const resultsSection = document.getElementById('results-section');
    const caloriesValue = document.getElementById('calories-value');
    const proteinsValue = document.getElementById('proteins-value');
    const fatsValue = document.getElementById('fats-value');
    const carbsValue = document.getElementById('carbs-value');
    const btnNewAnalysis = document.getElementById('btn-new-analysis');
    
    // DOM Elements - Error section
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    const btnTryAgain = document.getElementById('btn-try-again');
    
    // Variables for camera functionality
    let stream = null;
    let capturedImage = null;
    
    // Event Listeners - Input section
    fileUpload.addEventListener('change', handleFileUpload);
    btnTakePhoto.addEventListener('click', openCamera);
    
    // Event Listeners - Camera section
    btnCapture.addEventListener('click', capturePhoto);
    btnCancelCamera.addEventListener('click', closeCamera);
    
    // Event Listeners - Preview section
    btnAnalyze.addEventListener('click', analyzeImage);
    btnRetry.addEventListener('click', resetToInput);
    
    // Event Listeners - Results section
    btnNewAnalysis.addEventListener('click', resetToInput);
    
    // Event Listeners - Error section
    btnTryAgain.addEventListener('click', resetToInput);
    
    // Handle file upload
    function handleFileUpload(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check file type
            if (!file.type.match('image.*')) {
                showError('Please select an image file (JPEG, PNG, etc.)');
                return;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                capturedImage = e.target.result;
                
                // Hide input, show preview
                document.getElementById('input-section').classList.add('hidden');
                previewSection.classList.remove('hidden');
            };
            
            reader.readAsDataURL(file);
        }
    }
    
    // Camera functions
    function openCamera() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // Hide input section, show camera section
            document.getElementById('input-section').classList.add('hidden');
            cameraSection.classList.remove('hidden');
            
            // Start camera
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(mediaStream) {
                    stream = mediaStream;
                    cameraFeed.srcObject = mediaStream;
                    cameraFeed.play();
                })
                .catch(function(error) {
                    console.error('Error accessing camera:', error);
                    showError('Could not access camera. Please check permissions or try using image upload instead.');
                });
        } else {
            showError('Your browser does not support camera access. Please try using image upload instead.');
        }
    }
    
    function closeCamera() {
        // Stop camera stream
        if (stream) {
            stream.getTracks().forEach(track => {
                track.stop();
            });
            stream = null;
        }
        
        // Hide camera section, show input section
        cameraSection.classList.add('hidden');
        document.getElementById('input-section').classList.remove('hidden');
    }
    
    function capturePhoto() {
        if (!stream) return;
        
        const context = cameraCanvas.getContext('2d');
        
        // Set canvas dimensions to match video
        cameraCanvas.width = cameraFeed.videoWidth;
        cameraCanvas.height = cameraFeed.videoHeight;
        
        // Draw video frame to canvas
        context.drawImage(cameraFeed, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        // Get image data as base64
        capturedImage = cameraCanvas.toDataURL('image/jpeg');
        
        // Stop camera stream
        if (stream) {
            stream.getTracks().forEach(track => {
                track.stop();
            });
            stream = null;
        }
        
        // Update preview image
        previewImage.src = capturedImage;
        
        // Hide camera section, show preview section
        cameraSection.classList.add('hidden');
        previewSection.classList.remove('hidden');
    }
    
    // Function to analyze the image
    function analyzeImage() {
        if (!capturedImage) {
            showError('No image to analyze');
            return;
        }
        
        // Prepare form data
        const formData = new FormData();
        
        // Check if capturedImage is a data URL or file
        if (typeof capturedImage === 'string' && capturedImage.startsWith('data:')) {
            // It's a data URL (from camera)
            formData.append('image_data', capturedImage.split(',')[1]);
        } else {
            // It's a file (from file input)
            formData.append('file', fileUpload.files[0]);
        }
        
        // Hide preview section, show loading section
        previewSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        
        // Send AJAX request to server
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading section
            loadingSection.classList.add('hidden');
            
            if (data.success) {
                // Display results
                displayResults(data.data);
                resultsSection.classList.remove('hidden');
            } else {
                // Show error
                showError(data.error || 'An error occurred during analysis');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingSection.classList.add('hidden');
            showError('Network error. Please try again.');
        });
    }
    
    // Display analysis results
    function displayResults(data) {
        if (data) {
            // Update nutrition values with animation
            animateCounter(caloriesValue, 0, Math.round(data.calories || 0));
            animateCounter(proteinsValue, 0, Math.round(data.proteins || 0));
            animateCounter(fatsValue, 0, Math.round(data.fats || 0));
            animateCounter(carbsValue, 0, Math.round(data.carbs || 0));
        }
    }
    
    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        hideAllSections();
        errorSection.classList.remove('hidden');
    }
    
    // Reset to input screen
    function resetToInput() {
        // Reset file input
        fileUpload.value = '';
        
        // Reset capturedImage
        capturedImage = null;
        
        // Reset preview image
        previewImage.src = '';
        
        // Hide all sections except input
        hideAllSections();
        document.getElementById('input-section').classList.remove('hidden');
    }
    
    // Hide all main sections
    function hideAllSections() {
        document.getElementById('input-section').classList.add('hidden');
        cameraSection.classList.add('hidden');
        previewSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');
    }
    
    // Animate counter (for nutrition values)
    function animateCounter(element, start, end) {
        let current = start;
        const increment = end / 30;
        const duration = 1000;
        const stepTime = Math.abs(Math.floor(duration / (end - start)));
        
        if (start === end) {
            element.textContent = end;
            return;
        }
        
        const timer = setInterval(function() {
            current += increment;
            
            if (current >= end) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.round(current);
            }
        }, stepTime);
    }
}); 