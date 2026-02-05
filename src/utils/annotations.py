"""
Module to draw annotations on frames
"""
import cv2


def draw_detections(frame, results, people_count, max_people=0, elapsed_time=0.0):
    """
    Draw detections and information on the frame
    
    Args:
        frame: Original frame
        results: YOLO detection results
        people_count (int): Number of people in the frame
        max_people (int): Maximum people detected so far
        elapsed_time (float): Elapsed processing time
        
    Returns:
        Frame annotated with detections
    """
    annotated_frame = frame.copy()
    
    # Draw bounding boxes and labels
    for box in results.boxes:
        # Get coordinates and confidence
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        confidence = box.conf[0].cpu().numpy().astype(float)
        
        # Draw bounding box (green)
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 128, 0), 2)
        
        # Create label
        label = f"D {confidence:.2f}"
        
        # Calculate text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 2
        text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        
        # Box position (above bounding box)
        label_y1 = max(0, y1 - text_size[1] - 10)
        label_x1 = x1
        label_x2 = x1 + text_size[0] + 10
        label_y2 = y1
        
        # Adjust if outside image
        if label_y1 < 0:
            label_y1 = 0
            label_y2 = text_size[1] + 10
        
        # Draw background box (black with green border)
        cv2.rectangle(annotated_frame, (label_x1, label_y1), 
                     (label_x2, label_y2), (0, 128, 0), -1)
        cv2.rectangle(annotated_frame, (label_x1, label_y1), 
                     (label_x2, label_y2), (0, 128, 0), 1)
        
        # Draw text (white)
        text_x = x1 + 5
        text_y = y1 - 5
        cv2.putText(annotated_frame, label, (text_x, text_y),
                   font, font_scale, (255, 255, 255), thickness)
    
    # Add general information
    draw_info_overlay(annotated_frame, people_count, max_people, elapsed_time)
    
    return annotated_frame


def draw_info_overlay(frame, people_count, max_people=0, elapsed_time=0.0):
    """
    Draw information overlay on frame
    
    Args:
        frame: Frame to be annotated
        people_count (int): Number of people in current frame
        max_people (int): Maximum people detected
        elapsed_time (float): Elapsed time
    """
    # People counter (red)
    cv2.putText(frame, f"Detected: {people_count}",
               (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
    
    # Elapsed time (green)
    if elapsed_time > 0:
        cv2.putText(frame, f"Time: {elapsed_time:.1f}s",
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Maximum people (magenta)
    if max_people > 0:
        cv2.putText(frame, f"Max detection: {max_people}",
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
