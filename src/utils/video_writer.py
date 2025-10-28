"""
Módulo para gerenciar escrita de vídeos
"""
import cv2
import threading
import queue


class VideoWriterManager:
    """Gerenciador de escrita de vídeos com threading"""
    
    def __init__(self, output_path, fps, width, height, codec="mp4v"):
        """
        Inicializa o gerenciador de escrita de vídeo
        
        Args:
            output_path (str): Caminho do arquivo de saída
            fps (int): Frames por segundo
            width (int): Largura do vídeo
            height (int): Altura do vídeo
            codec (str): Codec do vídeo
        """
        self.output_path = output_path
        self.fps = fps
        self.width = width
        self.height = height
        
        # Criar VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not self.out.isOpened():
            raise RuntimeError(f"Erro ao criar vídeo de saída: {output_path}")
        
        # Configurar fila e thread de escrita
        self.write_queue = queue.Queue(maxsize=30)
        self.writer_thread = threading.Thread(target=self._writer_worker)
        self.writer_thread.start()
        self.is_writing = True
    
    def _writer_worker(self):
        """Worker thread para escrever frames"""
        while True:
            item = self.write_queue.get()
            
            if item is None:  # Sinal de parada
                break
            
            self.out.write(item)
            self.write_queue.task_done()
    
    def write(self, frame):
        """
        Adiciona frame à fila de escrita
        
        Args:
            frame: Frame a ser escrito
        """
        if self.is_writing:
            self.write_queue.put(frame)
    
    def release(self):
        """Finaliza a escrita e libera recursos"""
        # Sinalizar fim para thread
        self.write_queue.put(None)
        
        # Esperar thread terminar
        self.writer_thread.join()
        
        # Liberar VideoWriter
        self.out.release()
        self.is_writing = False
