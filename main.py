"""
People Detection System using YOLO
Main application entry point
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config_loader import load_config, validate_config
from src.processors.video_processor import VideoProcessor
from src.processors.image_processor import ImageProcessor
from src.processors.stream_processor import StreamProcessor


def print_header():
    """Print application header"""
    print("=" * 60)
    print("PEOPLE DETECTION SYSTEM - YOLO")
    print("=" * 60)
    print()


def display_menu():
    """Display menu options for the user and return the choice"""
    print("Currently, only people detection is configured. To process other things, modify config.json.")
    print("\nMenu Options:")
    print("1. Start Livestream processing")
    print("2. Start video processing | configure detection type in config.json")
    print("3. Start image processing | configure detection type in config.json")
    print("4. Exit")
    
    while True:
        choice = input("\nChoose an option (1-4): ").strip()
        if choice in ('1', '2', '3', '4'):
            return choice
        print("Invalid option. Please choose a valid option (1-4).")


def process_livestream(processor):
    """Livestream processing"""
    print("\nStarting Livestream processing...")
    processor.start_processing()


def process_videos(processor):
    """Video processing"""
    print("\nStarting video processing...")
    processor.process_all()


def process_images(processor):
    """Image processing"""
    print("\nStarting image processing...")
    # Implement image specific logic
    processor.process_all()


def main():
    """Main application function"""
    print_header()
    
    try:
        # Load configurations
        print("Loading configurations...")
        config = load_config("./configs/config.json")
        validate_config(config)
        print("✓ Configurations loaded successfully\n")
        
        # Create processors
        video_processor = VideoProcessor(config)
        image_processor = ImageProcessor(config)
        stream_processor = StreamProcessor(config)
        
        # Main menu loop
        while True:
            choice = display_menu()
            
            if choice == '1':
                process_livestream(stream_processor)
            elif choice == '2':
                process_videos(video_processor)
            elif choice == '3':
                process_images(image_processor)
            else:  # Option 4 (Exit)
                print("\nExiting application...")
                break
                
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("Make sure the config.json file exists.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()