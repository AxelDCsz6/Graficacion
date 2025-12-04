import cv2 as cv
import numpy as np

class JuegoRebote:
    def __init__(self, ancho=500, alto=500):
        self.ancho_juego = ancho
        self.alto_juego = alto
        self.lienzo_juego = np.ones((alto, ancho, 3), np.uint8) * 255
        
        # Configuración de la pelota
        self.posicion_x, self.posicion_y = ancho // 2, alto // 2
        self.velocidad_x, self.velocidad_y = 5, 5
        self.radio_pelota = 5
        self.color_pelota = (0, 0, 255)
        
    def actualizar_estado_juego(self):
        # Limpiar lienzo
        self.lienzo_juego[:] = 255
        
        # Dibujar elemento principal
        cv.circle(self.lienzo_juego, (self.posicion_x, self.posicion_y), 
                 self.radio_pelota, self.color_pelota, -1)
        
        # Actualizar posición
        self.posicion_x += self.velocidad_x
        self.posicion_y += self.velocidad_y
        
        # Detectar colisiones con bordes
        if (self.posicion_x - self.radio_pelota <= 0 or 
            self.posicion_x + self.radio_pelota >= self.ancho_juego):
            self.velocidad_x = -self.velocidad_x
            
        if (self.posicion_y - self.radio_pelota <= 0 or 
            self.posicion_y + self.radio_pelota >= self.alto_juego):
            self.velocidad_y = -self.velocidad_y
            
    def ejecutar_juego(self):
        print("🎮 Juego de Rebote activado")
        print("Presiona ESC para salir")
        
        while True:
            self.actualizar_estado_juego()
            
            cv.imshow('Juego de Rebote Dinámico', self.lienzo_juego)
            
            tecla_presionada = cv.waitKey(30)
            if tecla_presionada == 27:  # Tecla ESC
                break
                
        cv.destroyAllWindows()
        print("Juego finalizado")

def main():
    juego_principal = JuegoRebote()
    juego_principal.ejecutar_juego()

if __name__ == "__main__":
    main()
