"""
Módulo para rastreamento e salvamento de estatísticas
"""
import time
import os


class StatisticsTracker:
    """Rastreador de estatísticas de processamento"""
    
    def __init__(self):
        """Inicializa o rastreador"""
        self.frame_count = 0
        self.total_people_detected = 0
        self.max_people_in_frame = 0
        self.start_time = time.time()
        self.frame_stats = []
    
    def update(self, people_count):
        """
        Atualiza estatísticas com novo frame
        
        Args:
            people_count (int): Número de pessoas no frame
        """
        self.frame_count += 1
        self.total_people_detected += people_count
        self.max_people_in_frame = max(self.max_people_in_frame, people_count)
        
        # Armazenar estatísticas do frame
        self.frame_stats.append({
            "frame": self.frame_count,
            "people_count": people_count,
            "max_people": self.max_people_in_frame,
            "elapsed_time": time.time() - self.start_time
        })
    
    def get_elapsed_time(self):
        """Retorna tempo decorrido em segundos"""
        return time.time() - self.start_time
    
    def get_average_people(self):
        """Retorna média de pessoas por frame"""
        if self.frame_count == 0:
            return 0
        return self.total_people_detected / self.frame_count
    
    def get_processing_fps(self):
        """Retorna FPS de processamento"""
        elapsed = self.get_elapsed_time()
        if elapsed == 0:
            return 0
        return self.frame_count / elapsed
    
    def save(self, output_path, video_name, width, height):
        """
        Salva estatísticas em arquivo
        
        Args:
            output_path (str): Caminho do arquivo de saída
            video_name (str): Nome do vídeo processado
            width (int): Largura do vídeo
            height (int): Altura do vídeo
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        processing_time = self.get_elapsed_time()
        avg_people = self.get_average_people()
        processing_fps = self.get_processing_fps()
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("ESTATÍSTICAS DE DETECÇÃO DE PESSOAS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Vídeo processado: {video_name}\n")
            f.write(f"Resolução: {width}x{height}\n")
            f.write(f"Total de frames: {self.frame_count}\n\n")
            
            f.write(f"Tempo total de processamento: {processing_time:.2f}s\n")
            f.write(f"FPS de processamento: {processing_fps:.2f}\n\n")
            
            f.write(f"Total de pessoas detectadas: {self.total_people_detected}\n")
            f.write(f"Máximo de pessoas em um frame: {self.max_people_in_frame}\n")
            f.write(f"Média de pessoas por frame: {avg_people:.2f}\n")
            f.write("=" * 60 + "\n")
        
        print(f"Estatísticas salvas em: {output_path}")
    
    def print_summary(self):
        """Imprime resumo das estatísticas"""
        print(f"\nResumo do Processamento:")
        print(f"  Frames processados: {self.frame_count}")
        print(f"  Tempo total: {self.get_elapsed_time():.2f}s")
        print(f"  FPS médio: {self.get_processing_fps():.2f}")
        print(f"  Total de pessoas: {self.total_people_detected}")
        print(f"  Máximo simultâneo: {self.max_people_in_frame}")
        print(f"  Média por frame: {self.get_average_people():.2f}")
