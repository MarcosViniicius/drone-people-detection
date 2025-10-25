import cv2
import os
from ultralytics import YOLO
import threading
import queue
import time


def setup():
    """Configuração inicial do modelo e variáveis"""
    model = YOLO(
        "yolo11m.pt"
    )  # n, s, m, l, x, a partir do 11, tira o v e deixa somente yoloxx.pt

    # Diretórios
    input_directory = "./assets/input/videos"
    output_directory = "./assets/output/videos"

    # Criar pastas se não existirem
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)

    # Buscar todos os vídeos na pasta de input
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"]
    video_files = []

    if os.path.exists(input_directory):
        for file in os.listdir(input_directory):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(input_directory, file))

    if not video_files:
        print("Nenhum vídeo encontrado na pasta de entrada.")
        return None

    print(f"{len(video_files)} vídeo(s) encontrado(s).")
    return {
        "model": model,
        "input_directory": input_directory,
        "output_directory": output_directory,
        "video_files": video_files,
    }


def thread_process(target_func, args=(), kwargs=None):
    """Executa função em thread e retorna resultado"""
    if kwargs is None:
        kwargs = {}

    # Container para armazenar resultado
    result_container = {"result": None, "error": None}

    def wrapper():
        try:
            result = target_func(*args, **kwargs)
            result_container["result"] = result
        except Exception as e:
            result_container["error"] = e

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join()

    # Verificar se houve erro
    if result_container["error"]:
        raise result_container["error"]

    return result_container["result"]


def detect_people(model, frame):
    """Detecta pessoas em um frame usando YOLO"""
    results = model(
        frame,
        conf=0.3,
        iou=0.45,
        classes=[0],  # 0 = pessoa
        verbose=False,
    )
    return results[0]


def writer_thread_func(out, write_queue):
    """Thread dedicada para escrever frames"""
    while True:
        item = write_queue.get()

        if item is None:  # Sinal de parada
            break

        out.write(item)
        write_queue.task_done()


def processVideo(config, video_path):
    """Processa um único vídeo detectando e contando pessoas com threading"""
    model = config["model"]
    output_directory = config["output_directory"]

    # Gerar nome do arquivo de saída baseado no nome do vídeo de input
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_filename = f"result_{video_name}_annotated.mp4"
    output_path = os.path.join(output_directory, output_filename)

    # Abrir vídeo
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Erro ao abrir vídeo: {os.path.basename(video_path)}")
        return None

    # Obter propriedades
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = 1280
    height = 720
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Processando: {os.path.basename(video_path)}")

    # Criar VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("Erro ao criar vídeo de saída")
        video.release()
        return

    # Criar filas para comunicação entre threads
    write_queue = queue.Queue(maxsize=30)  # Fila para escrita de frames

    # Thread para escrever frames no vídeo
    def writer_thread():
        """Thread dedicada para escrever frames"""
        while True:
            item = write_queue.get()
            if item is None:  # Sinal de parada
                break
            out.write(item)
            write_queue.task_done()

    # Iniciar thread de escrita
    writer = threading.Thread(target=writer_thread)
    writer.start()

    # Variáveis para estatísticas
    frame_count = 0
    total_people_detected = 0
    max_people_in_frame = 0
    start_time = time.time()
    processing_stats = []

    # Processar frames
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        frame_count += 1

        # Redimensionar
        frame_resized = cv2.resize(frame, (width, height))

        # Detectar pessoas
        result = detect_people(model, frame_resized)

        # Criar cópia do frame para desenhar as detecções
        annotated_frame = frame_resized.copy()

        # Contar pessoas no frame atual
        people_count = len(result.boxes)
        total_people_detected += people_count
        max_people_in_frame = max(max_people_in_frame, people_count)

        # Desenhar caixas delimitadoras e rótulos com quadradinhos
        for box in result.boxes:
            # Obter coordenadas da caixa
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            confidence = box.conf[0].cpu().numpy().astype(float)

            # Desenhar caixa delimitadora (verde)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 128, 0), 1)

            # Criar texto do rótulo
            label = f"Person {confidence:.2f}"

            # Calcular tamanho do texto
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 2
            text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]

            # Calcular posição do quadradinho (acima da caixa)
            label_y1 = y1 - text_size[1] - 10
            label_x1 = x1
            label_x2 = x1 + text_size[0] + 10
            label_y2 = y1

            # Garantir que o quadradinho fique dentro da imagem
            if label_y1 < 0:
                label_y1 = 0
                label_y2 = text_size[1] + 10

            # Desenhar quadradinho (preto com borda verde)
            cv2.rectangle(
                annotated_frame,
                (label_x1, label_y1),
                (label_x2, label_y2),
                (0, 128, 0),
                -1,
            )
            cv2.rectangle(
                annotated_frame,
                (label_x1, label_y1),
                (label_x2, label_y2),
                (0, 128, 0),
                1,
            )

            # Desenhar texto dentro do quadradinho (branco)
            text_x = x1 + 5
            text_y = y1 - 5
            cv2.putText(
                annotated_frame,
                label,
                (text_x, text_y),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
            )

        # Adicionar contador de pessoas (vermelho)
        cv2.putText(
            annotated_frame,
            f"Pessoas: {people_count}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),  # Vermelho
            2,
        )

        # Adicionar tempo decorrido (verde)
        elapsed_time = time.time() - start_time
        cv2.putText(
            annotated_frame,
            f"Tempo: {elapsed_time:.1f}s",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),  # Verde
            2,
        )

        # Adicionar máximo de pessoas (magenta)
        cv2.putText(
            annotated_frame,
            f"Máximo: {max_people_in_frame}",
            (10, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 255),  # Magenta
            2,
        )

        # Adicionar à fila de escrita (não bloqueia processamento)
        write_queue.put(annotated_frame)

        # Armazenar estatísticas para análise posterior
        processing_stats.append(
            {
                "frame": frame_count,
                "people_count": people_count,
                "max_people": max_people_in_frame,
                "elapsed_time": time.time() - start_time,
            }
        )

        # Mostrar progresso ocasionalmente
        if frame_count % 100 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"{progress:.1f}% concluído")

    # Sinalizar fim para thread de escrita
    write_queue.put(None)

    # Esperar thread de escrita terminar
    writer.join()

    # Calcular estatísticas finais
    processing_time = time.time() - start_time
    avg_people_per_frame = total_people_detected / frame_count if frame_count > 0 else 0

    # Salvar estatísticas em arquivo
    stats_filename = f"stats_{video_name}.txt"
    stats_path = os.path.join(output_directory, stats_filename)

    with open(stats_path, "w") as f:
        f.write("Estatísticas do Processamento de Detecção de Pessoas\n")
        f.write("=" * 50 + "\n")
        f.write(f"Vídeo processado: {os.path.basename(video_path)}\n")
        f.write(f"Resolução: {width}x{height}\n")
        f.write(f"Total de frames: {frame_count}\n")
        f.write(f"Tempo total de processamento: {processing_time:.2f}s\n")
        f.write(f"FPS médio: {frame_count / processing_time:.2f}\n")
        f.write(f"Total de pessoas detectadas: {total_people_detected}\n")
        f.write(f"Máximo de pessoas em um frame: {max_people_in_frame}\n")
        f.write(f"Média de pessoas por frame: {avg_people_per_frame:.2f}\n")

    # Finalizar
    video.release()
    out.release()

    print(f"Concluído: {os.path.basename(video_path)}")
    return {"video_path": output_path, "stats_path": stats_path}


def main():
    """Função principal que processa todos os vídeos da pasta"""
    config = setup()

    if not config:
        print("Falha na configuração. Encerrando.")
        return

    video_files = config["video_files"]
    processed_videos = []
    failed_videos = []

    for i, video_path in enumerate(video_files, 1):
        try:
            result = processVideo(config, video_path)
            if result:
                processed_videos.append(result)
            else:
                failed_videos.append(os.path.basename(video_path))
        except Exception as e:
            print(f"Erro ao processar vídeo {os.path.basename(video_path)}: {str(e)}")
            failed_videos.append(os.path.basename(video_path))

    # Resumo final
    print("\nResumo do processamento:")
    if processed_videos:
        print(f"{len(processed_videos)} vídeo(s) processado(s) com sucesso.")
    if failed_videos:
        print(f"{len(failed_videos)} vídeo(s) falharam.")


if __name__ == "__main__":
    main()
