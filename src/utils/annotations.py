"""
Módulo para desenhar anotações nos frames
"""
import cv2


def draw_detections(frame, results, people_count, max_people=0, elapsed_time=0.0):
    """
    Desenha detecções e informações no frame
    
    Args:
        frame: Frame original
        results: Resultados da detecção YOLO
        people_count (int): Número de pessoas no frame
        max_people (int): Máximo de pessoas detectado até o momento
        elapsed_time (float): Tempo decorrido de processamento
        
    Returns:
        Frame anotado com as detecções
    """
    annotated_frame = frame.copy()
    
    # Desenhar caixas delimitadoras e labels
    for box in results.boxes:
        # Obter coordenadas e confiança
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        confidence = box.conf[0].cpu().numpy().astype(float)
        
        # Desenhar caixa delimitadora (verde)
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 128, 0), 2)
        
        # Criar label
        label = f"Person {confidence:.2f}"
        
        # Calcular tamanho do texto
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 2
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        
        # Posição do quadradinho (acima da caixa)
        label_y1 = max(0, y1 - text_size[1] - 10)
        label_x1 = x1
        label_x2 = x1 + text_size[0] + 10
        label_y2 = y1
        
        # Ajustar se estiver fora da imagem
        if label_y1 < 0:
            label_y1 = 0
            label_y2 = text_size[1] + 10
        
        # Desenhar quadradinho de fundo (preto com borda verde)
        cv2.rectangle(annotated_frame, (label_x1, label_y1), 
                     (label_x2, label_y2), (0, 128, 0), -1)
        cv2.rectangle(annotated_frame, (label_x1, label_y1), 
                     (label_x2, label_y2), (0, 128, 0), 1)
        
        # Desenhar texto (branco)
        text_x = x1 + 5
        text_y = y1 - 5
        cv2.putText(annotated_frame, label, (text_x, text_y),
                   font, font_scale, (255, 255, 255), thickness)
    
    # Adicionar informações gerais
    draw_info_overlay(annotated_frame, people_count, max_people, elapsed_time)
    
    return annotated_frame


def draw_info_overlay(frame, people_count, max_people=0, elapsed_time=0.0):
    """
    Desenha overlay de informações no frame
    
    Args:
        frame: Frame a ser anotado
        people_count (int): Número de pessoas no frame atual
        max_people (int): Máximo de pessoas detectado
        elapsed_time (float): Tempo decorrido
    """
    # Contador de pessoas (vermelho)
    cv2.putText(frame, f"Pessoas: {people_count}",
               (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
    
    # Tempo decorrido (verde)
    if elapsed_time > 0:
        cv2.putText(frame, f"Tempo: {elapsed_time:.1f}s",
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Máximo de pessoas (magenta)
    if max_people > 0:
        cv2.putText(frame, f"Maximo: {max_people}",
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
