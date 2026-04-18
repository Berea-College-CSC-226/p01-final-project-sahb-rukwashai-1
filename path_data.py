"""
Path data for the tower defense game.
Defines waypoints that enemies follow from spawn to exit.

Authors: Bhushan Sah, Daniel Rukwasha
"""

# Path width in pixels
PATH_WIDTH = 40

# Waypoints defining the enemy path.
# Enemies travel from waypoint to waypoint in order.
# First waypoint is the spawn point (off-screen left).
# Last waypoint is the exit point (off-screen right into panel).
GAME_AREA_WIDTH = 750

WAYPOINTS = [
    (-20, 150),  # Spawn (off-screen left)
    (100, 150),  # First visible turn
    (100, 400),  # Turn south
    (300, 400),  # Turn east
    (300, 200),  # Turn north
    (500, 200),  # Turn east
    (500, 500),  # Turn south
    (650, 500),  # Turn east
    (650, 100),  # Turn north
    (GAME_AREA_WIDTH + 20, 100)  # Exit (off-screen right)
]

SPAWN_POINT = WAYPOINTS[0]
EXIT_POINT = WAYPOINTS[-1]