import cv2
import mediapipe as mp
import numpy as np

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2)

# Variables para el cuadrado
square_size = 100  # Tamaño inicial del cuadrado
min_size = 50      # Tamaño mínimo del cuadrado
max_size = 300     # Tamaño máximo del cuadrado
square_color = (0, 255, 0)  # Color verde para el cuadrado

# Captura de video en tiempo real
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Obtener dimensiones del frame
    frame_height, frame_width, _ = frame.shape
    
    # Convertir a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Procesar la imagen con MediaPipe
    results = hands.process(frame_rgb)

    # Lista para almacenar las posiciones de los pulgares
    thumb_positions = []

    # Dibujar puntos de la mano y recolectar posiciones de pulgares
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Obtener coordenadas del pulgar (landmark 4) en píxeles
            thumb = hand_landmarks.landmark[4]
            thumb_x = int(thumb.x * frame_width)
            thumb_y = int(thumb.y * frame_height)
            thumb_positions.append((thumb_x, thumb_y))
            
            # Dibujar un círculo en el pulgar
            cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 0, 255), -1)

    # Si hay exactamente 2 pulgares detectados, calcular distancia y ajustar tamaño del cuadrado
    if len(thumb_positions) == 2:
        thumb1, thumb2 = thumb_positions
        
        # Calcular distancia Euclidiana entre los pulgares
        distance = np.linalg.norm(np.array(thumb1) - np.array(thumb2))
        
        # Dibujar línea entre los pulgares
        cv2.line(frame, thumb1, thumb2, (255, 0, 0), 3)
        
        # Mostrar la distancia en pantalla
        cv2.putText(frame, f"Distancia: {int(distance)}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Ajustar tamaño del cuadrado basado en la distancia (mapeo lineal)
        # Asumimos que la distancia mínima es 50px y máxima 300px para el control
        square_size = int(np.interp(distance, [50, 300], [min_size, max_size]))
        
        # Limitar el tamaño dentro de los rangos establecidos
        square_size = max(min_size, min(max_size, square_size))

    # Dibujar cuadrado en el centro de la pantalla
    center_x, center_y = frame_width // 2, frame_height // 2
    half_size = square_size // 2
    
    # Calcular las esquinas del cuadrado
    top_left = (center_x - half_size, center_y - half_size)
    bottom_right = (center_x + half_size, center_y + half_size)
    
    # Dibujar el cuadrado
    cv2.rectangle(frame, top_left, bottom_right, square_color, 3)
    
    # Mostrar el tamaño actual del cuadrado
    cv2.putText(frame, f"Tamano: {square_size}", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Mostrar el video
    cv2.imshow("Control de Cuadrado con Pulgares", frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
