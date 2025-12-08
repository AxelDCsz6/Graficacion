import cv2
import mediapipe as mp

class DetectorGestos:
    def __init__(self):
        self.mp_manos = mp.solutions.hands
        self.mp_dibujo = mp.solutions.drawing_utils
        self.manos = self.mp_manos.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
    def procesar_frame(self, frame):
        """Procesa un frame y detecta manos"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = self.manos.process(frame_rgb)
        
        if resultados.multi_hand_landmarks:
            for landmarks_mano in resultados.multi_hand_landmarks:
                self.mp_dibujo.draw_landmarks(
                    frame, landmarks_mano, self.mp_manos.HAND_CONNECTIONS,
                    self.mp_dibujo.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    self.mp_dibujo.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
        return frame

def main():
    detector = DetectorGestos()
    captura = cv2.VideoCapture(0)
    
    print("🖐️ Detector de Gestos de Manos activado")
    print("Presione 'Q' para salir")
    
    while captura.isOpened():
        exito, frame = captura.read()
        if not exito:
            break
            
        frame = cv2.flip(frame, 1)
        frame_procesado = detector.procesar_frame(frame)
        
        cv2.imshow('Deteccion de Gestos con Manos', frame_procesado)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    captura.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
