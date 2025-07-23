from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import math
from typing import List, Tuple, Dict
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class ImprovedStringArtGenerator:
    def __init__(self, num_nails=300, max_lines=4000, canvas_size=500):
        """
        Initialize the String Art Generator with improved algorithm
        
        Args:
            num_nails (int): Number of nails around the perimeter
            max_lines (int): Maximum number of string lines to generate
            canvas_size (int): Size of the output canvas (square)
        """
        self.num_nails = num_nails
        self.max_lines = max_lines
        self.canvas_size = canvas_size
        self.nails = []
        self.paths = []
        
        # Algorithm parameters
        self.line_opacity = 25  # How much each line darkens (0-255)
        self.min_distance = 15  # Minimum nail distance to prevent very short lines
        
        # Pre-compute line lookup table for performance
        self.line_cache = {}
        
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Improved image preprocessing for better string art results
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to target size while maintaining aspect ratio
        target_size = 400  # Increased for better quality
        image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Create a square version of the image
        size = min(image.size)
        square_image = Image.new('RGB', (size, size), (255, 255, 255))
        offset_x = (size - image.width) // 2
        offset_y = (size - image.height) // 2
        square_image.paste(image, (offset_x, offset_y))
        
        # Apply circular mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Apply mask to make background white outside circle
        circular_image = Image.new('RGB', (size, size), (255, 255, 255))
        circular_image.paste(square_image, (0, 0), mask)
        
        # Convert to grayscale
        gray_image = circular_image.convert('L')
        
        # Enhance contrast significantly for better string art
        enhancer = ImageEnhance.Contrast(gray_image)
        gray_image = enhancer.enhance(2.0)  # Strong contrast
        
        # Apply slight blur to reduce noise
        gray_image = gray_image.filter(ImageFilter.GaussianBlur(radius=0.8))
        
        # Resize to canvas size
        gray_image = gray_image.resize((self.canvas_size, self.canvas_size), Image.Resampling.LANCZOS)
        
        # Convert to numpy array (keep as-is, don't invert yet)
        img_array = np.array(gray_image, dtype=np.float32)
        
        # Invert so that dark areas have HIGH values (what we want to darken with strings)
        img_array = 255 - img_array
        
        return img_array
    
    def generate_nails(self):
        """Generate nail positions around the circular perimeter"""
        self.nails = []
        center = self.canvas_size // 2
        radius = center - 10  # Leave a small margin
        
        for i in range(self.num_nails):
            angle = 2 * math.pi * i / self.num_nails
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            # Return as simple [x, y] lists for easier JSON serialization
            self.nails.append([int(x), int(y)])
    
    def get_line_points(self, start_nail: int, end_nail: int) -> List[Tuple[int, int]]:
        """
        Get line points with caching for performance using Bresenham algorithm
        """
        key = (min(start_nail, end_nail), max(start_nail, end_nail))
        
        if key not in self.line_cache:
            x1, y1 = self.nails[start_nail][0], self.nails[start_nail][1]
            x2, y2 = self.nails[end_nail][0], self.nails[end_nail][1]
            self.line_cache[key] = self.bresenham_line(x1, y1, x2, y2)
        
        return self.line_cache[key]
    
    def bresenham_line(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Bresenham's line algorithm for drawing lines between nails"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if 0 <= x < self.canvas_size and 0 <= y < self.canvas_size:
                points.append((x, y))
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    def calculate_line_score(self, target_image: np.ndarray, current_canvas: np.ndarray, 
                           start_nail: int, end_nail: int) -> float:
        """
        Calculate the score for drawing a line between two nails.
        """
        line_points = self.get_line_points(start_nail, end_nail)
        
        if not line_points: return 0.0
        
        total_score = 0.0
        for x, y in line_points:
            target_darkness = target_image[y, x]
            current_darkness = current_canvas[y, x]
            
            if target_darkness > current_darkness:
                score = min(target_darkness - current_darkness, self.line_opacity)
            else:
                score = - (min(255, current_darkness + self.line_opacity) - target_darkness) * 0.5
            total_score += score
        
        return total_score / len(line_points)
    
    def is_valid_connection(self, current_nail: int, target_nail: int) -> bool:
        """Check if a connection between nails is valid"""
        distance = min(abs(target_nail - current_nail), self.num_nails - abs(target_nail - current_nail))
        return distance >= self.min_distance
    
    def generate_string_art_greedy(self, target_image: np.ndarray) -> Dict:
        """
        Generate string art using an improved greedy algorithm
        """
        logger.info("Starting improved greedy string art generation...")
        start_time = time.time()
        
        self.generate_nails()
        logger.info(f"Generated {len(self.nails)} nails")
        
        current_canvas = np.zeros((self.canvas_size, self.canvas_size), dtype=np.float32)
        self.paths = []
        
        current_nail = random.randint(0, self.num_nails - 1)
        recent_connections = set()
        recent_limit = 20
        low_score_count = 0
        min_score_threshold = 0.5
        
        logger.info("Starting greedy path finding...")
        
        for iteration in range(self.max_lines):
            if iteration % 200 == 0 and iteration > 0:
                elapsed = time.time() - start_time
                logger.info(f"Generated {iteration} lines in {elapsed:.1f}s")
            
            best_score = -float('inf')
            best_nail = None
            
            for target_nail in range(self.num_nails):
                if target_nail == current_nail or not self.is_valid_connection(current_nail, target_nail):
                    continue
                
                connection_key = tuple(sorted((current_nail, target_nail)))
                if connection_key in recent_connections:
                    continue
                
                score = self.calculate_line_score(target_image, current_canvas, current_nail, target_nail)
                
                if score > best_score:
                    best_score = score
                    best_nail = target_nail
            
            if best_nail is not None and best_score > min_score_threshold:
                # Return as simple [start, end] list for easier JSON
                self.paths.append([int(current_nail), int(best_nail)])
                
                line_points = self.get_line_points(current_nail, best_nail)
                for x, y in line_points:
                    current_canvas[y, x] = min(255, current_canvas[y, x] + self.line_opacity)
                
                connection_key = tuple(sorted((current_nail, best_nail)))
                recent_connections.add(connection_key)
                if len(recent_connections) > recent_limit:
                    recent_connections.pop()
                
                current_nail = best_nail
                low_score_count = 0
            else:
                low_score_count += 1
                if low_score_count > 50:
                    current_nail = random.randint(0, self.num_nails - 1)
                    low_score_count = 0
                    recent_connections.clear()
                    logger.info(f"Random jump to nail {current_nail}")
                if low_score_count > 100:
                    logger.info(f"Stopping early at iteration {iteration}")
                    break
        
        total_time = time.time() - start_time
        logger.info(f"Generated {len(self.paths)} string paths in {total_time:.1f}s")
        
        return {
            'nails': self.nails,
            'lines': self.paths,
            'message': f'Generated {len(self.paths)} connections in {total_time:.1f}s.'
        }

@app.route('/api/generate-string-art', methods=['POST'])
def generate_string_art_api():
    if 'image' not in request.files:
        return jsonify({"error": "No image file part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            image = Image.open(io.BytesIO(file.read()))
            
            # Initialize the generator
            generator = ImprovedStringArtGenerator()
            
            # Preprocess the image
            target_image_array = generator.preprocess_image(image)
            
            # Generate the string art data
            result_data = generator.generate_string_art_greedy(target_image_array)
            
            return jsonify(result_data)

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            return jsonify({"error": "An internal error occurred during image processing."}), 500

    return jsonify({"error": "An unknown error occurred"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Improved String Art Generator API is running'})

if __name__ == '__main__':
    logger.info("Starting Improved String Art Generator API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
