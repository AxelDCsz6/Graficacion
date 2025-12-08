import glfw
from OpenGL.GL import glClearColor, glEnable, glClear, glLoadIdentity, glTranslatef, glRotatef, glMatrixMode
from OpenGL.GL import glBegin, glColor3f, glVertex3f, glEnd, glFlush, glViewport
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_TRIANGLES, GL_QUADS, GL_PROJECTION, GL_MODELVIEW
from OpenGL.GLU import gluPerspective
import sys

# Variables globales
window = None
angle = 0  # Declaramos angle en el nivel superior

def init():
    # Configuración inicial de OpenGL
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Color de fondo
    glEnable(GL_DEPTH_TEST)  # Activar prueba de profundidad para 3D

    # Configuración de proyección
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0, 0.1, 50.0)

    # Cambiar a la matriz de modelo para los objetos
    glMatrixMode(GL_MODELVIEW)

def draw_pyramid():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpiar pantalla y buffer de profundidad

    # Configuración de la vista de la pirámide
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5)  # Alejar la pirámide para que sea visible
    glRotatef(angle, 1, 1, 1)   # Rotar la pirámide en todos los ejes

    glBegin(GL_TRIANGLES)  # Caras triangulares de la pirámide

    # Cara frontal (rojo)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)  # Vértice superior
    glVertex3f(-1.0, -1.0, 1.0)  # Vértice inferior izquierdo
    glVertex3f(1.0, -1.0, 1.0)   # Vértice inferior derecho

    # Cara derecha (verde)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)   # Vértice superior
    glVertex3f(1.0, -1.0, 1.0)  # Vértice inferior frontal
    glVertex3f(1.0, -1.0, -1.0) # Vértice inferior trasero

    # Cara trasera (azul)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 1.0, 0.0)    # Vértice superior
    glVertex3f(1.0, -1.0, -1.0)  # Vértice inferior derecho
    glVertex3f(-1.0, -1.0, -1.0) # Vértice inferior izquierdo

    # Cara izquierda (amarillo)
    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)    # Vértice superior
    glVertex3f(-1.0, -1.0, -1.0) # Vértice inferior trasero
    glVertex3f(-1.0, -1.0, 1.0)  # Vértice inferior frontal

    glEnd()

    # Base cuadrada (magenta)
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(-1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, 1.0)
    glVertex3f(1.0, -1.0, -1.0)
    glVertex3f(-1.0, -1.0, -1.0)
    glEnd()

    glFlush()

    glfw.swap_buffers(window)  # Intercambiar buffers para animación suave
    angle += 1  # Incrementar el ángulo para rotación

def main():
    global window

    # Inicializar GLFW
    if not glfw.init():
        sys.exit()

    # Crear ventana de GLFW
    width, height = 500, 500
    window = glfw.create_window(width, height, "Pirámide 3D Rotando con GLFW", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    # Configurar el contexto de OpenGL en la ventana
    glfw.make_context_current(window)

    # Configuración de viewport y OpenGL
    glViewport(0, 0, width, height)
    init()

    # Bucle principal
    while not glfw.window_should_close(window):
        draw_pyramid()
        glfw.poll_events()

    glfw.terminate()  # Cerrar GLFW al salir

if __name__ == "__main__":
    main()