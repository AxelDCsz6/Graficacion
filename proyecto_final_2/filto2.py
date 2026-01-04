import glfw
import cv2
import mediapipe as mp
import numpy as np
import math
from OpenGL.GL import *
from OpenGL.GLU import *

# ============================================================
# CONFIGURACIÓN INICIAL 
# ============================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Filtro Robot"

SCALE_FACTOR = 2.5
WIDTH_SCALE = 1.4

# COLORES
COLOR_GRAY_BOX = (0.9, 0.9, 0.92) 
COLOR_DARK_GRAY = (0.5, 0.5, 0.55)
COLOR_CYAN = (0.0, 1.0, 1.0)
COLOR_RED = (1.0, 0.0, 0.0)

# Landmarks
LEFT_EYE_TOP = 159
LEFT_EYE_BOTTOM = 145
RIGHT_EYE_TOP = 386
RIGHT_EYE_BOTTOM = 374
MOUTH_TOP = 13
MOUTH_BOTTOM = 14

def init_glfw():
    if not glfw.init():
        raise Exception("Error GLFW")
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        raise Exception("Error Ventana")
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    return window

def setup_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glLineWidth(2.0)

def create_video_texture():
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex

def setup_lights():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 5, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

# ============================================================
# UTILIDADES
# ============================================================
def norm_landmark(p):
    return ((p.x - 0.5) * 1.5, -(p.y - 0.5) * 1.5, p.z * 2.0)

def calculate_distance(lm_list, idx1, idx2):
    p1 = lm_list[idx1]
    p2 = lm_list[idx2]
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# ============================================================
# PRIMITIVAS DE DIBUJO
# ============================================================

def draw_sphere_at(x, y, z, radius, color):
    glPushMatrix()
    glTranslatef(x * SCALE_FACTOR * WIDTH_SCALE, y * SCALE_FACTOR, z * SCALE_FACTOR)
    glColor3f(*color)
    quad = gluNewQuadric()
    gluSphere(quad, radius * SCALE_FACTOR, 16, 16)
    gluDeleteQuadric(quad)
    glPopMatrix()

def draw_tech_ring(x, y, z, radius, color, segments=16, rot_angle=0):
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(x * SCALE_FACTOR * WIDTH_SCALE, y * SCALE_FACTOR, z * SCALE_FACTOR)
    glRotatef(rot_angle, 0, 0, 1) 
    
    glColor3f(*color)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        rx = radius * math.cos(theta) * SCALE_FACTOR
        ry = radius * math.sin(theta) * SCALE_FACTOR
        glVertex3f(rx, ry, 0)
    glEnd()
    glPopMatrix()
    glEnable(GL_LIGHTING)

# ANTENA
def draw_antenna(x, y, z):
    glPushMatrix()
    glTranslatef(x * SCALE_FACTOR * WIDTH_SCALE, y * SCALE_FACTOR, z * SCALE_FACTOR)
    
    quad = gluNewQuadric()
    
    glColor3f(0.3, 0.3, 0.3)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.03 * SCALE_FACTOR, 0.02 * SCALE_FACTOR, 0.05 * SCALE_FACTOR, 10, 2)
    
    glTranslatef(0, 0, 0.05 * SCALE_FACTOR)
    glColor3f(0.6, 0.6, 0.6)
    gluCylinder(quad, 0.008 * SCALE_FACTOR, 0.008 * SCALE_FACTOR, 0.15 * SCALE_FACTOR, 8, 2)
    
    glTranslatef(0, 0, 0.15 * SCALE_FACTOR)
    glColor3f(1.0, 0.2, 0.2)
    gluSphere(quad, 0.02 * SCALE_FACTOR, 10, 10)
    
    gluDeleteQuadric(quad)
    glPopMatrix()

def draw_equalizer_mouth(center_top, center_bottom, open_ratio):
    mx, my, mz = center_top
    bx, by, bz = center_bottom
    
    cx = (mx + bx) / 2
    cy = (my + by) / 2
    cz = (mz + bz) / 2
    
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(cx * SCALE_FACTOR * WIDTH_SCALE, cy * SCALE_FACTOR, cz * SCALE_FACTOR)
    
    if open_ratio > 0.05:
        glColor3f(0.2, 1.0, 0.2)
        spacing = 0.03 * SCALE_FACTOR
        
        max_height = 0.12 * SCALE_FACTOR
        current_h = max_height * open_ratio 
        
        for i in range(-2, 3):
            bar_h = current_h
            if i % 2 == 0: bar_h *= 0.7 
            
            x_pos = i * spacing
            glBegin(GL_QUADS)
            glVertex3f(x_pos - 0.01, -bar_h, 0)
            glVertex3f(x_pos + 0.01, -bar_h, 0)
            glVertex3f(x_pos + 0.01, bar_h, 0)
            glVertex3f(x_pos - 0.01, bar_h, 0)
            glEnd()
    else:
        glColor3f(0.2, 0.2, 1.0)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        len_half = 0.06 * SCALE_FACTOR
        glVertex3f(-len_half, 0, 0)
        glVertex3f(len_half, 0, 0)
        glEnd()
        
    glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_robot_box_face(lm_list):
    top = norm_landmark(lm_list[10])
    chin = norm_landmark(lm_list[152])
    left = norm_landmark(lm_list[234])
    right = norm_landmark(lm_list[454])
    nose = norm_landmark(lm_list[1]) 
    
    cx = (left[0] + right[0]) / 2.0
    cy = (top[1] + chin[1]) / 2.0
    cz = nose[2] - 0.05 
    
    real_height = abs(top[1] - chin[1]) * SCALE_FACTOR
    
    height_half = (real_height * 1.1) / 2.0
    width_half = (real_height * 1.3) / 2.0 
    
    glPushMatrix()
    world_cx = cx * SCALE_FACTOR * WIDTH_SCALE
    world_cy = cy * SCALE_FACTOR
    world_cz = cz * SCALE_FACTOR
    
    glTranslatef(world_cx, world_cy, world_cz)
    
    glColor3f(*COLOR_GRAY_BOX)
    glBegin(GL_QUADS)
    glVertex3f(-width_half, -height_half, 0)
    glVertex3f(width_half, -height_half, 0)
    glVertex3f(width_half, height_half, 0)
    glVertex3f(-width_half, height_half, 0)
    glEnd()
    
    glDisable(GL_LIGHTING)
    glLineWidth(5.0)
    glColor3f(*COLOR_DARK_GRAY)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-width_half, -height_half, 0.01)
    glVertex3f(width_half, -height_half, 0.01)
    glVertex3f(width_half, height_half, 0.01)
    glVertex3f(-width_half, height_half, 0.01)
    glEnd()
    glEnable(GL_LIGHTING)
    
    glColor3f(0.8, 0.8, 0.8)
    screw_offset = 0.02 * SCALE_FACTOR
    screw_size = 0.015
    for sx in [-width_half + screw_offset, width_half - screw_offset]:
        for sy in [-height_half + screw_offset, height_half - screw_offset]:
            glPushMatrix()
            glTranslatef(sx, sy, 0.02)
            quad = gluNewQuadric()
            gluSphere(quad, screw_size * SCALE_FACTOR, 8, 8)
            gluDeleteQuadric(quad)
            glPopMatrix()

    glPopMatrix()

# ============================================================
# RENDER PRINCIPAL
# ============================================================
def render_robot_filter(face_landmarks):
    glEnable(GL_DEPTH_TEST)
    glClear(GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluPerspective(50, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 100)
    
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    gluLookAt(0, 0, 3.5, 0, 0, 0, 0, 1, 0)
    
    setup_lights()
    lm = face_landmarks.landmark
    
    left_eye_dist = calculate_distance(lm, LEFT_EYE_TOP, LEFT_EYE_BOTTOM)
    right_eye_dist = calculate_distance(lm, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM)
    mouth_dist = calculate_distance(lm, MOUTH_TOP, MOUTH_BOTTOM)
    
    is_blinking = (left_eye_dist < 0.015) or (right_eye_dist < 0.015)
    
    min_mouth = 0.01; max_mouth = 0.08
    open_ratio = (mouth_dist - min_mouth) / (max_mouth - min_mouth)
    open_ratio = max(0.0, min(open_ratio, 1.0))

    draw_robot_box_face(lm)

    if len(lm) > 468:
        lp = norm_landmark(lm[468]); rp = norm_landmark(lm[473])
    else:
        lp = norm_landmark(lm[159]); lp = (lp[0], lp[1]-0.03, lp[2])
        rp = norm_landmark(lm[386]); rp = (rp[0], rp[1]-0.03, rp[2])

    eye_color = COLOR_RED if is_blinking else COLOR_CYAN
    rot_anim = glfw.get_time() * 50

    if is_blinking:
        glLineWidth(4.0)
        glDisable(GL_LIGHTING)
        glColor3f(*COLOR_RED)
        glBegin(GL_LINES)
        glVertex3f((lp[0]-0.04)*SCALE_FACTOR*WIDTH_SCALE, lp[1]*SCALE_FACTOR, lp[2]*SCALE_FACTOR)
        glVertex3f((lp[0]+0.04)*SCALE_FACTOR*WIDTH_SCALE, lp[1]*SCALE_FACTOR, lp[2]*SCALE_FACTOR)
        glVertex3f((rp[0]-0.04)*SCALE_FACTOR*WIDTH_SCALE, rp[1]*SCALE_FACTOR, rp[2]*SCALE_FACTOR)
        glVertex3f((rp[0]+0.04)*SCALE_FACTOR*WIDTH_SCALE, rp[1]*SCALE_FACTOR, rp[2]*SCALE_FACTOR)
        glEnd()
        glEnable(GL_LIGHTING)
    else:
        draw_tech_ring(lp[0], lp[1], lp[2], 0.025, eye_color, 12, rot_anim)
        draw_tech_ring(lp[0], lp[1], lp[2], 0.045, eye_color, 8, -rot_anim)
        draw_sphere_at(lp[0], lp[1], lp[2], 0.01, (1,1,1))
        draw_tech_ring(rp[0], rp[1], rp[2], 0.025, eye_color, 12, rot_anim)
        draw_tech_ring(rp[0], rp[1], rp[2], 0.045, eye_color, 8, -rot_anim)
        draw_sphere_at(rp[0], rp[1], rp[2], 0.01, (1,1,1))

    mp_top = norm_landmark(lm[MOUTH_TOP])
    mp_btm = norm_landmark(lm[MOUTH_BOTTOM])
    draw_equalizer_mouth(mp_top, mp_btm, open_ratio)

    forehead = norm_landmark(lm[10])
    draw_antenna(forehead[0], forehead[1], forehead[2])

    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def render_video_background(frame_rgb, video_tex):
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glBindTexture(GL_TEXTURE_2D, video_tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, frame_rgb.shape[1], frame_rgb.shape[0],
                 0, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
    glColor3f(1, 1, 1)
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(0, 0); glTexCoord2f(1, 1); glVertex2f(1, 0)
    glTexCoord2f(1, 0); glVertex2f(1, 1); glTexCoord2f(0, 0); glVertex2f(0, 1)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    try:
        window = init_glfw()
        setup_opengl()
        video_tex = create_video_texture()
        
        mp_face = mp.solutions.face_mesh
        face_mesh = mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True,
                                   min_detection_confidence=0.7, min_tracking_confidence=0.7)
        
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
        
        while not glfw.window_should_close(window):
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)
            
            glfw.poll_events()
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS: break
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            render_video_background(frame_rgb, video_tex)
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    render_robot_filter(face_landmarks)
            
            glfw.swap_buffers(window)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        face_mesh.close()
        glfw.terminate()

if __name__ == "__main__":
    main()
