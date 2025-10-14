# ------------------------------
# Electric Circuit Simulator (Mini-Game) - Beginner Version
# Using Pygame
# ------------------------------

# Import the pygame library
import pygame

# Import the sys library for system exit (optional but common)
import sys

# Initialize pygame so we can use its functions
pygame.init()

# ------------------------------
# BASIC WINDOW / CONSTANTS
# ------------------------------

# Set the window width in pixels
WIDTH = 900
# Set the window height in pixels
HEIGHT = 500
# Create the window (the game screen) with the width and height
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# Set the window title (caption) text
pygame.display.set_caption("Electric Circuit Simulator (Beginner)")

# Create a clock object to control the frame rate
clock = pygame.time.Clock()
# Set frames per second (how fast the game updates)
FPS = 60

# ------------------------------
# COLORS (R,G,B) tuples
# ------------------------------

# Define a black color
BLACK = (0, 0, 0)
# Define a white color
WHITE = (255, 255, 255)
# Define a gray color for panels and outlines
GRAY = (200, 200, 200)
# Define a darker gray
DARK_GRAY = (120, 120, 120)
# Define a green color for "ON" things
GREEN = (0, 200, 0)
# Define a red color for "OFF" or errors
RED = (220, 0, 0)
# Define a yellow color for bulb glow
YELLOW = (255, 230, 0)
# Define a blue color for wires
BLUE = (50, 120, 255)

# ------------------------------
# FONT SETTINGS
# ------------------------------

# Create a default font with size 20 (for labels)
font = pygame.font.SysFont(None, 20)
# Create a bigger font for titles
title_font = pygame.font.SysFont(None, 32)

# ------------------------------
# SIMPLE ELECTRIC MODEL
# ------------------------------

# Set a simple battery voltage in Volts (constant)
BATTERY_VOLTAGE = 9  # 9V battery (like a small battery)
# Set a simple resistance in Ohms for the bulb
BULB_RESISTANCE = 10  # 10 Ohms (simple number)
# Note: Current I = V / R (only when the switch is on and circuit closed)

# ------------------------------
# COMPONENT POSITIONS (just rectangles and points)
# ------------------------------

# Define rectangles for panels where components are drawn
battery_rect = pygame.Rect(60, 180, 120, 140)   # x, y, width, height for battery panel
bulb_rect    = pygame.Rect(300, 150, 120, 120)  # rectangle for bulb panel
switch_rect  = pygame.Rect(540, 160, 140, 100)  # rectangle for switch panel
return_rect  = pygame.Rect(760, 180, 100, 140)  # rectangle for "return to battery" panel

# Define fixed connection points (small circles) between components
# These are midpoints on the right/left edges of panels where wires attach
battery_to_bulb_p1 = (battery_rect.right, battery_rect.centery)  # right side of battery
battery_to_bulb_p2 = (bulb_rect.left, bulb_rect.centery)         # left side of bulb

bulb_to_switch_p1  = (bulb_rect.right, bulb_rect.centery)        # right side of bulb
bulb_to_switch_p2  = (switch_rect.left, switch_rect.centery)     # left side of switch

switch_to_return_p1 = (switch_rect.right, switch_rect.centery)   # right side of switch
switch_to_return_p2 = (return_rect.left, return_rect.centery)    # left side of return

# Final "return" back to battery negative (visual only to complete the loop)
# We'll consider the "return panel" itself as the last segment's end.
# For the beginner version, we treat the return_rect as the battery negative.

# ------------------------------
# GAME STATE (booleans and simple data)
# ------------------------------

# Each wire segment can be ON (draw thick bright line) or OFF (thin gray)
wire_battery_to_bulb_on = False  # is the first wire ON?
wire_bulb_to_switch_on  = False  # is the second wire ON?
wire_switch_to_return_on = False  # is the third wire ON?

# The switch can be ON (closed) or OFF (open). OFF means circuit is broken at the switch.
switch_on = False  # start with switch OFF

# A simple score that increases when player closes the circuit successfully
score = 0

# A message to show hints or feedback to the player
hint_text = "Click wires to toggle ON/OFF. Click the switch to toggle it."

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------

def draw_panel(rect, title):
    """Draws a labeled panel (simple box with title)."""
    # Draw a light gray filled rectangle for the panel
    pygame.draw.rect(screen, GRAY, rect, border_radius=12)
    # Draw a darker border around the rectangle
    pygame.draw.rect(screen, DARK_GRAY, rect, 2, border_radius=12)
    # Render the title text and blit (draw) it near the top-left
    label = font.render(title, True, BLACK)
    screen.blit(label, (rect.x + 8, rect.y + 8))

def draw_wire(p1, p2, is_on):
    """Draws a wire between two points. Blue and thick when ON, gray and thin when OFF."""
    # If the wire is ON, choose a thick line width and blue color
    if is_on:
        pygame.draw.line(screen, BLUE, p1, p2, 6)
    else:
        # If the wire is OFF, draw a thin gray line
        pygame.draw.line(screen, DARK_GRAY, p1, p2, 2)
    # Draw small connection dots at the endpoints so user sees the nodes
    pygame.draw.circle(screen, BLACK, p1, 5)
    pygame.draw.circle(screen, BLACK, p2, 5)

def point_on_segment(p, a, b, threshold=8):
    """
    Checks if a point p is close to the line segment a-b.
    This helps us detect clicks on a wire.
    """
    # Unpack point coordinates
    px, py = p
    # Unpack segment endpoints
    ax, ay = a
    bx, by = b
    # Compute segment length squared to avoid sqrt (faster)
    seg_len_sq = (bx - ax) ** 2 + (by - ay) ** 2
    # If the segment is extremely small, just check distance to one end
    if seg_len_sq == 0:
        # Compute simple distance to a
        dx = px - ax
        dy = py - ay
        # Return True if distance is small enough (near the point)
        return (dx * dx + dy * dy) <= threshold ** 2
    # Compute projection t of p onto a-b in [0,1]
    t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / seg_len_sq
    # Clamp t to [0,1] to stay on the segment
    t = max(0, min(1, t))
    # Find the closest point on the segment to p
    closest_x = ax + t * (bx - ax)
    closest_y = ay + t * (by - ay)
    # Compute squared distance from p to that closest point
    dx = px - closest_x
    dy = py - closest_y
    # Return True if this distance is within the threshold
    return (dx * dx + dy * dy) <= threshold ** 2

def draw_battery(rect):
    """Draw a simple battery icon inside its panel."""
    # Compute a small inner rect to represent the battery body
    inner = rect.inflate(-60, -60)
    # Draw the body as a white rectangle
    pygame.draw.rect(screen, WHITE, inner, border_radius=6)
    # Draw body outline
    pygame.draw.rect(screen, BLACK, inner, 2, border_radius=6)
    # Draw small positive cap on the right side
    cap = pygame.Rect(inner.right, inner.centery - 10, 18, 20)
    pygame.draw.rect(screen, BLACK, cap)
    # Draw plus and minus signs
    plus = font.render("+", True, RED)
    minus = font.render("-", True, BLACK)
    screen.blit(plus, (inner.right - 20, inner.top))
    screen.blit(minus, (inner.left, inner.bottom - 20))

def draw_bulb(rect, is_lit, current):
    """Draw a simple bulb; glow if lit."""
    # Find the center of the bulb area
    cx = rect.centerx
    cy = rect.centery
    # Draw a circle outline for the bulb glass
    pygame.draw.circle(screen, BLACK, (cx, cy), 36, 3)
    # If the bulb is lit, draw a yellow filled circle to simulate glow
    if is_lit:
        # The intensity of the glow can depend on current (simple mapping)
        # We clamp brightness so it doesn't become too large
        brightness = min(255, max(80, int(80 + current * 40)))
        # Compute a filled glow with the chosen brightness (R=255, G slightly lower)
        glow_color = (255, min(255, brightness), 0)
        pygame.draw.circle(screen, glow_color, (cx, cy), 30)
    # Draw a small base below the bulb
    base = pygame.Rect(cx - 20, cy + 30, 40, 12)
    pygame.draw.rect(screen, BLACK, base)
    # Draw label for "Bulb"
    label = font.render("Bulb", True, BLACK)
    screen.blit(label, (rect.x + 8, rect.y + 8))

def draw_switch(rect, is_on):
    """Draw a simple toggle switch."""
    # Draw the background panel (we already draw outer panel elsewhere; here we draw the switch itself)
    # Define a smaller inner rectangle for the switch track
    track = rect.inflate(-60, -60)
    # Draw the track as a rounded rectangle
    pygame.draw.rect(screen, DARK_GRAY, track, border_radius=20)
    # Compute knob size and position
    knob_radius = track.height // 2 - 6
    # If switch is ON, knob on right; else knob on left
    if is_on:
        knob_center = (track.right - knob_radius - 6, track.centery)
        knob_color = GREEN
        state_text = "ON"
    else:
        knob_center = (track.left + knob_radius + 6, track.centery)
        knob_color = RED
        state_text = "OFF"
    # Draw the circular knob
    pygame.draw.circle(screen, knob_color, knob_center, knob_radius)
    # Draw label text for the switch state
    label = font.render(f"Switch: {state_text}", True, WHITE)
    # Center the label inside the track
    label_pos = label.get_rect(center=(track.centerx, track.centery - knob_radius - 16))
    screen.blit(label, label_pos)

def draw_return(rect):
    """Draw the return panel (acts like path back to battery -)"""
    # Draw a simple ground-like symbol
    inner = rect.inflate(-30, -80)
    # Draw a line for ground
    pygame.draw.line(screen, BLACK, (inner.centerx - 20, inner.centery), (inner.centerx + 20, inner.centery), 4)
    pygame.draw.line(screen, BLACK, (inner.centerx - 12, inner.centery + 10), (inner.centerx + 12, inner.centery + 10), 3)
    pygame.draw.line(screen, BLACK, (inner.centerx - 6, inner.centery + 18), (inner.centerx + 6, inner.centery + 18), 2)
    # Draw label
    label = font.render("Return (-)", True, BLACK)
    screen.blit(label, (rect.x + 8, rect.y + 8))

def circuit_closed():
    """Returns True if the circuit loop is complete and the switch is ON."""
    # The circuit is considered closed if all wires are ON and the switch is ON
    return (wire_battery_to_bulb_on and wire_bulb_to_switch_on and wire_switch_to_return_on and switch_on)

def compute_current():
    """Compute current using I = V / R if circuit closed; otherwise 0."""
    # If loop is complete and switch is ON, compute current
    if circuit_closed():
        # Use Ohm's law: I = V / R (simple model)
        return BATTERY_VOLTAGE / BULB_RESISTANCE
    # Otherwise, no current flows
    return 0

def draw_ui_text():
    """Draws text information like voltage, resistance, current, score, and hints."""
    # Compute the current right now
    current = compute_current()
    # Render lines of info text
    t1 = title_font.render("Electric Circuit (Beginner)", True, BLACK)
    t2 = font.render(f"Battery: {BATTERY_VOLTAGE} V", True, BLACK)
    t3 = font.render(f"Bulb Resistance: {BULB_RESISTANCE} Ω", True, BLACK)
    t4 = font.render(f"Current I = V / R = {current:.2f} A", True, BLACK)
    t5 = font.render(f"Score: {score}", True, BLACK)
    t6 = font.render("Controls: Click wires to toggle. Click switch. Press R to reset.", True, BLACK)
    t7 = font.render(hint_text, True, BLACK)

    # Blit (draw) the texts on screen in the top area
    screen.blit(t1, (20, 20))
    screen.blit(t2, (20, 60))
    screen.blit(t3, (20, 85))
    screen.blit(t4, (20, 110))
    screen.blit(t5, (20, 135))
    screen.blit(t6, (20, 160))
    screen.blit(t7, (20, 185))

def handle_mouse_click(pos):
    """Toggle wires or the switch when the user clicks."""
    # Use global variables because we will change these boolean states
    global wire_battery_to_bulb_on
    global wire_bulb_to_switch_on
    global wire_switch_to_return_on
    global switch_on
    global score
    global hint_text

    # If click is close to the first wire segment, toggle it
    if point_on_segment(pos, battery_to_bulb_p1, battery_to_bulb_p2):
        wire_battery_to_bulb_on = not wire_battery_to_bulb_on
        hint_text = "Toggled wire: Battery → Bulb"
        return

    # If click is close to the second wire segment, toggle it
    if point_on_segment(pos, bulb_to_switch_p1, bulb_to_switch_p2):
        wire_bulb_to_switch_on = not wire_bulb_to_switch_on
        hint_text = "Toggled wire: Bulb → Switch"
        return

    # If click is close to the third wire segment, toggle it
    if point_on_segment(pos, switch_to_return_p1, switch_to_return_p2):
        wire_switch_to_return_on = not wire_switch_to_return_on
        hint_text = "Toggled wire: Switch → Return"
        return

    # If click is inside the switch rectangle, toggle the switch ON/OFF
    if switch_rect.collidepoint(pos):
        switch_on = not switch_on
        # If after toggling the circuit is closed, increase score
        if circuit_closed():
            score += 1
            hint_text = "Great! Circuit closed. Bulb is ON. (Press R to reset)"
        else:
            hint_text = "Switch toggled. Complete all wires to light the bulb."
        return

def reset_game():
    """Resets wires and switch to initial OFF states."""
    # Use global variables to change them here
    global wire_battery_to_bulb_on
    global wire_bulb_to_switch_on
    global wire_switch_to_return_on
    global switch_on
    global hint_text

    # Turn all wires OFF
    wire_battery_to_bulb_on = False
    wire_bulb_to_switch_on = False
    wire_switch_to_return_on = False
    # Turn the switch OFF
    switch_on = False
    # Update the hint text to guide the user
    hint_text = "Reset done. Toggle wires and the switch to complete the loop."

# ------------------------------
# MAIN GAME LOOP
# ------------------------------

# Create a variable to control whether the game is running
running = True

# Start the loop that will keep running until the user closes the window
while running:
    # Limit the loop to the desired frames per second (FPS)
    clock.tick(FPS)

    # Handle events (things that happen, like key presses or mouse clicks)
    for event in pygame.event.get():
        # If the user clicks the window close button, quit the game
        if event.type == pygame.QUIT:
            running = False
        # If the user presses a key on the keyboard
        elif event.type == pygame.KEYDOWN:
            # If the user pressed the 'r' or 'R' key, reset the game
            if event.key == pygame.K_r:
                reset_game()
        # If the user clicks a mouse button
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position where the user clicked
            mouse_pos = pygame.mouse.get_pos()
            # Handle the click to toggle wires or switch
            handle_mouse_click(mouse_pos)

    # --------------------------
    # UPDATE GAME STATE
    # --------------------------
    # Compute current to know if bulb should be lit
    I = compute_current()
    # Bulb is lit if current > 0 (i.e., circuit closed)
    bulb_lit = I > 0

    # --------------------------
    # DRAW EVERYTHING
    # --------------------------

    # Fill the screen with a white background each frame
    screen.fill(WHITE)

    # Draw UI text at the top-left (title, values, controls)
    draw_ui_text()

    # Draw component panels (battery, bulb, switch, return)
    draw_panel(battery_rect, "Battery (+)")
    draw_panel(bulb_rect, "Bulb")
    draw_panel(switch_rect, "Switch")
    draw_panel(return_rect, "Return (-)")

    # Draw the battery graphic
    draw_battery(battery_rect)
    # Draw the bulb graphic (with lit state and current)
    draw_bulb(bulb_rect, bulb_lit, I)
    # Draw the switch graphic (with ON/OFF state)
    draw_switch(switch_rect, switch_on)
    # Draw the return/ground graphic
    draw_return(return_rect)

    # Draw the three wire segments connecting the components
    draw_wire(battery_to_bulb_p1, battery_to_bulb_p2, wire_battery_to_bulb_on)
    draw_wire(bulb_to_switch_p1,  bulb_to_switch_p2,  wire_bulb_to_switch_on)
    draw_wire(switch_to_return_p1, switch_to_return_p2, wire_switch_to_return_on)

    # Optionally, draw a simple dashed line from return back to battery to visualize the loop (no toggle)
    # We'll make it very light to show it's implicit in this beginner version
    pygame.draw.line(screen, (180, 180, 180), (return_rect.centerx, return_rect.bottom),
                     (battery_rect.centerx, battery_rect.bottom), 1)

    # Update the full display to show our drawings
    pygame.display.flip()

# When the loop ends, quit pygame cleanly
pygame.quit()
# Also exit the program (optional)
sys.exit()
