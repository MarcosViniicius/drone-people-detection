"""
Módulo para processamento de vídeos
"""
import cv2
import os
from ..core.detector import PeopleDetector
from ..utils.annotations import draw_detections
from ..utils.video_writer import VideoWriterManager
from ..utils.stats import StatisticsTracker


class VideoProcessor:
    """Processador de vídeos com detecção de pessoas"""
    
    def __init__(self, config):
        """
        Inicializa o processador de vídeos
        
        Args:
            config (dict): Configurações do projeto
        """
        self.config = config
        self.detector = PeopleDetector(config["model"])
        self.video_input_directory = config["video_input_directory"]
        self.video_output_directory = config["video_output_directory"]
        self.video_extensions = config["video_extensions"]
        self.width = config["video_dimensions"]["width"]
        self.height = config["video_dimensions"]["height"]
        
        # Criar diretórios de saída
        os.makedirs(os.path.join(self.video_output_directory, "videos"), exist_ok=True)
        os.makedirs(os.path.join(self.video_output_directory, "stats"), exist_ok=True)
    
    def get_video_files(self):
        """
        Busca todos os vídeos na pasta de entrada
        
        Returns:
            list: Lista de caminhos de vídeos encontrados
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
        """Processa todos os vídeos encontrados na pasta de entrada"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("Nenhum vídeo encontrado na pasta de entrada.")
            print(f"Coloque vídeos em: {self.video_input_directory}")
            return
        
        print(f"\n{len(video_files)} vídeo(s) encontrado(s).\n")
        
        processed_videos = []
        failed_videos = []
        
        for i, video_path in enumerate(video_files, 1):
            print(f"[{i}/{len(video_files)}] Processando: {os.path.basename(video_path)}")
            
            try:
                result = self.process_single(video_path)
                if result:
                    processed_videos.append(result)
            except Exception as e:
                print(f"Erro ao processar {os.path.basename(video_path)}: {str(e)}")
                failed_videos.append(os.path.basename(video_path))
        
        # Resumo final
        self._print_summary(processed_videos, failed_videos)
    
    def process_single(self, video_path):
        """
        Processa um único vídeo
        
        Args:
            video_path (str): Caminho do vídeo
            
        Returns:
            dict: Informações sobre o vídeo processado
        """
        # Abrir vídeo
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            print(f"Erro ao abrir vídeo: {os.path.basename(video_path)}")
            return None
        
        # Obter propriedades
        fps = int(video.get(cv2.CAP_PROP_FPS))
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Gerar caminhos de saída
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_video_path = os.path.join(
            self.video_output_directory, "videos", f"result_{video_name}_annotated.mp4"
        )
        output_stats_path = os.path.join(
            self.video_output_directory, "stats", f"stats_{video_name}.txt"
        )
        
        # Inicializar gerenciadores
        writer = VideoWriterManager(output_video_path, fps, self.width, self.height)
        stats = StatisticsTracker()
        
        # Processar frames
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            
            # Redimensionar frame
            frame_resized = cv2.resize(frame, (self.width, self.height))
            
            # Detectar pessoas
            results = self.detector.detect(frame_resized)
            people_count = self.detector.count_people(results)
            
            # Atualizar estatísticas
            stats.update(people_count)
            
            # Anotar frame
            annotated_frame = draw_detections(
                frame_resized, 
                results, 
                people_count,
                stats.max_people_in_frame,
                stats.get_elapsed_time()
            )
            
            # Escrever frame
            writer.write(annotated_frame)
            
            # Mostrar progresso
            if stats.frame_count % 100 == 0:
                progress = (stats.frame_count / total_frames) * 100
                print(f"  Progresso: {progress:.1f}% ({stats.frame_count}/{total_frames} frames)")
        
        # Finalizar
        video.release()
        writer.release()
        
        # Salvar estatísticas
        stats.save(output_stats_path, video_name, self.width, self.height)
        stats.print_summary()
        
        print(f"✓ Concluído: {os.path.basename(video_path)}\n")
        
        return {
            "input_path": video_path,
            "output_video_path": output_video_path,
            "output_stats_path": output_stats_path,
            "stats": stats
        }
    
    def _print_summary(self, processed_videos, failed_videos):
        """
        Imprime resumo do processamento
        
        Args:
            processed_videos (list): Lista de vídeos processados
            failed_videos (list): Lista de vídeos que falharam
        """
        print("\n" + "=" * 60)
        print("RESUMO DO PROCESSAMENTO")
        print("=" * 60)
        
        if processed_videos:
            print(f"\n✓ {len(processed_videos)} vídeo(s) processado(s) com sucesso:")
            for video_info in processed_videos:
                print(f"  - {os.path.basename(video_info['input_path'])}")
        
        if failed_videos:
            print(f"\n✗ {len(failed_videos)} vídeo(s) falharam:")
            for video_name in failed_videos:
                print(f"  - {video_name}")
        
        if not processed_videos and not failed_videos:
            print("\nNenhum vídeo processado.")
        
        print("\n" + "=" * 60)
