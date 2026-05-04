"""
Enemy classes for the tower defense game.
Includes base Enemy and subclasses: FastEnemy, TankEnemy.
Each enemy type has a unique visual design.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import math
import pygame
from game_object import GameObject


class Enemy(GameObject):
    """
    Base enemy class. Moves along the path from waypoint to waypoint.
    Subclasses set their own health, speed, reward, and visual style.
    """

    enemy_name = "Enemy"
    max_health = 100
    speed = 2.0
    reward = 10
    color = (200, 50, 50)
    outline_color = (140, 30, 30)
    eye_color = (255, 255, 255)

    def __init__(self, waypoints):
        """
        Initialize an enemy at the first waypoint.

        :param waypoints: list of (x, y) tuples defining the path
        """
        start_x, start_y = waypoints[0]
        super().__init__(start_x, start_y, size=12)

        self.waypoints = waypoints
        self.current_waypoint_index = 1
        self.health = self.max_health
        self.alive = True
        self.reached_end = False
        self.original_speed = self.speed
        self.angle = 0  # direction the enemy is facing

    def move(self):
        """
        Move the enemy toward its current target waypoint.
        When it reaches one, advance to the next.
        If no waypoints remain, the enemy has reached the exit.
        """
        if not self.alive or self.reached_end:
            return

        target_x, target_y = self.waypoints[self.current_waypoint_index]

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # Track which direction enemy is facing
        if dist > 0:
            self.angle = math.atan2(dy, dx)

        if dist <= self.speed:
            self.x = target_x
            self.y = target_y
            self.current_waypoint_index += 1

            if self.current_waypoint_index >= len(self.waypoints):
                self.reached_end = True
                return
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def take_damage(self, amount):
        """
        Reduce health by the given amount. Mark as dead if health hits zero.

        :param amount: damage to deal
        """
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def is_dead(self):
        """
        Check if the enemy has been killed.

        :return: True if health is zero or below
        """
        return not self.alive

    def _draw_shadow(self, screen):
        """
        Draw a shadow underneath the enemy.

        :param screen: Pygame surface to draw on
        """
        shadow = pygame.Surface((self.size * 2 + 4, self.size + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50),
                            (0, 0, self.size * 2 + 4, self.size + 2))
        screen.blit(shadow, (int(self.x - self.size - 2), int(self.y + self.size - 2)))

    def _draw_health_bar(self, screen):
        """
        Draw a health bar above the enemy with a background, fill, and border.

        :param screen: Pygame surface to draw on
        """
        bar_width = self.size * 2 + 4
        bar_height = 5
        bar_x = int(self.x - bar_width / 2)
        bar_y = int(self.y - self.size - 10)

        # Background
        pygame.draw.rect(screen, (40, 40, 40),
                         (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2),
                         border_radius=2)
        pygame.draw.rect(screen, (80, 0, 0),
                         (bar_x, bar_y, bar_width, bar_height), border_radius=1)

        # Fill
        health_ratio = self.health / self.max_health
        fill_width = int(bar_width * health_ratio)
        if health_ratio > 0.5:
            bar_color = (50, 200, 50)
        elif health_ratio > 0.25:
            bar_color = (255, 180, 30)
        else:
            bar_color = (220, 40, 40)

        if fill_width > 0:
            pygame.draw.rect(screen, bar_color,
                             (bar_x, bar_y, fill_width, bar_height), border_radius=1)

            # Shiny highlight on top half of fill
            highlight = pygame.Surface((fill_width, bar_height // 2), pygame.SRCALPHA)
            highlight.fill((255, 255, 255, 40))
            screen.blit(highlight, (bar_x, bar_y))

    def render(self, screen):
        """
        Draw the normal enemy as a red circle with eyes facing movement direction.

        :param screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        cx, cy = int(self.x), int(self.y)
        s = self.size

        # Shadow
        self._draw_shadow(screen)

        # Body (layered circles for depth)
        pygame.draw.circle(screen, self.outline_color, (cx, cy), s + 1)
        pygame.draw.circle(screen, self.color, (cx, cy), s)

        # Inner body highlight
        highlight_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, highlight_color, (cx - 2, cy - 2), s - 4)

        # Eyes facing movement direction
        eye_offset = s // 2
        eye_x = cx + int(math.cos(self.angle) * eye_offset)
        eye_y = cy + int(math.sin(self.angle) * eye_offset)

        # Two eyes spread perpendicular to movement direction
        perp_angle = self.angle + math.pi / 2
        eye_spread = 4
        for side in [-1, 1]:
            ex = eye_x + int(math.cos(perp_angle) * eye_spread * side)
            ey = eye_y + int(math.sin(perp_angle) * eye_spread * side)
            # White of eye
            pygame.draw.circle(screen, self.eye_color, (ex, ey), 3)
            # Pupil (looking in movement direction)
            px = ex + int(math.cos(self.angle) * 1)
            py = ey + int(math.sin(self.angle) * 1)
            pygame.draw.circle(screen, (0, 0, 0), (px, py), 2)

        # Health bar
        self._draw_health_bar(screen)

    def __repr__(self):
        return f"{self.enemy_name}(hp={self.health}, pos=({self.x:.0f},{self.y:.0f}))"


class FastEnemy(Enemy):
    """Fast but fragile enemy. Drawn as a sleek orange diamond shape."""

    enemy_name = "Fast"
    max_health = 50
    speed = 4.0
    reward = 10
    color = (255, 165, 0)
    outline_color = (180, 110, 0)
    eye_color = (255, 255, 200)

    def render(self, screen):
        """
        Draw the FastEnemy as an orange diamond with a speed trail.

        :param screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        cx, cy = int(self.x), int(self.y)
        s = self.size

        # Shadow
        self._draw_shadow(screen)

        # Speed trail (fading circles behind the enemy)
        trail_dx = -math.cos(self.angle)
        trail_dy = -math.sin(self.angle)
        for i in range(3):
            trail_alpha = 80 - i * 25
            trail_x = int(cx + trail_dx * (i + 1) * 6)
            trail_y = int(cy + trail_dy * (i + 1) * 6)
            trail_surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
            trail_size = max(2, s - i * 3)
            pygame.draw.circle(trail_surf, (*self.color, trail_alpha),
                               (s, s), trail_size)
            screen.blit(trail_surf, (trail_x - s, trail_y - s))

        # Diamond body rotated to face movement direction
        front_x = cx + int(math.cos(self.angle) * (s + 2))
        front_y = cy + int(math.sin(self.angle) * (s + 2))
        back_x = cx + int(math.cos(self.angle + math.pi) * s)
        back_y = cy + int(math.sin(self.angle + math.pi) * s)
        left_x = cx + int(math.cos(self.angle + math.pi / 2) * (s - 3))
        left_y = cy + int(math.sin(self.angle + math.pi / 2) * (s - 3))
        right_x = cx + int(math.cos(self.angle - math.pi / 2) * (s - 3))
        right_y = cy + int(math.sin(self.angle - math.pi / 2) * (s - 3))

        points = [(front_x, front_y), (left_x, left_y),
                  (back_x, back_y), (right_x, right_y)]

        pygame.draw.polygon(screen, self.outline_color, points)
        # Inner lighter diamond
        inner_scale = 0.7
        inner_points = [
            (int(cx + (px - cx) * inner_scale), int(cy + (py - cy) * inner_scale))
            for px, py in points
        ]
        pygame.draw.polygon(screen, self.color, inner_points)

        # Highlight
        highlight_color = (255, 210, 100)
        tiny_points = [
            (int(cx + (px - cx) * 0.35), int(cy + (py - cy) * 0.35))
            for px, py in points
        ]
        pygame.draw.polygon(screen, highlight_color, tiny_points)

        # Small eye at front
        eye_x = cx + int(math.cos(self.angle) * (s // 2))
        eye_y = cy + int(math.sin(self.angle) * (s // 2))
        pygame.draw.circle(screen, (255, 255, 200), (eye_x, eye_y), 3)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), 2)

        # Health bar
        self._draw_health_bar(screen)


class TankEnemy(Enemy):
    """Slow but tanky enemy. Drawn as a large armored purple hexagon."""

    enemy_name = "Tank"
    max_health = 200
    speed = 1.0
    reward = 30
    color = (100, 50, 150)
    outline_color = (60, 30, 100)
    eye_color = (200, 180, 255)

    def __init__(self, waypoints):
        """
        Initialize tank enemy with larger size.

        :param waypoints: list of (x, y) tuples defining the path
        """
        super().__init__(waypoints)
        self.size = 16  # bigger than normal enemies

    def render(self, screen):
        """
        Draw the TankEnemy as a large armored hexagon with shield plates.

        :param screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        cx, cy = int(self.x), int(self.y)
        s = self.size

        # Shadow (bigger)
        shadow = pygame.Surface((s * 3, s + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, s * 3, s + 4))
        screen.blit(shadow, (cx - s * 3 // 2, cy + s - 2))

        # Hexagon body
        hex_points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            hx = cx + int(math.cos(angle) * (s + 1))
            hy = cy + int(math.sin(angle) * (s + 1))
            hex_points.append((hx, hy))

        # Outer armor
        pygame.draw.polygon(screen, self.outline_color, hex_points)

        # Inner hexagon
        inner_hex = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            hx = cx + int(math.cos(angle) * (s - 3))
            hy = cy + int(math.sin(angle) * (s - 3))
            inner_hex.append((hx, hy))
        pygame.draw.polygon(screen, self.color, inner_hex)

        # Armor plate lines
        for i in range(6):
            pygame.draw.line(screen, (80, 40, 120),
                             hex_points[i], (cx, cy), 1)

        # Center highlight
        highlight_hex = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            hx = cx + int(math.cos(angle) * (s // 3))
            hy = cy + int(math.sin(angle) * (s // 3))
            highlight_hex.append((hx, hy))
        highlight_color = (140, 90, 200)
        pygame.draw.polygon(screen, highlight_color, highlight_hex)

        # Shield glow effect
        glow_surf = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (150, 100, 255, 25), (s * 2, s * 2), s + 4)
        screen.blit(glow_surf, (cx - s * 2, cy - s * 2))

        # Eyes
        eye_offset = s // 3
        eye_x = cx + int(math.cos(self.angle) * eye_offset)
        eye_y = cy + int(math.sin(self.angle) * eye_offset)
        perp = self.angle + math.pi / 2
        for side in [-1, 1]:
            ex = eye_x + int(math.cos(perp) * 5 * side)
            ey = eye_y + int(math.sin(perp) * 5 * side)
            pygame.draw.circle(screen, self.eye_color, (ex, ey), 3)
            px = ex + int(math.cos(self.angle) * 1)
            py = ey + int(math.sin(self.angle) * 1)
            pygame.draw.circle(screen, (30, 0, 50), (px, py), 2)

        # Health bar
        self._draw_health_bar(screen)