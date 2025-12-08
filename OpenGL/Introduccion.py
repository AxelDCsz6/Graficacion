import glfw
from OpenGL.GL import *
import math

def main():
    if not glfw.init():
        return

    window = glfw.create_window(500, 500, "OpenGL con GLFW", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)

        # --- Cuadrado ---
        glBegin(GL_QUADS)
        glColor3f(1.0, 1.0, 0.0)  # Amarillo
        glVertex2f(-0.5, -0.5)
        glVertex2f(0.5, -0.5)
        glVertex2f(0.5, 0.5)
        glVertex2f(-0.5, 0.5)
        glEnd()

        # --- Triángulo ---
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)  # Rojo
        glVertex2f(-0.8, -0.8)
        glColor3f(0.0, 1.0, 0.0)  # Verde
        glVertex2f(-0.2, -0.8)
        glColor3f(0.0, 0.0, 1.0)  # Azul
        glVertex2f(-0.5, -0.2)
        glEnd()

        # --- Triángulo rotado ---
        glPushMatrix()
        glTranslatef(0.5, 0.0, 0.0)  # mover a la derecha
        glRotatef(45, 0.0, 0.0, 1.0)  # rotar 45 grados
        glBegin(GL_TRIANGLES)
        glColor3f(0.0, 1.0, 1.0)  # Cian
        glVertex2f(-0.3, -0.3)
        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glVertex2f(0.3, -0.3)
        glColor3f(1.0, 1.0, 1.0)  # Blanco
        glVertex2f(0.0, 0.3)
        glEnd()
        glPopMatrix()

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
