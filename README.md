# CSC226 Final Project

## Instructions

❗️Exclamation Marks ❗️indicate action items; you should remove these emoji as you complete/update the items which 
  they accompany. (This means that your final README should have no ❗️in it!)

**Author(s)**: Bhushan Sah 
**Author(s)**: Daniel Rukwasha

**Google Doc Link**: https://docs.google.com/document/d/1lKuOB9pPnH6yuEsixRnpE7bPGq9S8JdDnZPzu4O5a8s/edit?usp=sharing
**GitHub Link**: https://github.com/Berea-College-CSC-226/p01-final-project-sahb-rukwashai-1

---

## Milestone 1: Setup, Planning, Design

**Title**: `Path of No Return: A Tower Defense Game`

**Purpose**: `A tower defense game where the player places different types of towers along a winding path to stop waves
 of enemies from reaching the exit, built with Turtle graphics and a Tkinter control panel.`

**Source Assignment(s)**: `T02 (Exploring Turtles), HW02 (Loopy Turtles), HW09 (UPC Barcodes), HW10 (Caesar Cipher), T10 (Pet Adoption Center),
   T11 (The Legend of Tuna)`

**CRC Card(s)**:
    # CRC Cards

---

  ## Class name: GameObject
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | x, y (position coordinates) | |
  | size (for collision detection) | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | render(): draw itself on screen | Turtle |
  | distance_to(other): calculate distance to another object | GameObject |
  | collides_with(other): check collision with another object | GameObject |
  
  ---
  
  ## Class name: Tower (inherits GameObject)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | range (how far it can shoot) | |
  | damage (how much damage per shot) | |
  | fire_rate (time between shots) | |
  | cost (price to place the tower) | |
  | target (the enemy currently aimed at) | Enemy |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | find_target(enemies): find nearest enemy in range | Enemy |
  | fire(): create a projectile aimed at target | Projectile |
  | can_fire(): check if enough time has passed to shoot again | |
  | render(): draw the tower on the map | Turtle |
  
  ---
  
  ## Class name: ArrowTower (inherits Tower)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | damage = 25 | |
  | range = 150 | |
  | fire_rate = 1.0 | |
  | cost = 50 | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | fire(): deal single-target damage via projectile | Projectile, Enemy |
  
  ---
  
  ## Class name: BombTower (inherits Tower)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | damage = 40 | |
  | range = 100 | |
  | fire_rate = 2.0 | |
  | cost = 100 | |
  | blast_radius (area of explosion) | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | fire(): deal area damage to enemies near impact | Projectile, Enemy |
  
  ---
  
  ## Class name: FreezeTower (inherits Tower)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | range = 120 | |
  | slow_amount (how much to reduce enemy speed) | |
  | cost = 75 | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | apply_slow(enemies): slow all enemies within range | Enemy |
  
  ---
  
  ## Class name: Enemy (inherits GameObject)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | health (current hit points) | |
  | speed (how fast it moves per frame) | |
  | reward (money given when destroyed) | |
  | current_waypoint (index of next waypoint to reach) | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | move(): step toward the next waypoint | |
  | take_damage(amount): reduce health by amount | |
  | is_dead(): check if health is zero or below | |
  | reached_end(): check if past the last waypoint | |
  | render(): draw itself and its health bar | Turtle |
  
  ---
  
  ## Class name: FastEnemy (inherits Enemy)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | health = 50 (low) | |
  | speed = 4 (high) | |
  | reward = 10 | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | inherits all methods from Enemy | |
  
  ---
  
  ## Class name: TankEnemy (inherits Enemy)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | health = 200 (high) | |
  | speed = 1 (low) | |
  | reward = 30 | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | inherits all methods from Enemy | |
  
  ---
  
  ## Class name: Projectile (inherits GameObject)
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | damage (how much damage on hit) | |
  | speed (how fast it travels) | |
  | target (reference to the enemy it tracks) | Enemy |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | move(): step toward the target's current position | Enemy |
  | has_hit(): check if close enough to count as a hit | Enemy |
  | apply_damage(): deal damage to the target on hit | Enemy |
  | render(): draw itself on screen | Turtle |
  
  ---
  
  ## Class name: Wave
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | enemy_list (sequence of enemy types and spawn delays) | |
  | wave_number (which wave this is) | |
  | spawn_index (tracks which enemy to spawn next) | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | spawn_next(): create the next enemy in the sequence | Enemy, FastEnemy, TankEnemy |
  | is_complete(): check if all enemies have been spawned | |
  | reset(): reset the wave for replay | |
  
  ---
  
  ## Class name: Game
  
  | Class Attributes: | Class Collaborations (other classes): |
  |---|---|
  | towers (list of all placed towers) | Tower |
  | enemies (list of all active enemies) | Enemy |
  | projectiles (list of all active projectiles) | Projectile |
  | waves (list of all waves) | Wave |
  | money (player's current money) | |
  | lives (player's remaining lives) | |
  | score (player's current score) | |
  
  | Class Methods: | Class Collaborations (other classes): |
  |---|---|
  | setup(): initialize window, draw map, define path | Turtle, Tkinter |
  | handle_click(x, y): place a tower where the player clicks | Tower |
  | game_loop(): run one frame of the game | Tower, Enemy, Projectile |
  | start_wave(): begin spawning the next wave | Wave |
  | check_game_over(): check win or lose conditions | |
  | update_display(): refresh the side panel stats | Tkinter |

  
  - **Branches**: This project will **require** effective use of git. 

 Each partner should create a branch at the beginning of the project, and stay on this branch (or branches of their 
branch) as they work. When you need to bring each others branches together, do so by merging each other's branches 
into your own, following the process we've discussed in previous assignments, then re-branching out from the merged code.  

```
    Branch 1 starting name: sahb
    Branch 2 starting name: Rukwashai
    
    ### Task Delegation
  - Sahb: Game class, Tower classes (ArrowTower, BombTower, FreezeTower), tower placement logic, Tkinter side panel
  - Rukwashai: Enemy classes (FastEnemy, TankEnemy), Projectile class, Wave system, enemy pathfinding
  - Shared: GameObject base class, testing, README updates, bug fixes
```

### References 

Throughout this project, you will likely use outside resources. Reference all ideas which are not your own, 
and describe how you integrated the ideas or code into your program. This includes online sources, people who have 
helped you, AI tools you've used, and any other resources that are not solely your own contribution. Update this 
section as you go. DO NOT forget about it!
    

---

## Milestone 2: Code Setup and Issue Queue

Most importantly, keep your issue queue up to date, and focus on your code. 🙃

Reflect on what you’ve done so far. How’s it going? Are you feeling behind/ahead? What are you worried about? 
What has surprised you so far? Describe your general feelings. Be honest with yourself; this section is for you, not me.

```
    **Replace this text with your reflection
```

---

## Milestone 3: Virtual Check-In

❗Indicate what percentage of the project you have left to complete and how confident you feel. 

❗️**Completion Percentage**: `0 - 100%`

❗️**Confidence**: Describe how confident you feel about completing this project, and why. Then, describe some 
  strategies you can employ to increase the likelihood that you'll be successful in completing this project 
  before the deadline.

```
    **Replace this with your reflection
```

---

## Milestone 4: Final Code, Presentation, Demo

### ❗User Instructions

❗In a paragraph, explain how to use your program. Assume the user is starting just after they hit the "Run" button 
in PyCharm. 

### ❗Errors and Constraints

❗Every program has bugs or features that had to be scrapped for time. These bugs should be tracked in the issue queue. 
You should already have a few items in here from the prior weeks. Create a new issue for any undocumented errors and 
deficiencies that remain in your code. Bugs found that aren't acknowledged in the queue will be penalized.

### ❗Reflection

❗Each partner should write three to four well-written paragraphs address the following (at a minimum):
- Why did you select the project that you did?
- How closely did your final project reflect your initial design?
- What did you learn from this process?
- What was the hardest part of the final project?
- What would you do differently next time, knowing what you know now?
- How well did you work with your partner? What made it go well? What made it challenging?

```
    Partner 1: **Replace this with your reflection
```

```
    Partner 2: **Replace this with your reflection
```

---