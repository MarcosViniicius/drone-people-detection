"""
Video processing module
"""
import cv2
import os
from ..core.detector import PeopleDetector
from ..utils.annotations import draw_detections
from ..utils.video_writer import VideoWriterManager
from ..utils.stats import StatisticsTracker


class VideoProcessor:
    """Video processor with people detection"""
    
    def __init__(self, config):
        """
        Initialize the video processor
        
        Args:
            config (dict): Project configurations
        """
        self.config = config
        self.detector = PeopleDetector(config["model"])
        self.video_input_directory = config["video_input_directory"]
        self.video_output_directory = config["video_output_directory"]
        self.video_extensions = config["video_extensions"]
        self.width = config["video_dimensions"]["width"]
        self.height = config["video_dimensions"]["height"]
        
        # Create output directories
        os.makedirs(os.path.join(self.video_output_directory, "videos"), exist_ok=True)
        os.makedirs(os.path.join(self.video_output_directory, "stats"), exist_ok=True)
    
    def get_video_files(self):
        """
        Search for all videos in the input folder
        
        Returns:
            list: List of video paths found
        """
        if not os.path.exists(self.video_input_directory):
            os.makedirs(self.video_input_directory, exist_ok=True)
            return []
        
        video_files = []
        for file in os.listdir(self.video_input_directory):
            if any(file.lower().endswith(ext) for ext in self.video_extensions):
                video_files.append(os.path.join(self.video_input_directory, file))
        
        return video_files
    
    def process_all(self):
        """Process all videos found in the input folder"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("No videos found in the input folder.")
            print(f"Place videos in: {self.video_input_directory}")
            return
        
        print(f"\n{len(video_files)} video(s) found.\n")
        
        processed_videos = []
        failed_videos = []
        
        for i, video_path in enumerate(video_files, 1):
            print(f"[{i}/{len(video_files)}] Processing: {os.path.basename(video_path)}")
            
            try:
                result = self.process_single(video_path)
                if result:
                    processed_videos.append(result)
            except Exception as e:
                print(f"Error processing {os.path.basename(video_path)}: {str(e)}")
                failed_videos.append(os.path.basename(video_path))
        
        # Final summary
        self._print_summary(processed_videos, failed_videos)
    
    def process_single(self, video_path):
        """
        Process a single video
        
        Args:
            video_path (str): Path to the video
            
        Returns:
            dict: Information about the processed video
        """
        # Abrir vídeo
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"Erro ao abrir vídeo: {os.path.basename(video_path)}")
            return None
        
        # Get properties
        fps = int(video.get(cv2.CAP_PROP_FPS))
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Generate output paths
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_video_path = os.path.join(
            self.video_output_directory, "videos", f"result_{video_name}_annotated.mp4"
        )
        output_stats_path = os.path.join(
            self.video_output_directory, "stats", f"stats_{video_name}.txt"
        )
        
        # Initialize managers
        writer = VideoWriterManager(output_video_path, fps, self.width, self.height)
        stats = StatisticsTracker()
        
        # Process frames
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            
            # Resize frame
            frame_resized = cv2.resize(frame, (self.width, self.height))
            
            # Detectar pessoas
            results = self.detector.detect(frame_resized)
            people_count = self.detector.count_people(results)
            
            # Update statistics
            stats.update(people_count)
            
            # Anotar frame
            annotated_frame = draw_detections(
                frame_resized, 
                results, 
                people_count,
                stats.max_people_in_frame,
                stats.get_elapsed_time()
            )
            
            # Write frame
            writer.write(annotated_frame)
            
            # Show progress
            if stats.frame_count % 100 == 0:
                progress = (stats.frame_count / total_frames) * 100
                print(f"  Progress: {progress:.1f}% ({stats.frame_count}/{total_frames} frames)")
        
        # Finalize
        video.release()
        writer.release()
        
        # Save statistics
        stats.save(output_stats_path, video_name, self.width, self.height)
        stats.print_summary()
        
        print(f"✓ Completed: {os.path.basename(video_path)}\n")
        
        return {
            "input_path": video_path,
            "output_video_path": output_video_path,
            "output_stats_path": output_stats_path,
            "stats": stats
        }
    
    def _print_summary(self, processed_videos, failed_videos):
        """
        Print processing summary
        
        Args:
            processed_videos (list): List of processed videos
            failed_videos (list): List of failed videos
        """
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        
        if processed_videos:
            print(f"\n✓ {len(processed_videos)} video(s) processed successfully:")
            for video_info in processed_videos:
                print(f"  - {os.path.basename(video_info['input_path'])}")
        
        if failed_videos:
            print(f"\n✗ {len(failed_videos)} video(s) failed:")
            for video_name in failed_videos:
                print(f"  - {video_name}")
        
        if not processed_videos and not failed_videos:
            print("\nNo videos processed.")
        
        print("\n" + "=" * 60)
