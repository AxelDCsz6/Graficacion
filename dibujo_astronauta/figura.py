import cv2 as cv
import numpy as np

def crear_astronauta():
    """Crea una figura de astronauta usando primitivas gráficas"""
    # Configurar lienzo
    lienzo = np.ones((800, 800, 3), np.uint8) * 255
    
    # Colores
    blanco = (255, 255, 255)
    gris_casco = (200, 200, 200)
    gris_traje = (150, 150, 150)
    negro = (0, 0, 0)
    azul_visor = (200, 100, 0)
    
    # Casco (círculo principal)
    cv.circle(lienzo, (400, 200), 120, gris_casco, -1)
    cv.circle(lienzo, (400, 200), 120, negro, 3)
    
    # Visor (elipse azul)
    cv.ellipse(lienzo, (400, 220), (80, 60), 0, 0, 360, azul_visor, -1)
    cv.ellipse(lienzo, (400, 220), (80, 60), 0, 0, 360, negro, 2)
    
    # Reflector en casco
    cv.circle(lienzo, (320, 160), 15, blanco, -1)
    
    # Torso (rectángulo con detalles)
    cv.rectangle(lienzo, (300, 320), (500, 500), gris_traje, -1)
    cv.rectangle(lienzo, (300, 320), (500, 500), negro, 2)
    
    # Panel de control en pecho
    cv.rectangle(lienzo, (350, 350), (450, 400), blanco, -1)
    cv.rectangle(lienzo, (350, 350), (450, 400), negro, 1)
    
    # Botones del panel
    for i, color in enumerate([(0, 0, 255), (0, 255, 0), (255, 0, 0)]):
        cv.circle(lienzo, (370 + i * 25, 375), 8, color, -1)
    
    # Brazos (con articulaciones)
    # Brazo izquierdo
    cv.rectangle(lienzo, (250, 350), (300, 450), gris_traje, -1)
    cv.rectangle(lienzo, (250, 350), (300, 450), negro, 2)
    cv.circle(lienzo, (275, 450), 25, gris_traje, -1)
    
    # Brazo derecho
    cv.rectangle(lienzo, (500, 350), (550, 450), gris_traje, -1)
    cv.rectangle(lienzo, (500, 350), (550, 450), negro, 2)
    cv.circle(lienzo, (525, 450), 25, gris_traje, -1)
    
    # Piernas
    # Pierna izquierda
    cv.rectangle(lienzo, (350, 500), (400, 650), gris_traje, -1)
    cv.rectangle(lienzo, (350, 500), (400, 650), negro, 2)
    
    # Pierna derecha
    cv.rectangle(lienzo, (400, 500), (450, 650), gris_traje, -1)
    cv.rectangle(lienzo, (400, 500), (450, 650), negro, 2)
    
    # Botas
    cv.rectangle(lienzo, (330, 650), (420, 670), negro, -1)
    cv.rectangle(lienzo, (380, 650), (470, 670), negro, -1)
    
    # Mochila propulsora
    cv.rectangle(lienzo, (250, 320), (300, 450), gris_traje, -1)
    cv.rectangle(lienzo, (250, 320), (300, 450), negro, 2)
    
    # Propulsores
    cv.rectangle(lienzo, (240, 450), (310, 470), (50, 50, 50), -1)
    
    return lienzo

def main():
    print("Creando figura de astronauta...")
    astronauta = crear_astronauta()
    
    cv.imshow('Astronauta Espacial', astronauta)
    cv.imwrite('astronauta.png', astronauta)
    print("Astronauta guardado como 'astronauta.png'")
    
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
