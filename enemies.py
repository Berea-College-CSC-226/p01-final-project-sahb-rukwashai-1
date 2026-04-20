"""
Enemy classes for the tower defense game.
Includes base Enemy and subclasses: FastEnemy, TankEnemy.
Enemies move along waypoints from spawn to exit.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import math
import pygame
from game_object import GameObject


class Enemy(GameObject):
    """
    Base enemy class. Moves along the path from waypoint to waypoint.
    Subclasses set their own health, speed, and reward.
    """

    enemy_name = "Enemy"
    max_health = 100
    speed = 2.0
    reward = 10
    color = (200, 50, 50)

    def __init__(self, waypoints):
        """
        Initialize an enemy at the first waypoint.

        :param waypoints: list of (x, y) tuples defining the path
        """
        start_x, start_y = waypoints[0]
        super().__init__(start_x, start_y, size=12)

        self.waypoints = waypoints
        self.current_waypoint_index = 1     # heading toward the second waypoint
        self.health = self.max_health
        self.alive = True
        self.reached_end = False
        self.original_speed = self.speed    # stored so freeze towers can restore it

    def move(self):
        """
        Move the enemy toward its current target waypoint.
        When it reaches one, advance to the next.
        If no waypoints remain, the enemy has reached the exit.
        """
        if not self.alive or self.reached_end:
            return

        # Get the target waypoint
        target_x, target_y = self.waypoints[self.current_waypoint_index]

        # Calculate direction toward the target
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # If close enough to the waypoint, snap to it and move to the next one
        if dist <= self.speed:
            self.x = target_x
            self.y = target_y
            self.current_waypoint_index += 1

            # Check if the enemy has passed the last waypoint
            if self.current_waypoint_index >= len(self.waypoints):
                self.reached_end = True
                return
        else:
            # Normalize direction and move by speed
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

    def render(self, screen):
        """
        Draw the enemy as a colored circle with a health bar above it.

        :param screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        # Enemy body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), self.size, 2)

        # Health bar background (red)
        bar_width = self.size * 2
        bar_height = 4
        bar_x = int(self.x - bar_width / 2)
        bar_y = int(self.y - self.size - 8)
        pygame.draw.rect(screen, (100, 0, 0),
                         (bar_x, bar_y, bar_width, bar_height))

        # Health bar fill (green)
        health_ratio = self.health / self.max_health
        fill_width = int(bar_width * health_ratio)
        bar_color = (0, 200, 0) if health_ratio > 0.5 else (255, 165, 0) if health_ratio > 0.25 else (200, 0, 0)
        pygame.draw.rect(screen, bar_color,
                         (bar_x, bar_y, fill_width, bar_height))

    def __repr__(self):
        return f"{self.enemy_name}(hp={self.health}, pos=({self.x:.0f},{self.y:.0f}))"


class FastEnemy(Enemy):
    """Fast but fragile enemy. Moves quickly but dies easily."""

    enemy_name = "Fast"
    max_health = 50
    speed = 4.0
    reward = 10
    color = (255, 165, 0)       # orange


class TankEnemy(Enemy):
    """Slow but tanky enemy. Hard to kill but moves slowly."""

    enemy_name = "Tank"
    max_health = 200
    speed = 1.0
    reward = 30
    color = (100, 50, 150)      # purple