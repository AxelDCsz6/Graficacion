import glfw
import cv2
import mediapipe as mp
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# Aumentar el tamaño de la ventana para mejor visibilidad
WINDOW_WIDTH = 1280  # Aumentado de 640
WINDOW_HEIGHT = 720  # Aumentado de 480
WINDOW_TITLE = "Mascara 3D Extendida + Mediapipe"

# Factor de escala para agrandar la máscara facial
SCALE_FACTOR = 2.5
WIDTH_SCALE = 1.4   #Factor específico para ensanchar el rostro

# Conexiones para dibujar el contorno facial
contorno_cara  = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
             397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

# Cejas
LEFT_EYEBROW = [70, 63, 105, 66, 107]
RIGHT_EYEBROW = [336, 296, 334, 293, 300]

def init_glfw():
    if not glfw.init():
        raise Exception("No se pudo inicializar GLFW")
    
    # Configurar versión de OpenGL
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
    
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
    
    if not window:
        glfw.terminate()
        raise Exception("No se pudo crear la ventana GLFW")
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
    return window

# ============================================================
# Configuracion inicial de OpenGL
# ============================================================
def setup_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glPointSize(5.0)  # Aumentar tamaño de puntos
    glLineWidth(2.0)  # Aumentar grosor de líneas

def create_video_texture():
    video_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, video_tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    return video_tex

def setup_lights():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)  # Luz adicional
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Luz principal frontal
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 3, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1))
    
    # Luz de relleno lateral
    glLightfv(GL_LIGHT1, GL_POSITION, (2, 2, 2, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.7, 0.7, 0.7, 1))

# ============================================================
# Funciones de dibujo MEJORADAS con ensanchamiento
# ============================================================
def draw_sphere(x, y, z, radius, color=(1, 1, 1)):
    glPushMatrix()
    # Aplicar factor de escala global y ensanchamiento solo en X
    glTranslatef(x * SCALE_FACTOR * WIDTH_SCALE, y * SCALE_FACTOR, z * SCALE_FACTOR)
    glColor3f(*color)
    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)
    # Aumentar radio proporcionalmente (sin ensanchar las esferas, solo su posición)
    gluSphere(quad, radius * SCALE_FACTOR, 20, 20)
    gluDeleteQuadric(quad)
    glPopMatrix()

def draw_line(p1, p2, color=(1, 1, 1), width=3.0):
    """Dibuja una línea entre dos puntos 3D"""
    glDisable(GL_LIGHTING)
    glLineWidth(width)
    glColor3f(*color)
    glBegin(GL_LINES)
    # Aplicar factor de escala con ensanchamiento solo en X
    glVertex3f(p1[0] * SCALE_FACTOR * WIDTH_SCALE, p1[1] * SCALE_FACTOR, p1[2] * SCALE_FACTOR)
    glVertex3f(p2[0] * SCALE_FACTOR * WIDTH_SCALE, p2[1] * SCALE_FACTOR, p2[2] * SCALE_FACTOR)
    glEnd()
    glEnable(GL_LIGHTING)

def norm_landmark(p):
    # Normalizar y aplicar offset para centrar mejor
    # NOTA: No aplicamos WIDTH_SCALE aquí, lo aplicamos en las funciones de dibujo
    return ((p.x - 0.5) * 1.5, -(p.y - 0.5) * 1.5, p.z * 2.0)

# ============================================================
# Renderizado MEJORADO
# ============================================================
def render_video_background(frame_rgb, video_tex):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glBindTexture(GL_TEXTURE_2D, video_tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 
                 frame_rgb.shape[1], frame_rgb.shape[0],
                 0, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
    
    glColor3f(1.0, 1.0, 1.0)
    
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(0, 0)
    glTexCoord2f(1, 1); glVertex2f(1, 0)
    glTexCoord2f(1, 0); glVertex2f(1, 1)
    glTexCoord2f(0, 0); glVertex2f(0, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_face_contour(landmarks, indices, color=(0.3, 0.8, 0.4), width=2.5):
    glDisable(GL_LIGHTING)
    glLineWidth(width)
    glColor3f(*color)
    
    glBegin(GL_LINE_STRIP)
    for idx in indices:
        p = norm_landmark(landmarks[idx])
        # Aplicar factor de escala con ensanchamiento solo en X
        glVertex3f(p[0] * SCALE_FACTOR * WIDTH_SCALE, p[1] * SCALE_FACTOR, p[2] * SCALE_FACTOR)
    # Cerrar el contorno
    p = norm_landmark(landmarks[indices[0]])
    glVertex3f(p[0] * SCALE_FACTOR * WIDTH_SCALE, p[1] * SCALE_FACTOR, p[2] * SCALE_FACTOR)
    glEnd()
    
    glEnable(GL_LIGHTING)

def render_3d_mask_extended(face_landmarks):
    """Renderiza la máscara 3D extendida - VERSIÓN MEJORADA"""
    glEnable(GL_DEPTH_TEST)
    glClear(GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    # Ajustar perspectiva para mejor visualización
    gluPerspective(50, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 100)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    # Mover cámara ligeramente más atrás para ver la máscara completa
    gluLookAt(0, 0, 3.5, 0, 0, 0, 0, 1, 0)
    
    setup_lights()
    
    lm = face_landmarks.landmark
    
    # ============================================================
    # 1. CONTORNO CARA (MÁS ANCHO)
    # ============================================================
    draw_face_contour(lm, contorno_cara, color=(0.2, 0.8, 0.4), width=3.0)
    
    # ============================================================
    # 2. OJOS (MÁS BAJOS, MANTENIENDO EL ENSAÑCHAMIENTO)
    # ============================================================
    left_eye = lm[386]
    right_eye = lm[159]
    lx, ly, lz = norm_landmark(left_eye)
    rx, ry, rz = norm_landmark(right_eye)
    
    # BAJAR LOS OJOS (ajuste en Y)
    ly = ly - 0.04  # Bajar ojo izquierdo
    ry = ry - 0.04  # Bajar ojo derecho
    
    # Globos oculares (blancos) - CON AJUSTE DE POSICIÓN
    glColor3f(1.0, 1.0, 1.0)
    draw_sphere(lx, ly, lz, 0.035, (1, 1, 1))
    draw_sphere(rx, ry, rz, 0.035, (1, 1, 1))
    
    # Pupilas (azul oscuro) - CON AJUSTE DE POSICIÓN
    draw_sphere(lx, ly, lz + 0.015, 0.020, (0.1, 0.1, 0.6))
    draw_sphere(rx, ry, rz + 0.015, 0.020, (0.1, 0.1, 0.6))
    
    # Brillos en los ojos - CON AJUSTE DE POSICIÓN
    draw_sphere(lx + 0.010, ly + 0.010, lz + 0.022, 0.008, (1, 1, 1))
    draw_sphere(rx + 0.010, ry + 0.010, rz + 0.022, 0.008, (1, 1, 1))
    
    # ============================================================
    # 3. CEJAS (AJUSTADAS PARA MANTENER RELACIÓN CON OJOS)
    # ============================================================
    # Primero dibujamos las líneas de las cejas con ajuste de posición
    glDisable(GL_LIGHTING)
    glLineWidth(2.5)
    glColor3f(0.4, 0.3, 0.2)
    
    # Ceja izquierda (ajustada hacia abajo junto con los ojos)
    glBegin(GL_LINE_STRIP)
    for idx in LEFT_EYEBROW:
        px, py, pz = norm_landmark(lm[idx])
        py = py - 0.04  # Misma cantidad que los ojos
        glVertex3f(px * SCALE_FACTOR * WIDTH_SCALE, py * SCALE_FACTOR, pz * SCALE_FACTOR)
    glEnd()
    
    # Ceja derecha (ajustada hacia abajo junto con los ojos)
    glBegin(GL_LINE_STRIP)
    for idx in RIGHT_EYEBROW:
        px, py, pz = norm_landmark(lm[idx])
        py = py - 0.04  # Misma cantidad que los ojos
        glVertex3f(px * SCALE_FACTOR * WIDTH_SCALE, py * SCALE_FACTOR, pz * SCALE_FACTOR)
    glEnd()
    
    glEnable(GL_LIGHTING)
    
    # Ahora dibujamos las esferas de las cejas con ajuste
    for idx in LEFT_EYEBROW:
        px, py, pz = norm_landmark(lm[idx])
        py = py - 0.04  # Misma cantidad que los ojos
        # Nota: Usamos draw_sphere que ya aplica WIDTH_SCALE en X
        glPushMatrix()
        glTranslatef(px * SCALE_FACTOR * WIDTH_SCALE, py * SCALE_FACTOR, pz * SCALE_FACTOR)
        glColor3f(0.5, 0.4, 0.3)
        quad = gluNewQuadric()
        gluSphere(quad, 0.010 * SCALE_FACTOR, 20, 20)
        gluDeleteQuadric(quad)
        glPopMatrix()
    
    for idx in RIGHT_EYEBROW:
        px, py, pz = norm_landmark(lm[idx])
        py = py - 0.04  # Misma cantidad que los ojos
        glPushMatrix()
        glTranslatef(px * SCALE_FACTOR * WIDTH_SCALE, py * SCALE_FACTOR, pz * SCALE_FACTOR)
        glColor3f(0.5, 0.4, 0.3)
        quad = gluNewQuadric()
        gluSphere(quad, 0.010 * SCALE_FACTOR, 20, 20)
        gluDeleteQuadric(quad)
        glPopMatrix()
    
    # ============================================================
    # 4. NARIZ (CON ENSAÑCHAMIENTO)
    # ============================================================
    nose_tip = lm[1]
    nose_bridge = lm[6]
    nose_left = lm[98]
    nose_right = lm[327]
    
    nx, ny, nz = norm_landmark(nose_tip)
    nbx, nby, nbz = norm_landmark(nose_bridge)
    nlx, nly, nlz = norm_landmark(nose_left)
    nrx, nry, nrz = norm_landmark(nose_right)
    
    # Punta de la nariz (roja) - CON ENSAÑCHAMIENTO
    draw_sphere(nx, ny, nz, 0.028, (1.0, 0.4, 0.4))
    
    # Fosas nasales - CON ENSAÑCHAMIENTO
    draw_sphere(nlx, nly, nlz, 0.015, (0.9, 0.5, 0.5))
    draw_sphere(nrx, nry, nrz, 0.015, (0.9, 0.5, 0.5))
    
    # Puente de la nariz (línea más gruesa) - CON ENSAÑCHAMIENTO
    draw_line((nbx, nby, nbz), (nx, ny, nz), color=(1, 0.6, 0.6), width=4)
    
    # ============================================================
    # 5. BOCA (CON ENSAÑCHAMIENTO)
    # ============================================================
    mouth_left = lm[61]
    mouth_right = lm[291]
    mouth_top = lm[13]
    mouth_bottom = lm[14]
    
    mlx, mly, mlz = norm_landmark(mouth_left)
    mrx, mry, mrz = norm_landmark(mouth_right)
    mtx, mty, mtz = norm_landmark(mouth_top)
    mbx, mby, mbz = norm_landmark(mouth_bottom)
    
    # Comisuras (rosas) - CON ENSAÑCHAMIENTO
    draw_sphere(mlx, mly, mlz, 0.018, (1.0, 0.6, 0.7))
    draw_sphere(mrx, mry, mrz, 0.018, (1.0, 0.6, 0.7))
    
    # Labio superior e inferior - CON ENSAÑCHAMIENTO
    draw_sphere(mtx, mty, mtz, 0.015, (1.0, 0.5, 0.6))
    draw_sphere(mbx, mby, mbz, 0.015, (1.0, 0.5, 0.6))
    
    # Línea de la boca - MÁS GRUESA Y CON ENSAÑCHAMIENTO
    draw_line((mlx, mly, mlz), (mrx, mry, mrz), color=(1, 0.4, 0.5), width=4)
    
    # ============================================================
    # 6. CACHETES (CON ENSAÑCHAMIENTO)
    # ============================================================
    left_cheek = lm[234]
    right_cheek = lm[454]
    
    lcx, lcy, lcz = norm_landmark(left_cheek)
    rcx, rcy, rcz = norm_landmark(right_cheek)
    
    # Rubor en las mejillas - CON ENSAÑCHAMIENTO
    draw_sphere(lcx, lcy, lcz, 0.032, (1.0, 0.85, 0.9))
    draw_sphere(rcx, rcy, rcz, 0.032, (1.0, 0.85, 0.9))
    
    # ============================================================
    # 7. FRENTE Y BARBA (CON ENSAÑCHAMIENTO)
    # ============================================================
    forehead = lm[10]
    chin = lm[152]
    
    fx, fy, fz = norm_landmark(forehead)
    cx, cy, cz = norm_landmark(chin)
    
    # Punto en la frente - CON ENSAÑCHAMIENTO
    draw_sphere(fx, fy, fz, 0.020, (0.95, 0.95, 0.8))
    
    # Punto en la barbilla - CON ENSAÑCHAMIENTO
    draw_sphere(cx, cy, cz, 0.020, (0.8, 0.95, 0.85))
    
    # Línea entre frente y barbilla para definir rostro - CON ENSAÑCHAMIENTO
    draw_line((fx, fy, fz), (cx, cy, cz), color=(0.7, 0.9, 0.7), width=2)
    
    # Restaurar matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ============================================================
# Función principal
# ============================================================
def main():
    
    try:
        window = init_glfw()
    except Exception as e:
        print(f" Error al inicializar GLFW: {e}")
        return
    
    setup_opengl()
    video_tex = create_video_texture()
    
    mp_face = mp.solutions.face_mesh
    # Aumentar confianza de detección
    face_mesh = mp_face.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,  # Habilitar refinamiento
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(" No se pudo abrir la camara")
        glfw.terminate()
        return
    
    # Configurar resolución de cámara acorde a la ventana
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
    print(f"Camara inicializada en {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    
    frame_count = 0
    fps_timer = glfw.get_time()
    
    try:
        while not glfw.window_should_close(window):
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            # Redimensionar si es necesario
            frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = face_mesh.process(frame_rgb)
            
            glfw.poll_events()
            
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                break
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            render_video_background(frame_rgb, video_tex)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    render_3d_mask_extended(face_landmarks)
            
            glfw.swap_buffers(window)
            
            frame_count += 1
            current_time = glfw.get_time()
            if current_time - fps_timer >= 1.0:
                fps = frame_count / (current_time - fps_timer)
                glfw.set_window_title(window, f"{WINDOW_TITLE} - FPS: {fps:.1f} - Resolución: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
                frame_count = 0
                fps_timer = current_time
    
    except Exception as e:
        print(f" Error en el loop principal: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nCerrando aplicación...")
        cap.release()
        face_mesh.close()
        glfw.terminate()
      
if __name__ == "__main__":
    main()
