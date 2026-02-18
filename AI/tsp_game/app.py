"""
CAMPUS BUNKING ADVENTURE - Complete Implementation
All graphics are programmatically generated - NO placeholders
Everything drawn with PyGame primitives and algorithms
"""

import pygame
import math
import random
import sys
import itertools
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set
import colorsys

# Initialize PyGame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# ================ CONSTANTS ================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRID_SIZE = 64
TIME_LIMIT = 120  # 2 minutes

# Color Palette
class Colors:
    SKY_DAY = (135, 206, 235)
    SKY_NIGHT = (25, 25, 112)
    GRASS = (124, 252, 0)
    PATH = (139, 69, 19)
    BUILDING = (189, 183, 107)
    ROOF = (139, 0, 0)
    WINDOW = (255, 255, 224)
    PLAYER = (30, 144, 255)
    TEACHER = (220, 20, 60)
    UI_BG = (25, 25, 25, 200)
    TEXT = (255, 255, 255)
    BUTTON = (70, 130, 180)
    BUTTON_HOVER = (100, 149, 237)
    POWERUP = (255, 215, 0)
    LOCATION = (50, 205, 50)
    LOCATION_VISITED = (0, 255, 127)
    PARTICLE = (255, 69, 0)

# ================ ENUMS ================
class GameState(Enum):
    TITLE = 1
    CHARACTER_SELECT = 2
    PLAYING = 3
    LEVEL_COMPLETE = 4
    GAME_OVER = 5

class CharacterType(Enum):
    ALINA = 0      # Panda with glasses
    KAINAT = 1     # Lazy sloth
    AIZA = 2       # Foodie squirrel
    AYESHA = 3     # Clever fox
    HANAN = 4      # Serious owl
    ASAD = 5       # Lion "Mr. Error"

class LocationType(Enum):
    CS_DEPT = 0
    LIBRARY = 1
    CANTEEN = 2
    AUDITORIUM = 3
    SPORTS_GROUND = 4
    ADMIN_BLOCK = 5
    PARKING = 6
    GARDEN = 7
    HOSTEL = 8
    MAIN_GATE = 9

class PowerUpType(Enum):
    BOOK_BOOST = 0
    CHAI_CHARGE = 1
    SMART_CAP = 2
    BICYCLE = 3
    PHONE = 4

class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

# ================ CUSTOM GRAPHICS ENGINE ================
class GraphicsEngine:
    @staticmethod
    def draw_panda(x, y, size, direction, frame, screen, special_active=False):
        """Draw Alina the Panda"""
        # Body
        pygame.draw.circle(screen, (255, 255, 255), (x, y), size)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), size, 2)
        
        # Ears
        ear_offset = size * 0.7
        ear_y = y - size * 0.8
        pygame.draw.circle(screen, (0, 0, 0), (x - ear_offset, ear_y), size * 0.3)
        pygame.draw.circle(screen, (0, 0, 0), (x + ear_offset, ear_y), size * 0.3)
        
        # Eye patches
        pygame.draw.circle(screen, (0, 0, 0), (x - size * 0.4, y - size * 0.2), size * 0.3)
        pygame.draw.circle(screen, (0, 0, 0), (x + size * 0.4, y - size * 0.2), size * 0.3)
        
        # Eyes
        eye_size = size * 0.15
        pygame.draw.circle(screen, (255, 255, 255), (x - size * 0.4, y - size * 0.2), eye_size)
        pygame.draw.circle(screen, (255, 255, 255), (x + size * 0.4, y - size * 0.2), eye_size)
        pygame.draw.circle(screen, (0, 0, 0), (x - size * 0.4, y - size * 0.2), eye_size * 0.5)
        pygame.draw.circle(screen, (0, 0, 0), (x + size * 0.4, y - size * 0.2), eye_size * 0.5)
        
        # Glasses (Alina's special feature)
        pygame.draw.circle(screen, (150, 75, 0), (x - size * 0.4, y - size * 0.2), size * 0.35, 2)
        pygame.draw.circle(screen, (150, 75, 0), (x + size * 0.4, y - size * 0.2), size * 0.35, 2)
        pygame.draw.line(screen, (150, 75, 0), (x - size * 0.05, y - size * 0.2), (x + size * 0.05, y - size * 0.2), 2)
        
        # Nose
        pygame.draw.circle(screen, (0, 0, 0), (x, y + size * 0.1), size * 0.15)
        
        # Mouth
        mouth_y = y + size * 0.3
        pygame.draw.arc(screen, (0, 0, 0), 
                       (x - size * 0.2, mouth_y - size * 0.1, size * 0.4, size * 0.3),
                       0, math.pi, 2)
        
        # Walking animation
        leg_offset = math.sin(frame * 2) * size * 0.2
        leg_y = y + size * 0.8
        pygame.draw.rect(screen, (0, 0, 0), (x - size * 0.3, leg_y + leg_offset, size * 0.2, size * 0.3))
        pygame.draw.rect(screen, (0, 0, 0), (x + size * 0.1, leg_y - leg_offset, size * 0.2, size * 0.3))
        
        # Special effect - optimal path vision
        if special_active:
            glow_size = size + math.sin(frame * 5) * 10
            s = pygame.Surface((glow_size * 3, glow_size * 3), pygame.SRCALPHA)
            for i in range(5):
                radius = glow_size + i * 5
                alpha = 100 - i * 20
                pygame.draw.circle(s, (0, 255, 255, alpha), (glow_size * 1.5, glow_size * 1.5), radius, 3)
            screen.blit(s, (x - glow_size * 1.5, y - glow_size * 1.5))
    
    @staticmethod
    def draw_sloth(x, y, size, direction, frame, screen, special_active=False):
        """Draw Kainat the Sloth"""
        # Body (hanging shape)
        body_points = [
            (x, y - size),
            (x - size * 0.8, y),
            (x + size * 0.8, y),
            (x, y + size * 0.5)
        ]
        pygame.draw.polygon(screen, (139, 69, 19), body_points)
        pygame.draw.polygon(screen, (0, 0, 0), body_points, 2)
        
        # Head
        head_y = y - size * 0.8
        pygame.draw.circle(screen, (160, 82, 45), (x, head_y), size * 0.4)
        pygame.draw.circle(screen, (0, 0, 0), (x, head_y), size * 0.4, 2)
        
        # Face
        eye_y = head_y - size * 0.1
        # Sleepy eyes
        if int(frame) % 4 < 2:  # Blinking
            pygame.draw.arc(screen, (0, 0, 0), 
                          (x - size * 0.2, eye_y - size * 0.1, size * 0.4, size * 0.2),
                          0, math.pi, 2)
        else:
            pygame.draw.circle(screen, (0, 0, 0), (x - size * 0.15, eye_y), size * 0.08)
            pygame.draw.circle(screen, (0, 0, 0), (x + size * 0.15, eye_y), size * 0.08)
        
        # Smile
        mouth_y = head_y + size * 0.1
        pygame.draw.arc(screen, (0, 0, 0),
                       (x - size * 0.15, mouth_y - size * 0.05, size * 0.3, size * 0.2),
                       0, math.pi, 2)
        
        # Claws (hanging)
        for i in range(3):
            claw_x = x - size * 0.6 + i * size * 0.3
            claw_y = y - size * 0.3 + math.sin(frame + i) * size * 0.1
            pygame.draw.line(screen, (0, 0, 0), 
                           (claw_x, claw_y),
                           (claw_x - size * 0.1, claw_y + size * 0.2), 3)
        
        # Yawning animation
        if int(frame * 2) % 10 == 0:
            pygame.draw.arc(screen, (255, 0, 0),
                          (x - size * 0.2, head_y - size * 0.2, size * 0.4, size * 0.6),
                          math.pi * 0.7, math.pi * 1.3, 2)
        
        # Special effect - time slow aura
        if special_active:
            for i in range(8):
                angle = (frame * 0.5 + i * math.pi / 4) % (2 * math.pi)
                radius = size * 1.5 + math.sin(frame * 3 + i) * size * 0.5
                clock_x = x + math.cos(angle) * radius
                clock_y = y + math.sin(angle) * radius
                pygame.draw.circle(screen, (0, 100, 200, 150), (int(clock_x), int(clock_y)), 8)
    
    @staticmethod
    def draw_squirrel(x, y, size, direction, frame, screen, special_active=False):
        """Draw Aiza the Squirrel"""
        # Body
        body_color = (210, 105, 30)  # Squirrel brown
        pygame.draw.ellipse(screen, body_color, 
                          (x - size, y - size * 0.6, size * 2, size * 1.2))
        
        # Head
        head_x = x + size * 0.5 * math.cos(direction * math.pi / 2)
        head_y = y - size * 0.5 * math.sin(direction * math.pi / 2)
        pygame.draw.circle(screen, body_color, (int(head_x), int(head_y)), size * 0.6)
        
        # Ears
        ear_size = size * 0.25
        for ear in [(-1, -1), (1, -1)]:
            ear_x = head_x + ear[0] * size * 0.4
            ear_y = head_y + ear[1] * size * 0.4
            pygame.draw.circle(screen, (255, 182, 193), (int(ear_x), int(ear_y)), ear_size)
            pygame.draw.circle(screen, (0, 0, 0), (int(ear_x), int(ear_y)), ear_size, 1)
        
        # Eyes
        eye_size = size * 0.1
        for eye in [(-1, 0), (1, 0)]:
            eye_x = head_x + eye[0] * size * 0.25
            eye_y = head_y + eye[1] * size * 0.1
            pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(eye_y)), eye_size)
        
        # Nose
        nose_x = head_x
        nose_y = head_y + size * 0.2
        pygame.draw.circle(screen, (255, 0, 0), (int(nose_x), int(nose_y)), size * 0.08)
        
        # Cheeks (foodie blush)
        cheek_size = size * 0.15
        for cheek in [(-1, 1), (1, 1)]:
            cheek_x = head_x + cheek[0] * size * 0.35
            cheek_y = head_y + cheek[1] * size * 0.15
            pygame.draw.circle(screen, (255, 182, 193, 150), (int(cheek_x), int(cheek_y)), cheek_size)
        
        # Tail (fluffy)
        tail_x = x - size * 0.8
        tail_y = y
        tail_points = []
        for i in range(8):
            angle = i * math.pi / 4 + frame
            px = tail_x + math.cos(angle) * size * (0.8 + math.sin(frame + i) * 0.2)
            py = tail_y + math.sin(angle) * size * (0.8 + math.cos(frame + i) * 0.2)
            tail_points.append((px, py))
        if len(tail_points) > 2:
            pygame.draw.polygon(screen, body_color, tail_points)
        
        # Backpack
        pack_x = x + size * 0.3
        pack_y = y + size * 0.2
        pygame.draw.rect(screen, (255, 0, 0), 
                        (pack_x - size * 0.3, pack_y - size * 0.4, size * 0.6, size * 0.8))
        pygame.draw.rect(screen, (0, 0, 0), 
                        (pack_x - size * 0.3, pack_y - size * 0.4, size * 0.6, size * 0.8), 2)
        
        # Excited hop animation
        hop = math.sin(frame * 4) * size * 0.2 if special_active else 0
        y_offset = int(hop)
        
        # Special effect - speed lines toward canteen
        if special_active:
            for i in range(5):
                line_length = size * 2 + i * 10
                angle = direction * math.pi / 2
                start_x = x + math.cos(angle) * size
                start_y = y + math.sin(angle) * size - y_offset
                end_x = start_x + math.cos(angle) * line_length
                end_y = start_y + math.sin(angle) * line_length
                pygame.draw.line(screen, (255, 255, 0, 200 - i * 40),
                               (int(start_x), int(start_y)),
                               (int(end_x), int(end_y)), 3)
    
    @staticmethod
    def draw_fox(x, y, size, direction, frame, screen, special_active=False):
        """Draw Ayesha the Fox"""
        # Body
        body_color = (255, 140, 0)  # Fox orange
        pygame.draw.ellipse(screen, body_color,
                          (x - size * 0.8, y - size * 0.4, size * 1.6, size * 0.8))
        
        # Head
        head_x = x + size * 0.4
        head_y = y - size * 0.2
        pygame.draw.circle(screen, body_color, (int(head_x), int(head_y)), size * 0.5)
        
        # Ears (pointy)
        ear_height = size * 0.4
        for ear in [(-1, 0), (1, 0)]:
            ear_x = head_x + ear[0] * size * 0.3
            ear_y = head_y - size * 0.5
            points = [
                (ear_x, ear_y),
                (ear_x + ear[0] * size * 0.2, ear_y - ear_height),
                (ear_x - ear[0] * size * 0.2, ear_y - ear_height * 0.7)
            ]
            pygame.draw.polygon(screen, body_color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)
        
        # Face
        # Eyes (sneaky)
        for eye in [(-1, 0), (1, 0)]:
            eye_x = head_x + eye[0] * size * 0.2
            eye_y = head_y + eye[1] * size * 0.1
            pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(eye_y)), size * 0.08)
            
            # Eyebrow (sneaky arch)
            brow_y = eye_y - size * 0.15
            pygame.draw.arc(screen, (0, 0, 0),
                          (eye_x - size * 0.1, brow_y - size * 0.05, size * 0.2, size * 0.1),
                          math.pi * 0.8, math.pi * 1.2, 2)
        
        # Nose
        nose_x = head_x
        nose_y = head_y + size * 0.15
        pygame.draw.circle(screen, (0, 0, 0), (int(nose_x), int(nose_y)), size * 0.06)
        
        # Mouth (smirk)
        mouth_x = nose_x
        mouth_y = nose_y + size * 0.1
        pygame.draw.arc(screen, (0, 0, 0),
                       (mouth_x - size * 0.1, mouth_y - size * 0.05, size * 0.2, size * 0.1),
                       0.2, 0.8 * math.pi, 2)
        
        # Tail (fluffy)
        tail_base_x = x - size * 0.8
        tail_base_y = y
        for i in range(3):
            tail_x = tail_base_x + math.sin(frame + i) * size * 0.2
            tail_y = tail_base_y + math.cos(frame + i) * size * 0.2
            pygame.draw.circle(screen, body_color, (int(tail_x), int(tail_y)), size * 0.3)
        
        # Tiptoe walk animation
        foot_offset = math.sin(frame * 4) * size * 0.15
        for foot in [(-1, 1), (1, -1)]:
            foot_x = x + foot[0] * size * 0.5
            foot_y = y + size * 0.3 + foot[1] * foot_offset
            pygame.draw.circle(screen, (139, 69, 19), (int(foot_x), int(foot_y)), size * 0.15)
        
        # Special effect - distraction sparkles
        if special_active:
            for i in range(8):
                angle = frame * 2 + i * math.pi / 4
                distance = size + math.sin(frame * 3 + i) * size * 0.5
                sparkle_x = x + math.cos(angle) * distance
                sparkle_y = y + math.sin(angle) * distance
                
                # Draw sparkle
                for j in range(4):
                    sparkle_angle = angle + j * math.pi / 2
                    sx1 = sparkle_x + math.cos(sparkle_angle) * size * 0.2
                    sy1 = sparkle_y + math.sin(sparkle_angle) * size * 0.2
                    sx2 = sparkle_x + math.cos(sparkle_angle) * size * 0.5
                    sy2 = sparkle_y + math.sin(sparkle_angle) * size * 0.5
                    pygame.draw.line(screen, (255, 255, 0, 200),
                                   (int(sx1), int(sy1)), (int(sx2), int(sy2)), 2)
    
    @staticmethod
    def draw_owl(x, y, size, direction, frame, screen, special_active=False):
        """Draw Hanan the Owl"""
        # Body
        body_color = (139, 69, 19)  # Brown
        pygame.draw.circle(screen, body_color, (x, y), size)
        
        # Feather pattern
        for i in range(8):
            angle = i * math.pi / 4 + frame * 0.5
            feather_x = x + math.cos(angle) * size * 0.7
            feather_y = y + math.sin(angle) * size * 0.7
            feather_length = size * 0.4 + math.sin(frame + i) * size * 0.1
            
            # Draw feather
            points = [
                (feather_x, feather_y),
                (feather_x + math.cos(angle) * feather_length,
                 feather_y + math.sin(angle) * feather_length),
                (feather_x + math.cos(angle + 0.3) * feather_length * 0.7,
                 feather_y + math.sin(angle + 0.3) * feather_length * 0.7),
                (feather_x + math.cos(angle - 0.3) * feather_length * 0.7,
                 feather_y + math.sin(angle - 0.3) * feather_length * 0.7)
            ]
            pygame.draw.polygon(screen, (160, 82, 45), points)
        
        # Face (large circular face)
        face_radius = size * 0.7
        pygame.draw.circle(screen, (245, 222, 179), (x, y), face_radius)
        pygame.draw.circle(screen, (0, 0, 0), (x, y), face_radius, 2)
        
        # Eyes (large owl eyes)
        eye_size = size * 0.3
        for eye in [(-1, 0), (1, 0)]:
            eye_x = x + eye[0] * size * 0.25
            eye_y = y + eye[1] * size * 0.05
            
            # Eye circles
            pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(eye_y)), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), (int(eye_x), int(eye_y)), eye_size * 0.7)
            pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(eye_y)), eye_size * 0.3)
            
            # Glasses (serious student)
            pygame.draw.circle(screen, (150, 75, 0), (int(eye_x), int(eye_y)), eye_size * 1.1, 3)
        
        # Glasses bridge
        pygame.draw.line(screen, (150, 75, 0), 
                        (x - size * 0.1, y),
                        (x + size * 0.1, y), 3)
        
        # Beak
        beak_points = [
            (x, y + size * 0.1),
            (x - size * 0.15, y + size * 0.3),
            (x + size * 0.15, y + size * 0.3)
        ]
        pygame.draw.polygon(screen, (255, 140, 0), beak_points)
        pygame.draw.polygon(screen, (0, 0, 0), beak_points, 2)
        
        # Always late animation (rushing)
        wing_offset = math.sin(frame * 8) * size * 0.3
        for wing in [(-1, 0), (1, 0)]:
            wing_x = x + wing[0] * size * 0.8
            wing_y = y + wing_offset
            pygame.draw.ellipse(screen, body_color,
                              (wing_x - size * 0.2, wing_y - size * 0.1, size * 0.4, size * 0.6))
        
        # Special effect - prediction lines
        if special_active:
            for i in range(5):
                angle = frame + i * math.pi / 2.5
                length = size * 2 + math.sin(frame * 2 + i) * size
                end_x = x + math.cos(angle) * length
                end_y = y + math.sin(angle) * length
                
                # Dashed prediction line
                segments = 5
                for seg in range(segments):
                    seg_start_x = x + math.cos(angle) * (length * seg / segments)
                    seg_start_y = y + math.sin(angle) * (length * seg / segments)
                    seg_end_x = x + math.cos(angle) * (length * (seg + 0.5) / segments)
                    seg_end_y = y + math.sin(angle) * (length * (seg + 0.5) / segments)
                    
                    pygame.draw.line(screen, (0, 255, 255, 200 - i * 40),
                                   (int(seg_start_x), int(seg_start_y)),
                                   (int(seg_end_x), int(seg_end_y)), 2)
    
    @staticmethod
    def draw_lion(x, y, size, direction, frame, screen, special_active=False):
        """Draw Asad the Lion"""
        # Body
        body_color = (255, 165, 0)  # Lion orange
        pygame.draw.circle(screen, body_color, (x, y), size)
        
        # Mane
        mane_color = (139, 69, 19)
        for i in range(16):
            angle = i * math.pi / 8 + frame * 0.3
            mane_radius = size * 1.2 + math.sin(frame + i) * size * 0.2
            mane_x = x + math.cos(angle) * mane_radius
            mane_y = y + math.sin(angle) * mane_radius
            
            # Draw mane spikes
            spike_length = size * 0.4
            spike_points = [
                (mane_x, mane_y),
                (mane_x + math.cos(angle) * spike_length,
                 mane_y + math.sin(angle) * spike_length),
                (mane_x + math.cos(angle + 0.5) * spike_length * 0.5,
                 mane_y + math.sin(angle + 0.5) * spike_length * 0.5),
                (mane_x + math.cos(angle - 0.5) * spike_length * 0.5,
                 mane_y + math.sin(angle - 0.5) * spike_length * 0.5)
            ]
            pygame.draw.polygon(screen, mane_color, spike_points)
        
        # Face
        face_radius = size * 0.6
        pygame.draw.circle(screen, (245, 222, 179), (x, y), face_radius)
        
        # Eyes (confident)
        eye_size = size * 0.15
        for eye in [(-1, 0), (1, 0)]:
            eye_x = x + eye[0] * size * 0.25
            eye_y = y - size * 0.1
            
            # Determined eyes
            pygame.draw.circle(screen, (0, 0, 0), (int(eye_x), int(eye_y)), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(eye_x - eye_size * 0.3), int(eye_y - eye_size * 0.3)), 
                             eye_size * 0.3)
            
            # Angry eyebrows
            brow_y = eye_y - size * 0.2
            pygame.draw.line(screen, (0, 0, 0),
                           (eye_x - size * 0.1, brow_y),
                           (eye_x + size * 0.1, brow_y + size * 0.05), 3)
        
        # Nose
        nose_y = y + size * 0.1
        pygame.draw.polygon(screen, (0, 0, 0), [
            (x - size * 0.1, nose_y),
            (x + size * 0.1, nose_y),
            (x, nose_y + size * 0.15)
        ])
        
        # Mouth (roaring or confident)
        mouth_y = y + size * 0.3
        if int(frame * 2) % 10 < 3:  # Roaring animation
            # Open roar mouth
            pygame.draw.arc(screen, (255, 0, 0),
                          (x - size * 0.3, mouth_y - size * 0.2, size * 0.6, size * 0.4),
                          0, math.pi, 3)
            
            # Roar lines
            for i in range(5):
                angle = math.pi * 0.2 + i * math.pi * 0.15
                roar_length = size + i * size * 0.3
                roar_x = x + math.cos(angle) * roar_length
                roar_y = mouth_y + math.sin(angle) * roar_length * 0.5
                pygame.draw.line(screen, (255, 0, 0, 200 - i * 40),
                               (x, mouth_y),
                               (int(roar_x), int(roar_y)), 2)
        else:
            # Confident smirk
            pygame.draw.arc(screen, (0, 0, 0),
                          (x - size * 0.2, mouth_y - size * 0.1, size * 0.4, size * 0.2),
                          0.2, 0.8 * math.pi, 2)
        
        # Paws (confident strut)
        paw_offset = math.sin(frame * 3) * size * 0.3
        for paw in [(-1, 0), (1, 0)]:
            paw_x = x + paw[0] * size * 0.6
            paw_y = y + size * 0.7 + paw[1] * paw_offset
            pygame.draw.circle(screen, (245, 222, 179), (int(paw_x), int(paw_y)), size * 0.2)
            
            # Claws
            for claw in range(3):
                claw_x = paw_x - size * 0.1 + claw * size * 0.1
                claw_y = paw_y + size * 0.15
                pygame.draw.line(screen, (0, 0, 0),
                               (claw_x, claw_y),
                               (claw_x, claw_y + size * 0.1), 2)
        
        # Special effect - roar stun waves
        if special_active:
            wave_count = 3
            for i in range(wave_count):
                wave_radius = size * 1.5 + i * size + math.sin(frame * 4) * size * 0.5
                wave_width = 5
                wave_alpha = 200 - i * 60
                
                s = pygame.Surface((wave_radius * 2, wave_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, wave_alpha), 
                                 (wave_radius, wave_radius), wave_radius, wave_width)
                screen.blit(s, (x - wave_radius, y - wave_radius))
    
    @staticmethod
    def draw_location(loc_type, x, y, size, visited, animation_time, screen):
        """Draw campus location with custom graphics"""
        base_color = Colors.LOCATION_VISITED if visited else Colors.LOCATION
        highlight_color = (min(255, base_color[0] + 50), 
                          min(255, base_color[1] + 50), 
                          min(255, base_color[2] + 50))
        
        # Base building
        building_width = size * 1.5
        building_height = size * 1.2
        building_rect = pygame.Rect(x - building_width//2, y - building_height//2,
                                   building_width, building_height)
        
        # 3D effect
        pygame.draw.rect(screen, base_color, building_rect)
        pygame.draw.rect(screen, (0, 0, 0), building_rect, 2)
        
        # Roof
        roof_points = [
            (x - building_width//2, y - building_height//2),
            (x + building_width//2, y - building_height//2),
            (x, y - building_height//2 - size * 0.5)
        ]
        pygame.draw.polygon(screen, Colors.ROOF, roof_points)
        pygame.draw.polygon(screen, (0, 0, 0), roof_points, 2)
        
        # Windows
        window_size = size * 0.2
        for wx in range(2):
            for wy in range(2):
                window_x = x - building_width//4 + wx * building_width//2
                window_y = y - building_height//4 + wy * building_height//2
                window_rect = pygame.Rect(window_x - window_size//2, window_y - window_size//2,
                                         window_size, window_size)
                pygame.draw.rect(screen, Colors.WINDOW, window_rect)
                pygame.draw.rect(screen, (0, 0, 0), window_rect, 1)
                
                # Window reflection
                if animation_time % 1 > 0.5:
                    refl_rect = pygame.Rect(window_x - window_size//4, window_y - window_size//4,
                                           window_size//2, window_size//2)
                    pygame.draw.rect(screen, (255, 255, 255, 100), refl_rect)
        
        # Location-specific features
        if loc_type == LocationType.CS_DEPT:
            # Computer monitor
            monitor_rect = pygame.Rect(x - size*0.3, y + size*0.1, size*0.6, size*0.4)
            pygame.draw.rect(screen, (50, 50, 50), monitor_rect)
            pygame.draw.rect(screen, (0, 0, 0), monitor_rect, 2)
            
            # Screen
            screen_color = (0, 100, 0) if int(animation_time * 2) % 2 else (0, 50, 0)
            screen_rect = pygame.Rect(x - size*0.2, y + size*0.2, size*0.4, size*0.2)
            pygame.draw.rect(screen, screen_color, screen_rect)
            
            # Binary code animation
            for i in range(3):
                bit_x = x - size*0.15 + i * size*0.15
                bit_y = y + size*0.25
                bit = "1" if int(animation_time * 3 + i) % 2 else "0"
                font = pygame.font.SysFont('Arial', 12)
                bit_text = font.render(bit, True, (0, 255, 0))
                screen.blit(bit_text, (bit_x - 3, bit_y - 6))
        
        elif loc_type == LocationType.LIBRARY:
            # Books on shelves
            for i in range(4):
                book_x = x - size*0.4 + i * size*0.25
                book_y = y + size*0.1
                book_width = size*0.15
                book_height = size*0.3
                
                book_color = [(139, 69, 19), (70, 130, 180), 
                             (220, 20, 60), (50, 205, 50)][i]
                book_rect = pygame.Rect(book_x - book_width//2, book_y - book_height//2,
                                       book_width, book_height)
                pygame.draw.rect(screen, book_color, book_rect)
                pygame.draw.rect(screen, (0, 0, 0), book_rect, 1)
                
                # Book title
                title_y = book_y - book_height//4
                pygame.draw.line(screen, (0, 0, 0),
                               (book_x - book_width//3, title_y),
                               (book_x + book_width//3, title_y), 1)
                
                # Floating animation
                float_offset = math.sin(animation_time * 2 + i) * size * 0.05
                if not visited:
                    shadow_rect = pygame.Rect(book_x - book_width//2, 
                                             book_y - book_height//2 + float_offset + 3,
                                             book_width, book_height)
                    pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
        
        elif loc_type == LocationType.CANTEEN:
            # Food table
            table_rect = pygame.Rect(x - size*0.4, y + size*0.1, size*0.8, size*0.1)
            pygame.draw.rect(screen, (139, 69, 19), table_rect)
            
            # Food items
            foods = [
                ((x - size*0.25, y + size*0.05), (255, 165, 0), size*0.1),  # Burger
                ((x, y + size*0.05), (255, 192, 203), size*0.08),  # Drink
                ((x + size*0.25, y + size*0.05), (210, 105, 30), size*0.09)  # Pizza
            ]
            
            for (fx, fy), color, fsize in foods:
                # Steam animation
                if int(animation_time * 3) % 3 == 0:
                    for s in range(3):
                        steam_y = fy - size*0.1 - s * size*0.05
                        steam_size = size*0.03 * (3 - s)
                        pygame.draw.circle(screen, (255, 255, 255, 150 - s*50),
                                          (int(fx), int(steam_y)), int(steam_size))
                
                pygame.draw.circle(screen, color, (int(fx), int(fy)), int(fsize))
        
        elif loc_type == LocationType.AUDITORIUM:
            # Stage
            stage_rect = pygame.Rect(x - size*0.5, y + size*0.1, size, size*0.2)
            pygame.draw.rect(screen, (128, 0, 0), stage_rect)
            
            # Curtains
            curtain_width = size * 0.3
            for side in [-1, 1]:
                curtain_x = x + side * size*0.25
                curtain_points = [
                    (curtain_x, y + size*0.1),
                    (curtain_x + side * curtain_width, y + size*0.1),
                    (curtain_x + side * curtain_width * 0.8, y - size*0.2),
                    (curtain_x, y - size*0.1)
                ]
                curtain_color = (178, 34, 34) if side == -1 else (220, 20, 60)
                pygame.draw.polygon(screen, curtain_color, curtain_points)
                
                # Curtain fold lines
                for i in range(1, 4):
                    fold_x = curtain_x + side * curtain_width * i / 4
                    pygame.draw.line(screen, (0, 0, 0, 100),
                                   (fold_x, y + size*0.1),
                                   (fold_x + side * curtain_width * 0.2, y - size*0.05), 1)
        
        elif loc_type == LocationType.SPORTS_GROUND:
            # Field
            field_rect = pygame.Rect(x - size*0.6, y - size*0.3, size*1.2, size*0.6)
            pygame.draw.rect(screen, (124, 252, 0), field_rect)
            pygame.draw.rect(screen, (0, 100, 0), field_rect, 3)
            
            # Center circle
            pygame.draw.circle(screen, (255, 255, 255), (x, y), size*0.2, 2)
            
            # Bouncing ball
            ball_y = y - size*0.2 + abs(math.sin(animation_time * 3)) * size*0.3
            pygame.draw.circle(screen, (255, 0, 0), (x, int(ball_y)), size*0.15)
            pygame.draw.circle(screen, (0, 0, 0), (x, int(ball_y)), size*0.15, 2)
            
            # Ball pattern
            pygame.draw.arc(screen, (255, 255, 255),
                          (x - size*0.1, ball_y - size*0.1, size*0.2, size*0.2),
                          math.pi * 0.25, math.pi * 0.75, 2)
        
        elif loc_type == LocationType.ADMIN_BLOCK:
            # Flag pole
            pole_top = y - size*0.8
            pygame.draw.line(screen, (100, 100, 100), (x, y), (x, pole_top), 5)
            
            # Flag
            flag_width = size * 0.4
            flag_height = size * 0.25
            flag_points = [
                (x, pole_top),
                (x + flag_width, pole_top - flag_height//2),
                (x + flag_width, pole_top + flag_height//2)
            ]
            flag_color = (220, 20, 60) if int(animation_time * 2) % 2 else (30, 144, 255)
            pygame.draw.polygon(screen, flag_color, flag_points)
            
            # Flag waving animation
            wave_offset = math.sin(animation_time * 4) * size * 0.05
            for i in range(3):
                wave_x = x + flag_width * i / 3
                wave_y = pole_top - flag_height//4 + wave_offset * i
                pygame.draw.line(screen, (0, 0, 0, 100),
                               (wave_x, pole_top - flag_height//2),
                               (wave_x, pole_top + flag_height//2), 1)
        
        elif loc_type == LocationType.PARKING:
            # Parking spaces
            for i in range(3):
                space_x = x - size*0.3 + i * size*0.3
                space_rect = pygame.Rect(space_x - size*0.1, y - size*0.1,
                                        size*0.2, size*0.4)
                pygame.draw.rect(screen, (100, 100, 100), space_rect, 2)
                
                # Car
                if i == 1:  # Only one car visible
                    car_color = (255, 0, 0) if int(animation_time * 2) % 2 else (0, 0, 255)
                    car_rect = pygame.Rect(space_x - size*0.15, y - size*0.05,
                                          size*0.3, size*0.2)
                    pygame.draw.rect(screen, car_color, car_rect, border_radius=5)
                    
                    # Windows
                    window_rect = pygame.Rect(space_x - size*0.12, y - size*0.02,
                                            size*0.24, size*0.08)
                    pygame.draw.rect(screen, (135, 206, 235), window_rect, border_radius=3)
                    
                    # Wheels
                    for wheel in [(-1, 0), (1, 0)]:
                        wheel_x = space_x + wheel[0] * size*0.1
                        wheel_y = y + size*0.07
                        pygame.draw.circle(screen, (0, 0, 0), (int(wheel_x), int(wheel_y)), size*0.05)
        
        elif loc_type == LocationType.GARDEN:
            # Flower bed
            bed_radius = size * 0.5
            pygame.draw.circle(screen, (101, 67, 33), (x, y), bed_radius)
            
            # Flowers
            for i in range(8):
                angle = i * math.pi / 4 + animation_time
                flower_x = x + math.cos(angle) * bed_radius * 0.6
                flower_y = y + math.sin(angle) * bed_radius * 0.6
                
                # Petals
                petal_color = [(255, 105, 180), (255, 20, 147), 
                              (218, 112, 214), (138, 43, 226)][i % 4]
                for j in range(6):
                    petal_angle = j * math.pi / 3
                    petal_length = size * 0.15
                    petal_x = flower_x + math.cos(petal_angle) * petal_length
                    petal_y = flower_y + math.sin(petal_angle) * petal_length
                    pygame.draw.circle(screen, petal_color, 
                                     (int(petal_x), int(petal_y)), size*0.08)
                
                # Center
                pygame.draw.circle(screen, (255, 255, 0), (int(flower_x), int(flower_y)), size*0.05)
                
                # Blinking effect
                if int(animation_time * 4 + i) % 4 == 0:
                    blink_radius = size * 0.12
                    s = pygame.Surface((blink_radius * 2, blink_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 255, 255, 100), 
                                     (blink_radius, blink_radius), blink_radius)
                    screen.blit(s, (int(flower_x - blink_radius), int(flower_y - blink_radius)))
        
        elif loc_type == LocationType.HOSTEL:
            # Multi-story building
            for floor in range(3):
                floor_y = y - size*0.4 + floor * size*0.3
                floor_rect = pygame.Rect(x - size*0.4, floor_y, size*0.8, size*0.25)
                pygame.draw.rect(screen, base_color, floor_rect)
                pygame.draw.rect(screen, (0, 0, 0), floor_rect, 1)
                
                # Windows with twinkling effect
                for wx in range(4):
                    window_x = x - size*0.3 + wx * size*0.2
                    window_rect = pygame.Rect(window_x - size*0.04, floor_y + size*0.05,
                                            size*0.08, size*0.15)
                    
                    # Twinkling windows
                    if random.random() < 0.3:  # Some windows lit
                        window_color = (255, 255, 224)
                    else:
                        window_color = (100, 100, 100)
                    
                    pygame.draw.rect(screen, window_color, window_rect)
                    pygame.draw.rect(screen, (0, 0, 0), window_rect, 1)
        
        elif loc_type == LocationType.MAIN_GATE:
            # Gate pillars
            pillar_width = size * 0.15
            for side in [-1, 1]:
                pillar_x = x + side * size*0.4
                pillar_rect = pygame.Rect(pillar_x - pillar_width//2, y - size*0.6,
                                         pillar_width, size*0.8)
                pygame.draw.rect(screen, (139, 69, 19), pillar_rect)
                pygame.draw.rect(screen, (0, 0, 0), pillar_rect, 2)
                
                # Pillar top
                top_rect = pygame.Rect(pillar_x - size*0.1, y - size*0.7,
                                      size*0.2, size*0.1)
                pygame.draw.rect(screen, (128, 0, 0), top_rect)
            
            # Gate (swinging)
            gate_angle = math.sin(animation_time * 2) * 0.5  # -30 to 30 degrees
            gate_length = size * 0.6
            
            # Left gate
            left_gate_x = x - size*0.4 + math.cos(gate_angle) * gate_length * 0.1
            left_gate_y = y - math.sin(gate_angle) * gate_length * 0.1
            pygame.draw.line(screen, (160, 82, 45),
                           (x - size*0.4, y),
                           (int(left_gate_x), int(left_gate_y)), 10)
            
            # Right gate
            right_gate_x = x + size*0.4 - math.cos(gate_angle) * gate_length * 0.1
            right_gate_y = y - math.sin(gate_angle) * gate_length * 0.1
            pygame.draw.line(screen, (160, 82, 45),
                           (x + size*0.4, y),
                           (int(right_gate_x), int(right_gate_y)), 10)
            
            # Gate arch
            arch_rect = pygame.Rect(x - size*0.5, y - size*0.8, size, size*0.4)
            pygame.draw.arc(screen, (139, 69, 19), arch_rect, math.pi, 2*math.pi, 10)
        
        # Visited effect
        if visited:
            pulse_size = size + math.sin(animation_time * 5) * size * 0.2
            s = pygame.Surface((int(pulse_size * 3), int(pulse_size * 3)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*Colors.LOCATION_VISITED, 100),
                             (int(pulse_size * 1.5), int(pulse_size * 1.5)),
                             int(pulse_size))
            screen.blit(s, (x - pulse_size * 1.5, y - pulse_size * 1.5))
    
    @staticmethod
    def draw_teacher(teacher_type, x, y, size, direction, frame, screen):
        """Draw teacher characters"""
        if teacher_type == 0:  # Strict teacher
            # Body
            suit_color = (0, 0, 139)  # Dark blue suit
            pygame.draw.rect(screen, suit_color, 
                           (x - size*0.3, y - size*0.5, size*0.6, size))
            
            # Head
            head_y = y - size*0.7
            pygame.draw.circle(screen, (255, 218, 185), (x, head_y), size*0.25)
            
            # Strict glasses
            glass_size = size*0.15
            for side in [-1, 1]:
                glass_x = x + side * size*0.1
                pygame.draw.circle(screen, (100, 100, 100), (glass_x, head_y), glass_size)
                pygame.draw.circle(screen, (0, 0, 0), (glass_x, head_y), glass_size, 2)
                
                # Angry eyebrows
                brow_y = head_y - size*0.1
                pygame.draw.line(screen, (0, 0, 0),
                               (glass_x - size*0.08, brow_y),
                               (glass_x + size*0.08, brow_y - size*0.05), 3)
            
            # Frowning mouth
            mouth_y = head_y + size*0.1
            pygame.draw.arc(screen, (0, 0, 0),
                          (x - size*0.1, mouth_y - size*0.05, size*0.2, size*0.1),
                          math.pi, 2*math.pi, 2)
            
            # Tie
            tie_points = [
                (x, y - size*0.4),
                (x - size*0.1, y - size*0.1),
                (x + size*0.1, y - size*0.1)
            ]
            pygame.draw.polygon(screen, (220, 20, 60), tie_points)
            
            # Clipboard
            clipboard_x = x + size*0.4
            clipboard_y = y - size*0.2
            pygame.draw.rect(screen, (255, 255, 255),
                           (clipboard_x - size*0.15, clipboard_y - size*0.2,
                            size*0.3, size*0.4))
            pygame.draw.rect(screen, (0, 0, 0),
                           (clipboard_x - size*0.15, clipboard_y - size*0.2,
                            size*0.3, size*0.4), 2)
            
            # Walking animation (strict march)
            leg_offset = math.sin(frame * 4) * size * 0.2
            leg_y = y + size*0.3
            for leg in [-1, 1]:
                leg_x = x + leg * size*0.15
                pygame.draw.line(screen, (0, 0, 0),
                               (leg_x, leg_y),
                               (leg_x, leg_y + size*0.3 + leg * leg_offset), 5)
        
        elif teacher_type == 1:  # Punctual teacher
            # Body with lab coat
            coat_color = (255, 255, 255)
            pygame.draw.rect(screen, coat_color,
                           (x - size*0.4, y - size*0.6, size*0.8, size*1.2))
            pygame.draw.rect(screen, (0, 0, 0),
                           (x - size*0.4, y - size*0.6, size*0.8, size*1.2), 2)
            
            # Head
            head_y = y - size*0.8
            pygame.draw.circle(screen, (255, 218, 185), (x, head_y), size*0.25)
            
            # Glasses
            glass_size = size*0.12
            for side in [-1, 1]:
                glass_x = x + side * size*0.12
                pygame.draw.circle(screen, (150, 150, 150), (glass_x, head_y), glass_size)
                
                # Watch-checking eyes
                pupil_offset = math.sin(frame * 3) * glass_size * 0.5
                pygame.draw.circle(screen, (0, 0, 0),
                                 (int(glass_x + pupil_offset), head_y), glass_size*0.4)
            
            # Mustache
            mouth_y = head_y + size*0.1
            pygame.draw.arc(screen, (0, 0, 0),
                          (x - size*0.15, mouth_y - size*0.05, size*0.3, size*0.1),
                          math.pi * 0.3, math.pi * 0.7, 3)
            
            # Pocket watch
            watch_x = x + size*0.3
            watch_y = y - size*0.2
            pygame.draw.circle(screen, (192, 192, 192), (watch_x, watch_y), size*0.15)
            pygame.draw.circle(screen, (0, 0, 0), (watch_x, watch_y), size*0.15, 2)
            
            # Watch hands
            hour_angle = frame * 0.5
            minute_angle = frame * 3
            hour_x = watch_x + math.cos(hour_angle) * size*0.08
            hour_y = watch_y + math.sin(hour_angle) * size*0.08
            minute_x = watch_x + math.cos(minute_angle) * size*0.1
            minute_y = watch_y + math.sin(minute_angle) * size*0.1
            
            pygame.draw.line(screen, (0, 0, 0), (watch_x, watch_y), (hour_x, hour_y), 2)
            pygame.draw.line(screen, (0, 0, 0), (watch_x, watch_y), (minute_x, minute_y), 2)
        
        else:  # Fun teacher
            # Casual outfit
            shirt_color = (50, 205, 50)  # Lime green
            pygame.draw.rect(screen, shirt_color,
                           (x - size*0.4, y - size*0.5, size*0.8, size))
            
            # Head with big smile
            head_y = y - size*0.7
            pygame.draw.circle(screen, (255, 218, 185), (x, head_y), size*0.25)
            
            # Happy eyes
            eye_size = size*0.08
            for side in [-1, 1]:
                eye_x = x + side * size*0.1
                eye_y = head_y - size*0.05
                pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), eye_size)
                
                # Sparkle in eyes
                sparkle_x = eye_x - eye_size*0.3
                sparkle_y = eye_y - eye_size*0.3
                pygame.draw.circle(screen, (255, 255, 255), (sparkle_x, sparkle_y), eye_size*0.3)
            
            # Big smile
            mouth_y = head_y + size*0.1
            smile_rect = pygame.Rect(x - size*0.15, mouth_y - size*0.05, size*0.3, size*0.2)
            pygame.draw.arc(screen, (255, 0, 0), smile_rect, 0, math.pi, 3)
            
            # Messy hair
            for i in range(5):
                hair_angle = i * math.pi / 5 - math.pi/2 + frame
                hair_x = x + math.cos(hair_angle) * size*0.3
                hair_y = head_y + math.sin(hair_angle) * size*0.3 - size*0.2
                pygame.draw.circle(screen, (139, 69, 19), (int(hair_x), int(hair_y)), size*0.1)
            
            # Coffee cup
            cup_x = x + size*0.4
            cup_y = y - size*0.2
            pygame.draw.rect(screen, (139, 69, 19),
                           (cup_x - size*0.08, cup_y - size*0.15,
                            size*0.16, size*0.3))
            
            # Steam
            if int(frame * 4) % 4 < 2:
                for s in range(3):
                    steam_x = cup_x + math.sin(frame + s) * size*0.05
                    steam_y = cup_y - size*0.2 - s * size*0.05
                    steam_size = size*0.03 * (3 - s)
                    pygame.draw.circle(screen, (255, 255, 255, 150 - s*50),
                                      (int(steam_x), int(steam_y)), int(steam_size))
            
            # Random dance movements
            arm_offset = math.sin(frame * 5) * size * 0.3
            for arm in [-1, 1]:
                arm_x = x + arm * size*0.4
                arm_y = y - size*0.2 + arm_offset * arm
                pygame.draw.line(screen, (255, 218, 185),
                               (x + arm * size*0.15, y - size*0.3),
                               (arm_x, arm_y), 5)
    
    @staticmethod
    def draw_powerup(power_type, x, y, size, animation_time, collected, screen):
        """Draw power-up items"""
        if collected:
            return
        
        # Floating animation
        float_offset = math.sin(animation_time * 3) * size * 0.3
        y_pos = y + float_offset
        
        # Glow effect
        glow_size = size + math.sin(animation_time * 5) * size * 0.2
        s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        for i in range(3):
            radius = glow_size - i * 5
            alpha = 100 - i * 30
            pygame.draw.circle(s, (255, 255, 0, alpha), (glow_size, glow_size), radius)
        screen.blit(s, (x - glow_size, y_pos - glow_size))
        
        # Base circle
        pygame.draw.circle(screen, (255, 255, 255), (x, int(y_pos)), int(size))
        pygame.draw.circle(screen, (0, 0, 0), (x, int(y_pos)), int(size), 2)
        
        # Power-up specific graphics
        if power_type == PowerUpType.BOOK_BOOST:
            # Book
            book_width = size * 0.8
            book_height = size * 1.0
            book_rect = pygame.Rect(x - book_width//2, y_pos - book_height//2,
                                   book_width, book_height)
            pygame.draw.rect(screen, (139, 69, 19), book_rect, border_radius=3)
            pygame.draw.rect(screen, (0, 0, 0), book_rect, 2, border_radius=3)
            
            # Pages
            for i in range(3):
                page_y = y_pos - book_height//4 + i * book_height//6
                pygame.draw.line(screen, (255, 255, 255),
                               (x - book_width//3, page_y),
                               (x + book_width//3, page_y), 1)
            
            # Speed lines
            for i in range(3):
                line_angle = animation_time + i * math.pi / 3
                line_length = size * 0.5
                line_x = x + math.cos(line_angle) * size
                line_y = y_pos + math.sin(line_angle) * size
                pygame.draw.line(screen, (0, 0, 255, 150),
                               (x, y_pos),
                               (int(line_x), int(line_y)), 2)
        
        elif power_type == PowerUpType.CHAI_CHARGE:
            # Chai cup
            cup_radius = size * 0.6
            pygame.draw.circle(screen, (139, 69, 19), (x, int(y_pos)), int(cup_radius))
            
            # Chai liquid
            liquid_height = size * 0.4 + math.sin(animation_time * 4) * size * 0.1
            liquid_y = y_pos + cup_radius - liquid_height
            pygame.draw.circle(screen, (210, 105, 30), (x, int(liquid_y)), int(cup_radius * 0.8))
            
            # Steam
            for s in range(3):
                steam_x = x + math.sin(animation_time * 2 + s) * size * 0.2
                steam_y = y_pos - cup_radius - s * size * 0.1
                steam_size = size * 0.1 * (3 - s)
                pygame.draw.circle(screen, (255, 255, 255, 150 - s*50),
                                 (int(steam_x), int(steam_y)), int(steam_size))
            
            # Plus sign for extra time
            pygame.draw.line(screen, (0, 255, 0),
                           (x - size*0.3, y_pos),
                           (x + size*0.3, y_pos), 3)
            pygame.draw.line(screen, (0, 255, 0),
                           (x, y_pos - size*0.3),
                           (x, y_pos + size*0.3), 3)
        
        elif power_type == PowerUpType.SMART_CAP:
            # Graduation cap
            cap_size = size * 0.8
            # Cap square
            cap_rect = pygame.Rect(x - cap_size//2, y_pos - cap_size//2,
                                  cap_size, cap_size//2)
            pygame.draw.rect(screen, (0, 0, 139), cap_rect)
            
            # Cap top
            cap_top = pygame.Rect(x - cap_size//4, y_pos - cap_size,
                                 cap_size//2, cap_size//2)
            pygame.draw.rect(screen, (0, 0, 139), cap_top)
            
            # Tassel
            tassel_x = x
            tassel_y = y_pos - cap_size
            pygame.draw.line(screen, (255, 215, 0),
                           (tassel_x, tassel_y),
                           (tassel_x, tassel_y - size*0.3), 2)
            pygame.draw.circle(screen, (255, 215, 0),
                             (tassel_x, tassel_y - size*0.35), size*0.08)
            
            # Light bulb (smart idea)
            bulb_y = y_pos + size*0.2
            pygame.draw.circle(screen, (255, 255, 0), (x, int(bulb_y)), size*0.2)
            
            # Light rays
            for i in range(8):
                ray_angle = i * math.pi / 4 + animation_time
                ray_length = size * 0.4
                ray_x = x + math.cos(ray_angle) * ray_length
                ray_y = bulb_y + math.sin(ray_angle) * ray_length
                pygame.draw.line(screen, (255, 255, 0, 150),
                               (x, bulb_y),
                               (int(ray_x), int(ray_y)), 2)
        
        elif power_type == PowerUpType.BICYCLE:
            # Bicycle wheels
            wheel_radius = size * 0.4
            for wheel in [-1, 1]:
                wheel_x = x + wheel * size * 0.4
                pygame.draw.circle(screen, (0, 0, 0), (int(wheel_x), int(y_pos)), int(wheel_radius))
                pygame.draw.circle(screen, (200, 200, 200), (int(wheel_x), int(y_pos)), int(wheel_radius*0.8))
                pygame.draw.circle(screen, (0, 0, 0), (int(wheel_x), int(y_pos)), int(wheel_radius*0.2))
                
                # Spokes
                for spoke in range(8):
                    spoke_angle = spoke * math.pi / 4 + animation_time * 3
                    spoke_x = wheel_x + math.cos(spoke_angle) * wheel_radius * 0.7
                    spoke_y = y_pos + math.sin(spoke_angle) * wheel_radius * 0.7
                    pygame.draw.line(screen, (0, 0, 0),
                                   (wheel_x, y_pos),
                                   (int(spoke_x), int(spoke_y)), 1)
            
            # Bicycle frame
            frame_points = [
                (x - size*0.4, y_pos),  # Left wheel center
                (x, y_pos - size*0.3),  # Seat
                (x + size*0.4, y_pos),  # Right wheel center
                (x, y_pos + size*0.1),  # Pedals
                (x - size*0.2, y_pos - size*0.1)  # Handlebars
            ]
            pygame.draw.lines(screen, (255, 0, 0), False, frame_points, 5)
            
            # Seat
            pygame.draw.circle(screen, (139, 69, 19), (x, int(y_pos - size*0.3)), size*0.1)
            
            # Pedals
            pedal_angle = animation_time * 5
            pedal_x = x + math.cos(pedal_angle) * size * 0.15
            pedal_y = y_pos + size*0.1 + math.sin(pedal_angle) * size * 0.15
            pygame.draw.circle(screen, (0, 0, 0), (int(pedal_x), int(pedal_y)), size*0.08)
        
        elif power_type == PowerUpType.PHONE:
            # Smartphone
            phone_width = size * 0.6
            phone_height = size * 1.0
            phone_rect = pygame.Rect(x - phone_width//2, y_pos - phone_height//2,
                                    phone_width, phone_height)
            pygame.draw.rect(screen, (0, 0, 0), phone_rect, border_radius=5)
            pygame.draw.rect(screen, (50, 50, 50), phone_rect, 2, border_radius=5)
            
            # Screen
            screen_rect = pygame.Rect(x - phone_width*0.4, y_pos - phone_height*0.4,
                                     phone_width*0.8, phone_height*0.7)
            pygame.draw.rect(screen, (0, 50, 0), screen_rect, border_radius=3)
            
            # App icons
            for i in range(2):
                for j in range(3):
                    app_x = x - phone_width*0.3 + i * phone_width*0.3
                    app_y = y_pos - phone_height*0.3 + j * phone_height*0.25
                    app_size = size * 0.08
                    app_color = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                (255, 255, 0), (255, 0, 255), (0, 255, 255)][i * 3 + j]
                    pygame.draw.circle(screen, app_color, (int(app_x), int(app_y)), int(app_size))
            
            # Signal waves
            for wave in range(3):
                wave_radius = size * 0.8 + wave * size * 0.3
                wave_alpha = 150 - wave * 50
                s = pygame.Surface((wave_radius * 2, wave_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, wave_alpha),
                                 (wave_radius, wave_radius), wave_radius, 3)
                screen.blit(s, (x - wave_radius, y_pos - wave_radius))
        
        # Rotation
        rotation = animation_time * 2 % (2 * math.pi)
        if rotation != 0:
            # Create a surface for rotation
            item_size = int(size * 2.5)
            item_surface = pygame.Surface((item_size, item_size), pygame.SRCALPHA)
            
            # Draw the item centered on the surface
            GraphicsEngine.draw_powerup(power_type, item_size//2, item_size//2,
                                       size, animation_time, collected, item_surface)
            
            # Rotate the surface
            rotated = pygame.transform.rotate(item_surface, rotation * 180 / math.pi)
            rotated_rect = rotated.get_rect(center=(x, int(y_pos)))
            screen.blit(rotated, rotated_rect)

# ================ PARTICLE SYSTEM ================
class Particle:
    def __init__(self, x, y, particle_type="sparkle"):
        self.x = x
        self.y = y
        self.particle_type = particle_type
        self.lifetime = 1.0
        self.max_lifetime = 1.0
        
        if particle_type == "sparkle":
            self.color = random.choice([(255, 255, 0), (255, 200, 0), (255, 150, 0)])
            self.size = random.uniform(2, 6)
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-3, -1)
            self.gravity = 0.1
        elif particle_type == "footstep":
            self.color = (100, 100, 100, 150)
            self.size = random.uniform(3, 8)
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.2, 0.2)
            self.gravity = 0.05
        elif particle_type == "celebration":
            self.color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255),
                                       (255, 255, 0), (255, 0, 255), (0, 255, 255)])
            self.size = random.uniform(4, 10)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.gravity = 0.2
        elif particle_type == "caught":
            self.color = (255, 50, 50)
            self.size = random.uniform(3, 7)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.gravity = 0.15
    
    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= dt
        self.size = max(0, self.size * 0.95)
    
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            
            if self.particle_type == "sparkle":
                # Draw sparkle as a star
                s = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
                for i in range(4):
                    angle = i * math.pi / 2
                    end_x = self.size * 2 + math.cos(angle) * self.size * 1.5
                    end_y = self.size * 2 + math.sin(angle) * self.size * 1.5
                    pygame.draw.line(s, (*self.color[:3], alpha),
                                   (self.size * 2, self.size * 2),
                                   (end_x, end_y), 2)
                pygame.draw.circle(s, (*self.color[:3], alpha),
                                 (int(self.size * 2), int(self.size * 2)),
                                 int(self.size))
                screen.blit(s, (self.x - self.size * 2, self.y - self.size * 2))
            else:
                # Draw circular particle
                s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color[:3], alpha),
                                 (int(self.size), int(self.size)), int(self.size))
                screen.blit(s, (self.x - self.size, self.y - self.size))
    
    def is_alive(self):
        return self.lifetime > 0

# ================ GAME OBJECTS ================
@dataclass
class Character:
    type: CharacterType
    name: str
    position: List[float]
    target: List[float]
    speed: float
    animation_time: float
    direction: Direction
    visited_locations: Set[int]
    path_points: List[Tuple[float, float]]
    special_active: bool
    special_timer: float
    power_ups: List[PowerUpType]
    
    def __init__(self, char_type, name, speed=3.0):
        self.type = char_type
        self.name = name
        self.position = [100, 100]
        self.target = [100, 100]
        self.speed = speed
        self.animation_time = 0
        self.direction = Direction.RIGHT
        self.visited_locations = set()
        self.path_points = []
        self.special_active = False
        self.special_timer = 0
        self.power_ups = []
    
    def move_towards_target(self, dt):
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0.1:
            move_dist = min(distance, self.speed * dt * 60)
            self.position[0] += (dx / distance) * move_dist
            self.position[1] += (dy / distance) * move_dist
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
            
            # Add to path
            self.path_points.append((self.position[0], self.position[1]))
            return False
        return True
    
    def update(self, dt):
        self.animation_time += dt
        
        if self.special_active:
            self.special_timer -= dt
            if self.special_timer <= 0:
                self.special_active = False
    
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        size = 20
        
        # Draw based on character type
        if self.type == CharacterType.ALINA:
            GraphicsEngine.draw_panda(x, y, size, self.direction.value, 
                                    self.animation_time, screen, self.special_active)
        elif self.type == CharacterType.KAINAT:
            GraphicsEngine.draw_sloth(x, y, size, self.direction.value,
                                    self.animation_time, screen, self.special_active)
        elif self.type == CharacterType.AIZA:
            GraphicsEngine.draw_squirrel(x, y, size, self.direction.value,
                                       self.animation_time, screen, self.special_active)
        elif self.type == CharacterType.AYESHA:
            GraphicsEngine.draw_fox(x, y, size, self.direction.value,
                                  self.animation_time, screen, self.special_active)
        elif self.type == CharacterType.HANAN:
            GraphicsEngine.draw_owl(x, y, size, self.direction.value,
                                  self.animation_time, screen, self.special_active)
        elif self.type == CharacterType.ASAD:
            GraphicsEngine.draw_lion(x, y, size, self.direction.value,
                                   self.animation_time, screen, self.special_active)
        
        # Draw footsteps particles occasionally
        if len(self.path_points) > 1 and random.random() < 0.3:
            last_point = self.path_points[-1]
            if random.random() < 0.1:  # 10% chance per frame
                for _ in range(2):
                    particle = Particle(last_point[0], last_point[1], "footstep")
                    game.particles.append(particle)

@dataclass
class Location:
    type: LocationType
    name: str
    position: Tuple[float, float]
    visited: bool
    animation_time: float
    
    def __init__(self, loc_type, name, position):
        self.type = loc_type
        self.name = name
        self.position = position
        self.visited = False
        self.animation_time = 0
    
    def update(self, dt):
        self.animation_time += dt
    
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        GraphicsEngine.draw_location(self.type, x, y, 25, self.visited, 
                                   self.animation_time, screen)
        
        # Draw name
        font = pygame.font.SysFont('Arial', 16, bold=True)
        name_text = font.render(self.name, True, Colors.TEXT)
        text_rect = name_text.get_rect(center=(x, y + 40))
        
        # Text background
        text_bg = pygame.Rect(text_rect.x - 5, text_rect.y - 2,
                            text_rect.width + 10, text_rect.height + 4)
        pygame.draw.rect(screen, (0, 0, 0, 150), text_bg, border_radius=3)
        screen.blit(name_text, text_rect)

@dataclass
class Teacher:
    type: int  # 0: strict, 1: punctual, 2: fun
    patrol_points: List[Tuple[float, float]]
    position: List[float]
    current_target: int
    speed: float
    direction: Direction
    animation_time: float
    
    def __init__(self, teacher_type, patrol_points, speed=1.5):
        self.type = teacher_type
        self.patrol_points = patrol_points
        self.position = list(patrol_points[0])
        self.current_target = 0
        self.speed = speed
        self.direction = Direction.RIGHT
        self.animation_time = 0
    
    def update(self, dt):
        self.animation_time += dt
        
        target = self.patrol_points[self.current_target]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.speed:
            self.current_target = (self.current_target + 1) % len(self.patrol_points)
        else:
            move_dist = min(distance, self.speed * dt * 60)
            self.position[0] += (dx / distance) * move_dist
            self.position[1] += (dy / distance) * move_dist
            
            # Update direction
            if abs(dx) > abs(dy):
                self.direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.direction = Direction.DOWN if dy > 0 else Direction.UP
    
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        GraphicsEngine.draw_teacher(self.type, x, y, 20, self.direction.value,
                                  self.animation_time, screen)

@dataclass
class PowerUp:
    type: PowerUpType
    position: Tuple[float, float]
    collected: bool
    animation_time: float
    
    def __init__(self, power_type, position):
        self.type = power_type
        self.position = position
        self.collected = False
        self.animation_time = 0
    
    def update(self, dt):
        self.animation_time += dt
    
    def draw(self, screen):
        if not self.collected:
            x, y = int(self.position[0]), int(self.position[1])
            GraphicsEngine.draw_powerup(self.type, x, y, 15, 
                                      self.animation_time, self.collected, screen)

# ================ TSP SOLVER ================
class TSPSolver:
    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    @staticmethod
    def path_length(path, locations):
        total = 0
        for i in range(len(path) - 1):
            total += TSPSolver.distance(locations[path[i]].position,
                                       locations[path[i + 1]].position)
        return total
    
    @staticmethod
    def brute_force(locations):
        """Optimal TSP solution using brute force (feasible for 10 nodes)"""
        n = len(locations)
        indices = list(range(n))
        
        best_path = None
        best_length = float('inf')
        
        # Generate all permutations starting from CS Dept (index 0)
        start = 0
        remaining = indices[1:]
        
        for perm in itertools.permutations(remaining):
            # Create path: start -> permutation -> start
            path = [start] + list(perm) + [start]
            length = TSPSolver.path_length(path, locations)
            
            if length < best_length:
                best_length = length
                best_path = path
        
        return best_path, best_length
    
    @staticmethod
    def nearest_neighbor(locations):
        """Heuristic TSP solution using nearest neighbor"""
        n = len(locations)
        unvisited = set(range(n))
        current = 0  # Start from CS Dept
        path = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = None
            nearest_dist = float('inf')
            
            for loc in unvisited:
                dist = TSPSolver.distance(locations[current].position,
                                         locations[loc].position)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = loc
            
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to start
        path.append(0)
        return path, TSPSolver.path_length(path, locations)

# ================ MAIN GAME CLASS ================
class CampusBunkingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Campus Bunking Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.state = GameState.TITLE
        self.time_remaining = TIME_LIMIT
        self.score = 0
        self.level = 1
        self.game_start_time = 0
        self.day_night_cycle = 0
        self.all_visited = False
        self.level_complete_time = 0
        
        # Game objects
        self.characters = []
        self.locations = []
        self.teachers = []
        self.power_ups = []
        self.particles = []
        self.current_character = None
        self.selected_char_index = 0
        
        # Path data
        self.player_path = []
        self.optimal_path = []
        self.neighbor_path = []
        self.optimal_distance = 0
        self.neighbor_distance = 0
        self.player_distance = 0
        
        # UI
        self.buttons = {}
        
        # Initialize game
        self.init_game()
    
    def init_game(self):
        # Create characters
        self.characters = [
            Character(CharacterType.ALINA, "Alina", 3.0),
            Character(CharacterType.KAINAT, "Kainat", 2.0),
            Character(CharacterType.AIZA, "Aiza", 3.5),
            Character(CharacterType.AYESHA, "Ayesha", 3.0),
            Character(CharacterType.HANAN, "Hanan", 4.0),
            Character(CharacterType.ASAD, "Asad", 3.0)
        ]
        
        # Create locations in a circular layout
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = min(center_x, center_y) - 150
        
        location_data = [
            (LocationType.CS_DEPT, "CS Department"),
            (LocationType.LIBRARY, "Library"),
            (LocationType.CANTEEN, "Canteen"),
            (LocationType.AUDITORIUM, "Auditorium"),
            (LocationType.SPORTS_GROUND, "Sports Ground"),
            (LocationType.ADMIN_BLOCK, "Admin Block"),
            (LocationType.PARKING, "Parking"),
            (LocationType.GARDEN, "Garden"),
            (LocationType.HOSTEL, "Hostel"),
            (LocationType.MAIN_GATE, "Main Gate")
        ]
        
        for i, (loc_type, name) in enumerate(location_data):
            angle = (i / len(location_data)) * 2 * math.pi
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            self.locations.append(Location(loc_type, name, (x, y)))
        
        # Create teachers with patrol patterns
        self.teachers = [
            Teacher(0, [(200, 200), (400, 200), (400, 400), (200, 400)]),  # Strict
            Teacher(1, [(SCREEN_WIDTH - 300, 200), (SCREEN_WIDTH - 200, 300),
                       (SCREEN_WIDTH - 300, 400)]),  # Punctual
            Teacher(2, [(SCREEN_WIDTH // 2, 100), (100, SCREEN_HEIGHT // 2),
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),
                       (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)])  # Fun
        ]
        
        # Create power-ups
        for _ in range(8):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            power_type = random.choice(list(PowerUpType))
            self.power_ups.append(PowerUp(power_type, (x, y)))
    
    def reset_game(self):
        self.time_remaining = TIME_LIMIT
        self.score = 0
        self.all_visited = False
        
        if self.current_character:
            self.current_character.position = [100, 100]
            self.current_character.target = [100, 100]
            self.current_character.visited_locations.clear()
            self.current_character.path_points.clear()
            self.current_character.power_ups.clear()
        
        for location in self.locations:
            location.visited = False
        
        for power_up in self.power_ups:
            power_up.collected = False
        
        for teacher in self.teachers:
            teacher.position = list(teacher.patrol_points[0])
            teacher.current_target = 0
        
        self.particles.clear()
    
    def check_collisions(self):
        if not self.current_character:
            return
        
        # Check teacher collisions
        for teacher in self.teachers:
            dx = self.current_character.position[0] - teacher.position[0]
            dy = self.current_character.position[1] - teacher.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 30:
                self.time_remaining -= 10
                
                # Create caught particles
                for _ in range(20):
                    particle = Particle(self.current_character.position[0],
                                      self.current_character.position[1],
                                      "caught")
                    self.particles.append(particle)
                
                # Move character away
                push_angle = math.atan2(dy, dx)
                push_dist = 50
                self.current_character.position[0] += math.cos(push_angle) * push_dist
                self.current_character.position[1] += math.sin(push_angle) * push_dist
                
                break
        
        # Check power-up collection
        for power_up in self.power_ups:
            if not power_up.collected:
                dx = self.current_character.position[0] - power_up.position[0]
                dy = self.current_character.position[1] - power_up.position[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 25:
                    power_up.collected = True
                    self.current_character.power_ups.append(power_up.type)
                    
                    # Apply power-up effect
                    if power_up.type == PowerUpType.CHAI_CHARGE:
                        self.time_remaining += 15
                    elif power_up.type == PowerUpType.BOOK_BOOST:
                        self.current_character.speed *= 1.5
                        pygame.time.set_timer(pygame.USEREVENT, 5000, 1)
                    
                    # Create collection particles
                    for _ in range(15):
                        particle = Particle(power_up.position[0],
                                          power_up.position[1],
                                          "sparkle")
                        self.particles.append(particle)
        
        # Check location visits
        for i, location in enumerate(self.locations):
            if not location.visited:
                dx = self.current_character.position[0] - location.position[0]
                dy = self.current_character.position[1] - location.position[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 40:
                    location.visited = True
                    self.current_character.visited_locations.add(i)
                    
                    # Create visit particles
                    for _ in range(10):
                        particle = Particle(location.position[0],
                                          location.position[1],
                                          "sparkle")
                        self.particles.append(particle)
                    
                    # Check if all visited
                    self.all_visited = all(loc.visited for loc in self.locations)
                    if self.all_visited:
                        self.level_complete_time = pygame.time.get_ticks()
                        self.calculate_paths()
    
    def calculate_paths(self):
        # Player path
        if self.current_character:
            visited_order = list(self.current_character.visited_locations)
            if visited_order:
                self.player_path = [0] + visited_order + [0]
                self.player_distance = TSPSolver.path_length(self.player_path, self.locations)
        
        # TSP paths
        self.optimal_path, self.optimal_distance = TSPSolver.brute_force(self.locations)
        self.neighbor_path, self.neighbor_distance = TSPSolver.nearest_neighbor(self.locations)
        
        # Calculate score
        if self.optimal_distance > 0:
            efficiency = (self.optimal_distance / max(self.player_distance, 1)) * 100
        else:
            efficiency = 100
        
        time_bonus = max(0, self.time_remaining) * 10
        self.score = int(efficiency * 20 + time_bonus)
    
    def draw_path(self, screen, path, color, width=3, animated=False):
        if len(path) < 2:
            return
        
        for i in range(len(path) - 1):
            start_pos = self.locations[path[i]].position
            end_pos = self.locations[path[i + 1]].position
            
            pygame.draw.line(screen, color, start_pos, end_pos, width)
            
            # Draw arrow in the middle
            mid_x = (start_pos[0] + end_pos[0]) / 2
            mid_y = (start_pos[1] + end_pos[1]) / 2
            
            angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
            arrow_length = 15
            
            arrow_x1 = mid_x - arrow_length * math.cos(angle - math.pi/6)
            arrow_y1 = mid_y - arrow_length * math.sin(angle - math.pi/6)
            arrow_x2 = mid_x - arrow_length * math.cos(angle + math.pi/6)
            arrow_y2 = mid_y - arrow_length * math.sin(angle + math.pi/6)
            
            pygame.draw.line(screen, color, (mid_x, mid_y), (arrow_x1, arrow_y1), 2)
            pygame.draw.line(screen, color, (mid_x, mid_y), (arrow_x2, arrow_y2), 2)
            
            # Animated point
            if animated:
                progress = (pygame.time.get_ticks() % 2000) / 2000
                point_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                point_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                pygame.draw.circle(screen, (255, 255, 255), (int(point_x), int(point_y)), 5)
    
    def draw_minimap(self):
        size = 150
        x = SCREEN_WIDTH - size - 20
        y = SCREEN_HEIGHT - size - 20
        
        # Background
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        self.screen.blit(s, (x, y))
        pygame.draw.rect(self.screen, Colors.TEXT, (x, y, size, size), 2)
        
        # Scale factor
        scale = size / max(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Draw locations
        for location in self.locations:
            map_x = x + location.position[0] * scale
            map_y = y + location.position[1] * scale
            color = Colors.LOCATION_VISITED if location.visited else Colors.LOCATION
            pygame.draw.circle(self.screen, color, (int(map_x), int(map_y)), 4)
        
        # Draw character
        if self.current_character:
            map_x = x + self.current_character.position[0] * scale
            map_y = y + self.current_character.position[1] * scale
            pygame.draw.circle(self.screen, (255, 255, 0), (int(map_x), int(map_y)), 6)
        
        # Draw teachers
        for teacher in self.teachers:
            map_x = x + teacher.position[0] * scale
            map_y = y + teacher.position[1] * scale
            pygame.draw.circle(self.screen, Colors.TEACHER, (int(map_x), int(map_y)), 4)
    
    def draw_ui(self):
        # Top panel
        panel_height = 80
        s = pygame.Surface((SCREEN_WIDTH, panel_height), pygame.SRCALPHA)
        s.fill((*Colors.UI_BG[:3], 200))
        self.screen.blit(s, (0, 0))
        
        font = pygame.font.SysFont('Arial', 24, bold=True)
        small_font = pygame.font.SysFont('Arial', 18)
        
        # Time
        time_text = font.render(f"Time: {int(self.time_remaining)}s", True, Colors.TEXT)
        self.screen.blit(time_text, (20, 20))
        
        # Visited
        visited = sum(1 for loc in self.locations if loc.visited)
        visited_text = font.render(f"Visited: {visited}/10", True, Colors.TEXT)
        self.screen.blit(visited_text, (20, 50))
        
        # Distance
        if self.current_character and len(self.current_character.path_points) > 1:
            total_dist = 0
            for i in range(len(self.current_character.path_points) - 1):
                p1 = self.current_character.path_points[i]
                p2 = self.current_character.path_points[i + 1]
                total_dist += math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            self.player_distance = total_dist
        
        distance_text = font.render(f"Distance: {int(self.player_distance)}", True, Colors.TEXT)
        self.screen.blit(distance_text, (SCREEN_WIDTH // 3, 20))
        
        # Character info
        if self.current_character:
            char_text = font.render(f"Character: {self.current_character.name}", True, Colors.TEXT)
            self.screen.blit(char_text, (SCREEN_WIDTH // 3, 50))
            
            # Special ability indicator
            if self.current_character.special_active:
                special_text = small_font.render("SPECIAL ACTIVE!", True, (255, 255, 0))
                self.screen.blit(special_text, (SCREEN_WIDTH // 2, 20))
        
        # Power-ups
        power_text = font.render("Power-ups:", True, Colors.TEXT)
        self.screen.blit(power_text, (SCREEN_WIDTH * 2 // 3, 20))
        
        if self.current_character:
            for i, power_type in enumerate(self.current_character.power_ups[-3:]):
                # Draw power-up icon
                power_x = SCREEN_WIDTH * 2 // 3 + 80 + i * 40
                power_y = 40
                power_size = 15
                
                # Create a surface for the icon
                icon_surf = pygame.Surface((power_size * 2, power_size * 2), pygame.SRCALPHA)
                GraphicsEngine.draw_powerup(power_type, power_size, power_size,
                                          power_size, pygame.time.get_ticks() / 1000,
                                          False, icon_surf)
                self.screen.blit(icon_surf, (power_x - power_size, power_y - power_size))
    
    def draw_title_screen(self):
        # Animated background
        self.day_night_cycle = (pygame.time.get_ticks() % 60000) / 60000
        sky_r = int(135 * (1 - self.day_night_cycle) + 25 * self.day_night_cycle)
        sky_g = int(206 * (1 - self.day_night_cycle) + 25 * self.day_night_cycle)
        sky_b = int(235 * (1 - self.day_night_cycle) + 112 * self.day_night_cycle)
        self.screen.fill((sky_r, sky_g, sky_b))
        
        # Draw animated campus in background
        for i in range(10):
            angle = pygame.time.get_ticks() / 3000 + i * math.pi / 5
            radius = 100 + math.sin(pygame.time.get_ticks() / 2000 + i) * 50
            x = SCREEN_WIDTH // 2 + math.cos(angle) * radius
            y = SCREEN_HEIGHT // 3 + math.sin(angle) * radius
            
            # Draw simplified location
            GraphicsEngine.draw_location(LocationType(i), int(x), int(y),
                                       20, False, pygame.time.get_ticks() / 1000 + i,
                                       self.screen)
        
        # Title
        title_font = pygame.font.SysFont('Arial', 72, bold=True)
        title = title_font.render("Campus Bunking Adventure", True, Colors.TEXT)
        title_shadow = title_font.render("Campus Bunking Adventure", True, (0, 0, 0))
        
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        title_y = SCREEN_HEIGHT // 4
        
        self.screen.blit(title_shadow, (title_x + 4, title_y + 4))
        self.screen.blit(title, (title_x, title_y))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont('Arial', 28)
        subtitle = subtitle_font.render("Learn TSP while exploring campus!", True, Colors.TEXT)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, title_y + 80))
        
        # Start button
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60)
        
        button_color = Colors.BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else Colors.BUTTON
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=15)
        pygame.draw.rect(self.screen, Colors.TEXT, button_rect, 3, border_radius=15)
        
        button_font = pygame.font.SysFont('Arial', 36, bold=True)
        button_text = button_font.render("START", True, Colors.TEXT)
        self.screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 65))
        
        self.buttons["start"] = button_rect
        
        # Instructions
        instr_font = pygame.font.SysFont('Arial', 20)
        instructions = [
            "🎯 Visit all 10 campus locations in optimal order",
            "👥 Choose a character with special abilities",
            "👨‍🏫 Avoid teachers or lose time",
            "✨ Collect power-ups for bonuses",
            "📊 Learn Traveling Salesman Problem concepts!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instr_font.render(instruction, True, Colors.TEXT)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 + 150 + i * 35))
    
    def draw_character_select(self):
        self.screen.fill(Colors.SKY_DAY)
        
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title = title_font.render("Choose Your Character", True, Colors.TEXT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Draw characters
        char_width = 180
        start_x = (SCREEN_WIDTH - len(self.characters) * char_width) // 2 + char_width // 2
        
        mouse_pos = pygame.mouse.get_pos()
        self.buttons.clear()
        
        for i, character in enumerate(self.characters):
            x = start_x + i * char_width
            y = SCREEN_HEIGHT // 3
            
            # Character card
            card_rect = pygame.Rect(x - 70, y - 90, 140, 180)
            is_hovered = card_rect.collidepoint(mouse_pos)
            is_selected = i == self.selected_char_index
            
            # Card background
            card_color = (100, 100, 100, 100) if not is_selected else (255, 215, 0, 100)
            if is_hovered and not is_selected:
                card_color = (150, 150, 150, 100)
            
            s = pygame.Surface((140, 180), pygame.SRCALPHA)
            s.fill(card_color)
            self.screen.blit(s, (x - 70, y - 90))
            pygame.draw.rect(self.screen, Colors.TEXT, (x - 70, y - 90, 140, 180), 3)
            
            # Draw character
            char_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            if character.type == CharacterType.ALINA:
                GraphicsEngine.draw_panda(30, 30, 15, 0, pygame.time.get_ticks() / 1000,
                                        False, char_surf)
            elif character.type == CharacterType.KAINAT:
                GraphicsEngine.draw_sloth(30, 30, 15, 0, pygame.time.get_ticks() / 1000,
                                        False, char_surf)
            elif character.type == CharacterType.AIZA:
                GraphicsEngine.draw_squirrel(30, 30, 15, 0, pygame.time.get_ticks() / 1000,
                                           False, char_surf)
            elif character.type == CharacterType.AYESHA:
                GraphicsEngine.draw_fox(30, 30, 15, 0, pygame.time.get_ticks() / 1000,
                                      False, char_surf)
            elif character.type == CharacterType.HANAN:
                GraphicsEngine.draw_owl(30, 30, 15, 0, pygame.time.get_ticks() / 1000,
                                      False, char_surf)
            elif character.type == CharacterType.ASAD:
                GraphicsEngine.draw_lion(30, 30, 15, 0, pygame.time.get_ticks() / 1000,
                                       False, char_surf)
            
            self.screen.blit(char_surf, (x - 30, y - 60))
            
            # Name
            name_font = pygame.font.SysFont('Arial', 20, bold=True)
            name_text = name_font.render(character.name, True, Colors.TEXT)
            self.screen.blit(name_text, (x - name_text.get_width() // 2, y + 20))
            
            # Special ability
            ability_font = pygame.font.SysFont('Arial', 14)
            abilities = [
                "See optimal path",
                "Slow time",
                "Speed to canteen",
                "Distract teachers",
                "Predict movements",
                "Stun teachers"
            ]
            ability_text = ability_font.render(abilities[i], True, Colors.TEXT)
            self.screen.blit(ability_text, (x - ability_text.get_width() // 2, y + 50))
            
            self.buttons[f"char_{i}"] = card_rect
            
            # Selection indicator
            if is_selected:
                pygame.draw.circle(self.screen, (255, 215, 0), (x, y - 90), 10)
        
        # Select button
        select_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60)
        is_hovered = select_rect.collidepoint(mouse_pos)
        
        button_color = Colors.BUTTON_HOVER if is_hovered else Colors.BUTTON
        pygame.draw.rect(self.screen, button_color, select_rect, border_radius=15)
        pygame.draw.rect(self.screen, Colors.TEXT, select_rect, 3, border_radius=15)
        
        select_font = pygame.font.SysFont('Arial', 36, bold=True)
        select_text = select_font.render("SELECT", True, Colors.TEXT)
        self.screen.blit(select_text, (SCREEN_WIDTH // 2 - select_text.get_width() // 2,
                                      SCREEN_HEIGHT - 85))
        
        self.buttons["select"] = select_rect
        
        # Instructions
        instr_font = pygame.font.SysFont('Arial', 18)
        instr_text = instr_font.render("Click a character to select, then click SELECT", 
                                      True, Colors.TEXT)
        self.screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2,
                                     SCREEN_HEIGHT - 150))
    
    def draw_game_screen(self):
        # Animated sky
        self.day_night_cycle = ((pygame.time.get_ticks() - self.game_start_time) % 60000) / 60000
        sky_r = int(135 * (1 - self.day_night_cycle) + 25 * self.day_night_cycle)
        sky_g = int(206 * (1 - self.day_night_cycle) + 25 * self.day_night_cycle)
        sky_b = int(235 * (1 - self.day_night_cycle) + 112 * self.day_night_cycle)
        self.screen.fill((sky_r, sky_g, sky_b))
        
        # Draw ground
        ground_height = 100
        pygame.draw.rect(self.screen, Colors.GRASS,
                        (0, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, ground_height))
        
        # Draw paths between locations
        for i in range(len(self.locations)):
            for j in range(i + 1, len(self.locations)):
                pygame.draw.line(self.screen, Colors.PATH,
                               self.locations[i].position,
                               self.locations[j].position, 1)
        
        # Draw player path
        if self.current_character and len(self.current_character.path_points) > 1:
            pygame.draw.lines(self.screen, (0, 255, 0), False,
                            self.current_character.path_points, 3)
        
        # Draw locations
        for location in self.locations:
            location.draw(self.screen)
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        # Draw teachers
        for teacher in self.teachers:
            teacher.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw character
        if self.current_character:
            self.current_character.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        self.draw_minimap()
        
        # Instructions
        if not self.all_visited:
            instr_font = pygame.font.SysFont('Arial', 20)
            instr_text = instr_font.render("Click on locations to visit them. Visit all 10 locations!", 
                                          True, Colors.TEXT)
            text_bg = pygame.Rect(SCREEN_WIDTH // 2 - instr_text.get_width() // 2 - 10,
                                 SCREEN_HEIGHT - 50, instr_text.get_width() + 20, 40)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), text_bg, border_radius=5)
            self.screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2,
                                         SCREEN_HEIGHT - 40))
    
    def draw_level_complete(self):
        self.screen.fill((25, 25, 50))
        
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        title = title_font.render("Level Complete!", True, (0, 255, 127))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Path comparison
        path_y = 100
        path_height = 300
        
        # Player path
        player_title = title_font.render("Your Path", True, (0, 255, 0))
        self.screen.blit(player_title, (SCREEN_WIDTH // 4 - player_title.get_width() // 2, path_y))
        self.draw_path(self.screen, self.player_path, (0, 255, 0), 2, True)
        
        # Nearest neighbor
        neighbor_title = title_font.render("Nearest Neighbor", True, (155, 89, 182))
        self.screen.blit(neighbor_title, (SCREEN_WIDTH // 2 - neighbor_title.get_width() // 2, path_y))
        self.draw_path(self.screen, self.neighbor_path, (155, 89, 182), 2)
        
        # Optimal path
        optimal_title = title_font.render("Optimal TSP Path", True, (231, 76, 60))
        self.screen.blit(optimal_title, (3 * SCREEN_WIDTH // 4 - optimal_title.get_width() // 2, path_y))
        self.draw_path(self.screen, self.optimal_path, (231, 76, 60), 2)
        
        # Draw location markers
        for location in self.locations:
            x, y = location.position
            # Scale down for comparison view
            scale_x = x * 0.3 + SCREEN_WIDTH * 0.35
            scale_y = y * 0.3 + 250
            pygame.draw.circle(self.screen, (255, 255, 255), (int(scale_x), int(scale_y)), 8)
            
            # Draw connections for all paths
            for path, color in [(self.player_path, (0, 255, 0)),
                               (self.neighbor_path, (155, 89, 182)),
                               (self.optimal_path, (231, 76, 60))]:
                for i in range(len(path) - 1):
                    start = self.locations[path[i]].position
                    end = self.locations[path[i + 1]].position
                    start_x = start[0] * 0.3 + SCREEN_WIDTH * 0.35
                    start_y = start[1] * 0.3 + 250
                    end_x = end[0] * 0.3 + SCREEN_WIDTH * 0.35
                    end_y = end[1] * 0.3 + 250
                    pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 1)
        
        # Stats
        stats_y = path_y + path_height + 50
        stat_font = pygame.font.SysFont('Arial', 24)
        
        # Player stats
        player_stats = [
            f"Your Distance: {int(self.player_distance)}",
            f"Your Efficiency: {int((self.optimal_distance / max(self.player_distance, 1)) * 100)}%",
            f"Time Bonus: +{max(0, int(self.time_remaining)) * 10}"
        ]
        
        for i, stat in enumerate(player_stats):
            text = stat_font.render(stat, True, (0, 255, 0))
            self.screen.blit(text, (SCREEN_WIDTH // 4 - text.get_width() // 2, stats_y + i * 30))
        
        # AI stats
        ai_stats = [
            f"Nearest Neighbor: {int(self.neighbor_distance)}",
            f"Efficiency: {int((self.optimal_distance / max(self.neighbor_distance, 1)) * 100)}%"
        ]
        
        for i, stat in enumerate(ai_stats):
            text = stat_font.render(stat, True, (155, 89, 182))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, stats_y + i * 30))
        
        # Optimal stats
        optimal_stats = [
            f"Optimal Distance: {int(self.optimal_distance)}",
            f"Time Remaining: {int(self.time_remaining)}s"
        ]
        
        for i, stat in enumerate(optimal_stats):
            text = stat_font.render(stat, True, (231, 76, 60))
            self.screen.blit(text, (3 * SCREEN_WIDTH // 4 - text.get_width() // 2, stats_y + i * 30))
        
        # Score
        score_y = stats_y + 120
        score_font = pygame.font.SysFont('Arial', 36, bold=True)
        score_text = score_font.render(f"Total Score: {self.score}", True, (255, 215, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, score_y))
        
        # TSP explanation
        explanation_y = score_y + 60
        exp_font = pygame.font.SysFont('Arial', 18)
        explanations = [
            "Traveling Salesman Problem (TSP): Find shortest route visiting all locations.",
            "Optimal path is the absolute shortest possible route.",
            "Nearest Neighbor is a heuristic that picks closest unvisited location.",
            "Try to get as close to optimal path as possible!"
        ]
        
        for i, exp in enumerate(explanations):
            text = exp_font.render(exp, True, Colors.TEXT)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                   explanation_y + i * 25))
        
        # Continue button
        mouse_pos = pygame.mouse.get_pos()
        continue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60)
        
        button_color = Colors.BUTTON_HOVER if continue_rect.collidepoint(mouse_pos) else Colors.BUTTON
        pygame.draw.rect(self.screen, button_color, continue_rect, border_radius=15)
        pygame.draw.rect(self.screen, Colors.TEXT, continue_rect, 3, border_radius=15)
        
        continue_font = pygame.font.SysFont('Arial', 36, bold=True)
        continue_text = continue_font.render("CONTINUE", True, Colors.TEXT)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2,
                                        SCREEN_HEIGHT - 85))
        
        self.buttons["continue"] = continue_rect
        
        # Celebration particles
        if random.random() < 0.1:
            particle = Particle(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT,
                              "celebration")
            self.particles.append(particle)
    
    def draw_game_over(self):
        self.screen.fill((44, 62, 80))
        
        title_font = pygame.font.SysFont('Arial', 72, bold=True)
        title = title_font.render("GAME OVER", True, (231, 76, 60))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Message
        messages = [
            "Time's up! Better luck next time!",
            "The teachers caught you too many times!",
            "You need to optimize your route better!",
            "Try using Nearest Neighbor strategy next time!"
        ]
        
        message_font = pygame.font.SysFont('Arial', 32)
        message = random.choice(messages)
        message_text = message_font.render(message, True, (236, 240, 241))
        self.screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 200))
        
        # Score
        score_font = pygame.font.SysFont('Arial', 48)
        score_text = score_font.render(f"Final Score: {self.score}", True, (255, 195, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Retry button
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 80)
        retry_color = Colors.BUTTON_HOVER if retry_rect.collidepoint(mouse_pos) else Colors.BUTTON
        pygame.draw.rect(self.screen, retry_color, retry_rect, border_radius=20)
        pygame.draw.rect(self.screen, Colors.TEXT, retry_rect, 3, border_radius=20)
        
        retry_font = pygame.font.SysFont('Arial', 36, bold=True)
        retry_text = retry_font.render("RETRY", True, Colors.TEXT)
        self.screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, 425))
        
        self.buttons["retry"] = retry_rect
        
        # Menu button
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 80)
        menu_color = Colors.BUTTON_HOVER if menu_rect.collidepoint(mouse_pos) else Colors.BUTTON
        pygame.draw.rect(self.screen, menu_color, menu_rect, border_radius=20)
        pygame.draw.rect(self.screen, Colors.TEXT, menu_rect, 3, border_radius=20)
        
        menu_text = retry_font.render("MAIN MENU", True, Colors.TEXT)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 525))
        
        self.buttons["menu"] = menu_rect
        
        # Tips
        tips_font = pygame.font.SysFont('Arial', 18)
        tips = [
            "Tip: Visit locations in logical order to minimize travel distance",
            "Tip: Use character special abilities strategically",
            "Tip: Collect power-ups for bonuses",
            "Tip: Watch teacher patrol patterns to avoid them"
        ]
        
        for i, tip in enumerate(tips):
            text = tips_font.render(tip, True, (189, 195, 199))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                                   600 + i * 30))
    
    def handle_title_click(self, pos):
        if "start" in self.buttons and self.buttons["start"].collidepoint(pos):
            self.state = GameState.CHARACTER_SELECT
    
    def handle_character_select_click(self, pos):
        # Character selection
        for i in range(len(self.characters)):
            if f"char_{i}" in self.buttons and self.buttons[f"char_{i}"].collidepoint(pos):
                self.selected_char_index = i
        
        # Select button
        if "select" in self.buttons and self.buttons["select"].collidepoint(pos):
            self.current_character = self.characters[self.selected_char_index]
            self.state = GameState.PLAYING
            self.game_start_time = pygame.time.get_ticks()
            self.time_remaining = TIME_LIMIT
    
    def handle_game_click(self, pos):
        # Move to clicked location
        if self.current_character:
            self.current_character.target = list(pos)
    
    def handle_level_complete_click(self, pos):
        if "continue" in self.buttons and self.buttons["continue"].collidepoint(pos):
            self.reset_game()
            self.level += 1
            self.state = GameState.PLAYING
            self.game_start_time = pygame.time.get_ticks()
            self.time_remaining = TIME_LIMIT
    
    def handle_game_over_click(self, pos):
        if "retry" in self.buttons and self.buttons["retry"].collidepoint(pos):
            self.reset_game()
            self.state = GameState.PLAYING
            self.game_start_time = pygame.time.get_ticks()
            self.time_remaining = TIME_LIMIT
        elif "menu" in self.buttons and self.buttons["menu"].collidepoint(pos):
            self.reset_game()
            self.state = GameState.TITLE
    
    def run(self):
        last_time = pygame.time.get_ticks()
        
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    if self.state == GameState.TITLE:
                        self.handle_title_click(pos)
                    elif self.state == GameState.CHARACTER_SELECT:
                        self.handle_character_select_click(pos)
                    elif self.state == GameState.PLAYING:
                        self.handle_game_click(pos)
                    elif self.state == GameState.LEVEL_COMPLETE:
                        self.handle_level_complete_click(pos)
                    elif self.state == GameState.GAME_OVER:
                        self.handle_game_over_click(pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.GAME_OVER
                        else:
                            self.running = False
                    
                    elif event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                        if self.current_character and not self.current_character.special_active:
                            self.current_character.special_active = True
                            self.current_character.special_timer = 5.0
                
                elif event.type == pygame.USEREVENT:
                    # Book boost timer expired
                    if self.current_character:
                        self.current_character.speed = self.characters[self.selected_char_index].speed
            
            # Update game state
            if self.state == GameState.PLAYING:
                # Update time
                if not self.all_visited:
                    self.time_remaining -= dt
                    if self.time_remaining <= 0:
                        self.state = GameState.GAME_OVER
                
                # Update character
                if self.current_character:
                    self.current_character.update(dt)
                    self.current_character.move_towards_target(dt)
                
                # Update teachers
                for teacher in self.teachers:
                    teacher.update(dt)
                
                # Update locations
                for location in self.locations:
                    location.update(dt)
                
                # Update power-ups
                for power_up in self.power_ups:
                    power_up.update(dt)
                
                # Update particles
                for particle in self.particles[:]:
                    particle.update(dt)
                    if not particle.is_alive():
                        self.particles.remove(particle)
                
                # Check collisions
                self.check_collisions()
                
                # Check level completion
                if self.all_visited:
                    if current_time - self.level_complete_time > 2000:
                        self.state = GameState.LEVEL_COMPLETE
            
            elif self.state in [GameState.LEVEL_COMPLETE, GameState.GAME_OVER]:
                # Update particles for effects
                for particle in self.particles[:]:
                    particle.update(dt)
                    if not particle.is_alive():
                        self.particles.remove(particle)
                
                # Add celebration particles occasionally
                if self.state == GameState.LEVEL_COMPLETE and random.random() < 0.05:
                    particle = Particle(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT,
                                      "celebration")
                    self.particles.append(particle)
            
            # Draw current screen
            if self.state == GameState.TITLE:
                self.draw_title_screen()
            elif self.state == GameState.CHARACTER_SELECT:
                self.draw_character_select()
            elif self.state == GameState.PLAYING:
                self.draw_game_screen()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# ================ MAIN ENTRY POINT ================
if __name__ == "__main__":
    game = CampusBunkingGame()
    game.run()