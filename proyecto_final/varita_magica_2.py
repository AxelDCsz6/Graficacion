import cv2 as cv
import numpy as np
import math

class SistemaPintura:
    def __init__(self):
        # Definir rangos HSV para cada color
        self.colores = {
            "naranja": {
                "lower": np.array([5, 100, 100]),
                "upper": np.array([15, 255, 255]),
                "bgr": (0, 165, 255)  # BGR: naranja
            },
            "azul": {
                "lower": np.array([90, 100, 100]),
                "upper": np.array([130, 255, 255]),
                "bgr": (255, 0, 0)  # BGR: azul
            },
            "verde": {
                "lower": np.array([40, 100, 100]),
                "upper": np.array([80, 255, 255]),
                "bgr": (0, 255, 0)  # BGR: verde
            },
            "rojo": {
                "lower": np.array([0, 100, 100]),
                "upper": np.array([10, 255, 255]),
                "bgr": (0, 0, 255)  # BGR: rojo
            },
            "amarillo": {
                "lower": np.array([20, 100, 100]),
                "upper": np.array([30, 255, 255]),
                "bgr": (0, 255, 255)  # BGR: amarillo
            },
            "rosa": {
                "lower": np.array([140, 100, 100]),
                "upper": np.array([170, 255, 255]),
                "bgr": (203, 192, 255)  # BGR: rosa
            }
        }
        
        # Color actual para dibujar (comienza con naranja)
        self.color_actual = "naranja"
        self.modo_actual = "trazado_libre"
        self.estado_figura = "posicion"
        self.figura_actual = "circulo"
        self.ultimo_punto = None
        self.tamano_figura = 30
        self.rotacion_figura = 0
        
        # Variables temporales para configuración
        self.figura_temporal = None
        self.posicion_temporal = None
        self.rotacion_temporal = 0
        self.tamano_temporal = 30
        
        self.lienzo = None
        self.reset_lienzo()
        
    def reset_lienzo(self):
        self.lienzo = np.zeros((480, 640, 3), dtype=np.uint8)
        self.ultimo_punto = None
    
    def detectar_lapiz(self, frame):
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        
        # Detectar todos los colores
        detecciones = {}
        
        for color_nombre, color_info in self.colores.items():
            mask = cv.inRange(hsv, color_info["lower"], color_info["upper"])
            
            kernel = np.ones((5, 5), np.uint8)
            mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
            mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
            
            contornos, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            
            if contornos:
                contorno_lapiz = max(contornos, key=cv.contourArea)
                area = cv.contourArea(contorno_lapiz)
                
                if area > 150:
                    M = cv.moments(contorno_lapiz)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        detecciones[color_nombre] = {
                            "punto": (cx, cy),
                            "area": area
                        }
        
        # Encontrar la detección con mayor área (el lápiz más prominente)
        if detecciones:
            color_detectado = max(detecciones.items(), key=lambda x: x[1]["area"])[0]
            punto = detecciones[color_detectado]["punto"]
            # Actualizar color actual basado en lo detectado
            self.color_actual = color_detectado
            return punto, color_detectado
        
        return None, self.color_actual
    
    def dibujar_trazado_libre(self, punto_actual, color_nombre):
        color_bgr = self.colores[color_nombre]["bgr"]
        if self.ultimo_punto is not None:
            cv.line(self.lienzo, self.ultimo_punto, punto_actual, color_bgr, 3)
        self.ultimo_punto = punto_actual
    
    def dibujar_figura_rotada(self, frame, punto, figura, tamano, rotacion, color_nombre):
        x, y = punto
        color_bgr = self.colores[color_nombre]["bgr"]
        
        if figura == "circulo":
            cv.circle(frame, (x, y), tamano, color_bgr, -1)
            
        elif figura == "rectangulo":
            rect_points = np.array([[-tamano, -tamano//2], [tamano, -tamano//2], 
                                  [tamano, tamano//2], [-tamano, tamano//2]], np.float32)
            
            angle_rad = math.radians(rotacion)
            cos_val = math.cos(angle_rad)
            sin_val = math.sin(angle_rad)
            
            rotation_matrix = np.array([[cos_val, -sin_val], 
                                      [sin_val, cos_val]])
            
            rotated_points = np.dot(rect_points, rotation_matrix.T)
            rotated_points += [x, y]
            
            cv.fillConvexPoly(frame, rotated_points.astype(int), color_bgr)
            
        elif figura == "linea":
            angle_rad = math.radians(rotacion)
            x1 = int(x - tamano * math.cos(angle_rad))
            y1 = int(y - tamano * math.sin(angle_rad))
            x2 = int(x + tamano * math.cos(angle_rad))
            y2 = int(y + tamano * math.sin(angle_rad))
            
            cv.line(frame, (x1, y1), (x2, y2), color_bgr, 3)
    
    def calcular_parametro_segun_x(self, x, min_val, max_val):
        ancho_pantalla = 640
        normalizado = x / ancho_pantalla
        return int(min_val + normalizado * (max_val - min_val))
    
    def procesar_modo_figura(self, frame, punto_lapiz, color_detectado):
        if punto_lapiz:
            x, y = punto_lapiz
            
            if self.estado_figura == "posicion":
                self.posicion_temporal = punto_lapiz
                self.rotacion_temporal = 0
                self.tamano_temporal = 30
                
            elif self.estado_figura == "rotacion":
                self.rotacion_temporal = self.calcular_parametro_segun_x(x, 0, 360)
                
            elif self.estado_figura == "tamano":
                self.tamano_temporal = self.calcular_parametro_segun_x(x, 10, 100)
            
            # SOLO DIBUJAR EN EL FRAME DE CÁMARA (NO EN EL LIENZO)
            if self.posicion_temporal:
                self.dibujar_figura_rotada(frame, self.posicion_temporal, 
                                         self.figura_actual, self.tamano_temporal, 
                                         self.rotacion_temporal, color_detectado)
                
            cv.circle(frame, punto_lapiz, 8, (0, 255, 0), 2)
            
            if self.estado_figura in ["rotacion", "tamano"]:
                cv.line(frame, (320, 0), (320, 480), (255, 255, 0), 1)
    
    def confirmar_figura(self, color_detectado):
        # SOLO DIBUJAR EN EL LIENZO CUANDO SE CONFIRMA EN EL ESTADO "tamano"
        if self.estado_figura == "tamano" and self.posicion_temporal:
            self.dibujar_figura_rotada(self.lienzo, self.posicion_temporal,
                                     self.figura_actual, self.tamano_temporal,
                                     self.rotacion_temporal, color_detectado)
        
        if self.estado_figura == "posicion":
            self.estado_figura = "rotacion"
            print(f"Modo ROTACIÓN: Mueve el lápiz horizontalmente para rotar (Color: {self.color_actual})")
        elif self.estado_figura == "rotacion":
            self.estado_figura = "tamano"
            print(f"Modo TAMAÑO: Mueve el lápiz horizontalmente para ajustar tamaño (Color: {self.color_actual})")
        elif self.estado_figura == "tamano":
            self.estado_figura = "posicion"
            print(f"Figura confirmada! Modo POSICIÓN listo para nueva figura (Color: {self.color_actual})")
    
    def procesar_frame(self, frame):
        frame = cv.flip(frame, 1)
        punto_lapiz, color_detectado = self.detectar_lapiz(frame)
        
        if self.modo_actual == "trazado_libre":
            if punto_lapiz:
                self.dibujar_trazado_libre(punto_lapiz, color_detectado)
                cv.circle(frame, punto_lapiz, 10, (0, 255, 0), 2)
            else:
                self.ultimo_punto = None
                
        elif self.modo_actual == "figuras":
            self.procesar_modo_figura(frame, punto_lapiz, color_detectado)
        
        return frame
    
    def manejar_teclas(self, tecla):
        if tecla == ord('t'):
            self.modo_actual = "trazado_libre"
            self.estado_figura = "posicion"
            print(f"Modo: Trazado Libre (Color actual: {self.color_actual})")
            
        elif tecla == ord('f'):
            self.modo_actual = "figuras"
            self.estado_figura = "posicion"
            print(f"Modo Figuras - Estado: POSICIÓN (Color actual: {self.color_actual})")
            print("Mueve el lápiz a la posición deseada y presiona ESPACIO")
            
        elif tecla == ord('c'):
            self.figura_actual = "circulo"
            print(f"Figura: Círculo (Color actual: {self.color_actual})")
            
        elif tecla == ord('r'):
            self.figura_actual = "rectangulo"
            print(f"Figura: Rectángulo (Color actual: {self.color_actual})")
            
        elif tecla == ord('l'):
            self.figura_actual = "linea"
            print(f"Figura: Línea (Color actual: {self.color_actual})")
            
        elif tecla == ord('n'):
            self.reset_lienzo()
            print("Lienzo reiniciado")
            
        elif tecla == 32:  # Espacio
            if self.modo_actual == "figuras":
                self.confirmar_figura(self.color_actual)
                
        elif tecla == 27:  # ESC
            return False
            
        return True

def main():
    sistema = SistemaPintura()
    cap = cv.VideoCapture(0)
    
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    
    cv.namedWindow('Cámara - Sistema de Pintura')
    cv.namedWindow('Lienzo Virtual')
    
    print("=" * 50)
    print("SISTEMA DE PINTURA AVANZADO - CONTROLES")
    print("=" * 50)
    print("T - Modo Trazado Libre")
    print("F - Modo Figuras (con configuración por pasos)")
    print("C/R/L - Seleccionar Figura (Círculo/Rectángulo/Línea)")
    print("ESPACIO - Confirmar paso actual en modo figuras")
    print("N - Nuevo Lienzo")
    print("ESC - Salir")
    print()
    print("COLORES DISPONIBLES (usa un lápiz del color deseado):")
    print("- Naranja (original)")
    print("- Azul")
    print("- Verde")
    print("- Rojo")
    print("- Amarillo")
    print("- Rosa")
    print()
    print("FLUJO MODO FIGURAS:")
    print("1. F -> Modo Figuras")
    print("2. Posiciona la figura con el lápiz (color se selecciona automáticamente)")
    print("3. ESPACIO -> Confirma posición")
    print("4. Mueve horizontalmente para rotar")
    print("5. ESPACIO -> Confirma rotación") 
    print("6. Mueve horizontalmente para tamaño")
    print("7. ESPACIO -> Confirma y dibuja figura")
    print("=" * 50)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_procesado = sistema.procesar_frame(frame)
        
        cv.imshow('Cámara - Sistema de Pintura', frame_procesado)
        cv.imshow('Lienzo Virtual', sistema.lienzo)
        
        tecla = cv.waitKey(1) & 0xFF
        if tecla != 255:
            if not sistema.manejar_teclas(tecla):
                break
    
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
