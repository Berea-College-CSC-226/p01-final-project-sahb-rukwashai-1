"""
Path data for the tower defense game.
Defines waypoints that enemies follow from spawn to exit.

Authors: Bhushan Sah, Daniel Rukwasha
"""

# Path visual settings
PATH_WIDTH = 40

# Game area takes most of the screen, side panel gets the rest
GAME_AREA_WIDTH = 1000

# Waypoints in Pygame coordinates (top-left is 0,0).
# First waypoint is the spawn point (off-screen left).
# Last waypoint is the exit point (off-screen right).
WAYPOINTS = [
    (-20, 150),
    (100, 150),
    (100, 400),
    (350, 400),
    (350, 200),
    (600, 200),
    (600, 500),
    (850, 500),
    (850, 100),
    (GAME_AREA_WIDTH + 20, 100),
]

SPAWN_POINT = WAYPOINTS[0]
EXIT_POINT = WAYPOINTS[-1]