import pygame
import sys
import math
import random

pygame.init()

#----------SCREEN STUFF----------
SCREEN_WIDTH, SCREEN_HEIGHT = 800,600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ball collision")

#---------COLOR STUFF-----------
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)

clock = pygame.time.Clock()

#----------BALL DATA----------
class Ball:
    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.radius = 20
        self.color = WHITE

#--------RUNTIME STATE OF BALLS-----------               
balls = []
#-------SLINGSHOT STATE-------
dragging = False
drag_start = (0,0)
drag_current= (0,0)

MAX_SPEED = 15
SPEED_SCALE = 10

#----------RENDERING ARROW-----------
def draw_arrow(surface, start, end, color, width=3, head_length=15, head_angle=30):
    pygame.draw.line(surface, color, start, end, width)

    dx = start[0] - end[0]
    dy = start[1] - end[1]
    angle = math.atan2(dy, dx)

    left = (
        end[0] + head_length * math.cos(angle + math.radians(head_angle)),
        end[1] + head_length * math.sin(angle + math.radians(head_angle))
    )
    right = (
        end[0] + head_length * math.cos(angle - math.radians(head_angle)),
        end[1] + head_length * math.sin(angle - math.radians(head_angle))
    )

    pygame.draw.line(surface, color, end, left, width)
    pygame.draw.line(surface, color, end, right, width)

#------------RENDERING DASHED LINE---------
def draw_dashed_line(surface, color, start, end, dash_length=10, gap_length=6, width=2):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = math.sqrt(dx*dx + dy*dy)

    if distance == 0:
        return
    
    nx = dx / distance
    ny = dy / distance

    draw = 0
    while draw < distance: 
        seg_start = (
            start[0] + nx * draw,
            start[1] + ny * draw
        )
        seg_end = (
            start[0] + nx * min(draw + dash_length, distance),
            start[1] + ny * min(draw + dash_length, distance)
        )

        pygame.draw.line(surface, color, seg_start, seg_end, width)
        draw += dash_length + gap_length

#---------MAIN LOOP--------
while True:
    #INPUT HANDLING
    for event in pygame.event.get():
        #QUIT
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        #AIMING STUFF
        if event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
            drag_start = event.pos
            drag_current = event.pos
        
        if event.type == pygame.MOUSEMOTION and dragging:
            drag_current = event.pos
        
        if event.type == pygame.MOUSEBUTTONUP and dragging:
            dragging = False
            sx, sy = drag_start
            ex, ey = event.pos

            dx = sx - ex
            dy = sy - ey
            distance = math.sqrt(dx*dx + dy*dy)

            if distance != 0:
                speed = min(distance / SPEED_SCALE, MAX_SPEED)
                vx = (dx / distance) * speed
                vy = (dy / distance) * speed

                balls.append(Ball(sx, sy, vx, vy))

    screen.fill(BLACK)

    #------BALL TO WALL COLLISION---------
    for ball in balls:
        ball.x += ball.vx
        ball.y += ball.vy

        #LEFT WALL
        if ball.x - ball.radius <= 0:
            ball.x = ball.radius
            ball.vx *= -1

        #RIGHT WALL
        if ball.x + ball.radius >= SCREEN_WIDTH:
            ball.x = SCREEN_WIDTH - ball.radius
            ball.vx *= -1

        #TOP WALL
        if ball.y - ball.radius <= 0:
            ball.y = ball.radius
            ball.vy *= -1
        
        #BOTTOM WALL
        if ball.y + ball.radius >= SCREEN_HEIGHT:
            ball.y = SCREEN_HEIGHT - ball.radius
            ball.vy *= -1
        
    #----------BALL TO BALL COLLISION---------
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            b1 = balls[i]
            b2 = balls[j]

            dx = b1.x - b2.x
            dy = b1.y - b2.y
            distance = math.sqrt(dx*dx + dy*dy)
            min_dist = b1.radius + b2.radius

            if distance < min_dist and distance != 0:
                b1.vx, b2.vx = b2.vx, b1.vx
                b1.vy, b2.vy = b2.vy, b1.vy

                overlap = min_dist -distance
                nx = dx / distance
                ny = dy / distance

                b1.x += nx * overlap / 2
                b1.y += ny * overlap / 2
                b2.x -= nx * overlap / 2
                b2.y -= ny * overlap / 2
    
    #--------RENDERING----------
    for ball in balls: 
        pygame.draw.circle(
            screen,
            ball.color,
            (int(ball.x), int(ball.y)),
            ball.radius
        )
    #-------SLINGSHOT AIMING--------
    if dragging: 
        draw_dashed_line(screen, RED, drag_current,
         drag_start)
        draw_arrow(screen, drag_current, drag_start, RED)
        pygame.draw.circle(screen, RED, drag_start, 6)
        
    pygame.display.flip()
    clock.tick(60)
