import cv2 as cv
import numpy as np
import math

class SistemaPintura:
    def __init__(self):
        self.color_naranja_bgr = (0, 165, 255)
        self.lower_color = np.array([5, 100, 100])
        self.upper_color = np.array([15, 255, 255])
        
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
        mask = cv.inRange(hsv, self.lower_color, self.upper_color)
        
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
                    return (cx, cy)
        
        return None
    
    def dibujar_trazado_libre(self, punto_actual):
        if self.ultimo_punto is not None:
            cv.line(self.lienzo, self.ultimo_punto, punto_actual, (255, 255, 255), 3)
        self.ultimo_punto = punto_actual
    
    def dibujar_figura_rotada(self, frame, punto, figura, tamano, rotacion):
        x, y = punto
        
        if figura == "circulo":
            cv.circle(frame, (x, y), tamano, (255, 255, 255), -1)
            
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
            
            cv.fillConvexPoly(frame, rotated_points.astype(int), (255, 255, 255))
            
        elif figura == "linea":
            angle_rad = math.radians(rotacion)
            x1 = int(x - tamano * math.cos(angle_rad))
            y1 = int(y - tamano * math.sin(angle_rad))
            x2 = int(x + tamano * math.cos(angle_rad))
            y2 = int(y + tamano * math.sin(angle_rad))
            
            cv.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)
    
    def calcular_parametro_segun_x(self, x, min_val, max_val):
        ancho_pantalla = 640
        normalizado = x / ancho_pantalla
        return int(min_val + normalizado * (max_val - min_val))
    
    def procesar_modo_figura(self, frame, punto_lapiz):
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
                                         self.rotacion_temporal)
                
            cv.circle(frame, punto_lapiz, 8, (0, 255, 0), 2)
            
            if self.estado_figura in ["rotacion", "tamano"]:
                cv.line(frame, (320, 0), (320, 480), (255, 255, 0), 1)
    
    def confirmar_figura(self):
        # SOLO DIBUJAR EN EL LIENZO CUANDO SE CONFIRMA EN EL ESTADO "tamano"
        if self.estado_figura == "tamano" and self.posicion_temporal:
            self.dibujar_figura_rotada(self.lienzo, self.posicion_temporal,
                                     self.figura_actual, self.tamano_temporal,
                                     self.rotacion_temporal)
        
        if self.estado_figura == "posicion":
            self.estado_figura = "rotacion"
            print("Modo ROTACIÓN: Mueve el lápiz horizontalmente para rotar")
        elif self.estado_figura == "rotacion":
            self.estado_figura = "tamano"
            print("Modo TAMAÑO: Mueve el lápiz horizontalmente para ajustar tamaño")
        elif self.estado_figura == "tamano":
            self.estado_figura = "posicion"
            print("Figura confirmada! Modo POSICIÓN listo para nueva figura")
    
    def procesar_frame(self, frame):
        frame = cv.flip(frame, 1)
        punto_lapiz = self.detectar_lapiz(frame)
        
        if self.modo_actual == "trazado_libre":
            if punto_lapiz:
                self.dibujar_trazado_libre(punto_lapiz)
                cv.circle(frame, punto_lapiz, 10, (0, 255, 0), 2)
            else:
                self.ultimo_punto = None
                
        elif self.modo_actual == "figuras":
            self.procesar_modo_figura(frame, punto_lapiz)
        
        return frame
    
    def manejar_teclas(self, tecla):
        if tecla == ord('t'):
            self.modo_actual = "trazado_libre"
            self.estado_figura = "posicion"
            print("Modo: Trazado Libre")
            
        elif tecla == ord('f'):
            self.modo_actual = "figuras"
            self.estado_figura = "posicion"
            print("Modo Figuras - Estado: POSICIÓN")
            print("Mueve el lápiz a la posición deseada y presiona ESPACIO")
            
        elif tecla == ord('c'):
            self.figura_actual = "circulo"
            print("Figura: Círculo")
            
        elif tecla == ord('r'):
            self.figura_actual = "rectangulo"
            print("Figura: Rectángulo")
            
        elif tecla == ord('l'):
            self.figura_actual = "linea"
            print("Figura: Línea")
            
        elif tecla == ord('n'):
            self.reset_lienzo()
            print("Lienzo reiniciado")
            
        elif tecla == 32:
            if self.modo_actual == "figuras":
                self.confirmar_figura()
                
        elif tecla == 27:
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
    print("FLUJO MODO FIGURAS:")
    print("1. F -> Modo Figuras")
    print("2. Posiciona la figura con el lápiz")
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
