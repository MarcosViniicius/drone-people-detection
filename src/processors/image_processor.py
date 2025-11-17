"""
Módulo para processamento de imagens
"""
import cv2
import os
from ..core.detector import PeopleDetector
from ..utils.annotations import draw_detections
from ..utils.stats import StatisticsTracker


class ImageProcessor:
    """Processador de imagens com detecção de pessoas"""
    
    def __init__(self, config):
        """
        Inicializa o processador de imagens
        
        Args:
            config (dict): Configurações do projeto
        """
        self.config = config
        self.detector = PeopleDetector(config["model"])
        self.image_input_directory = config["image_input_directory"]
        self.image_output_directory = config["image_output_directory"]
        self.image_extensions = config["image_extensions"]
        self.width = config["image_dimensions"]["width"]
        self.height = config["image_dimensions"]["height"]
        
        # Criar diretório de saída
        os.makedirs(os.path.join(self.image_output_directory, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.image_output_directory, "stats"), exist_ok=True)
    
    def get_image_files(self):
        """
        Busca todas as imagens na pasta de entrada
        
        Returns:
            list: Lista de caminhos de imagens encontradas
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
        """Processa todas as imagens encontradas na pasta de entrada"""
        image_files = self.get_image_files()
        
        if not image_files:
            print("Nenhuma imagem encontrada na pasta de entrada.")
            print(f"Coloque imagens em: {self.image_input_directory}")
            return
        
        print(f"\n{len(image_files)} imagem(ns) encontrada(s).\n")
        
        processed_images = []
        failed_images = []
        
        for i, image_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] Processando: {os.path.basename(image_path)}")
            
            try:
                result = self.process_single(image_path)
                if result:
                    processed_images.append(result)
            except Exception as e:
                print(f"Erro ao processar {os.path.basename(image_path)}: {str(e)}")
                failed_images.append(os.path.basename(image_path))
        
        # Resumo final
        self._print_summary(processed_images, failed_images)
    
    def process_single(self, image_path):
        """
        Processa uma única imagem
        
        Args:
            image_path (str): Caminho da imagem
            
        Returns:
            dict: Informações sobre a imagem processada
        """
        # Carregar imagem
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erro ao abrir imagem: {os.path.basename(image_path)}")
            return None
        
        # Redimensionar imagem
        image_resized = cv2.resize(image, (self.width, self.height))
        
        # Detectar pessoas
        results = self.detector.detect(image_resized)
        people_count = self.detector.count_people(results)
        
        # Inicializar estatísticas
        stats = StatisticsTracker()
        stats.update(people_count)
        
        # Anotar imagem
        annotated_image = draw_detections(
            image_resized, 
            results, 
            people_count,
            stats.max_people_in_frame,
            stats.get_elapsed_time()
        )
        
        # Gerar caminhos de saída
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        output_image_path = os.path.join(
            self.image_output_directory, "images", f"result_{image_name}_annotated.jpg"
        )
        output_stats_path = os.path.join(
            self.image_output_directory, "stats", f"stats_{image_name}.txt"
        )
        
        # Salvar imagem processada
        cv2.imwrite(output_image_path, annotated_image)
        
        # Salvar estatísticas
        stats.save(output_stats_path, image_name, self.width, self.height)
        stats.print_summary()
        
        print(f"✓ Concluído: {os.path.basename(image_path)}\n")
        
        return {
            "input_path": image_path,
            "output_image_path": output_image_path,
            "output_stats_path": output_stats_path,
            "stats": stats
        }
    
    def _print_summary(self, processed_images, failed_images):
        """
        Imprime resumo do processamento
        
        Args:
            processed_images (list): Lista de imagens processadas
            failed_images (list): Lista de imagens que falharam
        """
        print("\n" + "=" * 60)
        print("RESUMO DO PROCESSAMENTO DE IMAGENS")
        print("=" * 60)
        
        if processed_images:
            print(f"\n✓ {len(processed_images)} imagem(ns) processada(s) com sucesso:")
            for image_info in processed_images:
                print(f"  - {os.path.basename(image_info['input_path'])}")
        
        if failed_images:
            print(f"\n✗ {len(failed_images)} imagem(ns) falharam:")
            for image_name in failed_images:
                print(f"  - {image_name}")
        
        if not processed_images and not failed_images:
            print("\nNenhuma imagem processada.")
        
        print("\n" + "=" * 60)