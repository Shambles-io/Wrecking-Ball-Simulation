import math
from turtle import color
from cv2 import circle
from numpy import angle, size
import pygame
import pymunk
import pymunk.pygame_util

#Initialize pygame
pygame.init()

#Window parameters
WIDTH, HEIGHT = 1000, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Calculate and returns absolute value of distance between two points
def calculate_distance(p1, p2):
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)

# Calculate and return angle (in radians) between two points *Assuming p2 is located at 0,0*
def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])


# Creating boundary (static) objects
def create_boundaries(space, width, height):
    # Creating a list of rectangles
    # For drawing rectangles in pymunk, you need an x,y position of the center of 
    # the rectangle and a width and height of teh rectangle
    rects = [
        [(width/2, height - 10), (width, 20)], # Floor
        [(width/2, 10), (width, 20)], # Ceiling
        [(10, height/2), (20, height)], # Left Wall
        [(width - 10, height/2), (20, height)] # Right Wall
    ]

    #Loop through list of rects to draw them to screen
    for pos, size in rects:
        # Creating static (non-moving) bodies
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        # Create_box takes in the body we want a shape associated with and the size
        shape = pymunk.Poly.create_box(body, size)
        # Giving elasticity and friction to rectangles
        shape.elasticity = 0.4
        shape.friction = 0.5

        space.add(body, shape)


# Creating objects to hit
def create_structure(space, width, height):
    BROWN = (139, 69, 19, 100) # Defining color brown with 100% opacity
    rects = [
        [(600, height - 120), (40, 200), BROWN, 100], # Brown rectangle with 100 mass
        [(900, height - 120), (40, 200), BROWN, 100], # Brown rectangle with 100 mass
        [(750, height - 240), (340, 40), BROWN, 150] # Brown rectangle with 150 mass
    ]

    for pos, size, color, mass in rects:
        body = pymunk.Body()
        body.position = pos
        shape = pymunk.Poly.create_box(body, size, radius=2) #radius is rectangles boarder thickness
        shape.color = color
        shape.mass = mass
        shape.elasticity = 0.4
        shape.friction = 0.4

        space.add(body, shape)


# Creating swinging pendulum
def create_pendulum(space):
    rotation_center_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    rotation_center_body.position = (300, 270)
    # Swinging body
    body = pymunk.Body()
    body.position = (300, 300)
    # Segment takes the body and the two positions of the line that we want to draw relative to the body
    # (0,0) is at the center of the body ; 5 is the thickness of the line
    line = pymunk.Segment(body, (0, 0), (255, 0), 5)
    # Circle with radius 40 and center at (255,0) -> end of our line segment
    circle = pymunk.Circle(body, 40, (255, 0))
    # Giving line and circle attributes
    line.friction = 1
    circle.friction = 1
    line.mass = 8
    circle.mass = 30
    circle.elasticity = 0.95

    # Creating the joint of rotation
    # Pass in the bodies we want to join, and where on body we want joint to be connected (center of each)
    rotation_center_joint = pymunk.PinJoint(body, rotation_center_body, (0, 0), (0, 0))
    space.add(circle, line, body, rotation_center_joint)


# Function for adding objects to screen
def create_ball(space, radius, mass, pos):
    # In pygame, we have an IMAGE and a BODY: 
    # the image is attached to a body and what is actually seen in games 
    # Example: in games there is the skin, and the hitbox of that skin
    # The body is first static, so it does not fall while user draws line
    body = pymunk.Body(body_type=pymunk.Body.STATIC) 
    # Setting body position with the tupple of its x,y location
    # Note: The top-left corner of a pygame window is the 0,0 position
    body.position = pos # When teh ball is creates, its center is at location of the mouse
    # Attach a shape to our body
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    # Giving elasticity and friction to ball
    shape.elasticity = 0.9
    shape.friction = 0.4
    # Color is in RBG value; 100 is the opacity of our color
    shape.color = (255, 0, 0, 100)
    # Adding body and shape to the simulation
    space.add(body, shape)
    return shape


# Draw function
def draw(space, window, draw_options, line):
    # Initially clear window by drawing/filling it white
    window.fill("white")

    # Adding a line to screen. We give it a color, endpoints, and thickness, respectively
    if line:
        pygame.draw.line(window, "black", line[0], line[1], 3)
    
    space.debug_draw(draw_options)

    # Update display
    pygame.display.update()


#Main event loop
def run(window, width, height):
    run = True
    # Clock ensures the main game loop runs at specified speed
    clock = pygame.time.Clock()
    fps = 60
    #delta time - difference in time
    dt = 1 / fps

    # Creating a pymunk space - where we put all of our objects
    space = pymunk.Space()
    # Gravity here is a tupple with an x and y componant. Here we are setting the x-gravity 
    # to 0, and the y-gravity to 981 (using 9.81 would be really slow)
    space.gravity = (0, 981)

    # Call create boundaries function
    create_boundaries(space, width, height)
    # Create objects we want to hit
    create_structure(space, width, height)
    # Create pendulum object
    create_pendulum(space)

    # Drawing options for our space
    # We pass in window because that is where the simulations will be drawn
    draw_options = pymunk.pygame_util.DrawOptions(window)

    # Initialize that we have pressed and the ball to none when first running program
    pressed_pause = None
    ball = None

    while run:
        line = None
        if ball and pressed_pos:
            # If ball is on the screen, we want to draw a line between the mouse position and ball
            line = [pressed_pos, pygame.mouse.get_pos()]

        # Event checking loop: loops through all events occuring in the
        # simulation and allows us to close out by clicking the red x on the window bar
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            # If user presses mouse button, we apply force toan object
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If there is no ball currently on the screen, we will create the ball
                if not ball:
                    # When the mouse is pressed, we want to create the ball at that location
                    pressed_pos = pygame.mouse.get_pos()
                    # Create ball object with radius=30 and mass=10 and pressed position
                    ball = create_ball(space, 30, 10, pressed_pos)
                
                # If ball is already created/placed, we want to be able to launch the 
                # ball, or click again to delete the ball
                elif pressed_pos:
                    # Changing the ball type to be dynamic
                    ball.body.body_type = pymunk.Body.DYNAMIC
                    
                    # Calculate the angle to shoot ball
                    # Passing *line breaks the line into 2 separate list elements (p1 & p2)
                    angle = calculate_angle(*line) # Angle in Radians
                    
                    # Calculate the force on the ball
                    # Passing the list elements (p1 & p2) of the line
                    # Multiply by 50 just to increase force (can be changed if/when we want)
                    force = calculate_distance(*line) * 50

                    # "Break" the force into x and y componants
                    force_x = math.cos(angle) * force
                    force_y = math.sin(angle) * force
                    
                    # applying 10000 force in x-direction at the 0,0 location within ball (center)
                    # Note: if we make the force too high, the ball could go through wall boundary between frames
                    ball.body.apply_impulse_at_local_point((force_x, force_y), (0, 0))
                    pressed_pos = None
                
                # If we have already launched the ball, when we click again it will delete the current ball
                else:
                    space.remove(ball, ball.body)
                    ball = None
                                        
        draw(space, window, draw_options, line)
        # Step is similar to clock.tick(), but it essentially says how fast the 
        # simulation should go
        space.step(dt)

        # While loop can run at a max 60 fps
        clock.tick(fps)

    # Quit pygame
    pygame.quit()

if __name__ == "__main__":
    run(window, WIDTH, HEIGHT)