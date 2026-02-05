"""
Stream processing module for live video feeds
"""
import cv2
import os
import time
from datetime import datetime
from ..core.detector import PeopleDetector
from ..utils.annotations import draw_detections
from ..utils.video_writer import VideoWriterManager
from ..utils.stats import StatisticsTracker


class StreamProcessor:
    """Stream processor with people detection for live video feeds"""
    
    def __init__(self, config):
        """
        Initialize the stream processor
        
        Args:
            config (dict): Project configurations
        """
        self.config = config
        self.detector = PeopleDetector(config["model"])
        
        # Stream configurations
        self.stream_config = config.get("stream", {})
        self.local_rtmp_url = self.stream_config.get("local_rtmp_url", "rtmp://localhost:1935/live")
        self.local_hls_url = self.stream_config.get("local_hls_url", "http://localhost:8081/live/.m3u8")
        self.hls_stream_directory = self.stream_config.get("hls_stream_directory", "./nginx-rtmp-stream/stream")
        self.output_directory = self.stream_config.get("output_directory", "./data/output/videos/lives")
        self.recording_directory = self.stream_config.get("recording_directory", "./data/output/videos/live_recordings")
        self.stats_directory = self.stream_config.get("stats_directory", "./data/output/videos/stats")
        
        # Stream dimensions
        stream_dims = self.stream_config.get("dimensions", {"width": 1280, "height": 720})
        self.width = stream_dims["width"]
        self.height = stream_dims["height"]
        
        # Create output directories
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(self.recording_directory, exist_ok=True)
        os.makedirs(self.stats_directory, exist_ok=True)
        
        # Control flags
        self.is_processing = False
        self.should_record = False
    
    def select_stream_source(self):
        """
        Ask user to select stream source (internal or external)
        
        Returns:
            str: Stream URL or None if cancelled
        """
        print("\n" + "=" * 60)
        print("STREAM SOURCE SELECTION")
        print("=" * 60)
        print("\n1. Internal stream (Local RTMP/HLS server)")
        print("2. External stream (Custom URL)")
        print("3. Cancel")
        
        while True:
            choice = input("\nChoose an option (1-3): ").strip()
            
            if choice == '1':
                return self._select_internal_stream()
            elif choice == '2':
                return self._select_external_stream()
            elif choice == '3':
                return None
            else:
                print("Invalid option. Please choose 1, 2, or 3.")
    
    def _check_hls_stream_active(self):
        """
        Check if HLS stream files exist (indicates active transmission)
        
        Returns:
            bool: True if HLS files found, False otherwise
        """
        hls_file_path = os.path.join(self.hls_stream_directory, "index.m3u8")
        return os.path.exists(hls_file_path)
    
    def _select_internal_stream(self):
        """
        Select internal stream protocol
        
        Returns:
            str: Stream URL
        """
        print("\nInternal stream options:")
        print("1. RTMP (rtmp://localhost:1935/live)")
        print("2. HLS (http://localhost:8081/live/index.m3u8)")
        print(f"\nNote: HLS streams are generated in: {self.hls_stream_directory}")
        
        # Check if HLS stream is active
        if not self._check_hls_stream_active():
            print("\n⚠ Warning: No active HLS stream detected!")
            print("  Make sure you are transmitting to the RTMP server first.")
            print("  Steps:")
            print("    1. Start nginx server: cd nginx-rtmp-stream && docker compose up -d")
            print("    2. Start transmitting (OBS/ffmpeg) to: rtmp://localhost:1935/live")
            print("    3. Wait a few seconds for HLS files to be generated")
            print("    4. Then try processing the stream")
        
        while True:
            choice = input("\nChoose protocol (1-2): ").strip()
            
            if choice == '1':
                return self.local_rtmp_url
            elif choice == '2':
                return self.local_hls_url
            else:
                print("Invalid option. Please choose 1 or 2.")
    
    def _select_external_stream(self):
        """
        Get external stream URL from user
        
        Returns:
            str: Stream URL
        """
        print("\nEnter the external stream URL:")
        print("Examples:")
        print("  - RTMP: rtmp://example.com/live/stream")
        print("  - HLS: http://example.com/stream.m3u8")
        print("  - HTTP: http://example.com/video.mp4")
        
        url = input("\nStream URL: ").strip()
        
        if not url:
            print("⚠ Empty URL. Returning to menu.")
            return None
        
        return url
    
    def process_stream(self, stream_url, record=True, show_preview=False):
        """
        Process a live stream
        
        Args:
            stream_url (str): URL of the stream to process
            record (bool): Whether to save the processed stream (default: True)
            show_preview (bool): Whether to show live preview window (default: False)
            
        Returns:
            dict: Information about the processed stream
        """
        print(f"\n{'=' * 60}")
        print(f"STARTING STREAM PROCESSING")
        print(f"{'=' * 60}")
        print(f"Stream URL: {stream_url}")
        print(f"Recording: {'Yes' if record else 'No'}")
        print(f"Preview: {'Yes' if show_preview else 'No'}")
        print(f"{'=' * 60}")
        
        # Special message for HLS
        if ".m3u8" in stream_url and "localhost" in stream_url:
            print("\n💡 Tip: Make sure you're streaming to RTMP before processing HLS")
        
        print()
        
        # Open video stream
        stream = cv2.VideoCapture(stream_url)
        
        if not stream.isOpened():
            print(f"✗ Error: Unable to open stream: {stream_url}")
            print("\n  Common causes:")
            
            # Check if it's HLS stream
            if "localhost:8081" in stream_url or ".m3u8" in stream_url:
                print("\n  For HLS streams:")
                print("  1. Check if nginx-rtmp server is running:")
                print("     → cd nginx-rtmp-stream && docker compose ps")
                print("  2. Verify you are transmitting to RTMP first:")
                print("     → Use OBS/ffmpeg to stream to: rtmp://localhost:1935/live")
                print("  3. Check if HLS files are being generated:")
                print(f"     → Look for files in: {self.hls_stream_directory}/")
                print("  4. Wait 5-10 seconds after starting transmission")
                print("     → HLS needs time to generate initial segments")
            
            # Check if it's RTMP stream
            elif "rtmp://" in stream_url:
                print("\n  For RTMP streams:")
                print("  1. Check if nginx-rtmp server is running")
                print("  2. Verify you are transmitting to the server")
                print("  3. RTMP can be processed in real-time (no need to wait)")
            
            # External stream
            else:
                print("\n  For external streams:")
                print("  - Verify the URL is correct and accessible")
                print("  - Test the URL in VLC or another media player first")
                print("  - Check your internet connection")
                print("  - Some streams may have geographic restrictions")
            
            return None
        
        print("✓ Stream opened successfully")
        
        # Get stream properties
        fps = int(stream.get(cv2.CAP_PROP_FPS))
        if fps == 0:
            fps = 30  # Default FPS if unable to detect
            print(f"⚠ Warning: Unable to detect FPS. Using default: {fps}")
        
        # Generate output paths
        writer = None
        stats = StatisticsTracker()
        output_video_path = None
        output_stats_path = None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_video_path = os.path.join(
            self.recording_directory, f"stream_recording_{timestamp}.mp4"
        )
        output_stats_path = os.path.join(
            self.stats_directory, f"stats_stream_{timestamp}.txt"
        )
        
        if record:
            writer = VideoWriterManager(output_video_path, fps, self.width, self.height)
            print(f"✓ Recording to: {output_video_path}")
        
        # Control flags
        self.is_processing = True
        frame_count = 0
        
        print("\n" + "=" * 60)
        print("PROCESSING LIVE STREAM")
        print("=" * 60)
        if show_preview:
            print("Press 'q' to stop processing")
            print("Press 's' to toggle statistics display")
            print("Press 'p' to toggle preview window")
        else:
            print("Preview disabled - Processing in background")
            print("Press Ctrl+C to stop processing")
        print("=" * 60 + "\n")
        
        show_stats = True
        preview_enabled = show_preview
        
        try:
            while self.is_processing:
                ret, frame = stream.read()
                
                if not ret:
                    print("\n⚠ Warning: Unable to read frame from stream")
                    print("  Stream may have ended or connection lost")
                    break
                
                frame_count += 1
                
                # Resize frame
                frame_resized = cv2.resize(frame, (self.width, self.height))
                
                # Detect people
                results = self.detector.detect(frame_resized)
                people_count = self.detector.count_people(results)
                
                # Update statistics
                stats.update(people_count)
                
                # Annotate frame
                annotated_frame = draw_detections(
                    frame_resized, 
                    results, 
                    people_count,
                    stats.max_people_in_frame,
                    stats.get_elapsed_time()
                )
                
                # Write frame if recording
                if record and writer:
                    writer.write(annotated_frame)
                
                # Display frame if preview is enabled
                if preview_enabled:
                    cv2.imshow('Live Stream Processing - Press Q to quit, P to hide', annotated_frame)
                
                # Show statistics every 30 frames
                if show_stats and frame_count % 30 == 0:
                    print(f"Frames: {frame_count} | "
                          f"People: {people_count} | "
                          f"Max: {stats.max_people_in_frame} | "
                          f"Avg: {stats.get_average_people():.2f} | "
                          f"FPS: {stats.get_processing_fps():.2f}")
                
                # Handle keyboard input (only if preview is enabled)
                if preview_enabled:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == ord('Q'):
                        print("\n✓ Processing stopped by user")
                        break
                    elif key == ord('s') or key == ord('S'):
                        show_stats = not show_stats
                        status = "enabled" if show_stats else "disabled"
                        print(f"\nStatistics display {status}")
                    elif key == ord('p') or key == ord('P'):
                        preview_enabled = not preview_enabled
                        if not preview_enabled:
                            cv2.destroyAllWindows()
                            print("\n✓ Preview window hidden")
                        else:
                            print("\n✓ Preview window shown")
                else:
                    # Small delay to prevent CPU overload when no preview
                    time.sleep(0.001)
        
        except KeyboardInterrupt:
            print("\n\n✓ Processing interrupted by user (Ctrl+C)")
        
        except Exception as e:
            print(f"\n✗ Error during processing: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            self.is_processing = False
            stream.release()
            cv2.destroyAllWindows()
            
            if writer:
                writer.release()
                print(f"\n✓ Recording saved to: {output_video_path}")
            
            # Save statistics
            if output_stats_path:
                stats.save(output_stats_path, f"stream_{timestamp}", self.width, self.height)
                print(f"✓ Statistics saved to: {output_stats_path}")
            
            # Print final summary
            print("\n" + "=" * 60)
            print("STREAM PROCESSING SUMMARY")
            print("=" * 60)
            stats.print_summary()
            print("=" * 60 + "\n")
        
        return {
            "frame_count": frame_count,
            "stats": stats,
            "recorded": record,
            "output_path": output_video_path if record else None
        }
    
    def start_processing(self):
        """
        Start stream processing with user interaction
        """
        # Select stream source
        stream_url = self.select_stream_source()
        
        if not stream_url:
            print("\n✓ Stream processing cancelled")
            return
        
        # Ask if user wants to record
        print("\n" + "=" * 60)
        record_choice = input("Do you want to record the processed stream? (y/n) [default: y]: ").strip().lower()
        record = record_choice in ['y', 'yes', 's', 'sim', '']  # Empty = yes
        
        # Ask if user wants preview window
        preview_choice = input("Do you want to show live preview window? (y/n) [default: n]: ").strip().lower()
        show_preview = preview_choice in ['y', 'yes', 's', 'sim']
        
        # Process stream
        result = self.process_stream(stream_url, record, show_preview)
        
        if result:
            print("\n✓ Stream processing completed successfully")
            if result.get("output_path"):
                print(f"✓ Output saved to: {result['output_path']}")
        else:
            print("\n✗ Stream processing failed")
