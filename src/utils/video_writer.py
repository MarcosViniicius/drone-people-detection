"""
Module to manage video writing
"""
import cv2
import threading
import queue


class VideoWriterManager:
    """Video writing manager with threading"""
    
    def __init__(self, output_path, fps, width, height, codec="mp4v"):
        """
        Initialize the video writing manager
        
        Args:
            output_path (str): Output file path
            fps (int): Frames per second
            width (int): Video width
            height (int): Video height
            codec (str): Video codec
        """
        self.output_path = output_path
        self.fps = fps
        self.width = width
        self.height = height
        
        # Create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not self.out.isOpened():
            raise RuntimeError(f"Error creating output video: {output_path}")
        
        # Configure queue and writing thread
        self.write_queue = queue.Queue(maxsize=30)
        self.writer_thread = threading.Thread(target=self._writer_worker)
        self.writer_thread.start()
        self.is_writing = True
    
    def _writer_worker(self):
        """Worker thread to write frames"""
        while True:
            item = self.write_queue.get()
            
            if item is None:  # Stop signal
                break
            
            self.out.write(item)
            self.write_queue.task_done()
    
    def write(self, frame):
        """
        Add frame to writing queue
        
        Args:
            frame: Frame to be written
        """
        if self.is_writing:
            self.write_queue.put(frame)
    
    def release(self):
        """Finalize writing and release resources"""
        # Signal end to thread
        self.write_queue.put(None)
        
        # Wait for thread to finish
        self.writer_thread.join()
        
        # Release VideoWriter
        self.out.release()
        self.is_writing = False
