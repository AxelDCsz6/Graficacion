import cv2
import mediapipe as mp
import time

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# Inicializar cámara
cap = cv2.VideoCapture(0)

# Variables para la calculadora
current_number = ""
current_operator = ""
first_number = None
second_number = None
result = None
input_mode = "first"  # "first", "operator", "second"
selection_start_time = None
selected_button = None

# Definir los botones de la calculadora
buttons = {
    '7': (50, 100), '8': (150, 100), '9': (250, 100), '/': (350, 100),
    '4': (50, 200), '5': (150, 200), '6': (250, 200), '*': (350, 200),
    '1': (50, 300), '2': (150, 300), '3': (250, 300), '-': (350, 300),
    '0': (50, 400), 'C': (150, 400), '=': (250, 400), '+': (350, 400)
}

button_size = 80

def draw_calculator(frame):
    """Dibuja la interfaz de la calculadora"""
    # Dibajar display
    cv2.rectangle(frame, (50, 30), (350, 80), (255, 255, 255), -1)
    cv2.rectangle(frame, (50, 30), (350, 80), (0, 0, 0), 2)
    
    # Mostrar operación actual
    display_text = ""
    if first_number is not None:
        display_text += str(first_number)
    if current_operator:
        display_text += " " + current_operator
    if second_number is not None:
        display_text += " " + str(second_number)
    if result is not None:
        display_text += " = " + str(result)
    
    cv2.putText(frame, display_text, (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # Dibujar botones
    for btn, (x, y) in buttons.items():
        color = (200, 200, 200)
        if btn in ['/', '*', '-', '+']:
            color = (150, 200, 255)  # Azul para operadores
        elif btn in ['C', '=']:
            color = (255, 150, 150)  # Rojo para clear e igual
            
        cv2.rectangle(frame, (x, y), (x + button_size, y + button_size), color, -1)
        cv2.rectangle(frame, (x, y), (x + button_size, y + button_size), (0, 0, 0), 2)
        cv2.putText(frame, btn, (x + 30, y + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def is_finger_on_button(finger_pos, button_pos):
    """Verifica si el dedo está sobre un botón"""
    x, y = finger_pos
    btn_x, btn_y = button_pos
    return (btn_x <= x <= btn_x + button_size and 
            btn_y <= y <= btn_y + button_size)

def reset_calculator():
    """Reinicia la calculadora"""
    global current_number, current_operator, first_number, second_number, result, input_mode
    current_number = ""
    current_operator = ""
    first_number = None
    second_number = None
    result = None
    input_mode = "first"

def calculate_result():
    """Realiza el cálculo"""
    global result
    try:
        if current_operator == '+':
            result = first_number + second_number
        elif current_operator == '-':
            result = first_number - second_number
        elif current_operator == '*':
            result = first_number * second_number
        elif current_operator == '/':
            if second_number != 0:
                result = first_number / second_number
            else:
                result = "Error"
    except:
        result = "Error"

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Convertir a RGB para MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    # Dibujar calculadora
    draw_calculator(frame)
    
    # Variables para coordenadas de dedos
    left_index = None
    right_index = None
    
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label
            
            # Coordenadas del dedo índice (landmark 8)
            index_tip = hand_landmarks.landmark[8]
            x, y = int(index_tip.x * w), int(index_tip.y * h)
            
            if label == 'Left':
                left_index = (x, y)
            elif label == 'Right':
                right_index = (x, y)
            
            # Dibujar landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # Usar el dedo índice derecho para seleccionar (puedes cambiar a left_index si prefieres)
    finger_pos = right_index if right_index else left_index
    
    if finger_pos:
        cv2.circle(frame, finger_pos, 10, (0, 255, 0), -1)
        
        # Verificar si el dedo está sobre algún botón
        current_button = None
        for btn, btn_pos in buttons.items():
            if is_finger_on_button(finger_pos, btn_pos):
                current_button = btn
                break
        
        # Manejar la selección del botón
        if current_button:
            if current_button != selected_button:
                selected_button = current_button
                selection_start_time = time.time()
            else:
                elapsed_time = time.time() - selection_start_time
                
                # Mostrar cuenta regresiva
                cv2.putText(frame, f"{3 - int(elapsed_time)}", 
                           (finger_pos[0] + 15, finger_pos[1] - 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Si han pasado 3 segundos
                if elapsed_time >= 3:
                    if current_button in '0123456789':
                        if input_mode == "first":
                            current_number += current_button
                            first_number = float(current_number) if '.' in current_number else int(current_number)
                        elif input_mode == "second":
                            current_number += current_button
                            second_number = float(current_number) if '.' in current_number else int(current_number)
                    
                    elif current_button in ['/', '*', '-', '+']:
                        if first_number is not None:
                            current_operator = current_button
                            current_number = ""
                            input_mode = "second"
                    
                    elif current_button == '=':
                        if first_number is not None and current_operator and second_number is not None:
                            calculate_result()
                            input_mode = "result"
                    
                    elif current_button == 'C':
                        reset_calculator()
                    
                    # Reiniciar temporizador después de la selección
                    selection_start_time = None
                    selected_button = None
        else:
            selected_button = None
            selection_start_time = None
    
    cv2.imshow("Calculadora con Manos", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # Presionar ESC para salir
        break

cap.release()
cv2.destroyAllWindows()