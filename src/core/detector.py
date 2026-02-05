"""
People detection module using YOLO
"""
from ultralytics import YOLO


class PeopleDetector:
    """Class responsible for people detection using YOLO"""
    
    def __init__(self, model_config):
        """
        Initialize YOLO detector
        
        Args:
            model_config (dict): Model configurations
        """
        self.model = YOLO(model_config["weights"])
        self.conf = model_config.get("conf", 0.25)
        self.iou = model_config.get("iou", 0.7)
        self.classes = model_config.get("classes", [0])  # 0 = person
        self.verbose = model_config.get("verbose", False)
    
    def detect(self, frame):
        """
        Detect people in a frame
        
        Args:
            frame: Video frame (numpy array)
            
        Returns:
            YOLO detection result
        """
        results = self.model(
            frame,
            conf=self.conf,
            iou=self.iou,
            classes=self.classes,
            verbose=self.verbose
        )
        return results[0]
    
    def count_people(self, results):
        """
        Count the number of detected people
        
        Args:
            results: YOLO detection result
            
        Returns:
            int: Number of detected people
        """
        return len(results.boxes)
