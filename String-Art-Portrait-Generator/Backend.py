from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import math
from typing import List, Tuple, Dict
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class OptimizedStringArtGenerator:
    def __init__(self, num_nails=200, max_lines=3000, canvas_size=500):
        """
        Initialize the String Art Generator with optimized parameters
        
        Args:
            num_nails (int): Number of nails around the perimeter (reduced for performance)
            max_lines (int): Maximum number of string lines to generate (reduced)
            canvas_size (int): Size of the output canvas (square)
        """
        self.num_nails = num_nails
        self.max_lines = max_lines
        self.canvas_size = canvas_size
        self.nails = []
        self.paths = []
        
        # Pre-compute line lookup table for performance
        self.line_cache = {}
        
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess the input image for string art generation
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize while maintaining aspect ratio
        target_size = 150  # Reduced for better performance
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Create a square canvas and center the image
        square_image = Image.new('RGB', (target_size, target_size), (255, 255, 255))
        offset = ((target_size - image.width) // 2, (target_size - image.height) // 2)
        square_image.paste(image, offset)
        
        # Convert to grayscale
        gray_image = square_image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray_image)
        gray_image = enhancer.enhance(1.3)
        
        # Apply slight blur to reduce noise
        gray_image = gray_image.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        # Convert to numpy array and invert
        img_array = np.array(gray_image)
        img_array = 255 - img_array  # Invert so dark areas have higher values
        
        return img_array
    
    def generate_nails(self):
        """Generate nail positions around the circular perimeter"""
        self.nails = []
        center = self.canvas_size // 2
        radius = center - 20  # Leave some margin
        
        for i in range(self.num_nails):
            angle = 2 * math.pi * i / self.num_nails
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            self.nails.append({'x': int(x), 'y': int(y)})
    
    def get_line_points(self, start_nail: int, end_nail: int) -> List[Tuple[int, int]]:
        """
        Get line points with caching for performance
        """
        key = (min(start_nail, end_nail), max(start_nail, end_nail))
        
        if key not in self.line_cache:
            x1, y1 = self.nails[start_nail]['x'], self.nails[start_nail]['y']
            x2, y2 = self.nails[end_nail]['x'], self.nails[end_nail]['y']
            self.line_cache[key] = self.bresenham_line(x1, y1, x2, y2)
        
        return self.line_cache[key]
    
    def bresenham_line(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Optimized Bresenham's line algorithm"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            points.append((x1, y1))
            
            if x1 == x2 and y1 == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        
        return points
    
    def calculate_line_contribution_fast(self, target_image: np.ndarray, canvas: np.ndarray, 
                                       start_nail: int, end_nail: int) -> float:
        """
        Fast vectorized calculation of line contribution
        """
        line_points = self.get_line_points(start_nail, end_nail)
        
        if len(line_points) == 0:
            return 0.0
        
        # Convert points to numpy arrays for vectorized operations
        points_array = np.array(line_points)
        x_coords = points_array[:, 0]
        y_coords = points_array[:, 1]
        
        # Filter valid points
        valid_mask = ((x_coords >= 0) & (x_coords < self.canvas_size) & 
                     (y_coords >= 0) & (y_coords < self.canvas_size))
        
        if not np.any(valid_mask):
            return 0.0
        
        x_valid = x_coords[valid_mask]
        y_valid = y_coords[valid_mask]
        
        # Scale coordinates to target image
        scale_x = target_image.shape[1] / self.canvas_size
        scale_y = target_image.shape[0] / self.canvas_size
        
        target_x = np.clip((x_valid * scale_x).astype(int), 0, target_image.shape[1] - 1)
        target_y = np.clip((y_valid * scale_y).astype(int), 0, target_image.shape[0] - 1)
        
        # Vectorized contribution calculation
        target_darkness = target_image[target_y, target_x] / 255.0
        current_darkness = np.clip(canvas[y_valid, x_valid] / 255.0, 0, 1)
        
        needed_darkness = np.maximum(0, target_darkness - current_darkness)
        contribution = np.sum(needed_darkness) / len(needed_darkness)
        
        return contribution
    
    def generate_string_art_optimized(self, target_image: np.ndarray) -> Dict:
        """
        Optimized string art generation with better performance
        """
        logger.info("Starting optimized string art generation...")
        start_time = time.time()
        
        # Generate nail positions
        self.generate_nails()
        logger.info(f"Generated {len(self.nails)} nails")
        
        # Initialize canvas
        canvas = np.zeros((self.canvas_size, self.canvas_size), dtype=np.float32)
        self.paths = []
        
        # Pre-compute good nail pairs to avoid checking all combinations
        good_pairs = []
        min_distance = 8  # Minimum distance between connected nails
        
        for i in range(self.num_nails):
            for j in range(i + min_distance, min(i + self.num_nails - min_distance, self.num_nails)):
                if j != i:
                    good_pairs.append((i, j))
        
        # Also add some cross-connections
        for i in range(0, self.num_nails, 4):
            for j in range(self.num_nails // 4, self.num_nails, 8):
                if abs(i - j) > min_distance:
                    good_pairs.append((i, j))
        
        logger.info(f"Pre-computed {len(good_pairs)} potential nail pairs")
        
        # Track recent connections to avoid repetition
        recent_connections = set()
        max_recent = 50
        
        # Generate string paths with timeout protection
        timeout_seconds = 180  # 3 minutes maximum
        
        for iteration in range(self.max_lines):
            current_time = time.time()
            if current_time - start_time > timeout_seconds:
                logger.info(f"Timeout reached after {timeout_seconds}s, stopping generation")
                break
                
            if iteration % 500 == 0:
                logger.info(f"Generated {iteration} lines in {current_time - start_time:.1f}s...")
            
            best_contribution = -1
            best_pair = None
            
            # Sample a subset of pairs for efficiency
            sample_size = min(200, len(good_pairs))
            sampled_indices = np.random.choice(len(good_pairs), sample_size, replace=False)
            
            for idx in sampled_indices:
                start_nail, end_nail = good_pairs[idx]
                
                # Skip recently used connections
                connection_key = (min(start_nail, end_nail), max(start_nail, end_nail))
                if connection_key in recent_connections:
                    continue
                
                contribution = self.calculate_line_contribution_fast(
                    target_image, canvas, start_nail, end_nail
                )
                
                if contribution > best_contribution:
                    best_contribution = contribution
                    best_pair = (start_nail, end_nail)
            
            # If we found a good line, add it
            if best_contribution > 0.005:  # Adjusted threshold
                start_nail, end_nail = best_pair
                
                self.paths.append({
                    'startIndex': int(start_nail),
                    'endIndex': int(end_nail)
                })
                
                # Draw the line on canvas
                line_points = self.get_line_points(start_nail, end_nail)
                for x, y in line_points:
                    if 0 <= x < canvas.shape[1] and 0 <= y < canvas.shape[0]:
                        canvas[y, x] += 3.0
                
                # Update recent connections
                connection_key = (min(start_nail, end_nail), max(start_nail, end_nail))
                recent_connections.add(connection_key)
                if len(recent_connections) > max_recent:
                    # Remove oldest connections (simplified approach)
                    recent_connections = set(list(recent_connections)[-max_recent:])
            
            # Early stopping if contribution is too low for several iterations
            if best_contribution < 0.001:
                if iteration > 500:  # Allow some initial iterations
                    logger.info(f"Stopping early at iteration {iteration} due to low contribution")
                    break
        
        total_time = time.time() - start_time
        logger.info(f"Generated {len(self.paths)} string paths in {total_time:.1f}s")
        
        return {
            'nails': self.nails,
            'paths': self.paths,
            'message': f'String art pattern generated with {len(self.nails)} nails and {len(self.paths)} connections in {total_time:.1f}s. Optimized for performance and visual quality.'
        }

@app.route('/api/generate-string-art', methods=['POST'])
def generate_string_art():
    """
    API endpoint to generate string art from uploaded image
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'base64Image' not in data:
            return jsonify({'error': 'Missing base64Image in request'}), 400
        
        base64_image = data['base64Image']
        mime_type = data.get('mimeType', 'image/jpeg')
        
        logger.info(f"Received image generation request with MIME type: {mime_type}")
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            logger.error(f"Error decoding image: {str(e)}")
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Initialize optimized string art generator
        generator = OptimizedStringArtGenerator(
            num_nails=200,   # Reduced for performance
            max_lines=3000,  # Reduced for performance
            canvas_size=500
        )
        
        # Preprocess image
        processed_image = generator.preprocess_image(image)
        
        # Generate string art with optimizations
        result = generator.generate_string_art_optimized(processed_image)
        
        logger.info("String art generation completed successfully")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in string art generation: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Optimized String Art API is running'})

if __name__ == '__main__':
    logger.info("Starting Optimized String Art Generator API...")
    app.run(host='0.0.0.0', port=5000, debug=True)