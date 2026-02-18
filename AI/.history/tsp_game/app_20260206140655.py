import pygame
import math
import random
import sys
import itertools
from enum import Enum

# Initialize PyGame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TILE_SIZE = 64
TIME_LIMIT = 120  # 2 minutes in seconds

# Colors
BACKGROUND = (240, 248, 255)
PATH_COLOR = (100, 149, 237)
PLAYER_PATH_COLOR = (46, 204, 113)
OPTIMAL_PATH_COLOR = (231, 76, 60)
NEIGHBOR_PATH_COLOR = (155, 89, 182)
TEXT_COLOR = (44, 62, 80)
BUTTON_COLOR = (52, 152, 219)
BUTTON_HOVER_COLOR = (41, 128, 185)
UI_BG = (236, 240, 241, 200)

class GameState(Enum):
    TITLE = 1
    CHARACTER_SELECT = 2
    PLAYING = 3
    LEVEL_COMPLETE = 4
    GAME_OVER = 5

class CharacterType(Enum):
    ALINA = 0
    KAINAT = 1
    AIZA = 2
    AYESHA = 3
    HANAN = 4
    ASAD = 5

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

class Animation:
    def __init__(self, frames, speed=0.1):
        self.frames = frames
        self.speed = speed
        self.current_frame = 0
        self.timer = 0
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        return self.frames[int(self.current_frame)]

class Character:
    def __init__(self, char_type, name, color, special_ability):
        self.type = char_type
        self.name = name
        self.color = color
        self.special_ability = special_ability
        self.position = [100, 100]
        self.target_position = [100, 100]
        self.speed = 3
        self.animation_timer = 0
        self.animation_frame = 0
        self.direction = 0  # 0: right, 1: down, 2: left, 3: up
        self.visited_locations = []
        self.path_points = []
        self.special_active = False
        self.special_timer = 0
        self.power_ups = []
        
    def move_towards_target(self):
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > self.speed:
            self.position[0] += (dx / dist) * self.speed
            self.position[1] += (dy / dist) * self.speed
            
            # Update direction for animation
            if abs(dx) > abs(dy):
                self.direction = 0 if dx > 0 else 2
            else:
                self.direction = 1 if dy > 0 else 3
                
            self.animation_timer += 0.1
            if self.animation_timer > 0.5:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0
                
            # Add to path
            self.path_points.append(self.position.copy())
            
            return False
        else:
            self.position = self.target_position.copy()
            return True
    
    def use_special(self):
        self.special_active = True
        self.special_timer = 5.0  # 5 seconds
        
    def update(self, dt):
        if self.special_active:
            self.special_timer -= dt
            if self.special_timer <= 0:
                self.special_active = False
    
    def draw(self, screen):
        # Draw walking character (simplified with colored circles and rectangles)
        size = 20
        x, y = int(self.position[0]), int(self.position[1])
        
        # Body
        pygame.draw.circle(screen, self.color, (x, y - 10), 15)
        
        # Direction indicator
        dir_offsets = [(15, 0), (0, 15), (-15, 0), (0, -15)]
        dx, dy = dir_offsets[self.direction]
        pygame.draw.line(screen, (0, 0, 0), (x, y - 10), (x + dx, y - 10 + dy), 3)
        
        # Animation effect
        if self.animation_frame % 2 == 0:
            pygame.draw.circle(screen, (255, 255, 255), (x + 5, y - 15), 3)
        
        # Special ability effect
        if self.special_active:
            pygame.draw.circle(screen, (255, 255, 0, 100), (x, y - 10), 
                             25 + math.sin(pygame.time.get_ticks() * 0.01) * 5, 2)

class Location:
    def __init__(self, loc_type, name, position, icon_char):
        self.type = loc_type
        self.name = name
        self.position = position
        self.icon_char = icon_char
        self.visited = False
        self.animation_timer = 0
        self.visited_animation = 0
        self.connections = []
        
    def update(self, dt):
        self.animation_timer += dt
        if self.visited:
            self.visited_animation += dt * 2
            
    def draw(self, screen, font):
        x, y = self.position
        size = 30
        
        # Draw location circle
        color = (46, 204, 113) if self.visited else (52, 152, 219)
        pygame.draw.circle(screen, color, (x, y), size)
        pygame.draw.circle(screen, (255, 255, 255), (x, y), size, 2)
        
        # Animated icon
        anim_offset = math.sin(self.animation_timer) * 3
        icon = font.render(self.icon_char, True, (255, 255, 255))
        screen.blit(icon, (x - 8, y - 12 + anim_offset))
        
        # Visited animation
        if self.visited:
            alpha = max(0, 255 - int(self.visited_animation * 50))
            if alpha > 0:
                pulse_size = size + int(self.visited_animation * 10)
                s = pygame.Surface((pulse_size * 2, pulse_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (46, 204, 113, alpha), (pulse_size, pulse_size), pulse_size)
                screen.blit(s, (x - pulse_size, y - pulse_size))
        
        # Draw name
        name_text = font.render(self.name, True, TEXT_COLOR)
        screen.blit(name_text, (x - name_text.get_width() // 2, y + size + 5))

class Teacher:
    def __init__(self, teacher_type, patrol_points):
        self.type = teacher_type
        self.patrol_points = patrol_points
        self.current_target = 0
        self.position = patrol_points[0].copy()
        self.speed = 1.5
        self.direction = 0
        self.animation_timer = 0
        self.color = (231, 76, 60)  # Red
        
    def update(self, dt):
        target = self.patrol_points[self.current_target]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.speed:
            self.current_target = (self.current_target + 1) % len(self.patrol_points)
        else:
            self.position[0] += (dx / dist) * self.speed
            self.position[1] += (dy / dist) * self.speed
            self.direction = 0 if dx > 0 else 2 if dx < 0 else (1 if dy > 0 else 3)
            
        self.animation_timer += dt
        
    def draw(self, screen):
        x, y = int(self.position[0]), int(self.position[1])
        
        # Teacher body
        pygame.draw.rect(screen, self.color, (x - 15, y - 20, 30, 40))
        
        # Teacher head
        pygame.draw.circle(screen, (255, 218, 185), (x, y - 30), 12)
        
        # Direction indicator
        if math.sin(self.animation_timer * 5) > 0:
            dir_points = {
                0: [(x + 15, y), (x + 25, y)],
                1: [(x, y + 20), (x, y + 30)],
                2: [(x - 15, y), (x - 25, y)],
                3: [(x, y - 20), (x, y - 30)]
            }
            points = dir_points.get(self.direction, [])
            if points:
                pygame.draw.line(screen, (0, 0, 0), points[0], points[1], 3)
        
        # Vision cone
        vision_length = 100
        angle = self.direction * 90
        left_angle = math.radians(angle - 30)
        right_angle = math.radians(angle + 30)
        
        points = [(x, y)]
        points.append((x + math.cos(left_angle) * vision_length, 
                      y + math.sin(left_angle) * vision_length))
        points.append((x + math.cos(right_angle) * vision_length, 
                      y + math.sin(right_angle) * vision_length))
        
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(s, (231, 76, 60, 50), points)
        screen.blit(s, (0, 0))

class PowerUp:
    def __init__(self, power_type, position):
        self.type = power_type
        self.position = position
        self.animation_timer = 0
        self.collected = False
        self.colors = {
            PowerUpType.BOOK_BOOST: (41, 128, 185),
            PowerUpType.CHAI_CHARGE: (192, 57, 43),
            PowerUpType.SMART_CAP: (39, 174, 96),
            PowerUpType.BICYCLE: (142, 68, 173),
            PowerUpType.PHONE: (44, 62, 80)
        }
        self.icons = ["📚", "☕", "🎓", "🚲", "📱"]
        
    def update(self, dt):
        self.animation_timer += dt
        
    def draw(self, screen, font):
        if self.collected:
            return
            
        x, y = self.position
        anim_offset = math.sin(self.animation_timer * 3) * 5
        
        # Draw glow effect
        for i in range(3):
            radius = 15 + i * 5
            alpha = 100 - i * 30
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = self.colors[self.type]
            pygame.draw.circle(s, (*color, alpha), (radius, radius), radius)
            screen.blit(s, (x - radius, y - radius + anim_offset))
        
        # Draw icon
        icon = font.render(self.icons[self.type.value], True, (255, 255, 255))
        screen.blit(icon, (x - 10, y - 10 + anim_offset))

class TSP_Solver:
    @staticmethod
    def calculate_distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    @staticmethod
    def calculate_path_length(path, locations):
        total = 0
        for i in range(len(path) - 1):
            pos1 = locations[path[i]].position
            pos2 = locations[path[i + 1]].position
            total += TSP_Solver.calculate_distance(pos1, pos2)
        return total
    
    @staticmethod
    def brute_force_optimal_path(locations):
        """Brute force TSP solution for 10 locations (feasible)"""
        indices = list(range(len(locations)))
        best_path = None
        best_distance = float('inf')
        
        # Start from location 0 (CS Department)
        start_index = 0
        remaining = indices[1:]
        
        for perm in itertools.permutations(remaining):
            path = [start_index] + list(perm) + [start_index]
            distance = TSP_Solver.calculate_path_length(path, locations)
            if distance < best_distance:
                best_distance = distance
                best_path = path
                
        return best_path, best_distance
    
    @staticmethod
    def nearest_neighbor_path(locations):
        """Nearest neighbor heuristic solution"""
        unvisited = set(range(len(locations)))
        current = 0  # Start from CS Department
        path = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = None
            nearest_dist = float('inf')
            
            for loc in unvisited:
                dist = TSP_Solver.calculate_distance(
                    locations[current].position,
                    locations[loc].position
                )
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = loc
            
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to start
        path.append(0)
        return path, TSP_Solver.calculate_path_length(path, locations)

class Particle:
    def __init__(self, x, y, color, velocity, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(3, 8)
        
    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.lifetime -= dt
        self.size = max(0, int(self.size * (self.lifetime / self.max_lifetime)))
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
            screen.blit(s, (self.x - self.size, self.y - self.size))
            
    def is_alive(self):
        return self.lifetime > 0

class CampusBunkingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Campus Bunking Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.TITLE
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.normal_font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Game elements
        self.characters = []
        self.locations = []
        self.teachers = []
        self.power_ups = []
        self.particles = []
        self.current_character = None
        self.selected_character_index = 0
        
        # Game state
        self.time_remaining = TIME_LIMIT
        self.score = 0
        self.level = 1
        self.game_start_time = 0
        self.path_distance = 0
        self.all_visited = False
        self.level_complete_time = 0
        
        # TSP paths
        self.player_path = []
        self.optimal_path = []
        self.neighbor_path = []
        self.optimal_distance = 0
        self.neighbor_distance = 0
        
        # UI
        self.buttons = {}
        self.day_night_cycle = 0  # 0-1, where 0 is day, 1 is night
        self.sky_color = (135, 206, 235)
        
        # Initialize game
        self.create_characters()
        self.create_locations()
        self.create_teachers()
        self.create_power_ups()
        
    def create_characters(self):
        self.characters = [
            Character(CharacterType.ALINA, "Alina", (52, 152, 219), "See optimal path"),
            Character(CharacterType.KAINAT, "Kainat", (39, 174, 96), "Slow time"),
            Character(CharacterType.AIZA, "Aiza", (230, 126, 34), "Speed to canteen"),
            Character(CharacterType.AYESHA, "Ayesha", (155, 89, 182), "Distract teachers"),
            Character(CharacterType.HANAN, "Hanan", (22, 160, 133), "Predict movements"),
            Character(CharacterType.ASAD, "Asad", (192, 57, 43), "Stun teachers")
        ]
        
    def create_locations(self):
        # Create 10 campus locations in a circular layout
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = min(center_x, center_y) - 150
        
        location_data = [
            (LocationType.CS_DEPT, "CS Dept", "💻"),
            (LocationType.LIBRARY, "Library", "📚"),
            (LocationType.CANTEEN, "Canteen", "🍔"),
            (LocationType.AUDITORIUM, "Auditorium", "🎭"),
            (LocationType.SPORTS_GROUND, "Sports", "⚽"),
            (LocationType.ADMIN_BLOCK, "Admin", "🏛️"),
            (LocationType.PARKING, "Parking", "🚗"),
            (LocationType.GARDEN, "Garden", "🌸"),
            (LocationType.HOSTEL, "Hostel", "🏠"),
            (LocationType.MAIN_GATE, "Main Gate", "🚪")
        ]
        
        for i, (loc_type, name, icon) in enumerate(location_data):
            angle = (i / len(location_data)) * 2 * math.pi
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            self.locations.append(Location(loc_type, name, [x, y], icon))
        
        # Start player at CS Department
        self.characters[0].position = self.locations[0].position.copy()
        self.characters[0].target_position = self.locations[0].position.copy()
        
    def create_teachers(self):
        # Create 3 teachers with different patrol patterns
        patterns = [
            [(200, 200), (400, 200), (400, 400), (200, 400)],  # Square pattern
            [(SCREEN_WIDTH - 200, 200), (SCREEN_WIDTH - 400, 300), 
             (SCREEN_WIDTH - 200, 400)],  # Triangle pattern
            [(SCREEN_WIDTH // 2, 100), (100, SCREEN_HEIGHT // 2),
             (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), 
             (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)]  # Diamond pattern
        ]
        
        for i, pattern in enumerate(patterns):
            teacher = Teacher(i, pattern)
            # Position teacher at first patrol point
            teacher.position = pattern[0].copy()
            self.teachers.append(teacher)
    
    def create_power_ups(self):
        # Create 5 power-ups at random locations
        for i in range(5):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            power_type = PowerUpType(i)
            self.power_ups.append(PowerUp(power_type, [x, y]))
    
    def check_collision_with_teacher(self, character):
        for teacher in self.teachers:
            dx = character.position[0] - teacher.position[0]
            dy = character.position[1] - teacher.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 40:  # Collision distance
                # Create caught particles
                for _ in range(20):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 5)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    self.particles.append(Particle(
                        character.position[0], character.position[1],
                        (231, 76, 60), (vx, vy), 1.0
                    ))
                
                return True
        return False
    
    def collect_power_up(self, character):
        for power_up in self.power_ups:
            if not power_up.collected:
                dx = character.position[0] - power_up.position[0]
                dy = character.position[1] - power_up.position[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 30:
                    power_up.collected = True
                    character.power_ups.append(power_up.type)
                    
                    # Create collection particles
                    for _ in range(15):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(1, 3)
                        vx = math.cos(angle) * speed
                        vy = math.sin(angle) * speed
                        self.particles.append(Particle(
                            power_up.position[0], power_up.position[1],
                            power_up.colors[power_up.type], (vx, vy), 1.5
                        ))
                    
                    # Apply power-up effect
                    if power_up.type == PowerUpType.CHAI_CHARGE:
                        self.time_remaining += 10  # Add 10 seconds
                    elif power_up.type == PowerUpType.BOOK_BOOST:
                        character.speed = 5  # Speed boost for 5 seconds
                        pygame.time.set_timer(pygame.USEREVENT + 1, 5000, 1)
                    
                    return True
        return False
    
    def check_location_visit(self, character):
        for i, location in enumerate(self.locations):
            if not location.visited:
                dx = character.position[0] - location.position[0]
                dy = character.position[1] - location.position[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 40:  # Visit distance
                    location.visited = True
                    character.visited_locations.append(i)
                    
                    # Create visit particles
                    for _ in range(10):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(1, 2)
                        vx = math.cos(angle) * speed
                        vy = math.sin(angle) * speed
                        self.particles.append(Particle(
                            location.position[0], location.position[1],
                            (46, 204, 113), (vx, vy), 1.0
                        ))
                    
                    # Check if all locations visited
                    self.all_visited = all(loc.visited for loc in self.locations)
                    if self.all_visited:
                        self.level_complete_time = pygame.time.get_ticks()
                        self.calculate_paths()
                    
                    return True
        return False
    
    def calculate_paths(self):
        # Calculate player path
        if self.current_character and self.current_character.visited_locations:
            self.player_path = [0] + self.current_character.visited_locations + [0]
            self.path_distance = TSP_Solver.calculate_path_length(
                self.player_path, self.locations
            )
        
        # Calculate optimal TSP path using brute force
        self.optimal_path, self.optimal_distance = TSP_Solver.brute_force_optimal_path(self.locations)
        
        # Calculate nearest neighbor path
        self.neighbor_path, self.neighbor_distance = TSP_Solver.nearest_neighbor_path(self.locations)
        
        # Calculate score
        efficiency = (self.optimal_distance / max(self.path_distance, 0.1)) * 100
        time_bonus = max(0, self.time_remaining) * 10
        self.score = int(efficiency * 10 + time_bonus)
    
    def draw_path(self, screen, path, color, width=2):
        if len(path) < 2:
            return
            
        for i in range(len(path) - 1):
            start_pos = self.locations[path[i]].position
            end_pos = self.locations[path[i + 1]].position
            
            # Draw animated line (pulse effect)
            progress = (pygame.time.get_ticks() % 2000) / 2000
            pulse_pos = [
                start_pos[0] + (end_pos[0] - start_pos[0]) * progress,
                start_pos[1] + (end_pos[1] - start_pos[1]) * progress
            ]
            
            pygame.draw.line(screen, color, start_pos, end_pos, width)
            
            # Draw moving point on line
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(pulse_pos[0]), int(pulse_pos[1])), 4)
    
    def draw_title_screen(self):
        # Animated background
        self.day_night_cycle = (pygame.time.get_ticks() % 60000) / 60000
        sky_r = int(135 + 100 * math.sin(self.day_night_cycle * math.pi))
        sky_g = int(206 - 50 * math.sin(self.day_night_cycle * math.pi))
        sky_b = int(235 - 100 * math.sin(self.day_night_cycle * math.pi))
        self.sky_color = (sky_r, sky_g, sky_b)
        
        self.screen.fill(self.sky_color)
        
        # Draw floating campus elements
        for i in range(10):
            x = (pygame.time.get_ticks() // 50 + i * 100) % SCREEN_WIDTH
            y = SCREEN_HEIGHT // 3 + math.sin(pygame.time.get_ticks() / 1000 + i) * 50
            icon = self.locations[i].icon_char
            text = self.title_font.render(icon, True, (255, 255, 255, 128))
            self.screen.blit(text, (x, y))
        
        # Title
        title = self.title_font.render("Campus Bunking Adventure", True, TEXT_COLOR)
        title_shadow = self.title_font.render("Campus Bunking Adventure", True, (255, 255, 255))
        
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        title_y = SCREEN_HEIGHT // 4
        
        self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title, (title_x, title_y))
        
        # Subtitle
        subtitle = self.normal_font.render("Learn TSP while exploring campus!", True, TEXT_COLOR)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, title_y + 90))
        
        # Start button
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60)
        
        button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3, border_radius=15)
        
        start_text = self.header_font.render("START", True, (255, 255, 255))
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 
                                     SCREEN_HEIGHT // 2 + 65))
        
        # Instructions
        instructions = [
            "🎯 Visit all 10 campus locations in optimal order",
            "👥 Choose a character with special abilities",
            "👨‍🏫 Avoid teachers or lose time",
            "✨ Collect power-ups for bonuses",
            "📊 Learn Traveling Salesman Problem concepts!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, TEXT_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                                   SCREEN_HEIGHT // 2 + 150 + i * 30))
        
        # Store button for click detection
        self.buttons["start"] = button_rect
    
    def draw_character_selection(self):
        self.screen.fill(BACKGROUND)
        
        # Title
        title = self.header_font.render("Choose Your Character", True, TEXT_COLOR)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw characters
        char_width = 150
        start_x = (SCREEN_WIDTH - len(self.characters) * char_width) // 2 + char_width // 2
        
        mouse_pos = pygame.mouse.get_pos()
        self.buttons.clear()
        
        for i, character in enumerate(self.characters):
            x = start_x + i * char_width
            y = SCREEN_HEIGHT // 3
            
            # Draw character card
            card_rect = pygame.Rect(x - 60, y - 80, 120, 160)
            is_hovered = card_rect.collidepoint(mouse_pos)
            is_selected = i == self.selected_character_index
            
            color = character.color if not is_selected else (255, 195, 0)
            if is_hovered and not is_selected:
                color = tuple(min(255, c + 30) for c in color)
            
            pygame.draw.rect(self.screen, color, card_rect, border_radius=15)
            pygame.draw.rect(self.screen, (255, 255, 255), card_rect, 3, border_radius=15)
            
            # Draw character
            char_x, char_y = x, y
            pygame.draw.circle(self.screen, character.color, (char_x, char_y - 10), 40)
            
            # Draw face
            pygame.draw.circle(self.screen, (255, 218, 185), (char_x, char_y - 20), 20)
            pygame.draw.circle(self.screen, (0, 0, 0), (char_x - 5, char_y - 25), 3)
            pygame.draw.circle(self.screen, (0, 0, 0), (char_x + 5, char_y - 25), 3)
            
            # Draw name
            name_text = self.normal_font.render(character.name, True, TEXT_COLOR)
            self.screen.blit(name_text, (x - name_text.get_width() // 2, y + 40))
            
            # Draw special ability
            ability_text = self.small_font.render(character.special_ability, True, TEXT_COLOR)
            self.screen.blit(ability_text, (x - ability_text.get_width() // 2, y + 70))
            
            # Store button
            self.buttons[f"char_{i}"] = card_rect
            
            # Draw selection indicator
            if is_selected:
                pygame.draw.circle(self.screen, (255, 195, 0), (x, y - 80), 10)
        
        # Select button
        select_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60)
        is_hovered = select_rect.collidepoint(mouse_pos)
        
        button_color = BUTTON_HOVER_COLOR if is_hovered else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, select_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), select_rect, 3, border_radius=15)
        
        select_text = self.header_font.render("SELECT", True, (255, 255, 255))
        self.screen.blit(select_text, (SCREEN_WIDTH // 2 - select_text.get_width() // 2, 
                                      SCREEN_HEIGHT - 85))
        
        self.buttons["select"] = select_rect
        
        # Instructions
        instructions = self.small_font.render("Click a character to select, then click SELECT", True, TEXT_COLOR)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 
                                       SCREEN_HEIGHT - 150))
    
    def draw_game_screen(self):
        # Draw animated background
        self.screen.fill(self.sky_color)
        
        # Draw day/night cycle
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        night_alpha = int(150 * abs(math.sin(self.day_night_cycle * math.pi)))
        overlay.fill((0, 0, 50, night_alpha))
        self.screen.blit(overlay, (0, 0))
        
        # Draw connections between locations
        for i, loc1 in enumerate(self.locations):
            for j, loc2 in enumerate(self.locations[i+1:], i+1):
                pygame.draw.line(self.screen, (200, 200, 200, 50), 
                               loc1.position, loc2.position, 1)
        
        # Draw player path
        if self.current_character and len(self.current_character.path_points) > 1:
            pygame.draw.lines(self.screen, PLAYER_PATH_COLOR, False, 
                            self.current_character.path_points, 3)
        
        # Draw locations
        for location in self.locations:
            location.draw(self.screen, self.normal_font)
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen, self.normal_font)
        
        # Draw teachers
        for teacher in self.teachers:
            teacher.draw(self.screen)
        
        # Draw particles
        for particle in self.particles[:]:
            particle.draw(self.screen)
        
        # Draw character
        if self.current_character:
            self.current_character.draw(self.screen)
        
        # Draw UI panel
        ui_panel = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        ui_panel.fill(UI_BG)
        self.screen.blit(ui_panel, (0, 0))
        
        # Draw time remaining
        time_text = self.normal_font.render(f"Time: {int(self.time_remaining)}s", True, TEXT_COLOR)
        self.screen.blit(time_text, (20, 20))
        
        # Draw progress
        visited_count = sum(1 for loc in self.locations if loc.visited)
        progress_text = self.normal_font.render(f"Visited: {visited_count}/10", True, TEXT_COLOR)
        self.screen.blit(progress_text, (20, 50))
        
        # Draw distance
        distance_text = self.normal_font.render(f"Distance: {int(self.path_distance)}", True, TEXT_COLOR)
        self.screen.blit(distance_text, (200, 20))
        
        # Draw current character info
        if self.current_character:
            char_text = self.normal_font.render(f"Character: {self.current_character.name}", True, TEXT_COLOR)
            self.screen.blit(char_text, (200, 50))
        
        # Draw power-up inventory
        pygame.draw.rect(self.screen, (255, 255, 255), (SCREEN_WIDTH - 220, 20, 200, 60), border_radius=10)
        power_text = self.normal_font.render("Power-ups:", True, TEXT_COLOR)
        self.screen.blit(power_text, (SCREEN_WIDTH - 210, 25))
        
        for i, power_type in enumerate(self.current_character.power_ups[-3:]):  # Show last 3
            icon = self.small_font.render(["📚", "☕", "🎓", "🚲", "📱"][power_type.value], True, TEXT_COLOR)
            self.screen.blit(icon, (SCREEN_WIDTH - 210 + i * 30, 50))
        
        # Draw instructions
        if not self.all_visited:
            instr_text = self.small_font.render("Click on locations to visit them. Visit all 10 locations!", True, TEXT_COLOR)
            self.screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2, 70))
        
        # Draw minimap
        self.draw_minimap()
    
    def draw_minimap(self):
        minimap_size = 150
        minimap_x = SCREEN_WIDTH - minimap_size - 20
        minimap_y = SCREEN_HEIGHT - minimap_size - 20
        
        # Draw minimap background
        minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        minimap_surface.fill((0, 0, 0, 100))
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Scale factor for locations
        scale = minimap_size / max(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Draw location dots
        for location in self.locations:
            x = minimap_x + location.position[0] * scale
            y = minimap_y + location.position[1] * scale
            color = (46, 204, 113) if location.visited else (52, 152, 219)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 4)
        
        # Draw character dot
        if self.current_character:
            x = minimap_x + self.current_character.position[0] * scale
            y = minimap_y + self.current_character.position[1] * scale
            pygame.draw.circle(self.screen, (255, 255, 0), (int(x), int(y)), 6)
        
        # Draw teacher dots
        for teacher in self.teachers:
            x = minimap_x + teacher.position[0] * scale
            y = minimap_y + teacher.position[1] * scale
            pygame.draw.circle(self.screen, (231, 76, 60), (int(x), int(y)), 4)
    
    def draw_level_complete(self):
        self.screen.fill(BACKGROUND)
        
        # Title
        title = self.header_font.render("Level Complete!", True, (46, 204, 113))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw path comparison
        path_y = 150
        path_height = 300
        
        # Player's path
        player_title = self.normal_font.render("Your Path", True, PLAYER_PATH_COLOR)
        self.screen.blit(player_title, (SCREEN_WIDTH // 4 - player_title.get_width() // 2, path_y - 40))
        self.draw_path(self.screen, self.player_path, PLAYER_PATH_COLOR)
        
        # Nearest Neighbor path
        neighbor_title = self.normal_font.render("Nearest Neighbor", True, NEIGHBOR_PATH_COLOR)
        self.screen.blit(neighbor_title, (SCREEN_WIDTH // 2 - neighbor_title.get_width() // 2, path_y - 40))
        self.draw_path(self.screen, self.neighbor_path, NEIGHBOR_PATH_COLOR)
        
        # Optimal path
        optimal_title = self.normal_font.render("Optimal TSP Path", True, OPTIMAL_PATH_COLOR)
        self.screen.blit(optimal_title, (3 * SCREEN_WIDTH // 4 - optimal_title.get_width() // 2, path_y - 40))
        self.draw_path(self.screen, self.optimal_path, OPTIMAL_PATH_COLOR)
        
        # Stats
        stats_y = path_y + path_height + 50
        
        # Player stats
        player_stats = [
            f"Your Distance: {int(self.path_distance)}",
            f"Your Efficiency: {int((self.optimal_distance / max(self.path_distance, 0.1)) * 100)}%",
            f"Time Bonus: {max(0, int(self.time_remaining)) * 10} points"
        ]
        
        for i, stat in enumerate(player_stats):
            text = self.normal_font.render(stat, True, PLAYER_PATH_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 4 - text.get_width() // 2, stats_y + i * 30))
        
        # AI stats
        ai_stats = [
            f"Nearest Neighbor: {int(self.neighbor_distance)}",
            f"Efficiency: {int((self.optimal_distance / max(self.neighbor_distance, 0.1)) * 100)}%"
        ]
        
        for i, stat in enumerate(ai_stats):
            text = self.normal_font.render(stat, True, NEIGHBOR_PATH_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, stats_y + i * 30))
        
        # Optimal stats
        optimal_stats = [
            f"Optimal Distance: {int(self.optimal_distance)}",
            f"Time Remaining: {int(self.time_remaining)}s"
        ]
        
        for i, stat in enumerate(optimal_stats):
            text = self.normal_font.render(stat, True, OPTIMAL_PATH_COLOR)
            self.screen.blit(text, (3 * SCREEN_WIDTH // 4 - text.get_width() // 2, stats_y + i * 30))
        
        # Score
        score_y = stats_y + 120
        score_text = self.header_font.render(f"Total Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, score_y))
        
        # TSP Explanation
        explanation = [
            "Traveling Salesman Problem (TSP): Find the shortest route visiting all locations.",
            "The optimal path is the absolute shortest possible route.",
            "Nearest Neighbor is a heuristic that picks the closest unvisited location.",
            "Try to get as close to the optimal path as possible!"
        ]
        
        for i, line in enumerate(explanation):
            text = self.small_font.render(line, True, TEXT_COLOR)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, score_y + 60 + i * 25))
        
        # Continue button
        mouse_pos = pygame.mouse.get_pos()
        continue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 60)
        
        button_color = BUTTON_HOVER_COLOR if continue_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, continue_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), continue_rect, 3, border_radius=15)
        
        continue_text = self.header_font.render("CONTINUE", True, (255, 255, 255))
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 
                                        SCREEN_HEIGHT - 85))
        
        self.buttons["continue"] = continue_rect
        
        # Celebration particles
        if random.random() < 0.1:
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT
            for _ in range(10):
                angle = random.uniform(math.pi, 2 * math.pi)
                speed = random.uniform(2, 5)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                color = random.choice([(255, 50, 50), (50, 255, 50), (50, 50, 255), 
                                      (255, 255, 50), (255, 50, 255)])
                self.particles.append(Particle(x, y, color, (vx, vy), 2.0))
    
    def draw_game_over(self):
        self.screen.fill((44, 62, 80))
        
        # Game Over text
        game_over = self.title_font.render("GAME OVER", True, (231, 76, 60))
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 100))
        
        # Message
        messages = [
            "Time's up! Better luck next time!",
            "The teachers caught you too many times!",
            "You need to optimize your route better!",
            "Try using Nearest Neighbor strategy next time!"
        ]
        
        message = random.choice(messages)
        message_text = self.header_font.render(message, True, (236, 240, 241))
        self.screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 200))
        
        # Score
        score_text = self.header_font.render(f"Final Score: {self.score}", True, (255, 195, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
        
        # Retry button
        mouse_pos = pygame.mouse.get_pos()
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 400, 300, 80)
        
        button_color = BUTTON_HOVER_COLOR if retry_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, retry_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), retry_rect, 3, border_radius=20)
        
        retry_text = self.header_font.render("RETRY", True, (255, 255, 255))
        self.screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, 425))
        
        self.buttons["retry"] = retry_rect
        
        # Menu button
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 500, 300, 80)
        button_color = BUTTON_HOVER_COLOR if menu_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, menu_rect, border_radius=20)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 3, border_radius=20)
        
        menu_text = self.header_font.render("MAIN MENU", True, (255, 255, 255))
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 525))
        
        self.buttons["menu"] = menu_rect
        
        # Tips
        tips = [
            "Tip: Visit locations in a logical order to minimize travel distance",
            "Tip: Use character special abilities strategically",
            "Tip: Collect power-ups for bonuses",
            "Tip: Watch teacher patrol patterns to avoid them"
        ]
        
        for i, tip in enumerate(tips):
            tip_text = self.small_font.render(tip, True, (189, 195, 199))
            self.screen.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, 
                                       600 + i * 30))
    
    def handle_title_click(self, pos):
        if "start" in self.buttons and self.buttons["start"].collidepoint(pos):
            self.state = GameState.CHARACTER_SELECT
    
    def handle_character_select_click(self, pos):
        # Check character selection
        for i in range(len(self.characters)):
            if f"char_{i}" in self.buttons and self.buttons[f"char_{i}"].collidepoint(pos):
                self.selected_character_index = i
                # Play selection sound (placeholder)
                return
        
        # Check select button
        if "select" in self.buttons and self.buttons["select"].collidepoint(pos):
            self.current_character = self.characters[self.selected_character_index]
            self.state = GameState.PLAYING
            self.game_start_time = pygame.time.get_ticks()
            self.time_remaining = TIME_LIMIT
    
    def handle_game_click(self, pos):
        # Check if clicking on a location
        for location in self.locations:
            dx = pos[0] - location.position[0]
            dy = pos[1] - location.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 40:  # Click radius
                self.current_character.target_position = location.position.copy()
                return
    
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
    
    def reset_game(self):
        # Reset game state
        self.time_remaining = TIME_LIMIT
        self.score = 0
        self.all_visited = False
        
        # Reset character
        if self.current_character:
            self.current_character.position = self.locations[0].position.copy()
            self.current_character.target_position = self.locations[0].position.copy()
            self.current_character.visited_locations = []
            self.current_character.path_points = []
            self.current_character.power_ups = []
        
        # Reset locations
        for location in self.locations:
            location.visited = False
            location.visited_animation = 0
        
        # Reset power-ups
        for power_up in self.power_ups:
            power_up.collected = False
        
        # Reset particles
        self.particles.clear()
        
        # Reset teachers positions
        for teacher in self.teachers:
            teacher.position = teacher.patrol_points[0].copy()
            teacher.current_target = 0
    
    def update(self, dt):
        # Update day/night cycle
        self.day_night_cycle = ((pygame.time.get_ticks() - self.game_start_time) % 60000) / 60000
        
        if self.state == GameState.PLAYING:
            # Update time
            if not self.all_visited:
                self.time_remaining -= dt
                
                if self.time_remaining <= 0:
                    self.state = GameState.GAME_OVER
                    return
            
            # Update character
            if self.current_character:
                self.current_character.update(dt)
                arrived = self.current_character.move_towards_target()
                
                # Check for collisions and collections
                if arrived:
                    self.check_location_visit(self.current_character)
                
                if self.check_collision_with_teacher(self.current_character):
                    self.time_remaining -= 10  # Lose 10 seconds
                
                self.collect_power_up(self.current_character)
                
                # Update path distance
                if len(self.current_character.path_points) > 1:
                    total_dist = 0
                    for i in range(len(self.current_character.path_points) - 1):
                        p1 = self.current_character.path_points[i]
                        p2 = self.current_character.path_points[i + 1]
                        total_dist += math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    self.path_distance = total_dist
            
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
        
        elif self.state == GameState.LEVEL_COMPLETE:
            # Update particles for celebration
            for particle in self.particles[:]:
                particle.update(dt)
                if not particle.is_alive():
                    self.particles.remove(particle)
            
            # Add occasional celebration particles
            if random.random() < 0.05:
                x = random.randint(0, SCREEN_WIDTH)
                y = SCREEN_HEIGHT
                for _ in range(5):
                    angle = random.uniform(math.pi, 2 * math.pi)
                    speed = random.uniform(2, 5)
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    color = random.choice([(255, 50, 50), (50, 255, 50), (50, 50, 255)])
                    self.particles.append(Particle(x, y, color, (vx, vy), 2.0))
    
    def run(self):
        last_time = pygame.time.get_ticks()
        
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Delta time in seconds
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
                        if self.current_character:
                            self.current_character.use_special()
                
                elif event.type == pygame.USEREVENT + 1:  # Book boost timer
                    if self.current_character:
                        self.current_character.speed = 3  # Reset speed
            
            # Update game state
            self.update(dt)
            
            # Check for level completion
            if self.state == GameState.PLAYING and self.all_visited:
                if pygame.time.get_ticks() - self.level_complete_time > 2000:  # 2 second delay
                    self.state = GameState.LEVEL_COMPLETE
            
            # Draw current screen
            if self.state == GameState.TITLE:
                self.draw_title_screen()
            elif self.state == GameState.CHARACTER_SELECT:
                self.draw_character_selection()
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

if __name__ == "__main__":
    game = CampusBunkingGame()
    game.run()