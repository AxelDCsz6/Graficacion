import math
import cv2 as cv
import numpy as np
import random as ran

class GeneradorCurvasOptimizado:
    def __init__(self, ancho=800, alto=800):
        self.dimension_ancho = ancho
        self.dimension_alto = alto
        self.centro_x, self.centro_y = ancho // 2, alto // 2
        
        # UNA sola superficie de dibujo
        self.superficie_principal = np.zeros((alto, ancho, 3), np.uint8)
        
        # Parámetros de configuración
        self.escala_principal = 170
        self.angulo_actual = 0
        self.radio_principal = self.escala_principal
        self.radio_secundario = self.escala_principal / 10
        
        # Control de FPS
        self.ultimo_tiempo = 0
        self.fps_objetivo = 30
        
    def generar_color_armonico(self):
        """Genera colores más armónicos en lugar de aleatorios"""
        base_hue = (self.angulo_actual * 50) % 180
        return (int(base_hue), 200, 200)
        
    def actualizar_curvas(self):
        color_actual = self.generar_color_armonico()
        
        # Solo una curva a la vez para mejor rendimiento
        tipo_curva = int(self.angulo_actual * 2) % 3
        
        if tipo_curva == 0:
            # Curva tipo cardioide
            radio_temporal = self.escala_principal * (0.7 - math.cos(self.angulo_actual))
            x = int(self.centro_x - radio_temporal * math.cos(self.angulo_actual))
            y = int(self.centro_y - radio_temporal * math.sin(self.angulo_actual))
            
        elif tipo_curva == 1:
            # Curva tipo hipocicloide
            x = int(self.centro_x + 
                   (self.radio_principal - self.radio_secundario) * math.cos(self.angulo_actual) + 
                   self.radio_secundario * math.cos((self.radio_principal - self.radio_secundario) / 
                   self.radio_secundario * self.angulo_actual))
            y = int(self.centro_y + 
                   (self.radio_principal - self.radio_secundario) * math.sin(self.angulo_actual) - 
                   self.radio_secundario * math.sin((self.radio_principal - self.radio_secundario) / 
                   self.radio_secundario * self.angulo_actual))
        else:
            # Curva tipo Lissajous
            x = int(self.centro_x + 150 * math.sin(3 * self.angulo_actual))
            y = int(self.centro_y + 150 * math.cos(5 * self.angulo_actual))
        
        # Dibujar punto
        cv.circle(self.superficie_principal, (x, y), 2, color_actual, -1)
        
        self.angulo_actual += 0.008
        
    def controlar_fps(self):
        """Controla los FPS para no saturar la CPU"""
        tiempo_actual = cv.getTickCount()
        tiempo_transcurrido = (tiempo_actual - self.ultimo_tiempo) / cv.getTickFrequency()
        
        if tiempo_transcurrido < 1.0 / self.fps_objetivo:
            return False
            
        self.ultimo_tiempo = tiempo_actual
        return True
        
    def mostrar_resultados(self):
        # SOLO UNA VENTANA
        cv.imshow("Generador de Curvas Paramétricas", self.superficie_principal)
        
    def limpiar_lienzo(self):
        """Limpia el lienzo periódicamente"""
        if self.angulo_actual > 100:  # Limpiar cada 100 iteraciones
            self.superficie_principal = np.zeros((self.dimension_alto, self.dimension_ancho, 3), np.uint8)
            self.angulo_actual = 0
        
    def ejecutar_generador(self):
        print("🌀 Generador de Curvas Paramétricas (Versión Optimizada)")
        print("Presiona ESC para salir")
        print("Presiona 'C' para limpiar el lienzo")
        print("Presiona '+' para aumentar velocidad, '-' para disminuir")
        
        velocidad = 0.008
        
        while True:
            if not self.controlar_fps():
                continue
                
            self.actualizar_curvas()
            self.mostrar_resultados()
            
            tecla = cv.waitKey(1) & 0xFF
            if tecla == 27:  # ESC
                break
            elif tecla == ord('c'):  # Limpiar
                self.superficie_principal = np.zeros((self.dimension_alto, self.dimension_ancho, 3), np.uint8)
            elif tecla == ord('+'):  # Aumentar velocidad
                velocidad = min(0.05, velocidad + 0.001)
            elif tecla == ord('-'):  # Disminuir velocidad
                velocidad = max(0.001, velocidad - 0.001)
                
        cv.destroyAllWindows()

def main():
    generador = GeneradorCurvasOptimizado()
    generador.ejecutar_generador()

if __name__ == "__main__":
    main()
