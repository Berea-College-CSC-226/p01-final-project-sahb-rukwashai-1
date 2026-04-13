This folder is for holding your original assignments that you are using as a reference. 
Put the code in this folder, but DO NOT modify it directly!

class AdoptionCenter:
    def __init__(self):
        """
        Runs an adoption center of cats and dogs
        """
        # self.pets is a dictionary where the key = pet name; value = pet object (Dog or Cat)
        self.pets = {}

    def add_pet(self, pet):
        """
        Add a pet to the adoption center by inserting them into the self.pets attribute.

        :param pet: A dog or cat object
        :return: None
        """
        if not self.pets.get(pet.name):
            self.pets[pet.name] = pet
        else:
            print(f"Pet already in shop with that name {pet.name}; please give a unique name")

    def adopt_pet(self, pet):
        """
        Adds a pet to the adoption center.

        :param pet: a Pet object
        :return: None
        """
        pet = self.pets.get(pet.name)     # retrieves the pet, or None if it doesn't exist.
        if pet:
            try:
                pet.adopt()
                print(f"{pet.name} has been adopted!")
            except AlreadyAdoptedError as e:
                print(f"Error: {e}")
        else:
            print(f"Pet not found in the center.")



class Cat(Pet):
   

class Dog(Pet):
    """
    Dog subclass with a trained attribute and bark method.
    """
    def __init__(self, adoption_center, name, breed, age, trained=False):
        super().__init__(adoption_center, name, "Dog", breed, age)
        self.trained = trained

    def bark(self):
        """
        Woof!

        :return: String of dog-speak
        """
        return f"{self.name} says: Woof!"
class AlreadyAdoptedError(Exception):
    """
    Raised when attempting to adopt a pet that's already been adopted.
    """
    def __init__(self, pet_name):
        super().__init__(f"{pet_name} has already been adopted!")

class Pet:
    """
    Base class for pets in the adoption center.
    """
    def __init__(self, adoption_center, name, species, breed, age):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.adopted = False        # All pets are up for adoption when they are added to the center
        adoption_center.add_pet(self)

    def adopt(self):
        """
        Method for adopting pets. Throws AlreadyAdoptedError if pet is unavailable.

        :return: None
        """
        if self.adopted:
            raise AlreadyAdoptedError(self.name)
        self.adopted = True

    def __str__(self):
        """
        String override method for better printing.

        :return: String representation of the pet
        """
        return f"{self.name} ({self.species}, {self.breed}, {self.age} years old)"

class Game:
    def __init__(self):
        """
        Game class for handling the game logic.
        """
        self.size = 800, 600
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill('#9CBEBA')
        self.clock = pygame.time.Clock()
        self.tuna = Player(self.size)
        self.tacocat = NPC(self.size)


    def run(self):
        """
        Runs the game forever

        :return: None
        """
        while self.running:
            # Handle game ending first
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Handle user and game events next
            if pygame.sprite.spritecollide(self.tuna, [self.tacocat], False):
                # Collision! Prints the game ending text to the screen.
                font = pygame.font.SysFont("ComicSans", 36)
                txt = font.render('Taco, you caught me!!', True, "darkblue")
                self.screen.blit(txt, (self.size[0]//2, self.size[1]-100))
            else:
                # Keep playing!
                self.tuna.movement(pygame.key.get_pressed())
                self.tacocat.movement()
                self.screen.fill('#9CBEBA')
                self.screen.blit(self.tuna.surf, self.tuna.rect)
                self.screen.blit(self.tacocat.surf, self.tacocat.rect)
            pygame.display.update()
            self.clock.tick(24)

        pygame.quit()



class NPC(pygame.sprite.Sprite):
    move_distance = 10
    directions = ["north", "east", "south", "west"]

    def __init__(self, screen_size):
        """
        Represents the Good NPC in the game.

        :param screen_size: size of the window, for ensuring the NPC stays on screen
        """
        print("Spawning NPC")
        self.screen_size = screen_size
        super().__init__()
        self.surf = pygame.image.load('images/tacocat.png').convert_alpha()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.move_ip(self.screen_size[0]//4, self.screen_size[1]//4)
        self.path = random.choice(self.directions)
        self.position = [0,0]

    def get_direction(self):
        """
        Keeps the NPC on the screen.

        :return: None
        """
        if self.rect.bottom >= self.screen_size[1]:
            # Bottom
            self.path = "north"
        if self.rect.top <= 0:
            # Top
            self.path = "south"
        if self.rect.left <= 0:
            # Left
            self.path = "east"
        if self.rect.right >= self.screen_size[0]:
            # Right
            self.path = "west"
        elif random.random() > .95:
            # Randomly change direction 5% of the time
            self.path = random.choice(self.directions)

    def movement(self):
        """
        Moves the NPC around.

        :return: None
        """
        if self.path == "north":
            self.rect.move_ip(0, -self.move_distance)
            self.position[1] -= self.move_distance
        elif self.path == "south":
            self.rect.move_ip(0, self.move_distance)
            self.position[1] += self.move_distance
        if self.path == "east":
            self.rect.move_ip(self.move_distance, 0)
            self.position[0] -= self.move_distance
        if self.path == "west":
            self.rect.move_ip(-self.move_distance, 0)
            self.position[0] += self.move_distance

        self.get_direction()


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_size):
        """
        Represents the player in the game.

        :param screen_size: Screen size, for keeping character on the screen
        """
        super().__init__()
        self.screen_size = screen_size
        print("Spawning player")
        self.surf = pygame.image.load('images/tuna.png').convert_alpha()
        self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.move_ip(self.screen_size[0]//2, self.screen_size[1]//2)


    def movement(self, keys):
        """
        Handles up, down, left, right movement events from the user

        :param keys: key presses from pygame event listener
        :return: None
        """
        if keys[pygame.K_UP]:
            self.rect.move_ip(0, -3)
        elif keys[pygame.K_DOWN]:
            self.rect.move_ip(0, 3)
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(3, 0)
        elif keys[pygame.K_LEFT]:
            self.rect.move_ip(-3, 0)

for color in colors:
    alex.color(color)  # Set pen color for this side
    alex.left(90)
    alex.forward(50)

for color in colors:

    for i in range(4):
        alex.color("red")
        alex.left(45)
        alex.forward(50)
        alex.left(45)
        alex.forward(50)
    alex.penup()
    alex.forward(100)
    alex.pendown()
    for i in range(4):
        alex.color("green")
        alex.forward(50)
        alex.left(-135)
        alex.forward(50)
        alex.right(135)
        alex.forward(50)

    for i in range(1):

        alex.penup()
        alex.right(90)
        alex.forward(100)
        alex.pendown()
        alex.color("green")
        alex.left(90)
        alex.forward(50)
        alex.left(45)
        alex.forward(50)
        alex.right(90)
        alex.forward(50)
        alex.left(45)
        alex.forward(50)
        alex.right(90)
        alex.forward(100)
        alex.right(90)
        alex.forward(190)
        alex.right(90)
        alex.forward(100)
        alex.right(90)
        alex.forward(25)
    turtle.done()


# Keep the window open
turtle.done()



for i in range(numTurtles):
    nt = turtle.Turtle()        # Make a new turtle, initialize values
    nt.setheading(head)
    nt.pensize(2)

    nt.color(random.randrange(256),random.randrange(256),random.randrange(256))
    nt.speed(10)
    wn.tracer(30,0)
    tList.append(nt)            # Add the new turtle to the list
    head = head + 360/numTurtles

dist = 15
for angle in range(100):        # moveTurtles(tList,dist,angle) function removed by Dr. Jan Pearce
    for tur in tList:           # Make every turtle on the list do the same actions.
        tur.forward(dist)
        tur.right(angle)

w = tList[0]
w.up()


height = 50
width = 50
depth = 7.5
# All the colors to use; the rows loop will select a color on each iteration
colors = ['purple', 'blue', 'green', 'yellow', 'orange', 'red']

turn_amount = 15
wn = turtle.Screen()                    # creates a graphics window

box_turtle = turtle.Turtle()            # create a turtle named myturtle
box_turtle.speed(0)
box_turtle.penup()
box_turtle.shape('circle')              # possible shapes are 'arrow', 'turtle', 'circle', 'square', 'triangle', 'classic'

color_counter = 0  #

for row in range(6):  # Ligne 18
    for col in range(6):  # Ligne 19
        for dep in range(6):  # Ligne 20
            for turn in range(4):
                x_cord = col * width - 300 + dep * depth
                y_cord = row * height - 300 + dep * depth * 1.2
                box_turtle.goto(x_cord, y_cord)


            box_turtle.color(colors[col])
            color_counter += 1


            box_turtle.stamp()          # Loop for the depth
            # Moves box_turtle to a position based on row, col, and dep
            x_cord = col * width - 300 + dep * depth
            y_cord = row * height - 300 + dep * depth * 1.2
            box_turtle.goto(x_cord, y_cord)
            box_turtle.stamp()          # Stamps the shape onto the window

wn.exitonclick()                      

colors = ['purple', 'blue', 'green', 'yellow', 'orange', 'red']

turn_amount = 15
wn = turtle.Screen()                    # creates a graphics window

box_turtle = turtle.Turtle()            # create a turtle named myturtle
box_turtle.speed(0)
box_turtle.penup()
box_turtle.shape('circle')              # possible shapes are 'arrow', 'turtle', 'circle', 'square', 'triangle', 'classic'

color_counter = 0  #

for row in range(6):  # Ligne 18
    for col in range(6):  # Ligne 19
        for dep in range(6):  # Ligne 20
            for turn in range(4):
                x_cord = col * width - 300 + dep * depth
                y_cord = row * height - 300 + dep * depth * 1.2
                box_turtle.goto(x_cord, y_cord)


            box_turtle.color(colors[col])
            color_counter += 1


            box_turtle.stamp()          # Loop for the depth
            # Moves box_turtle to a position based on row, col, and dep
            x_cord = col * width - 300 + dep * depth
            y_cord = row * height - 300 + dep * depth * 1.2
            box_turtle.goto(x_cord, y_cord)
            box_turtle.stamp()          # Stamps the shape onto the window

# Draws a house on the screen
shape = turtle.Turtle()
shape.hideturtle()

# Make the roof
shape.color('red')
shape.begin_fill()          # Tells Python to fill the shape with a color when done
for side in range(3):
    shape.forward(100)
    shape.left(120)
shape.end_fill()            # Tells Python the shape is complete; now fill it
shape.penup()

# Make the main house rectangle
shape.color('#3333FF')
shape.pendown()
shape.begin_fill()
for side in range(2):
    shape.forward(100)
    shape.right(90)
    shape.forward(140)
    shape.right(90)
shape.end_fill()
shape.penup()




class Nascii:
    def __init__(self, name=""):
        '''
        Creates a new Nascii object.

        :param name: The text to write to the screen.
        '''
        self.block_size = 30
        self.wn = None
        self.setup_window()
        while name == "":
            name = self.wn.textinput("Enter your name", "Enter your name: ")
        self.name = name

    def setup_window(self):
        '''
        Sets up the turtle window and places the turtle at the starting location

        :return:
        '''
        self.wn = turtle.Screen()
        self.t = turtle.Turtle()
        self.t.teleport(-300, 300)
        self.t.speed(0)

    def draw(self):
        '''
        Draws the name in Ascii

        :return:
        '''
        for letter in self.name:
            self.draw_row(letter)
            self.t.penup()
            self.t.bk(7 * self.block_size)
            self.t.right(90)
            self.t.fd(self.block_size)
            self.t.left(90)
            self.t.pendown()
            self.t.speed(0)
        self.t.hideturtle()

    def draw_row(self, letter):
        '''
        Draws a single row, representing a letter in Ascii

        :param letter: the letter to draw
        :return:
        '''
        # Converts any character to it's ASCII value
        letter_ord = "{:07b}".format(ord(letter))
        for bin_val in letter_ord:
            self.t.color("black")
            self.t.fillcolor("white" if bin_val == "0" else "black")
            self.t.begin_fill()
            self.draw_square()
            self.t.end_fill()
            self.t.penup()
            self.t.fd(self.block_size)
            self.t.pendown()
            self.t.speed(0)

        self.t.color("white" if bin_val == "1" else "black")
        self.t.write(letter, align="right", font=("Arial", 18, "normal"))

    def draw_square(self):
        '''
        Draws the individual squares

        :return:
        '''
        for i in range(4):
            self.t.fd(self.block_size)
            self.t.lt(90)




def unittest(did_pass):
    """
    Print the result of a unit test.

    :param did_pass: a boolean representing the test
    :return: None
    """
    linenum = getframeinfo(stack()[1][0]).lineno
    if did_pass:
        msg = "Test at line {0} ok.".format(linenum)
    else:
        msg = ("Test at line {0} FAILED.".format(linenum))
    print(msg)


def reverse_list_test_suite():
    print("Testing clean_string_to_list() function")
    unittest(clean_string_to_list("A test string") == ["a", "test",  "string"])
    unittest(clean_string_to_list("A string, with punctuation? It's true!") == ["a", "string", "with", "punctuation", "its", "true"])

    print("Testing reverse() function")
    unittest(reverse(["a", "list", "in", "order"]) == ["order", "in", "list", "a"])
    unittest(reverse(["another", "fine", "example"]) == ["example", "fine", "another"])

    print("End of the test suite")


def clean_string_to_list(in_string):
    """
    Removes all punctuation from the list, and converts it to a list.
    Typically, you wouldn't combine two functions in one (removing punctuation AND converting to list).
    :param in_string: A string to strip and convert
    :return: A list, representing each word in the original string
    """
    # Code modified from Chapter 8 on Strings; how to strip punctuation
    s_without_punct = ""
    for letter in in_string:
        if letter not in string.punctuation:
            s_without_punct += letter
    return s_without_punct.lower().split()          


def reverse(input_list):
    """
    Reverses a list

    :param input_list: A list of strings (any list would work though)
    :return: A list, in reverse order
    """
    output_list = []
    list_length = len(input_list)
    for index in range(list_length-1, -1, -1):      # Pay attention to the range here; why'd I do this?
        # print input_list[index]                   # For testing purposes only
        output_list.append(input_list[index])
    return output_list



 

def unittest(did_pass):
    """
    Print the result of a unit test.

    :param did_pass: a boolean representing the test
    :return: None
    """

    caller = getframeinfo(stack()[1][0])
    linenum = caller.lineno
    if did_pass:
        msg = "Test at line {0} ok.".format(linenum)
    else:
        msg = ("Test at line {0} FAILED.".format(linenum))
    print(msg)


def a09_test_suite():
    # We have began your test suite here. You should add more as you develop fruitful functions!
    unittest(is_valid_input("036000291452") == True)
    unittest(is_valid_input("1") == False)
    unittest(is_valid_input("1324A") == False)
    unittest(is_valid_input("aaa") == False)
    unittest(is_valid_input("111111111111") == True)
    unittest(is_valid_modulo("036000291452") == True)
    unittest(is_valid_modulo("036000291453") == False)
    unittest(translate("036000291452")== "10100011010111101010111100011010001101000110101010110110011101001100110101110010011101101100101")


def is_valid_input(barcode):
    if len(barcode) == 12 and barcode.isdigit():
        return True
    return False


def is_valid_modulo(barcode):
    odd_idx_sum = sum([int(i) for i in range(1,len(barcode),2)])
    even_idx_sum = sum([int(i) for i in range(0,len(barcode)-1,2)])

    total_sum = (odd_idx_sum * 3) + even_idx_sum
    calculate_module_checker = 0
    if total_sum % 10 != 0:
        calculate_module_checker = 10 - (total_sum % 10)

    if calculate_module_checker == int(barcode[-1]):
        return True

    return False


def translate(barcode_num): # removed the side parament because it was unnecessary to have a block of code just for each side.
    # the first index is the left side and the second index is the right side

    barcode_encoding = {
        0: ("0001101","1110010"),
        1: ("0011001","1100110"),
        2: ("0010011","1101100"),
        3: ("0111101","1000010"),
        4: ("0100011","1011100"),
        5: ("0110001","1001110"),
        6: ("0101111","1010000"),
        7: ("0111011","1000100"),
        8: ("0110111","1001000"),
        9: ("0001011","1110100")
    }

    translation = ""

    barcode_num_left = barcode_num[:6]
    barcode_num_right = barcode_num[6:]

    translation += "101" # adding left guard bars

    for i in barcode_num_left:
        translation += barcode_encoding[int(i)][0]

    translation += "01010" # adding the Center bars

    for i in barcode_num_right:
        translation += barcode_encoding[int(i)][1]

    translation += "101"  # adding right guard bars
    return translation

def draw_square(length,pen):
    for i in range(4):
        pen.forward(length)
        pen.left(90)




class CaesarCipher:
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"            # The alphabet, which will be used to do our shifts

    def __init__(self, crypt_type, input_file="letters/message_input.txt", key=0):
        self.input_file = input_file                            # The file to be encrypted or decrypted
        self.key = key                                          # The amount each message/cipher will be shifted
        self.crypt_type = crypt_type                            # Either "encrypt" or "decrypt"
        if self.crypt_type == "encrypt":
            self.message = ""                                       # A placeholder for the message
        else:
            self.cipher = ""                                        # A placeholder for the cipher
        self.import_file()                                      # Calls the import_file() method below

    def import_file(self):
        """
        Imports a file stored in the variable self.input_file

        :return: a string representing the contents of the file
        """
        f = open(self.input_file, "r")
        if self.crypt_type == "encrypt":
            self.message = f.read()                  # Set self.message to the file contents
        elif self.crypt_type == "decrypt":
            self.cipher = f.read()                   # Set self.cipher to the file contents
        f.close()
        if __name__ == "__main__":
            print("File imported: {0}".format(self.input_file))

    def export_file(self, filename):
        """
        Exports a file called filename

        :param text_to_export: the string to be written to the exported file
        :param filename: a string representing the name of the file to be exported to
        """
        f = open(filename, "w")
        if self.crypt_type == "encrypt":
            f.write(self.cipher)
        else:
            f.write(self.message)
        f.close()
        if __name__ == "__main__":
            print("File exported: {0}".format(filename))

    def encrypt(self):
        """
        Converts an original message into a ciphered message with each letter shifted to the right by the key.
        
        :return: None
        """
        if self.crypt_type == "encrypt":
            output = ""
            for i in self.message:
                if i.upper() in self.alphabet:
                    old_letter = self.alphabet.find(i.upper())
                    # Uses modulus to return the correct index for each letter after the shift
                    # (for cases where the index is outside the range of self.alphabet,
                    #  it wraps back to the beginning of the alphabet)
                    output += self.alphabet[(old_letter + self.key) % 26]
                else:
                    output += i         # Adds non-alphabet characters directly
            if __name__ == "__main__":
                print("Message Encrypted")
            self.cipher = output

    def decrypt(self):
        """
        We will convers a ciphertext back into original message by shifting each letter by the key.

        :return:None
        """
        if self.crypt_type == "decrypt":
            output = ""
            for i in self.cipher:
                if i.upper() in self.alphabet:
                    old_letter = self.alphabet.find(i.upper())

                    output += self.alphabet[(old_letter - self.key) % 26]
                else:
                    output += i
        if __name__ == "__main__":
            print("Message Decrypted")
        self.message = output


class ImageCipher(CaesarCipher):
    def __init__(self, crypt_type, input_file, original_image_path, shifted_image_path):
        original_img = ImageConverter(original_image_path)
        shifted_img = ImageConverter(shifted_image_path)
        key = find_red_shift(original_img, shifted_img)
        super().__init__(crypt_type, input_file, key)

    def decrypt(self):
        super().decrypt()



def unittest(did_pass):
    """
    Print the result of a unit test.
    :param did_pass: a boolean representing the test
    :return: None
    """

    caller = getframeinfo(stack()[1][0])
    linenum = caller.lineno
    if did_pass:
        msg = "Test at line {0} ok.".format(linenum)
    else:
        msg = ("Test at line {0} FAILED.".format(linenum))
    print(msg)




class ImageConverter:
    """
    Useful tool for converting images
    """
    def __init__(self, img_path):
        self.im = Image.open(img_path)
        self.pixelList = list(self.im.getdata())
        self.im_modified = None

    def shift_red(self, shift_val):
        """
        Shifts the red pixels by amount shift_val using modulo (wraps around).
        """
        im2_pixels = []

        for i in self.pixelList:
            # Use modulo to wrap around (0-255)
            newRed = (i[0] + shift_val) % 256
            pixel = (newRed, i[1], i[2])
            im2_pixels.append(pixel)

        self.im_modified = Image.new('RGB', self.im.size)
        self.im_modified.putdata(im2_pixels)

    def get_red_channel(self):
        """
        Returns a list of red channel values from the original image.
        """
        return [pixel[0] for pixel in self.pixelList]
    def save_img(self, filename):
        """
        Saves the image to filename

        Args:
            filename: String of the new files filename

        Returns: None

        """
        if self.im_modified:
            self.im_modified.save(filename)


def find_red_shift(image1, image2):
    """
    Compares two images and returns the red shift amount.
    Works by comparing the first pixel's red value in both images.

    :param image1: ImageConverter object (original)
    :param image2: ImageConverter object (shifted)
    :return: integer representing the shift amount
    """
    # Get the first pixel's red value from each image
    red1 = image1.pixelList[0][0]  # First pixel, red channel
    red2 = image2.pixelList[0][0]  # First pixel, red channel

    # Calculate the shift (using modulo to handle wrap-around)
    shift = (red2 - red1) % 256

    return shift
def main():
    """
    Small program to demonstrate shifting red. The first one has very little red, thus very little shift is noticed.
    The second image has lots of red, so a large shift is noticed.

    Returns:

    """
    i = ImageConverter("images/map.png")
    i.shift_red(3)
    i.save_img("images/map_2.png")

    i = ImageConverter("images/RF9152.png")
    i.shift_red(-200)
    i.save_img("images/RF9152_2.png")

if __name__ == "__main__":
    main()