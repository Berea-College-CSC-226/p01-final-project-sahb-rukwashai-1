"""
GameObject base class for all objects on the game map.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import math
import pygame


class GameObject:
    """Base class for every object that lives on the game map."""

    def __init__(self, x, y, size=20):
        """
        Initialize a game object with position and size.

        :param x: x-coordinate on screen
        :param y: y-coordinate on screen
        :param size: radius used for collision detection
        """
        self.x = x
        self.y = y
        self.size = size

    def distance_to(self, other):
        """
        Calculate Euclidean distance to another GameObject.

        :param other: another GameObject
        :return: float distance
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def collides_with(self, other):
        """
        Check if this object overlaps with another (circle collision).

        :param other: another GameObject
        :return: True if objects overlap
        """
        return self.distance_to(other) < (self.size + other.size)

    def render(self, screen):
        """
        Draw the object on screen. Subclasses override this.

        :param screen: Pygame surface to draw on
        """
        raise NotImplementedError