"""
Image processing module
"""
import cv2
import os
from ..core.detector import PeopleDetector
from ..utils.annotations import draw_detections
from ..utils.stats import StatisticsTracker


class ImageProcessor:
    """Image processor with people detection"""
    
    def __init__(self, config):
        """
        Initialize the image processor
        
        Args:
            config (dict): Project configurations
        """
        self.config = config
        self.detector = PeopleDetector(config["model"])
        self.image_input_directory = config["image_input_directory"]
        self.image_output_directory = config["image_output_directory"]
        self.image_extensions = config["image_extensions"]
        self.width = config["image_dimensions"]["width"]
        self.height = config["image_dimensions"]["height"]
        
        # Create output directories
        os.makedirs(os.path.join(self.image_output_directory, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.image_output_directory, "stats"), exist_ok=True)
    
    def get_image_files(self):
        """
        Search for all images in the input folder
        
        Returns:
            list: List of image paths found
        """
        if not os.path.exists(self.image_input_directory):
            os.makedirs(self.image_input_directory, exist_ok=True)
            return []
        
        image_files = []
        for file in os.listdir(self.image_input_directory):
            if any(file.lower().endswith(ext) for ext in self.image_extensions):
                image_files.append(os.path.join(self.image_input_directory, file))
        
        return image_files
    
    def process_all(self):
        """Process all images found in the input folder"""
        image_files = self.get_image_files()
        
        if not image_files:
            print("No images found in the input folder.")
            print(f"Place images in: {self.image_input_directory}")
            return
        
        print(f"\n{len(image_files)} image(s) found.\n")
        
        processed_images = []
        failed_images = []
        
        for i, image_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] Processing: {os.path.basename(image_path)}")
            
            try:
                result = self.process_single(image_path)
                if result:
                    processed_images.append(result)
            except Exception as e:
                print(f"Error processing {os.path.basename(image_path)}: {str(e)}")
                failed_images.append(os.path.basename(image_path))
        
        # Final summary
        self._print_summary(processed_images, failed_images)
    
    def process_single(self, image_path):
        """
        Process a single image
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            dict: Information about the processed image
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error opening image: {os.path.basename(image_path)}")
            return None
        
        # Resize image
        image_resized = cv2.resize(image, (self.width, self.height))
        
        # Detect people
        results = self.detector.detect(image_resized)
        people_count = self.detector.count_people(results)
        
        # Initialize statistics
        stats = StatisticsTracker()
        stats.update(people_count)
        
        # Annotate image
        annotated_image = draw_detections(
            image_resized, 
            results, 
            people_count,
            stats.max_people_in_frame,
            stats.get_elapsed_time()
        )
        
        # Generate output paths
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        output_image_path = os.path.join(
            self.image_output_directory, "images", f"result_{image_name}_annotated.jpg"
        )
        output_stats_path = os.path.join(
            self.image_output_directory, "stats", f"stats_{image_name}.txt"
        )
        
        # Save processed image
        cv2.imwrite(output_image_path, annotated_image)
        
        # Save statistics
        stats.save(output_stats_path, image_name, self.width, self.height)
        stats.print_summary()
        
        print(f"✓ Completed: {os.path.basename(image_path)}\n")
        
        return {
            "input_path": image_path,
            "output_image_path": output_image_path,
            "output_stats_path": output_stats_path,
            "stats": stats
        }
    
    def _print_summary(self, processed_images, failed_images):
        """
        Print processing summary
        
        Args:
            processed_images (list): List of processed images
            failed_images (list): List of failed images
        """
        print("\n" + "=" * 60)
        print("IMAGE PROCESSING SUMMARY")
        print("=" * 60)
        
        if processed_images:
            print(f"\n✓ {len(processed_images)} image(s) processed successfully:")
            for image_info in processed_images:
                print(f"  - {os.path.basename(image_info['input_path'])}")
        
        if failed_images:
            print(f"\n✗ {len(failed_images)} image(s) failed:")
            for image_name in failed_images:
                print(f"  - {image_name}")
        
        if not processed_images and not failed_images:
            print("\nNo images processed.")
        
        print("\n" + "=" * 60)