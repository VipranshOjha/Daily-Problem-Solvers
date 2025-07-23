from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
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
        
        # Create circular mask - crop to circle
        size = min(image.size)
        
        # Create a square version of the image
        square_image = Image.new('RGB', (size, size), (255, 255, 255))
        offset_x = (size - image.width) // 2
        offset_y = (size - image.height) // 2
        square_image.paste(image, (offset_x, offset_y))
        
        # Apply circular mask
        mask = Image.new('L', (size, size), 0)
        from PIL import ImageDraw
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
        radius = center - 30  # Leave margin for nails
        
        for i in range(self.num_nails):
            angle = 2 * math.pi * i / self.num_nails
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            self.nails.append({'x': int(x), 'y': int(y)})
    
    def get_line_points(self, start_nail: int, end_nail: int) -> List[Tuple[int, int]]:
        """
        Get line points with caching for performance using Bresenham algorithm
        """
        key = (min(start_nail, end_nail), max(start_nail, end_nail))
        
        if key not in self.line_cache:
            x1, y1 = self.nails[start_nail]['x'], self.nails[start_nail]['y']
            x2, y2 = self.nails[end_nail]['x'], self.nails[end_nail]['y']
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
        Higher score means the line better matches what we want to achieve.
        """
        line_points = self.get_line_points(start_nail, end_nail)
        
        if len(line_points) == 0:
            return 0.0
        
        total_score = 0.0
        valid_points = 0
        
        for x, y in line_points:
            if 0 <= x < self.canvas_size and 0 <= y < self.canvas_size:
                # How dark should this pixel be in the target?
                target_darkness = target_image[y, x]
                
                # How dark is it currently?
                current_darkness = current_canvas[y, x]
                
                # How much darker would it be if we add this line?
                new_darkness = min(255, current_darkness + self.line_opacity)
                
                # Score based on how much closer we get to the target
                # If target is dark and we're light, adding darkness is good
                # If target is light and we're already dark, adding more darkness is bad
                if target_darkness > current_darkness:
                    # We need more darkness here
                    score = min(target_darkness - current_darkness, self.line_opacity)
                else:
                    # We already have enough or too much darkness
                    score = -(new_darkness - target_darkness) * 0.5
                
                total_score += score
                valid_points += 1
        
        if valid_points == 0:
            return 0.0
        
        return total_score / valid_points
    
    def is_valid_connection(self, current_nail: int, target_nail: int) -> bool:
        """Check if a connection between nails is valid"""
        # Calculate distance between nails (in nail indices, not pixels)
        distance = min(abs(target_nail - current_nail), 
                      self.num_nails - abs(target_nail - current_nail))
        
        # Don't allow connections that are too short
        return distance >= self.min_distance
    
    def generate_string_art_greedy(self, target_image: np.ndarray) -> Dict:
        """
        Generate string art using an improved greedy algorithm
        """
        logger.info("Starting improved greedy string art generation...")
        start_time = time.time()
        
        # Generate nail positions
        self.generate_nails()
        logger.info(f"Generated {len(self.nails)} nails")
        
        # Initialize canvas (current state)
        current_canvas = np.zeros((self.canvas_size, self.canvas_size), dtype=np.float32)
        self.paths = []
        
        # Start from a random nail
        current_nail = random.randint(0, self.num_nails - 1)
        
        # Keep track of recently used connections to avoid immediate repetition
        recent_connections = set()
        recent_limit = 20
        
        # Track consecutive low scores to detect when to stop
        low_score_count = 0
        min_score_threshold = 0.5
        
        logger.info("Starting greedy path finding...")
        
        for iteration in range(self.max_lines):
            if iteration % 200 == 0 and iteration > 0:
                elapsed = time.time() - start_time
                logger.info(f"Generated {iteration} lines in {elapsed:.1f}s, current nail: {current_nail}")
            
            best_score = -float('inf')
            best_nail = None
            
            # Evaluate all possible connections from current nail
            for target_nail in range(self.num_nails):
                if target_nail == current_nail:
                    continue
                
                if not self.is_valid_connection(current_nail, target_nail):
                    continue
                
                # Skip recently used connections
                connection_key = (min(current_nail, target_nail), max(current_nail, target_nail))
                if connection_key in recent_connections:
                    continue
                
                # Calculate score for this connection
                score = self.calculate_line_score(target_image, current_canvas, 
                                                current_nail, target_nail)
                
                if score > best_score:
                    best_score = score
                    best_nail = target_nail
            
            # If we found a good connection, use it
            if best_nail is not None and best_score > min_score_threshold:
                # Add the path
                self.paths.append({
                    'startIndex': int(current_nail),
                    'endIndex': int(best_nail)
                })
                
                # Draw the line on the current canvas
                line_points = self.get_line_points(current_nail, best_nail)
                for x, y in line_points:
                    if 0 <= x < self.canvas_size and 0 <= y < self.canvas_size:
                        current_canvas[y, x] = min(255, current_canvas[y, x] + self.line_opacity)
                
                # Update recent connections
                connection_key = (min(current_nail, best_nail), max(current_nail, best_nail))
                recent_connections.add(connection_key)
                if len(recent_connections) > recent_limit:
                    # Remove oldest connection
                    recent_connections.pop()
                
                # Move to the new nail
                current_nail = best_nail
                low_score_count = 0
                
            else:
                # No good connection found
                low_score_count += 1
                
                # If we haven't found good connections for a while, try a random jump
                if low_score_count > 50:
                    current_nail = random.randint(0, self.num_nails - 1)
                    low_score_count = 0
                    recent_connections.clear()  # Clear recent connections after jump
                    logger.info(f"Random jump to nail {current_nail} at iteration {iteration}")
                
                # If we still can't find good connections, stop early
                if low_score_count > 100:
                    logger.info(f"Stopping early at iteration {iteration} - no good connections found")
                    break
        
        total_time = time.time() - start_time
        logger.info(f"Generated {len(self.paths)} string paths in {total_time:.1f}s")
        
        return {
            'nails': self.nails,
            'paths': self.paths,
            'message': f'String art pattern generated with {len(self.nails)} nails and {len(self.paths)} connections in {total_time:.1f}s. Uses improved greedy algorithm for better visual quality.'
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
        
        # Initialize improved string art generator
        generator = ImprovedStringArtGenerator(
            num_nails=300,   # Good balance of detail and performance
            max_lines=4000,  # Increased for better quality
            canvas_size=500
        )
        
        # Preprocess image
        processed_image = generator.preprocess_image(image)
        
        # Generate string art with improved algorithm
        result = generator.generate_string_art_greedy(processed_image)
        
        logger.info("String art generation completed successfully")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in string art generation: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Improved String Art Generator API is running'})

if __name__ == '__main__':
    logger.info("Starting Improved String Art Generator API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
