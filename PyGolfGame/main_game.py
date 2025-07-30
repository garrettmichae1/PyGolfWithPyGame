#import statements
from matplotlib.pyplot import title
import pygame
import math
import sys

#initialize the game
pygame.init()

#sets up the screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyGolf")

#constants
clock = pygame.time.Clock()
FPS = 60

#color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRASS_GREEN = (34, 139, 34)
SAND_YELLOW = (240, 230, 140)
WATER_BLUE = (30, 144, 255)
RED = (200, 0, 0)
GREY = (100, 100, 100)
UI_BACKGROUND = (20, 20, 20, 180)

#font constants
FONT_TITLE = pygame.font.Font(None, 100)
FONT_MAIN = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 28)

#game levels
# A list of dictionaries, where each dictionary defines a level's layout.
# 'ball_start': Starting position of the ball.
# 'hole_pos': Position of the hole.
# 'obstacles': A list of all obstacles for the level.
# Each obstacle is a dictionary with 'type' and 'rect' (for walls, sand traps, water hazards).
# Types can be "wall", "sand", or "water". Rectangles are defined using pygame.Rect.
LEVELS = [
    #level 1
    {
        "ball_start": (200, SCREEN_HEIGHT // 2),
        "hole_pos": (1000, SCREEN_HEIGHT // 2),
        "obstacles": [
            # Simple straight shot to introduce the mechanics
        ]
    },
    {
        #level 2
        "ball_start": (200, 200),
        "hole_pos": (1000, 600),
        "obstacles": [
            # A large sand trap in the middle
            {"type": "sand", "rect": pygame.Rect(450, 250, 300, 300)},
        ]
    },
    {
        #level 3
        "ball_start": (200, SCREEN_HEIGHT // 2),
        "hole_pos": (1000, SCREEN_HEIGHT // 2),
        "obstacles": [
            # A water hazard to cross
            {"type": "water", "rect": pygame.Rect(575, 100, 70, 600)},
        ]
    },
    {
        #level 4
        "ball_start": (200, 150),
        "hole_pos": (1000, 150),
        "obstacles": [
            # A walled corridor
            {"type": "wall", "rect": pygame.Rect(350, 200, 500, 20)},
            {"type": "wall", "rect": pygame.Rect(350, 100, 500, 20)},
        ]
    },
    {
        #level 5
        "ball_start": (200, 600),
        "hole_pos": (1000, 200),
        "obstacles": [
           
            {"type": "wall", "rect": pygame.Rect(400, 400, 20, 300)},
            {"type": "sand", "rect": pygame.Rect(600, 100, 200, 200)},
            {"type": "water", "rect": pygame.Rect(850, 300, 200, 150)},
        ]
    },
]

#class for a main screen before starting the game

# Represents the golf ball
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.radius = 10
        self.vx = 0
        self.vy = 0
        self.is_moving = False
        #friction for grass
        self.friction = 0.985 

    def update(self):
        #updates the ball's position and handles friction
        if self.is_moving:
            self.x += self.vx
            self.y += self.vy
            self.vx *= self.friction
            self.vy *= self.friction

            # Stop the ball if its speed is very low
            if math.sqrt(self.vx**2 + self.vy**2) < 0.1:
                self.vx = 0
                self.vy = 0
                self.is_moving = False

    def draw(self, screen):
        # Draws the ball on the screen.
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

    def hit(self, power, angle):
        # Convert power and angle to velocity components
        self.vx = power * math.cos(angle)
        self.vy = power * math.sin(angle)
        self.is_moving = True
        
    def reset_to_last_pos(self):
        # Resets the ball to its position before the last hit.
        self.x = self.start_x
        self.y = self.start_y
        self.vx = 0
        self.vy = 0
        self.is_moving = False

#class for a main screen before starting the game
class MainMenu:
    #represents the main menu screen before starting the game
    def __init__(self):
        self.title = "PyGolf"
        self.subtitle = "Created after watching Happy Gilmore. \n Press SPACE to Start" \
                       "\n Use the mouse to aim and click to hit the ball."

    def draw(self, screen):
        title_surf = FONT_TITLE.render(self.title, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title_surf, title_rect)

        subtitle_surf = FONT_MAIN.render(self.subtitle, True, WHITE)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(subtitle_surf, subtitle_rect)

class Hole:
    # Represents the golf hole.
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15

    def draw(self, screen):
        # Draws the hole on the screen.
        pygame.draw.circle(screen, BLACK, (self.x, self.y), self.radius)

    def check_collision(self, ball):
        # Checks if the ball has entered the hole.
        dist = math.sqrt((self.x - ball.x)**2 + (self.y - ball.y)**2)
        # The ball must be close to the center and moving slowly to fall in
        return dist < self.radius and not ball.is_moving

#classes for obstacles

class Wall:
    # Represents a solid wall obstacle.
    def __init__(self, rect):
        self.rect = rect

    def draw(self, screen):
        # Draws the wall.
        pygame.draw.rect(screen, GREY, self.rect)

    def check_collision(self, ball):
        # Checks for and resolves collision with the ball.
        # Check for collision from each side to determine bounce direction
        if self.rect.colliderect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2):
            # Check horizontal collision
            # Check if the ball is colliding with the wall horizontally
            if ball.x + ball.radius > self.rect.left and ball.x - ball.radius < self.rect.right:
                if ball.vy > 0 and ball.y < self.rect.top:
                     
                     ball.y = self.rect.top - ball.radius
                     ball.vy *= -0.8 # Bounce with some energy loss
                elif ball.vy < 0 and ball.y > self.rect.bottom:
                     ball.y = self.rect.bottom + ball.radius
                     ball.vy *= -0.8
            
            # Check vertical collision
            if ball.y + ball.radius > self.rect.top and ball.y - ball.radius < self.rect.bottom:
                if ball.vx > 0 and ball.x < self.rect.left:
                    ball.x = self.rect.left - ball.radius
                    ball.vx *= -0.8
                elif ball.vx < 0 and ball.x > self.rect.right:
                    ball.x = self.rect.right + ball.radius
                    ball.vx *= -0.8


class SandTrap:
    # Represents a sand trap that slows the ball down.
    def __init__(self, rect):
        self.rect = rect

    def draw(self, screen):
        # Draws the sand trap.
        pygame.draw.rect(screen, SAND_YELLOW, self.rect, border_radius=15)

    def check_collision(self, ball):
        # Checks if the ball is in the sand and applies high friction.
        if self.rect.collidepoint(ball.x, ball.y):
            ball.friction = 0.92 # Much higher friction in sand
        # Note: We reset friction in the main game loop

class WaterHazard:
    # Represents a water hazard that resets the ball.
    def __init__(self, rect):
        self.rect = rect

    def draw(self, screen):
        # Draws the water hazard.
        pygame.draw.rect(screen, WATER_BLUE, self.rect, border_radius=10)

    def check_collision(self, ball):
        # Checks if the ball is in the water.
        if self.rect.collidepoint(ball.x, ball.y):
            return True
        return False

#main game class

class Game:
    # Manages the overall game state, levels, and UI.
    def __init__(self):
        self.current_level_index = 0
        self.strokes = 0
        self.game_state = "MENU" # Can be MENU, PLAYING, LEVEL_COMPLETE, GAME_COMPLETE
        
        self.ball = None
        self.hole = None
        self.obstacles = []

        # Swing mechanics variables
        self.is_aiming = False
        self.aim_start_pos = None
        self.max_power = 15

    def load_level(self, level_index):
        # Loads a specific level from the LEVELS constant.
        if level_index >= len(LEVELS):
            self.game_state = "GAME_COMPLETE"
            return
            
        level_data = LEVELS[level_index]
        self.current_level_index = level_index
        self.strokes = 0
        
        # Create ball and hole
        self.ball = Ball(*level_data["ball_start"])
        self.hole = Hole(*level_data["hole_pos"])

        # Create obstacles
        self.obstacles = []
        for obs_data in level_data["obstacles"]:
            if obs_data["type"] == "wall":
                self.obstacles.append(Wall(obs_data["rect"]))
            elif obs_data["type"] == "sand":
                self.obstacles.append(SandTrap(obs_data["rect"]))
            elif obs_data["type"] == "water":
                self.obstacles.append(WaterHazard(obs_data["rect"]))
        
        self.game_state = "PLAYING"

    def handle_input(self):
        # Handles all user input.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.game_state == "PLAYING":
                # Handle aiming and hitting the ball
                if not self.ball.is_moving:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Start aiming if the click is near the ball
                        mouse_pos = pygame.mouse.get_pos()
                        dist_to_ball = math.sqrt((mouse_pos[0] - self.ball.x)**2 + (mouse_pos[1] - self.ball.y)**2)
                        if dist_to_ball < 30: # Allow to right click near the ball
                            self.is_aiming = True
                            self.aim_start_pos = mouse_pos
                    # Handle aiming
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.is_aiming:
                        self.is_aiming = False
                        mouse_end_pos = pygame.mouse.get_pos()
                        
                        # Calculate power and angle
                        dx = self.ball.x - mouse_end_pos[0]
                        dy = self.ball.y - mouse_end_pos[1]
                        # Calculate distance and clamp power
                        dist = math.sqrt(dx**2 + dy**2)
                        power = min(dist / 20, self.max_power) # Clamp power
                        angle = math.atan2(dy, dx)
                        
                        # Hit the ball and update game state
                        self.ball.start_x, self.ball.start_y = self.ball.x, self.ball.y
                        self.ball.hit(power, angle)
                        self.strokes += 1
            
            # Handle menu and screen transitions
            elif self.game_state in ["MENU", "LEVEL_COMPLETE", "GAME_COMPLETE"]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.game_state == "LEVEL_COMPLETE":
                        self.load_level(self.current_level_index + 1)
                    else: # MENU or GAME_COMPLETE
                        self.load_level(0)

    def update(self):
        # Updates the game state and handles collisions.
        if self.game_state != "PLAYING":
            return

        self.ball.update()
        
        # Reset ball friction before checking obstacles
        self.ball.friction = 0.985 

        #Screen Border Collision
        if self.ball.x - self.ball.radius <= 0 or self.ball.x + self.ball.radius >= SCREEN_WIDTH:
            self.ball.vx *= -0.8
            self.ball.x = max(self.ball.radius, min(self.ball.x, SCREEN_WIDTH - self.ball.radius))
        if self.ball.y - self.ball.radius <= 0 or self.ball.y + self.ball.radius >= SCREEN_HEIGHT:
            self.ball.vy *= -0.8
            self.ball.y = max(self.ball.radius, min(self.ball.y, SCREEN_HEIGHT - self.ball.radius))

        # Obstacle Collisions
        for obs in self.obstacles:
            if isinstance(obs, WaterHazard):
                if obs.check_collision(self.ball):
                    self.ball.reset_to_last_pos()
                    self.strokes += 1 # Penalty stroke
                    break # Stop checking other collisions for this frame
            else:
                obs.check_collision(self.ball)

        #Hole Collision
        if self.hole.check_collision(self.ball):
            self.game_state = "LEVEL_COMPLETE"

    def draw(self):
        # Draws everything to the screen.
        # Fill background with grass color
        screen.fill(GRASS_GREEN)

        if self.game_state == "MENU":
            self.draw_menu_screen("PyGolf", "Created after watching Happy Gilmore.\nPress SPACE to Start")
        elif self.game_state == "LEVEL_COMPLETE":
            self.draw_menu_screen(f"Level {self.current_level_index + 1} Completed!", f"Strokes: {self.strokes}. Press SPACE for Next Level.")
        elif self.game_state == "GAME_COMPLETE":
            self.draw_menu_screen("You've completed the game! Press SPACE to play again.")
        elif self.game_state == "PLAYING":
            # Draw all game elements
            for obs in self.obstacles:
                obs.draw(screen)
            
            self.hole.draw(screen)
            self.ball.draw(screen)
            
            # Draw aiming indicator if aiming
            if self.is_aiming and not self.ball.is_moving:
                self.draw_aiming_line()

            self.draw_ui()
        
        pygame.display.flip()

    def draw_ui(self):
        # Draw the Heads-Up Display (Level, Strokes, Power)
        # Create a semi-transparent background for the UI
        ui_panel = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        ui_panel.fill(UI_BACKGROUND)
        screen.blit(ui_panel, (0, 0))

        # Level Text
        level_text = FONT_MAIN.render(f"Level: {self.current_level_index + 1}", True, WHITE)
        screen.blit(level_text, (20, 10))

        # Strokes Text
        strokes_text = FONT_MAIN.render(f"Strokes: {self.strokes}", True, WHITE)
        screen.blit(strokes_text, (200, 10))
        
        # Power Bar
        if self.is_aiming:
            mouse_pos = pygame.mouse.get_pos()
            dx = self.ball.x - mouse_pos[0]
            dy = self.ball.y - mouse_pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            power_ratio = min(dist / 20 / self.max_power, 1.0)

            power_bar_width = 200
            power_bar_height = 20
            
            # Draw power bar background
            pygame.draw.rect(screen, GREY, (SCREEN_WIDTH - power_bar_width - 20, 15, power_bar_width, power_bar_height))
            # Draw current power
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH - power_bar_width - 20, 15, power_bar_width * power_ratio, power_bar_height))


    def draw_aiming_line(self):
        # Draw the line indicating shot direction and power.
        mouse_pos = pygame.mouse.get_pos()
        dx = self.ball.x - mouse_pos[0]
        dy = self.ball.y - mouse_pos[1]
        
        # The line starts at the ball and goes in the direction of the shot
        line_end_x = self.ball.x + dx
        line_end_y = self.ball.y + dy
        
        pygame.draw.line(screen, WHITE, (self.ball.x, self.ball.y), (line_end_x, line_end_y), 2)
        pygame.draw.line(screen, BLACK, (self.ball.x, self.ball.y), (line_end_x, line_end_y), 1)

    def draw_menu_screen(self, title, subtitle):
        # Helper function to draw centered text screens.
        title_surf = FONT_TITLE.render(title, True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        
        subtitle_surf = FONT_MAIN.render(subtitle, True, WHITE)
        subtitle_rect = subtitle_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        screen.blit(title_surf, title_rect)
        screen.blit(subtitle_surf, subtitle_rect)

    def run(self):
        # The main game loop.
        #start with the game menu
        MainMenu().draw(screen)
        self.load_level(0) 
        self.game_state = "MENU"

        while True:
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)

# Main entry point to run the game
if __name__ == "__main__":
    game = Game()
    game.run()