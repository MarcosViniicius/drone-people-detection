"""
Módulo de detecção de pessoas usando YOLO
"""
from ultralytics import YOLO


class PeopleDetector:
    """Classe responsável pela detecção de pessoas usando YOLO"""
    
    def __init__(self, model_config):
        """
        Inicializa o detector YOLO
        
        Args:
            model_config (dict): Configurações do modelo
        """
        self.model = YOLO(model_config["weights"])
        self.conf = model_config.get("conf", 0.25)
        self.iou = model_config.get("iou", 0.7)
        self.classes = model_config.get("classes", [0])  # 0 = pessoa
        self.verbose = model_config.get("verbose", False)
    
    def detect(self, frame):
        """
        Detecta pessoas em um frame
        
        Args:
            frame: Frame de vídeo (numpy array)
            
        Returns:
            Resultado da detecção YOLO
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
        Conta o número de pessoas detectadas
        
        Args:
            results: Resultado da detecção YOLO
            
        Returns:
            int: Número de pessoas detectadas
        """
        return len(results.boxes)
