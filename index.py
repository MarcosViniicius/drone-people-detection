import cv2
import os
from ultralytics import YOLO
import threading
import queue


def setup():
    """Configuração inicial do modelo e variáveis"""
    model = YOLO(
        "yolov8m.pt",
    )  # yolov8n, yolov8s, yolov8m, yolov8l, yolov8x

    # Diretórios
    output_directory = "./assets/output/videos"
    output_filename = "result_annotated.mp4"
    video_name = "video.mp4"
    video_directory = f"./assets/videos_for_processing/{video_name}"

    # Criar pasta de saída se não existir
    os.makedirs(output_directory, exist_ok=True)
    os.makedirs(video_directory, exist_ok=True)
    output_path = os.path.join(output_directory, output_filename)

    return {
        "model": model,
        "video_directory": video_directory,
        "output_path": output_path,
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


def processVideo(config):
    """Processa vídeo completo detectando e contando pessoas com threading"""
    model = config["model"]
    video_directory = config["video_directory"]
    output_path = config["output_path"]

    # Abrir vídeo
    video = cv2.VideoCapture(video_directory)
    if not video.isOpened():
        print(
            f"❌ Erro ao abrir vídeo. Adicione arquivo .mp4 dentro da pasta {video_directory}"
        )
        return

    # Obter propriedades
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = 1280
    height = 720
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f" Processando: {width}x{height} @ {fps}fps")
    print(f" Total de frames: {total_frames}")

    # Criar VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("❌ Erro ao criar vídeo de saída")
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

    # Processar frames
    frame_count = 0

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        frame_count += 1

        # Redimensionar
        frame_resized = cv2.resize(frame, (width, height))

        # Detectar pessoas
        result = detect_people(model, frame_resized)

        # Obter frame anotado com detecções desenhadas
        annotated_frame = result.plot()

        # Adicionar contador de pessoas
        people_count = len(result.boxes)
        cv2.putText(
            annotated_frame,
            f"Pessoas: {people_count}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 0, 255),
            3,
        )

        # Adicionar à fila de escrita (não bloqueia processamento)
        write_queue.put(annotated_frame)

        # Mostrar progresso
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100
            print(f" Progresso: {progress:.1f}% ({frame_count}/{total_frames})")

    # Sinalizar fim para thread de escrita
    write_queue.put(None)

    # Esperar thread de escrita terminar
    writer.join()

    # Finalizar
    video.release()
    out.release()

    print(f"\n Vídeo salvo em: {output_path}")
    print(f" Total de frames processados: {frame_count}")


def main():
    """Função principal"""
    config = setup()
    processVideo(config)


if __name__ == "__main__":
    main()
