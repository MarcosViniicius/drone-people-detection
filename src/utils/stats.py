"""
Module for tracking and saving statistics
"""
import time
import os


class StatisticsTracker:
    """Processing statistics tracker"""
    
    def __init__(self):
        """Initialize the tracker"""
        self.frame_count = 0
        self.total_people_detected = 0
        self.max_people_in_frame = 0
        self.start_time = time.time()
        self.frame_stats = []
    
    def update(self, people_count):
        """
        Update statistics with new frame
        
        Args:
            people_count (int): Number of people in the frame
        """
        self.frame_count += 1
        self.total_people_detected += people_count
        self.max_people_in_frame = max(self.max_people_in_frame, people_count)
        
        # Store frame statistics
        self.frame_stats.append({
            "frame": self.frame_count,
            "people_count": people_count,
            "max_people": self.max_people_in_frame,
            "elapsed_time": time.time() - self.start_time
        })
    
    def get_elapsed_time(self):
        """Return elapsed time in seconds"""
        return time.time() - self.start_time
    
    def get_average_people(self):
        """Return average people per frame"""
        if self.frame_count == 0:
            return 0
        return self.total_people_detected / self.frame_count
    
    def get_processing_fps(self):
        """Return processing FPS"""
        elapsed = self.get_elapsed_time()
        if elapsed == 0:
            return 0
        return self.frame_count / elapsed
    
    def save(self, output_path, video_name, width, height):
        """
        Save statistics to file
        
        Args:
            output_path (str): Output file path
            video_name (str): Processed video name
            width (int): Video width
            height (int): Video height
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        processing_time = self.get_elapsed_time()
        avg_people = self.get_average_people()
        processing_fps = self.get_processing_fps()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("PEOPLE DETECTION STATISTICS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Processed video: {video_name}\n")
            f.write(f"Resolution: {width}x{height}\n")
            f.write(f"Total frames: {self.frame_count}\n\n")
            
            f.write(f"Total processing time: {processing_time:.2f}s\n")
            f.write(f"Processing FPS: {processing_fps:.2f}\n\n")
            
            f.write(f"Total people detected: {self.total_people_detected}\n")
            f.write(f"Maximum people in one frame: {self.max_people_in_frame}\n")
            f.write(f"Average people per frame: {avg_people:.2f}\n")
            f.write("=" * 60 + "\n")
        
        print(f"Statistics saved in: {output_path}")
    
    def print_summary(self):
        """Print statistics summary"""
        print(f"\nProcessing Summary:")
        print(f"  Processed frames: {self.frame_count}")
        print(f"  Total time: {self.get_elapsed_time():.2f}s")
        print(f"  Average FPS: {self.get_processing_fps():.2f}")
        print(f"  Total people: {self.total_people_detected}")
        print(f"  Maximum simultaneous: {self.max_people_in_frame}")
        print(f"  Average per frame: {self.get_average_people():.2f}")
