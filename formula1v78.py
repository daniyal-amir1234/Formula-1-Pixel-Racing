"""
Formula 1 Pixel Racing (Beta)

Author: Daniyal Amir
Started: June 2024
Language: Python
Framework: Pygame

A retro-inspired top-down Formula 1 time trial game.
Built entirely in a single file as a solo project, with
custom rendering, physics, camera, and tyre wear systems.

Originally developed as an OCR A-Level CS NEA (69/70),
then extended post-submission.
"""

import pygame # for the graphics module to run the game
from pygame import Vector2 # for the track position of the player's car
import time # for the timing system and other telemetry elements
import random # for exhaust flame animations
import math # for splash screen sequence
import numpy as np # for engine sound

print("\nFormula 1 Pixel Racing by Daniyal Amir. A pure Pygame-based development project made in raw Python.")

pygame.init() # initialise pygame

screen_size_x = 1080
screen_size_y = 810

screen_center = (screen_size_x//2), (screen_size_y//2), 
screen = pygame.display.set_mode((screen_size_x, screen_size_y))

# INITIALISATION:
# CAR SPEEDS, ANGLES, POSITIONS AND (MAXIMUM) ROTATION SPEED
track_speed = 0
track_angle = -90
rotation_speed = 60
rate_of_change_of_speed = 0
carcentrex, carcentrey = (screen_size_x//2)-20, (screen_size_y//2)-39
wheel_angle = 0
attempt_number = 0
rate_of_change_of_turning_speed = 0
steering_pivot_limiter_multiple = 0


# COORDINATE TRACK POSITION SYSTEM INITIALISATION:
track_pos = Vector2()

starting_position = -5560, -6817 # we need to fine-tune this whenever we render a new map # FOR SOME REASON BOTH X AND Y IS NEGATIVE
# oh yeah the image reference AND the coordinates need to be right.
# e.g. 800, 200 will make you spawn in the 0-0 image, regardless of other things that you change
# starting_position = 835, 384 # you need to change this every time you render in a new map

# are x and y switched or something?! - sorta - don't ask what "sorta" means
# starting_position like actually works btw - it really does do the starting position

track_pos.x, track_pos.y = starting_position # this is where the finish line is
# track_pos now has the x and y attributes of 1236 and 624. i think you can combine the above two lines as 'track_pos = Vector2(1236, 624)'
# > Vector2 assigns an x and y attribute to a given variable

square_length_of_each_tile = 1600 # NOT THE RED BORDERS FOR EACH QUADRANT/TILE
half_length_of_each_tile = square_length_of_each_tile/2

x_y_conversion_multiplier = 0
x_y_conversion_multiplier_for_y = 0
x_y_conversion_multiplier_for_x = 0

original_car_image = pygame.image.load("redbull carv19 with no front wheelsv1.png")
carrect = original_car_image.get_rect()

leftfrontwheelimg = pygame.image.load("left front wheelv3.png")
leftfrontwheelimg = pygame.transform.scale(leftfrontwheelimg, (9, 17))
leftfrontwheelrect = leftfrontwheelimg.get_rect()

rightfrontwheelimg = pygame.image.load("right front wheelv3.png")
rightfrontwheelimg = pygame.transform.scale(rightfrontwheelimg, (9, 17))
rightfrontwheelrect = rightfrontwheelimg.get_rect()


##### TEXT RENDERING #####
# RENDER TEXT ONCE FUNCTION
def render_text_once(font_size, string, anti_aliasing, colour):
    text_surface = font_size.render(string, anti_aliasing, (colour))
    return text_surface


# FONT TYPE AND SIZE INITIALISATION
font_size_15 = pygame.font.Font('freesansbold.ttf', 15)
font_size_17 = pygame.font.Font('freesansbold.ttf', 17)
font_size_20 = pygame.font.Font('freesansbold.ttf', 20)
font_size_25 = pygame.font.Font('freesansbold.ttf', 25)
font_size_30 = pygame.font.Font('freesansbold.ttf', 30)
font_size_35 = pygame.font.Font('freesansbold.ttf', 35)
font_size_37_italics = pygame.font.SysFont('freesansbold.ttf', 37, italic=True)
font_size_40 = pygame.font.Font('freesansbold.ttf', 40)
font_size_70 = pygame.font.Font('freesansbold.ttf', 70)
font_size_75 = pygame.font.Font('freesansbold.ttf', 75)


# TIMING INITIALISATION:
timer_toggle = False

sector1_time = "00:00.000" # formatted time to calculate sector 2
sector2_time = "00:00.000" # formatted time to calculate sector 3

sector1_times_list = []
sector2_times_list = []
sector3_times_list = []

sector1_times_list = ["00:16.312"]
sector2_times_list = ["00:18.145"]
sector3_times_list = ["00:24.478"]

# SECTOR BOX COLOURS:
# by default, the sectors' colours will be a grey colour (this will be when no time has been set yet)
sector1_colour = (100, 100, 100)
sector2_colour = (100, 100, 100)
sector3_colour = (100, 100, 100)
green_colour = (0, 240, 0)
yellow_colour = (240, 240, 0)

# we need to add boolean flags to ensure only one time is recorded when we cross a sector marking/the finish line
sector1_passed = False
sector2_passed = False
sector3_passed = False

sector1_text = render_text_once(font_size_20, "S1", False, (225, 225, 225))
sector2_text = render_text_once(font_size_20, "S2", False, (225, 225, 225))
sector3_text = render_text_once(font_size_20, "S3", False, (225, 225, 225))


# TIMING FORMATTING FUNCTIONS - CONVERSIONS BETWEEN FORMATTED TIMES "00:00.000" AND MINUTES, SECONDS AND MILLISECONDS
def convert_formatted_time_into_seconds_and_milliseconds(unconverted_time_string): # e.g. from
    # print("entered 'convert_formatted_time_into_seconds_and_milliseconds()' ")
    list_of_unconverted_time_string = list(unconverted_time_string)
    # print("LISTY WISTY BISTY:", list_of_unconverted_time_string, len(list_of_unconverted_time_string))

    minutes = int(list_of_unconverted_time_string[0] + list_of_unconverted_time_string[1])
    added_seconds = minutes * 60
    # print("added_seconds:", added_seconds)

    string = list_of_unconverted_time_string[3] + list_of_unconverted_time_string[4] + list_of_unconverted_time_string[5] + list_of_unconverted_time_string[6] + list_of_unconverted_time_string[7] + list_of_unconverted_time_string[8]


    # print(string)

    # FIXES ".." FORMATTING ISSUE
    if ".." in string: # e.g. if ".." in "36..64"
        # print("medic", string)

        string = string.replace("..", ".") # "36..64" -> "36.64"
        string = string + "0" # "36.64" -> "36.640"

        # print("MEDIC", string)

        for i in range(50):
            # print("MEDDICCC!!! JA??? I'M DYING 'ERE!!!!")
            pass

    seconds_and_milliseconds = float(string) + added_seconds # float() not int(), duh
    return seconds_and_milliseconds # return the float, not the string version of seconds_and_milliseconds

def convert_seconds_and_milliseconds_into_formatted_time(unconverted_time_float): # e.g. 23.456 # this is a very, very elegant function i cooked up
    # print("entered 'convert_seconds_and_milliseconds_into_formatted_time'")

    # calculate minutes:
    minutes = unconverted_time_float // 60

    # concatenate a minutes string:
    string_of_minutes = str(int(minutes))
    if minutes < 10:
        string_of_minutes = "0" + string_of_minutes

    # print(string_of_minutes)

    # calculate seconds remaining after the minutes have been taken off the float value:
    seconds_remaining = int(unconverted_time_float) - (minutes * 60) # e.g. int(64.987) = 64. then: 64 - (1*60) = 4 seconds remaining

    # print(seconds_remaining)

    # concatenate a seconds string:
    string_of_seconds = str(int(seconds_remaining))
    if seconds_remaining < 10:
        string_of_seconds =  "0" + string_of_seconds

    # print(string_of_seconds)

    # concatenate a milliseconds string (BUT DEPENDING ON THE LENGTH OF THE unconverted_time_float):
 # this means that the length of the unconverted_time_float can be like 2.1, 2.12 or 2.123
    if (seconds_remaining < 10 and len(str(unconverted_time_float)) == 3) or (seconds_remaining >= 10 and len(str(unconverted_time_float)) == 4):
        string_of_milliseconds = str(unconverted_time_float)[-1] + "00"

    if (seconds_remaining < 10 and len(str(unconverted_time_float)) == 4) or (seconds_remaining >= 10 and len(str(unconverted_time_float)) == 5):
        string_of_milliseconds = str(unconverted_time_float)[-2] + str(unconverted_time_float)[-1] + "0"

    if (seconds_remaining < 10 and len(str(unconverted_time_float)) == 5) or (seconds_remaining >= 10 and len(str(unconverted_time_float)) == 6):
        string_of_milliseconds = str(unconverted_time_float)[-3] + str(unconverted_time_float)[-2] + str(unconverted_time_float)[-1]

    # print(string_of_milliseconds)

    # concatenate the minutes, seconds and milliseconds strings together with the appropriate formatting
    print()
    print("seconds remaining:", seconds_remaining, "len(str(unconverted_time_float)):", len(str(unconverted_time_float)), "unconverted_time_float:", unconverted_time_float)
    print()
    try:
        string_of_formatted_time = string_of_minutes + ":"+ string_of_seconds + "." + string_of_milliseconds
    except:
        string_of_formatted_time = string_of_minutes + ":"+ string_of_seconds + "." + "000" # TEMPORARY FIX - LOOK AT SCREENSHOTS ON 10/08/25

    # print(string_of_milliseconds)

    # return this fully formatted time string
    return string_of_formatted_time


def return_difference_between_two_formatted_times_as_a_float(time1, time2):
    # time1 should be larger than time2, otherwise you will get a negative time. this is a validation check we need to perform:
    # convert both formatted times (minutes, seconds, milliseconds) into just seconds and milliseconds
    time_difference = convert_formatted_time_into_seconds_and_milliseconds(time1) - convert_formatted_time_into_seconds_and_milliseconds(time2)
    
    # (there was more code that was like if time1 > time2: ... else:) print("Negative time detected. Handling: returning a negative value; the program will continue to run without crashing.") # lol nah i actually wanted negative values in the end (for delta sector time calculations)

    return time_difference

def return_minimum_of_list(list):
    if len(list) == 0:
        return None

    # minimum = "99999" # arbitrarily high value (actually don't write this, because in rare cases this value may be exceeded)
    minimum = list[0]
    for i in range(len(list)):
        if list[i] < minimum:
            minimum = list[i]
    return minimum

def format_sector_delta_time(sector_delta_time):
    if sector_delta_time < 0:
        formatted_sector_delta_time = str(sector_delta_time)[:6]
    else:
        formatted_sector_delta_time = "+"+str(sector_delta_time)[:5]

    return formatted_sector_delta_time

def display_splash_screen():
    FPS = 60
    clock = pygame.time.Clock()

    font_size_175_lucidasans = pygame.font.SysFont("lucidasans", 175) # this is upscaled by 5 from 35 (i.e. 35 *5 = 175) so you need to downscale it by a scale factor of 0.2 later
    font_size_80_lucidasans = pygame.font.SysFont("lucidasans", 80) # "pygame.font.SysFont" instead of "pygame.font.Font" and now you don't need ".ttf"

    formula_1_text = font_size_80_lucidasans.render("Formula 1", True, (255, 255, 255)).convert_alpha()

    pixel_racing_text = font_size_80_lucidasans.render("Pixel Racing", True, (255, 255, 255)).convert_alpha()

    splash_screen_road_and_car_and_text_angle = 25

    upscaled_by_Daniyal_Amir_text = font_size_175_lucidasans.render("by Daniyal Amir", True, (255, 255, 255))
    rotated_upscaled_by_Daniyal_Amir_text = pygame.transform.rotate(upscaled_by_Daniyal_Amir_text, 90-splash_screen_road_and_car_and_text_angle)
    by_Daniyal_Amir_text_scale_factor = 0.2
    smooth_by_Daniyal_Amir_text = pygame.transform.smoothscale(rotated_upscaled_by_Daniyal_Amir_text, (int(rotated_upscaled_by_Daniyal_Amir_text.get_width() * by_Daniyal_Amir_text_scale_factor), int(rotated_upscaled_by_Daniyal_Amir_text.get_height() * by_Daniyal_Amir_text_scale_factor)))


    alpha_value = 0
    fading_in = True

    # ssrbci = splash screen redbull car image
    ssrbci = pygame.image.load("splash_screen_redbull_car_imagev3.png")
    ssrbci = pygame.transform.scale_by(ssrbci, 4.5)
    ssrbci = pygame.transform.rotate(ssrbci, -(splash_screen_road_and_car_and_text_angle))

    ssrbci_x_pos, ssrbci_y_pos = -445, 2500

    ssrbci_speed = 28

    ss_track = pygame.image.load("splash_screen_track.png")
    ss_track = pygame.transform.scale_by(ss_track, 3)
    ss_track = pygame.transform.rotate(ss_track, -(splash_screen_road_and_car_and_text_angle))

    # Create a channel for the eighth track
    # SPLASH SCREEN SEQUENCE ENGINE SOUNDS
    channel8 = pygame.mixer.Channel(7) 
    channel8.set_volume(1)
    channel8.play(pygame.mixer.Sound("splash screen audiov1.mp3"), fade_ms=5000)

    while True:
        dt = clock.tick(FPS) / 1000.0 # delta time calculates the amount of time has elapsed since the last frame, and returns that time in milliseconds. / 1000.0 then converts that time from milliseconds to seconds
        current_fps = clock.get_fps()
        pygame.display.set_caption(f'Formula 1 Pixel Racing by Daniyal Amir')
        screen.fill((0, 0, 0))

        formula_1_text.set_alpha(alpha_value)
        screen.blit(formula_1_text, (115, 280))

        pixel_racing_text.set_alpha(alpha_value)
        screen.blit(pixel_racing_text, (65, 370))

        screen.blit(ss_track, (250, -150))

        ssrbci_x_pos = ssrbci_x_pos + math.sin(math.radians(splash_screen_road_and_car_and_text_angle))*ssrbci_speed
        ssrbci_y_pos = ssrbci_y_pos - math.cos(math.radians(splash_screen_road_and_car_and_text_angle))*ssrbci_speed

        if fading_in:
            screen.blit(ssrbci, (ssrbci_x_pos, ssrbci_y_pos))
            alpha_value = alpha_value + 2

            if ssrbci_y_pos < 1100:
                ssrbci_speed = ssrbci_speed*0.971
                
            if ssrbci_speed < 0.1: # 0.1 not 0 because otherwise the 0.97 thingy will make it very slowly crawl at a very low speed still visible on screen. it's annoying when the car slowly crawls on screen at close to 0 mph but not 0 mph so just set a boundary where the speed just snaps to 0. the boundary here is set at 0.1 - when ssrbci_speed is less than 0.1, ssrbci_speed snaps to 0
                ssrbci_speed = 0

            if alpha_value > 890:
                ssrbci_speed = 0.1
                fading_in = False

        else:
            by_Daniyal_Amir_text_rect = smooth_by_Daniyal_Amir_text.get_rect(center=(788, 410))
            screen.blit(smooth_by_Daniyal_Amir_text, by_Daniyal_Amir_text_rect.topleft)

            screen.blit(ssrbci, (ssrbci_x_pos, ssrbci_y_pos))
            alpha_value = alpha_value - 3
            ssrbci_speed = ssrbci_speed*1.05

        if alpha_value < -400:
            break
        
        pygame.display.flip()





boolean_flag_run_once_after_click = False # bloody hell im a genius - this method worked first try and was implemented in the correct place in the correct way first try
new_FPS = 60
boolean_flag_max_FPS_button_slider_pressed_down = False # you're a genius again with this boolean flag! this boolean flag allows the slider to only be updated when the left click button is depressed, and stops updating the x position of the slider when the left click is released

class Button:
    def __init__ (self, current_button_colour, original_button_colour, button_x_pos, button_y_pos, button_width, button_height, text_on_button, text_on_button_x_pos_offset, button_name):
        # parameter is "incolour"
        # self.colour = incolour
        self.current_button_colour = current_button_colour
        self.original_button_colour = original_button_colour # initialised as the same as current_button_colour, but this original_button_colour attribute never changes once initialised
        # > this ensures we can return to the original button colour without having to manually state the colour. all you need to do is call self.current_button_colour = original_button_colour
        
        # Rect object, which also acts as an attribute for the button containing x, y, width, height
        # self.rect = pygame.Rect(x_pos, y_pos, width, height)
        self.button_x_pos = button_x_pos
        self.button_y_pos = button_y_pos
        self.button_width = button_width
        self.button_height = button_height

        self.text_on_button = text_on_button
        self.text_on_button_x_pos_offset = text_on_button_x_pos_offset
        self.button_name = button_name # serves as a unique identifier of the button other than its original variable name - storing the unique identifier as an ATTRIBUTE makes it a lot easier to access and operate on




    # draw ONE button (and then use a for loop later to draw all of them)
    def draw_button(self, screen):
        pygame.draw.rect(screen, self.current_button_colour, (self.button_x_pos, self.button_y_pos, self.button_width, self.button_height)) #  pygame.draw.rect(screen, (colour), (x, y, width, height))
        # print(self.current_button_colour)
        
    def draw_text_on_button(self, screen):
        font_size_30_lucidasans = pygame.font.SysFont("lucidasans", 30)
        text_on_button_object = font_size_30_lucidasans.render(self.text_on_button, True, (255, 255, 255))

        screen.blit(text_on_button_object, (self.button_x_pos+self.text_on_button_x_pos_offset, self.button_y_pos+3)) # +3 is done to all texts on buttons cuz all the text is slightly too high. +3 fixes this.

        
    def check_if_mouse_is_hovering(self, mousex, mousey):
        if (self.button_x_pos < mousex < self.button_x_pos + self.button_width) and (self.button_y_pos < mousey < self.button_y_pos + self.button_height):
            # if hovering, but not clicked down:
            if self.original_button_colour == (0, 255, 0):
                self.current_button_colour = (0, 200, 0)

            if self.original_button_colour == (255, 0, 0):
                self.current_button_colour = (200, 0, 0)

            if self.original_button_colour == (100, 100, 100):
                self.current_button_colour = (80, 80, 80)

            if self.original_button_colour == (200, 200, 200):
                self.current_button_colour = (0, 200, 0)

        else:
            # if not hovering nor clicked down:
            if self.original_button_colour == (0, 255, 0):
                self.current_button_colour = (0, 255, 0)

            if self.original_button_colour == (255, 0, 0):
                self.current_button_colour = (255, 0, 0)

            if self.original_button_colour == (100, 100, 100):
                self.current_button_colour = (100, 100, 100)

            if self.original_button_colour == (200, 200, 200):
                self.current_button_colour = (200, 200, 200)

    def check_if_mouse_clicked(self, mousex, mousey, event):
        global boolean_flag_run_once_after_click, about_screen_activated, settings_screen_activated, wasd_keys_activated, track_selection_screen_activated, team_selection_screen_activated, new_FPS, boolean_flag_max_FPS_button_slider_pressed_down, end_game_menu, artificially_activate_end_game_leaderboard, team_selection_array_pointer, team_selection_screen_teams_and_car_images_array, track_selection_array_pointer, track_selection_screen_array, leaderboard_scroll_start_index, merge_sorted_final_lap_times_list
        mouse_buttons_states = pygame.mouse.get_pressed()

        if (self.button_x_pos < mousex < self.button_x_pos + self.button_width) and (self.button_y_pos < mousey < self.button_y_pos + self.button_height):
            # if event.type == pygame.MOUSEBUTTONDOWN: # this runs for multiple frames
            if mouse_buttons_states[0]:
                # if hovering, and clicked down:
                if self.original_button_colour == (0, 255, 0):
                    self.current_button_colour = (0, 140, 0)

                if self.original_button_colour == (255, 0, 0):
                    self.current_button_colour = (140, 0, 0)

                if self.original_button_colour == (100, 100, 100):
                    self.current_button_colour = (65, 65, 65)

                if self.original_button_colour == (200, 200, 200):
                    self.current_button_colour = (0, 140, 0)

                boolean_flag_run_once_after_click = True
            if event.type == pygame.MOUSEBUTTONUP and boolean_flag_run_once_after_click: # this runs for one frame
                
                # MAIN MENU SCREEN:
                # PLAY BUTTON
                if self.button_name == "play_button":
                    track_selection_screen_activated = True

                # SETTINGS BUTTON AND CHILD BUTTONS
                if self.button_name == "settings_button":
                    settings_screen_activated = True
                if self.button_name == "settings_screen_close_button":
                    settings_screen_activated = False
                if self.button_name == "arrow_keys_setting_button":
                    wasd_keys_activated = False
                if self.button_name == "wasd_keys_setting_button":
                    wasd_keys_activated = True

                # ABOUT BUTTON AND CHILD BUTTONS
                if self.button_name == "about_button":
                    about_screen_activated = True
                if self.button_name == "about_screen_close_button":
                    about_screen_activated = False
                    
                # TRACK SELECTION SCREEN AND CHILD BUTTONS
                if self.button_name == "track_selection_screen_canada_button":
                    track_selection_screen_activated = False
                    team_selection_screen_activated = True
                if self.button_name == "track_selection_screen_back_button":
                    track_selection_screen_activated = False
                if self.button_name == "track_selection_screen_leftward_selection_arrow_button":
                    if track_selection_array_pointer > 0:
                        track_selection_array_pointer = track_selection_array_pointer - 1
                if self.button_name == "track_selection_screen_rightward_selection_arrow_button":
                    if track_selection_array_pointer < len(track_selection_screen_array) - 1:
                        track_selection_array_pointer = track_selection_array_pointer + 1


                # TEAM SELECTION SCREEN AND CHILD BUTTONS BUTTON
                if self.button_name == "team_selection_screen_back_button":
                    team_selection_screen_activated = False
                    track_selection_screen_activated = True
                if self.button_name == "team_selection_screen_race_button":
                    end_game_menu = True
                if self.button_name == "team_selection_screen_leftward_selection_arrow_button":
                    if team_selection_array_pointer > 0:
                        team_selection_array_pointer = team_selection_array_pointer - 1
                if self.button_name == "team_selection_screen_rightward_selection_arrow_button":
                    if team_selection_array_pointer < len(team_selection_screen_teams_and_car_images_array) - 1:
                        team_selection_array_pointer = team_selection_array_pointer + 1
            



                # END GAME LEADERBOARD SCREEN
                # END SCREEN LEADERBOARD SCROLL UP/DOWN BUTTONS
                if self.button_name == "end_game_screen_leaderboard_scroll_up_button":
                    if leaderboard_scroll_start_index > 0:
                        leaderboard_scroll_start_index = leaderboard_scroll_start_index - 1
                if self.button_name == "end_game_screen_leaderboard_scroll_down_button":
                    if leaderboard_scroll_start_index <= len(merge_sorted_final_lap_times_list)-8: # 8 because only 8 entries can fit on the leaderboard screen
                        leaderboard_scroll_start_index = leaderboard_scroll_start_index + 1
                # END SCREEN RESTART BUTTON
                if self.button_name == "end_game_screen_leaderboard_restart_button":
                    artificially_activate_end_game_leaderboard = False
                    restart_timed_lap_fade_in_and_out_and_lights_sequence()


                boolean_flag_run_once_after_click = False

class ButtonSlider(Button):
    def __init__(self, current_button_colour, original_button_colour, button_x_pos, button_y_pos, button_width, button_height, text_on_button, text_on_button_x_pos_offset, button_name, button_slider_circle_radius, lower_x_position_slider_limit, upper_x_position_slider_limit):
        Button.__init__(self, current_button_colour, original_button_colour, button_x_pos, button_y_pos, button_width, button_height, text_on_button, text_on_button_x_pos_offset, button_name)
        self.button_slider_circle_radius = button_slider_circle_radius
        self.lower_x_position_slider_limit = lower_x_position_slider_limit
        self.upper_x_position_slider_limit = upper_x_position_slider_limit

    # OVERRIDING PARENT CLASS draw_button() METHOD:
    def draw_button(self, screen):
        pygame.draw.circle(screen, self.current_button_colour, (self.button_x_pos+self.button_slider_circle_radius, self.button_y_pos+self.button_slider_circle_radius), self.button_slider_circle_radius) #  pygame.draw.rect(screen, (colour), (x, y, width, height))

    def check_if_mouse_clicked_for_button_slider(self, mousex, mousey, event):
        global boolean_flag_run_once_after_click, new_FPS, boolean_flag_max_FPS_button_slider_pressed_down
        mouse_buttons_states = pygame.mouse.get_pressed()

        if ((self.button_x_pos < mousex < self.button_x_pos + self.button_width) and (self.button_y_pos < mousey < self.button_y_pos + self.button_height)) or boolean_flag_max_FPS_button_slider_pressed_down:
            if self.button_name == "max_FPS_button_slider" and mouse_buttons_states[0]: # ChatGPT: Improving reading mouse clicking reliability: "In Pygame, handling continuous mouse clicks or holding down the mouse button can sometimes be more reliable by checking the mouse button state rather than relying solely on MOUSEBUTTONDOWN events, which only trigger once per click."
                boolean_flag_max_FPS_button_slider_pressed_down = True # this boolean flag must be placed inside this if statement like done here
                self.button_x_pos = mousex - self.button_slider_circle_radius # 20 = half the width of the max_FPS_button_slider (or just the radius if the slider is a circle (which it is))
                
                if self.button_x_pos < self.lower_x_position_slider_limit:
                    self.button_x_pos = self.lower_x_position_slider_limit
                if self.button_x_pos > self.upper_x_position_slider_limit:
                    self.button_x_pos = self.upper_x_position_slider_limit

                # 270 = x_pos of max_FPS_button_slider from edge of screen
                # # 490 = width of max_FPS_button_slider
                # # 120 = max FPS. i solved for 270 and 490 using simultaneous equations anyway lol
                new_FPS = (self.button_x_pos - 270)/(490/120) 
                new_FPS = int(new_FPS)
        

        if event.type == pygame.MOUSEBUTTONUP and boolean_flag_max_FPS_button_slider_pressed_down:
            boolean_flag_max_FPS_button_slider_pressed_down = False



# default (Red Bull) car if the start menu is skipped:
team_selection_screen_red_bull_car = pygame.image.load("redbull carv19 with no front wheelsv1.png").convert_alpha()

team_selection_screen_red_bull_car_scaled = pygame.transform.scale_by(team_selection_screen_red_bull_car, 3)

team_selection_screen_red_bull_car =  pygame.transform.scale_by(team_selection_screen_red_bull_car, 1) # UPDATE THIS VALUE


original_car_image = team_selection_screen_red_bull_car

carrect = original_car_image.get_rect()





team_selection_screen_mercedes_car = pygame.image.load("mercedes car with no front wheelsv6.png").convert_alpha()
original_car_image = team_selection_screen_mercedes_car


team_selection_screen_mercedes_car_scaled = pygame.image.load("mercedes car with no front wheelsv6.png").convert_alpha()
team_selection_screen_mercedes_car_scaled = pygame.transform.scale_by(team_selection_screen_mercedes_car, 2.41)


mercedes_rear_wing_drs_flap = pygame.image.load("mercedes rear wing drs flapv2.png").convert_alpha()

# team_selection_array_pointer = 0
team_selection_array_pointer = 1 # by default, this is set to Mercedes
team_selection_screen_teams_and_car_images_array = [("Oracle Red Bull Racing", team_selection_screen_red_bull_car, team_selection_screen_red_bull_car_scaled, 0, mercedes_rear_wing_drs_flap), ("Mercedes AMG Petronas F1 Team", team_selection_screen_mercedes_car, team_selection_screen_mercedes_car_scaled, -160, mercedes_rear_wing_drs_flap)] # (NAME OF TEAM, TEAM'S CAR IMAGE, TEAM'S NAME TEXT X POSITION OFFSET)


track_selection_array_pointer = 0
track_selection_screen_array = ["Canada", "Singapore"]
# Canada = index of 0
# Singapore = index of 1

def get_events_and_regulate_FPS():
    global event, keys, mousex, mousey, dt

    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            pygame.quit()

    # calculate delta time
    dt = clock.tick(FPS) / 1000.0  # dt in seconds

    current_fps = clock.get_fps()
    pygame.display.set_caption(f'Formula 1 Pixel Racing')

end_game_menu = False
about_screen_activated = False
settings_screen_activated = False
wasd_keys_activated = False
track_selection_screen_activated = False
team_selection_screen_activated = False
def display_start_menu():
    global FPS, clock, team_selection_array_pointer, team_selection_screen_teams_and_car_images_array, original_car_image, carrect

    FPS = 60
    clock = pygame.time.Clock()

    mousex = 0
    mousey = 0

    font_size_80_lucidasans = pygame.font.SysFont("lucidasans", 80)
    formula_1_text2 = font_size_80_lucidasans.render("Formula 1", True, (255, 255, 255))
    pixel_racing_text2 = font_size_80_lucidasans.render("Pixel Racing", True, (255, 255, 255))

    font_size_40_lucidasans = pygame.font.SysFont("lucidasans", 40)
    start_menu_by_Daniyal_Amir_text = font_size_40_lucidasans.render("by Daniyal Amir", True, (255, 255, 255))

    canada_track_main_straight_image = pygame.image.load("canada_track_main_straight.png").convert_alpha()
    canada_track_main_straight_image = pygame.transform.scale_by(canada_track_main_straight_image, 1.3)

    start_menu_red_bull_car_image = pygame.image.load("start_menu_red_bull_carv1.png").convert_alpha()
    start_menu_red_bull_car_image = pygame.transform.rotate(start_menu_red_bull_car_image, 90)

    start_menu_mercedes_car_image = pygame.image.load("start_menu_mercedes_carv1.png").convert_alpha()
    start_menu_mercedes_car_image = pygame.transform.rotate(start_menu_mercedes_car_image, 90)
    start_menu_mercedes_car_relative_additional_x_position = 0
    start_menu_mercedes_car_relative_additional_y_position = 0
    start_menu_rate_of_change_of_steering_of_mercedes_car = 0
    start_menu_overtake_started = False
    additional_boolean_flag_that_i_need_for_some_reason = False
    start_menu_mercedes_car_relative_additional_starting_x_position = 185
    start_menu_relative_speed_of_overtake = 0

    start_menu_red_bull_car_x_position = screen_size_x + 1000
    start_menu_red_bull_car_y_position = 340
    start_menu_red_bull_car_relative_additional_y_position = 0

    start_menu_car_direction_and_rate_of_steering = 0

    start_menu_cars_event = 0

    start_menu_buttons = []

    play_button = Button((0, 255, 0), (0, 255, 0), (screen_size_x//2)-200, 525, 400, 50, "PLAY", 165, "play_button")
    start_menu_buttons.append(play_button)

    settings_button = Button((0, 255, 0), (0, 255, 0), (screen_size_x//2)-200, 600, 400, 50, "SETTINGS", 135, "settings_button")
    start_menu_buttons.append(settings_button)

    about_button = Button((0, 255, 0), (0, 255, 0), (screen_size_x//2)-200, 675, 400, 50, "ABOUT", 155, "about_button")
    start_menu_buttons.append(about_button)

    about_screen_close_button = Button((255, 0, 0), (255, 0, 0), 925, 55, 50, 50, "X", 16, "about_screen_close_button")

    about_description_text = "This racing game project was developed for the A-Level OCR Computer Science NEA\n(Non-Examined Assessment) project for 2024-2025.\n\nDesigned for racing enthusiasts and strategists, this game was developed to simulate\nthe precision, strategy and speed that encompasses Formula 1 in the form of a simple\n2D pixel art racing game.\n\nThis game was built entirely with Pygame, without using any other libraries, including\nPython's math module. All custom mathematical algorithms, track graphics, user\ninterface (UI) elements, animations, telemetry and special visual effects were created\nby the sole developer.\n\nNote: the source code for Formula 1 Pixel Racing is not publicly available."
    about_description_lines = about_description_text.splitlines()  # splits the above text into individual lines marked at "\n"

    supporters_names_column_1_text = "- Hers(h) Singh\n- Alex Lipski\n- Yusuf Tufal"
    supporters_names_column_1_lines = supporters_names_column_1_text.splitlines()  # splits the above text into individual lines marked at "\n"

    supporters_names_column_2_text = "- Anant Sahay\n- Jia Zi Chen\n- Charlie Loman"
    supporters_names_column_2_lines = supporters_names_column_2_text.splitlines()  # splits the above text into individual lines marked at "\n"

    supporters_names_column_3_text = "- Jamie Knights\n- Teni Funsho\n- William Poxon"
    supporters_names_column_3_lines = supporters_names_column_3_text.splitlines()  # splits the above text into individual lines marked at "\n"

    supporters_names_column_4_text = "- Nifemi Femi-Sanni\n- Tobi Ayodele\n- Ethan Hossain"
    supporters_names_column_4_lines = supporters_names_column_4_text.splitlines()  # splits the above text into individual lines marked at "\n"

    settings_screen_buttons = []
    settings_screen_close_button = Button((255, 0, 0), (255, 0, 0), 925, 55, 50, 50, "X", 16, "settings_screen_close_button")
    settings_screen_buttons.append(settings_screen_close_button)

    arrow_keys_setting_button = Button((100, 100, 100), (100, 100, 100), 140, 175, 192, 130, "", 0, "arrow_keys_setting_button")
    settings_screen_buttons.append(arrow_keys_setting_button)

    wasd_keys_setting_button = Button((100, 100, 100), (100, 100, 100), 350, 175, 192, 130, "", 0, "wasd_keys_setting_button")
    settings_screen_buttons.append(wasd_keys_setting_button)

    arrow_keys_setting_image = pygame.image.load("arrow_keys_setting.png").convert_alpha()
    arrow_keys_setting_image = pygame.transform.scale(arrow_keys_setting_image, (192, 140))

    wasd_keys_setting_image = pygame.image.load("wasd_keys_setting.png").convert_alpha()
    wasd_keys_setting_image = pygame.transform.scale(wasd_keys_setting_image, (192, 140))

    max_FPS_button_slider = ButtonSlider((100, 100, 100), (100, 100, 100), 515, 390, 40, 40, "", 0, "max_FPS_button_slider", 20, 270, 760) # 20 is the radius - this is HALF of the old rectangle's height/width (40/40)
    settings_screen_buttons.append(max_FPS_button_slider)



    track_selection_screen_buttons = []
    track_selection_screen_canada_button =  Button((200, 200, 200), (200, 200, 200), (screen_size_x//2)-200, 175, 400, 500, "", 0, "track_selection_screen_canada_button")
    track_selection_screen_buttons.append(track_selection_screen_canada_button)


    # ----------CANADA IMAGES----------
    canada_flag_image = pygame.image.load("canada_flag_pixel_art.png").convert_alpha()
    canada_flag_image = pygame.transform.scale_by(canada_flag_image, 0.1)

    canada_track_outline_image = pygame.image.load("canada_track_outline.png").convert_alpha()
    canada_track_outline_image = pygame.transform.scale_by(canada_track_outline_image, 0.35)



    # ----------SINGAPORE IMAGES----------
    singapore_flag_image = pygame.image.load("singapore_flag_pixel_art.png").convert_alpha()
    singapore_flag_image = pygame.transform.scale_by(singapore_flag_image, 0.1)

    singapore_track_outline_image = pygame.image.load("singapore_track_outline.png").convert_alpha()
    singapore_track_outline_image = pygame.transform.scale(singapore_track_outline_image, (336, 189)) # 336x189


    # ----------TEAM SELECTION SCREEN BUTTONS----------
    leftward_selection_arrow_image_for_track_selection_screen = pygame.image.load("selection_arrow.png").convert_alpha()
    leftward_selection_arrow_image_for_track_selection_screen = pygame.transform.scale_by(leftward_selection_arrow_image_for_track_selection_screen, 0.75)
    leftward_selection_arrow_image_for_track_selection_screen = pygame.transform.rotate(leftward_selection_arrow_image_for_track_selection_screen, 180)

    rightward_selection_arrow_image_for_track_selection_screen = pygame.image.load("selection_arrow.png").convert_alpha()
    rightward_selection_arrow_image_for_track_selection_screen = pygame.transform.scale_by(rightward_selection_arrow_image_for_track_selection_screen, 0.75)


    track_selection_screen_leftward_selection_arrow_button =  Button((100, 100, 100), (100, 100, 100), 190, 385, 49, 100, "", 0, "track_selection_screen_leftward_selection_arrow_button")
    track_selection_screen_buttons.append(track_selection_screen_leftward_selection_arrow_button)

    track_selection_screen_rightward_selection_arrow_button =  Button((100, 100, 100), (100, 100, 100), 850, 385, 49, 100, "", 0, "track_selection_screen_rightward_selection_arrow_button")
    track_selection_screen_buttons.append(track_selection_screen_rightward_selection_arrow_button)


    track_selection_screen_back_button =  Button((255, 0, 0), (255, 0, 0), 105, 55, 150, 50, "< BACK", 14, "track_selection_screen_back_button")
    track_selection_screen_buttons.append(track_selection_screen_back_button)






    # ----------TEAM SELECTION SCREEN BUTTONS----------
    team_selection_screen_buttons = []
    team_selection_screen_leftward_selection_arrow_button =  Button((100, 100, 100), (100, 100, 100), 190, 385, 49, 100, "", 0, "team_selection_screen_leftward_selection_arrow_button")
    team_selection_screen_buttons.append(team_selection_screen_leftward_selection_arrow_button)

    team_selection_screen_rightward_selection_arrow_button =  Button((100, 100, 100), (100, 100, 100), 850, 385, 49, 100, "", 0, "team_selection_screen_rightward_selection_arrow_button")
    team_selection_screen_buttons.append(team_selection_screen_rightward_selection_arrow_button)
    
    team_selection_screen_race_button =  Button((0, 255, 0), (0, 255, 0), 800, 705, 175, 50, "RACE >>>", 10, "team_selection_screen_race_button")
    team_selection_screen_buttons.append(team_selection_screen_race_button)

    leftward_selection_arrow_image_for_team_selection_screen = pygame.image.load("selection_arrow.png").convert_alpha()
    leftward_selection_arrow_image_for_team_selection_screen = pygame.transform.scale_by(leftward_selection_arrow_image_for_team_selection_screen, 0.75)
    leftward_selection_arrow_image_for_team_selection_screen = pygame.transform.rotate(leftward_selection_arrow_image_for_team_selection_screen, 180)

    rightward_selection_arrow_image_for_team_selection_screen = pygame.image.load("selection_arrow.png").convert_alpha()
    rightward_selection_arrow_image_for_team_selection_screen = pygame.transform.scale_by(rightward_selection_arrow_image_for_team_selection_screen, 0.75)

    team_selection_screen_back_button =  Button((255, 0, 0), (255, 0, 0), 105, 55, 150, 50, "< BACK", 14, "team_selection_screen_back_button")
    team_selection_screen_buttons.append(team_selection_screen_back_button)

    while not end_game_menu:
        screen.fill((0, 0, 0))

        get_events_and_regulate_FPS()

        mousex, mousey = pygame.mouse.get_pos()

        for i in range(len(start_menu_buttons)):
            start_menu_buttons[i].draw_button(screen)
            start_menu_buttons[i].check_if_mouse_is_hovering(mousex, mousey)
            start_menu_buttons[i].draw_text_on_button(screen)
        
        if about_screen_activated or settings_screen_activated or track_selection_screen_activated or team_selection_screen_activated:
            pass
        else:
            for i in range(len(start_menu_buttons)):
                start_menu_buttons[i].check_if_mouse_clicked(mousex, mousey, event)




        start_menu_red_bull_car_x_position = start_menu_red_bull_car_x_position - 15



        if start_menu_red_bull_car_x_position < -500:
            start_menu_red_bull_car_x_position = screen_size_x + random.randint(500, 2000)
            start_menu_red_bull_car_y_position = int(random.normalvariate(377.5, 10)) # normalvariate() takes the mean and standard deviation as its two parameters: mean = (328-427)/2 = 377.5, standard deviation = 15 (arbitrary number) 
            # start_menu_red_bull_car_relative_additional_y_position = 0
            start_menu_car_direction_and_rate_of_steering = random.uniform(-1, 1)
            start_menu_mercedes_car_relative_additional_x_position = 0
            start_menu_mercedes_car_relative_additional_y_position = 0
            start_menu_rate_of_change_of_steering_of_mercedes_car = 0
            start_menu_overtake_started = False
            additional_boolean_flag_that_i_need_for_some_reason = False
            start_menu_cars_event = random.randint(0, 1)
            start_menu_mercedes_car_relative_additional_starting_x_position = 175 + random.randint(-10, 10)
            start_menu_relative_speed_of_overtake = random.uniform(1, 2)
            start_menu_steering_speed_of_overtake = start_menu_relative_speed_of_overtake/24


            # print("NEW:", start_menu_red_bull_car_y_position, start_menu_car_direction_and_rate_of_steering)

        # print(start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position)
        if start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position < 333:
            start_menu_car_direction_and_rate_of_steering = 0
            start_menu_red_bull_car_y_position = start_menu_red_bull_car_y_position

        if start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position > 422:
            start_menu_car_direction_and_rate_of_steering = 0
            start_menu_red_bull_car_y_position = start_menu_red_bull_car_y_position

        if 0 <= start_menu_red_bull_car_x_position <= screen_size_x:
            start_menu_red_bull_car_relative_additional_y_position = start_menu_red_bull_car_relative_additional_y_position + start_menu_car_direction_and_rate_of_steering


        formula_1_text2_rect = formula_1_text2.get_rect()
        formula_1_text2_rect.center = (screen_size_x//2, 65)
        screen.blit(formula_1_text2, formula_1_text2_rect)

        pixel_racing_text2_rect = pixel_racing_text2.get_rect()
        pixel_racing_text2_rect.center = (screen_size_x//2, 160)
        screen.blit(pixel_racing_text2, pixel_racing_text2_rect)


        start_menu_by_Daniyal_Amir_text_rect = start_menu_by_Daniyal_Amir_text.get_rect()
        start_menu_by_Daniyal_Amir_text_rect.center = (screen_size_x/2, 240)
        screen.blit(start_menu_by_Daniyal_Amir_text, start_menu_by_Daniyal_Amir_text_rect)

        screen.blit(canada_track_main_straight_image, (-80, 310))
        screen.blit(start_menu_red_bull_car_image, (start_menu_red_bull_car_x_position, start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position)) # 328-427

        if start_menu_cars_event == 1:
            start_menu_mercedes_car_relative_additional_x_position = start_menu_mercedes_car_relative_additional_x_position - start_menu_relative_speed_of_overtake
            screen.blit(start_menu_mercedes_car_image, (start_menu_red_bull_car_x_position+start_menu_mercedes_car_relative_additional_starting_x_position+start_menu_mercedes_car_relative_additional_x_position, start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position+start_menu_mercedes_car_relative_additional_y_position)) # 328-427)


            if start_menu_mercedes_car_relative_additional_x_position+start_menu_mercedes_car_relative_additional_starting_x_position < 125 and not start_menu_overtake_started and not additional_boolean_flag_that_i_need_for_some_reason:
                start_menu_overtake_started = True


            if start_menu_rate_of_change_of_steering_of_mercedes_car <= 1.75 and start_menu_overtake_started:
                start_menu_rate_of_change_of_steering_of_mercedes_car = start_menu_rate_of_change_of_steering_of_mercedes_car + start_menu_steering_speed_of_overtake
                if start_menu_rate_of_change_of_steering_of_mercedes_car >= 1.75:
                    start_menu_overtake_started = False
                    additional_boolean_flag_that_i_need_for_some_reason = True
                
            if start_menu_rate_of_change_of_steering_of_mercedes_car > 0 and not start_menu_overtake_started:
                start_menu_rate_of_change_of_steering_of_mercedes_car = start_menu_rate_of_change_of_steering_of_mercedes_car - start_menu_steering_speed_of_overtake
                if start_menu_rate_of_change_of_steering_of_mercedes_car <= 0:
                    start_menu_rate_of_change_of_steering_of_mercedes_car = 0


            # print(start_menu_rate_of_change_of_steering_of_mercedes_car)

            if start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position > 377.5:
                start_menu_mercedes_car_relative_additional_y_position = start_menu_mercedes_car_relative_additional_y_position - start_menu_rate_of_change_of_steering_of_mercedes_car

            if start_menu_red_bull_car_y_position+start_menu_red_bull_car_relative_additional_y_position < 377.5:
                start_menu_mercedes_car_relative_additional_y_position = start_menu_mercedes_car_relative_additional_y_position + start_menu_rate_of_change_of_steering_of_mercedes_car




        if about_screen_activated:
            pygame.draw.rect(screen, (255, 255, 255), (100, 50, 880, 710)) # white background square
            pygame.draw.rect(screen, (50, 50, 50), (105, 55, 870, 700)) # grey foreground square

            pygame.draw.rect(screen, (255, 255, 255), (100, 105, 880, 5)) # white border line

            about_text = font_size_40.render("ABOUT", True, (255, 255, 255))
            screen.blit(about_text, (470, 63))

            about_description_1 = font_size_37_italics.render("Formula 1 Pixel Racing", True, (255, 255, 255))
            screen.blit(about_description_1, (116, 120))

            about_description_2 = font_size_25.render("is a pure Pygame-based development project", True, (255, 255, 255))
            screen.blit(about_description_2, (407, 120))

            about_description_3 = font_size_25.render("made in raw Python.", True, (255, 255, 255))
            screen.blit(about_description_3, (265, 150))

            about_description_4 = font_size_25.render("Created by Daniyal Amir.", True, (20, 255, 150))
            screen.blit(about_description_4, (515, 150))

            pygame.draw.rect(screen, (255, 255, 255), (100, 540, 880, 5)) # white border line

            special_thanks_to_my_supporters_text = font_size_30.render("Special Thanks to My Supporters", True, (255, 255, 255))
            screen.blit(special_thanks_to_my_supporters_text, (293, 560))

            for i in range(len(about_description_lines)):
                about_description_line = font_size_20.render(about_description_lines[i], True, (255, 255, 255))
                screen.blit(about_description_line, (115, 205 + (i*25)))
        
            for i in range(len(supporters_names_column_1_lines)):
                supporters_names_column_1_line = font_size_20.render(supporters_names_column_1_lines[i], True, (255, 255, 255))
                screen.blit(supporters_names_column_1_line, (115, 610 + (i*30)))

            for i in range(len(supporters_names_column_2_lines)):
                supporters_names_column_2_line = font_size_20.render(supporters_names_column_2_lines[i], True, (255, 255, 255))
                screen.blit(supporters_names_column_2_line, (325, 610 + (i*30)))

            for i in range(len(supporters_names_column_3_lines)):
                supporters_names_column_3_line = font_size_20.render(supporters_names_column_3_lines[i], True, (255, 255, 255))
                screen.blit(supporters_names_column_3_line, (535, 610 + (i*30)))

            for i in range(len(supporters_names_column_4_lines)):
                supporters_names_column_4_line = font_size_20.render(supporters_names_column_4_lines[i], True, (255, 255, 255))
                screen.blit(supporters_names_column_4_line, (745, 610 + (i*30)))

            about_screen_close_button.draw_button(screen)
            about_screen_close_button.check_if_mouse_is_hovering(mousex, mousey)
            about_screen_close_button.check_if_mouse_clicked(mousex, mousey, event)
            about_screen_close_button.draw_text_on_button(screen)

            pygame.draw.rect(screen, (255, 255, 255), (100, screen_size_y-92, 880, 5)) # white border line

            last_updated_text = font_size_20.render("This game was last updated on 04/05/25.", True, (200, 200, 200))
            screen.blit(last_updated_text, (333, screen_size_y-80))


        if settings_screen_activated:
            pygame.draw.rect(screen, (255, 255, 255), (100, 50, 880, 710)) # white background square
            pygame.draw.rect(screen, (50, 50, 50), (105, 55, 870, 700)) # grey foreground square

            pygame.draw.rect(screen, (255, 255, 255), (100, 105, 880, 5)) # white border line

            about_text = font_size_40.render("SETTINGS", True, (255, 255, 255))
            screen.blit(about_text, (450, 63))

            controls_text = font_size_25.render("CONTROLS:", True, (255, 255, 255))
            screen.blit(controls_text, (115, 120))

            arrows_text = font_size_20.render("ARROWS", True, (255, 255, 255))
            screen.blit(arrows_text, (190, 312))

            wasd_text = font_size_20.render("WASD", True, (255, 255, 255))
            screen.blit(wasd_text, (416, 312))

            selected_text = font_size_20.render("Selected!", True, (0, 255, 0))
            if not wasd_keys_activated:
                screen.blit(selected_text, (191, 153))
            else:
                screen.blit(selected_text, (402, 153))

            # MAX FPS SLIDER
            pygame.draw.rect(screen, (255, 255, 255), (290, 400, 490, 20))

            for i in range(len(settings_screen_buttons)):
                settings_screen_buttons[i].draw_button(screen)
                settings_screen_buttons[i].check_if_mouse_is_hovering(mousex, mousey)
                settings_screen_buttons[i].check_if_mouse_clicked(mousex, mousey, event)
                settings_screen_buttons[i].draw_text_on_button(screen)

            max_FPS_button_slider.check_if_mouse_clicked_for_button_slider(mousex, mousey, event)

            screen.blit(arrow_keys_setting_image, (140, 170))

            screen.blit(wasd_keys_setting_image, (350, 170))

            max_FPS_text = font_size_25.render("SET MAXIMUM FPS:", True, (255, 255, 255))
            screen.blit(max_FPS_text, (115, 360))

            new_FPS_text = font_size_25.render("FPS: "+ str(new_FPS), True, (255, 255, 255))
            screen.blit(new_FPS_text, (490, 450))


        if track_selection_screen_activated:
            pygame.draw.rect(screen, (255, 255, 255), (100, 50, 880, 710)) # white background square
            pygame.draw.rect(screen, (50, 50, 50), (105, 55, 870, 700)) # grey foreground square
 
            pygame.draw.rect(screen, (255, 255, 255), (100, 105, 880, 5)) # white border line

            track_selection_text = font_size_40.render("TRACK SELECTION", True, (255, 255, 255))
            screen.blit(track_selection_text, (345, 63))

            for i in range(len(track_selection_screen_buttons)):
                track_selection_screen_buttons[i].draw_button(screen)
                track_selection_screen_buttons[i].check_if_mouse_is_hovering(mousex, mousey)
                track_selection_screen_buttons[i].check_if_mouse_clicked(mousex, mousey, event)
                track_selection_screen_buttons[i].draw_text_on_button(screen)

            pygame.draw.rect(screen, (20, 20, 20), ((screen_size_x//2)-190, 185, 380, 480))


            if track_selection_array_pointer == 0: # i.e. when the pointer is pointing at Canada
                screen.blit(canada_track_outline_image, (370, 192))

                canada_text = font_size_40.render("Canada", True, (255, 255, 255))
                screen.blit(canada_text, (360, 415))

                montreal_text = font_size_20.render("Montreal", True, (255, 255, 255))
                screen.blit(montreal_text, (362, 460))

                screen.blit(canada_flag_image, (595, 415))

                circuit_name_text = font_size_20.render("Circuit Gilles-Villeneuve", True, (255, 255, 255))
                screen.blit(circuit_name_text, (360, 500))

                lap_record_text = font_size_20.render("LAP RECORD: 01:03.050 - Daniyal", True, (255, 255, 255))
                screen.blit(lap_record_text, (360, 545))

                circuit_length_text = font_size_20.render("CIRCUIT LENGTH: 4.361 km", True, (255, 255, 255))
                screen.blit(circuit_length_text, (360, 575))

                number_of_turns_text = font_size_20.render("TURNS: 14", True, (255, 255, 255))
                screen.blit(number_of_turns_text, (360, 605))

            if track_selection_array_pointer == 1:
                screen.blit(singapore_track_outline_image, (370, 192))

                canada_text = font_size_40.render("Singapore", True, (255, 255, 255))
                screen.blit(canada_text, (360, 415))

                montreal_text = font_size_20.render("Marina Bay", True, (255, 255, 255))
                screen.blit(montreal_text, (360, 460))

                screen.blit(singapore_flag_image, (595, 415))

                circuit_name_text = font_size_20.render("Marina Bay Street Circuit", True, (255, 255, 255))
                screen.blit(circuit_name_text, (360, 500))

                lap_record_text = font_size_20.render("LAP RECORD: [LAP TIME] - [NAME]", True, (255, 255, 255))
                screen.blit(lap_record_text, (360, 545))

                circuit_length_text = font_size_20.render("CIRCUIT LENGTH: 5.063 km", True, (255, 255, 255))
                screen.blit(circuit_length_text, (360, 575))

                number_of_turns_text = font_size_20.render("TURNS: 19", True, (255, 255, 255))
                screen.blit(number_of_turns_text, (360, 605))


            screen.blit(rightward_selection_arrow_image_for_track_selection_screen, (850, 390))
            screen.blit(leftward_selection_arrow_image_for_track_selection_screen, (190, 390))

        if team_selection_screen_activated:
            pygame.draw.rect(screen, (255, 255, 255), (100, 50, 880, 710)) # white background square
            pygame.draw.rect(screen, (50, 50, 50), (105, 55, 870, 700)) # grey foreground square

            pygame.draw.rect(screen, (255, 255, 255), (100, 105, 880, 5)) # white border line

            team_selection_text = font_size_40.render("TEAM SELECTION", True, (255, 255, 255))
            screen.blit(team_selection_text, (360, 63))

            for i in range(len(team_selection_screen_buttons)):
                team_selection_screen_buttons[i].draw_button(screen)
                team_selection_screen_buttons[i].check_if_mouse_is_hovering(mousex, mousey)
                team_selection_screen_buttons[i].check_if_mouse_clicked(mousex, mousey, event)
                team_selection_screen_buttons[i].draw_text_on_button(screen)

            screen.blit(rightward_selection_arrow_image_for_team_selection_screen, (850, 390))
            screen.blit(leftward_selection_arrow_image_for_team_selection_screen, (190, 390))

            team_currently_selected_text = font_size_40.render(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][0], True, (255, 255, 255)) # render the team name on screen

            team_currently_selected_text_rect = team_currently_selected_text.get_rect()
            team_currently_selected_text_rect.center = (screen_size_x//2, 630)

            screen.blit(team_currently_selected_text, team_currently_selected_text_rect)


            screen.blit(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][2], (480, 300)) # render the team car image on screen
            pygame.draw.rect(screen, (0, 0, 0), (482, 348, 21, 39)) # team selection screen left wheel # it's 21x39 cuz that's it's scaled up by 3 (from the scaling you did for these team selection screen car images) from 7x13
            pygame.draw.rect(screen, (0, 0, 0), (580, 348, 21, 39)) # team selection screen right wheel # it's 21x39 cuz that's it's scaled up by 3 (from the scaling you did for these team selection screen car images) from 7x13

            # override the default (Red Bull) car with the newly chosen car
            original_car_image = team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][1]
            carrect = original_car_image.get_rect()


        pygame.display.flip()

# ADVANCED MAP RENDERING AND ABSTRACTION
# 1 represents the tiles which should be rotating
# the filename of an image corresponds to the inverse of their index. e.g. middle is bitmap[2][1] but the filename for that is 12.png

# NORMAL PYTHON BITMAP INDEXES WERE USED: [y][x] now - NOT [x][y]
# grid = [[0]*24]*10
# grid = [[0]*j]*i # WHAT THE FUCK I DON'T THINK THIS WORKS?????
# > yeah it doesn't cuz of "In this method, each row will be referencing the same column. This means, even if we update only one element of the array, it will update the same column in our array."
        

i_value = 12
j_value = 41

track_images = [[0 for i in range(j_value)]for j in range(i_value)] # list comprehension

# DISABLE EXTRA STUFF:
disable_splash_screen_sequence = False
disable_start_menu = False
disable_extra_loading_sequence = False

def load_game():
    global image_to_be_blitted, dt, FPS, clock, i_value, j_value, square_length_of_each_tile, DP_x_component, DP_y_component, DP_diagonal_x_component, DP_diagonal_y_component, disable_extra_loading_sequence

    """
    When rendering in a new map, you need to:
    - Update half_length_of_each_tile
    - Update the datum point coordinate (set both i_value and j_value to be 3 so it's easier to find)
    - Update the track_images bitmap
    - Update i_value and j_value
    - Update the starting_position and restart_timed_lap() position
    - Update image_to_be_blitted[y][x] in restart_timed_lap()
    - Update image_to_be_blitted[y][x] in load_game()? - i dont think you need to do this?
    """

    FPS = 120
    clock = pygame.time.Clock()

    # TEMPORARILY CHANGING BOTH i_value AND j_value to 3 so it's a 3x3 grid so we can easily find the new datum point when rendering in the new map
    # i_value = 3
    # j_value = 3

    # DATUM POINT (DP) COORDINATE COMPONENTS AND THEIR RESPECTIVE DIAGONALS
    # 1800x1800:
    # DP_x_component = 990 # this is always a higher value than its diagonal counterpart
    # DP_y_component = 855 # this is always a higher value than its diagonal counterpart

    # 1720x1720
    # DP_x_component = 970 # this is always a higher value than its diagonal counterpart
    # DP_y_component = 838 # this is always a higher value than its diagonal counterpart

    # 1600x1600
    DP_x_component = 938 # this is always a higher value than its diagonal counterpart
    DP_y_component = 804 # this is always a higher value than its diagonal counterpart

    DP_diagonal_x_component = DP_x_component - (square_length_of_each_tile/2)
    DP_diagonal_y_component = DP_y_component - (square_length_of_each_tile/2)


    loading_bar_width = 500
    loading_bar_height = 10

    total_assets = i_value*j_value
    loaded_assets = 0

    disable_loading_bar = False

    random_tyre = random.randint(1,5)

    if random_tyre == 1:
        original_loading_wheel_image = pygame.image.load("loading_wheel_soft_tyrev1.png").convert_alpha()
    if random_tyre == 2:
        original_loading_wheel_image = pygame.image.load("loading_wheel_medium_tyrev5.png").convert_alpha()
    if random_tyre == 3:
        original_loading_wheel_image = pygame.image.load("loading_wheel_hard_tyrev1.png").convert_alpha()
    if random_tyre == 4:
        original_loading_wheel_image = pygame.image.load("loading_wheel_wet_tyrev1.png").convert_alpha()
    if random_tyre == 5:
        original_loading_wheel_image = pygame.image.load("loading_wheel_intermediate_tyrev1.png").convert_alpha()


    
    original_loading_wheel_image = pygame.transform.scale(original_loading_wheel_image, (75, 75))
    loading_wheel_angle = 0
    loading_wheel_speed = 420

    burnout_start = False
    rollback_completed = False
    max_burnout_speed_reached = False

    # 15 is excluded; it only goes up to 14 but still 15 distinct indexes
    # 37 is excluded; it only goes up to 36 but still 37 distinct indexes

    print("Loading...")

    for i in range(i_value):
        for j in range(j_value):
            # print("i,j:", i,j)
            # print("track_images[i][j]:", track_images[i][j])
            track_images[i][j] = pygame.image.load("canada_splitv15\\" + str(i) + "-" + str(j) + ".png").convert() # \ needs to be \\ for file directory paths
            # track_images[i][j] = track_images[i][j].convert(16) # you may not wanna do this actually cuz it'll just take longer to load the game with this extra process, I think? or does it increase FPS whilst displaying the image in-game?
            track_images[i][j] = pygame.transform.scale(track_images[i][j], (square_length_of_each_tile, square_length_of_each_tile)).convert() # (70x70) for red border boxes then (140x140) for the actual images. then it gets upscaled by 10 to (1400x1400)
            # pygame.transform.smoothscale


            if not disable_loading_bar:
                screen.fill((0, 0, 0))

                dt = clock.tick(FPS) / 1000.0 # delta time calculates the amount of time has elapsed since the last frame, and returns that time in milliseconds. / 1000.0 then converts that time from milliseconds to seconds
                current_fps = clock.get_fps()
                pygame.display.set_caption(f'Formula 1 Pixel Racing')


                loaded_assets = loaded_assets + 1
                progress = loaded_assets/total_assets

                pygame.draw.rect(screen, (255, 255, 255), ((screen_size_x-loading_bar_width)/2, (screen_size_y-loading_bar_height)/2, loading_bar_width, loading_bar_height))

                pygame.draw.rect(screen, (0, 255, 0), ((screen_size_x-loading_bar_width)/2, (screen_size_y-loading_bar_height)/2, progress*loading_bar_width, loading_bar_height))

                if loading_wheel_angle < -360:
                    loading_wheel_angle = 0

                loading_wheel_angle = loading_wheel_angle - loading_wheel_speed*dt



                # ChatGPT: The size of the image after rotation changes: When an image is rotated, its bounding box expands to fit the rotated version. So the image may keep changing size, causing it to look strange.
                # ChatGPT: You should always rotate the original image, and label the variables as such.
                rotated_loading_wheel_image = pygame.transform.rotate(original_loading_wheel_image, loading_wheel_angle)

                # To ensure that the image stays centered in the desired position on the screen, you get a new rectangle that describes the rotated image: .get_rect().
                # Get the new rect and center it at the desired position. The 'center' is not the pivot point. It literally defines the center, where the center then IS the pivot point. Alt explanation: You can change the center point to move the entire image and its rotation, because the center defined here IS ALSO the pivot point.
                rotated_loading_wheel_rect = rotated_loading_wheel_image.get_rect(center=(screen_size_x-75, screen_size_y-75))

                # .topleft is used to retrieve the coordinates of the top-left corner of the rectangle, which is where you need to blit the rotated image on the screen. TLDR: .topleft returns the top left coordinates of the rectangle for blitting. TLDR: .topleft is for blitting.
                screen.blit(rotated_loading_wheel_image, rotated_loading_wheel_rect.topleft)

                pygame.display.flip() # YOU FORGOT TO UPDATE THE SCREEN BEFORE - YOU MUST INCLUDE pygame.display.flip()!


                # and (-210 < angle_until_exactly_upright < -150)


                if loaded_assets == total_assets:
                    print("Loading complete!")
                    angle_until_exactly_upright = 360 + loading_wheel_angle
                    deceleration_of_loading_wheel = loading_wheel_speed/angle_until_exactly_upright

                    # print(loading_wheel_angle, loading_wheel_speed, angle_until_exactly_upright, "GRADIENT:", deceleration_of_loading_wheel)

                if not disable_extra_loading_sequence:
                    loading_complete_text = font_size_30.render("Loading complete!", True, (255, 255, 255))
                    while loaded_assets == total_assets:
                        screen.fill((0, 0, 0))
                        screen.blit(loading_complete_text, (15, screen_size_y - 40))


                        dt = clock.tick(FPS) / 1000.0 # delta time calculates the amount of time has elapsed since the last frame, and returns that time in milliseconds. / 1000.0 then converts that time from milliseconds to seconds
                        current_fps = clock.get_fps()
                        pygame.display.set_caption(f'Formula 1 Pixel Racing')

                        angle_until_exactly_upright = 360 + loading_wheel_angle # YOU HAVE TO KEEP THIS LINE IN - idk why tho i sorta fluked it - see F1 schematics on 12/10/24


                        # print(loading_wheel_angle, loading_wheel_speed)
                        loading_wheel_angle = loading_wheel_angle - loading_wheel_speed*dt


                        loading_wheel_speed = angle_until_exactly_upright*(deceleration_of_loading_wheel) # calculates a variable acceleration in real time to ENSURE the loading_wheel_angle reaches 0 regardless of burnout_speed and/or angle_until_exactly_upright

                        if loading_wheel_speed < 1.5:
                            loading_wheel_speed = 0
                            loading_wheel_angle = 0.01
                            burnout_start = True
                            break

                        rotated_loading_wheel_image = pygame.transform.rotate(original_loading_wheel_image, loading_wheel_angle)
                        rotated_loading_wheel_rect = rotated_loading_wheel_image.get_rect(center=(screen_size_x-75, screen_size_y-75))
                        screen.blit(rotated_loading_wheel_image, rotated_loading_wheel_rect.topleft)
                        pygame.display.flip()


                    while burnout_start:
                        screen.fill((0, 0, 0))
                        screen.blit(loading_complete_text, (15, screen_size_y - 40))

                        dt = clock.tick(FPS) / 1000.0 # delta time calculates the amount of time has elapsed since the last frame, and returns that time in milliseconds. / 1000.0 then converts that time from milliseconds to seconds
                        current_fps = clock.get_fps()
                        pygame.display.set_caption(f'Formula 1 Pixel Racing')

                        loading_wheel_angle = loading_wheel_angle - loading_wheel_speed*dt

                        if loading_wheel_angle < -360:
                            loading_wheel_angle = 0




                        if not rollback_completed:
                            loading_wheel_speed = loading_wheel_speed - 10

                            if loading_wheel_speed < -130:
                                rollback_completed = True

                        rotated_loading_wheel_image = pygame.transform.rotate(original_loading_wheel_image, loading_wheel_angle)
                        rotated_loading_wheel_rect = rotated_loading_wheel_image.get_rect(center=(screen_size_x-75, screen_size_y-75))
                        screen.blit(rotated_loading_wheel_image, rotated_loading_wheel_rect.topleft)
                        pygame.display.flip()



                        if rollback_completed:
                            if not max_burnout_speed_reached:
                                loading_wheel_speed = loading_wheel_speed + 30
                                # print("LOOOL")
                                # print("LWA:", loading_wheel_angle, "LWS:", loading_wheel_speed, "AUEU:", angle_until_exactly_upright, "GRADIENT:", deceleration_of_loading_wheel)
                            else:
                                # loading_wheel_speed = loading_wheel_speed - 15
                                # print("LWA:", loading_wheel_angle, "LWS:", loading_wheel_speed, "AUEU:", angle_until_exactly_upright, "GRADIENT:", deceleration_of_loading_wheel)

                                # print("AYO?!")
                                if loading_wheel_angle < -360:
                                    loading_wheel_angle = 0
                                angle_until_exactly_upright = 360 + loading_wheel_angle
                                deceleration_of_loading_wheel = loading_wheel_speed/angle_until_exactly_upright
                                # print("LWA:", loading_wheel_angle, "LWS:", loading_wheel_speed, "AUEU:", angle_until_exactly_upright, "GRADIENT:", deceleration_of_loading_wheel)


                                while True:

                                    if loading_wheel_angle < -360:
                                        loading_wheel_angle = 0
                                    dt = clock.tick(FPS) / 1000.0 # delta time calculates the amount of time has elapsed since the last frame, and returns that time in milliseconds. / 1000.0 then converts that time from milliseconds to seconds
                                    current_fps = clock.get_fps()
                                    pygame.display.set_caption(f'Formula 1 Pixel Racing')


                                    angle_until_exactly_upright = 360 + loading_wheel_angle # YOU HAVE TO KEEP THIS LINE IN - idk why tho i sorta fluked it - see F1 schematics on 12/10/24


                                    # print("LWA:", loading_wheel_angle, "LWS:", loading_wheel_speed, "AUEU:", angle_until_exactly_upright, "GRADIENT:", deceleration_of_loading_wheel)
                                    loading_wheel_angle = loading_wheel_angle - loading_wheel_speed*dt
                                    loading_wheel_speed = angle_until_exactly_upright*(deceleration_of_loading_wheel) # calculates a variable acceleration in real time to ENSURE the loading_wheel_angle reaches 0 regardless of burnout_speed and/or angle_until_exactly_upright


                                    if loading_wheel_speed < 1:
                                        return
                                

                                    rotated_loading_wheel_image = pygame.transform.rotate(original_loading_wheel_image, loading_wheel_angle)
                                    rotated_loading_wheel_rect = rotated_loading_wheel_image.get_rect(center=(screen_size_x-75, screen_size_y-75))
                                    screen.blit(rotated_loading_wheel_image, rotated_loading_wheel_rect.topleft)
                                    pygame.display.flip()



                            if loading_wheel_speed > 2000:
                                max_burnout_speed_reached = True

                                # for row in track_images:
                                    # print(row)
                                # for i in range(5):
                                    # print("MAX")
   

    # for row in track_images:
        # print(row)

    image_to_be_blitted = track_images[9][8] # this makes it so we spawn in the 00 quadrant # THESE TWO NEED TO BE CHANGED WHENEVER YOU RENDER IN A NEW MAP
    # check_if_new_quadrant_has_been_entered = ["0-0", "0-0"] # THESE TWO NEED TO BE CHANGED WHENEVER YOU RENDER IN A NEW MAP

# MOVEMENT INITIALISATION
gear = 1
automatic = True
accelerating = False
time_started_for_shift_lights = False
start_time_for_shift_lights = 0
elapsed_time_for_shift_lights = 0

offsety = 0
offsetx = 0

previously_added_track_posy = 0
previously_added_track_posx = 0

flame_spitting = False
flame_spitting_frames1 = [True, True, True, True, True, False, False, False, False, False, True, True, True, True, True, False, False, False, False, False] # repeats every 10, but the entire cycle of a frame spit will occur in 8 frames # DO NOT PUT IN "True" - YOU PUT IN JUST TRUE
flame_spitting_frames2 = [True, True, True, True, False, False, False, False, True, True, True, True, False, False, False, False]
flame_spitting_frames3 = [True, True, True, False, False, False, True, True, True, False, False, False]
f = 0

n = 0
minutes_to_seconds = 0
start_time = 0

time_started_for_check_if_green_pixel_flag = False
elapsed_time_for_check_if_green_pixel = 0
start_time_for_check_if_green_pixel = 0

gear_changed_flag = False

recording = False
playing_back = False

# MACRO LISTS
length_of_macro_lists = 99
frame_counter = 0

throttle_macro_list = [1]*length_of_macro_lists
brake_macro_list = [0]*length_of_macro_lists
leftward_steering_macro_list  = [0]*length_of_macro_lists
rightward_steering_macro_list = [0]*length_of_macro_lists
gear_up_macro_list = [0]*length_of_macro_lists
gear_down_macro_list = [0]*length_of_macro_lists

# ADVANCED CONTROLS
advanced_controls_flag = False

frame_counter2 = 0

shift_lights_silhouette_image = pygame.image.load("shift_lights_silhouette.png")
canada_minimap_image = pygame.image.load("canadanewtrack_minimapv7.png").convert_alpha()
canada_minimap_image = pygame.transform.scale_by(canada_minimap_image, 0.03)
# canada_minimap_image = pygame.transform.smoothscale(canada_minimap_image(    x    ,    y    ))

minimap_marker_relative_track_pos_x = 0
minimap_marker_relative_track_pos_y = 0
minimap_marker_start_pos_x = 87
minimap_marker_start_pos_y = 124

mph_text = render_text_once(font_size_20, "mph", False, (255, 255, 255))

speedmaxratio = 100

on_grass = False

timed_lap_has_started = True # initialise as true so that you can enable free roaming when you initially spawn in

def x_y_conversion(track_angle):
    global x_y_conversion_multiplier_for_y, x_y_conversion_multiplier_for_x, minimap_marker_relative_track_pos_y, minimap_marker_relative_track_pos_x

    x_y_conversion_multiplier = 0
    # FIX THE INCLUSIVE/EXCLUSIVE ANGLES FOR THE NEGATIVE ONES HERE:
    if (0 <= track_angle <= 90) or (-360 <= track_angle < -270): # oh I didn't include angles between 90 and 91, 180 and 181... etc.
        if track_angle >= 0: # i.e. if the track angle is positive
            x_y_conversion_multiplier = (track_angle)/90
        else:
            x_y_conversion_multiplier = ((track_angle+360)/90)

        x_y_conversion_multiplier_for_y = (1-x_y_conversion_multiplier)
        x_y_conversion_multiplier_for_x = (x_y_conversion_multiplier)

        # calculate negated transformed trigonometric equivalent values first
        negated_transformed_trigonometric_equivalent_values_y_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_y)
        negated_transformed_trigonometric_equivalent_values_x_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_x)

        normal_transformed_trigonometric_equivalent_values_y_increment = -negated_transformed_trigonometric_equivalent_values_y_increment
        normal_transformed_trigonometric_equivalent_values_x_increment = -negated_transformed_trigonometric_equivalent_values_x_increment


        track_pos.y += negated_transformed_trigonometric_equivalent_values_y_increment
        track_pos.x -= negated_transformed_trigonometric_equivalent_values_x_increment

        minimap_marker_relative_track_pos_y += normal_transformed_trigonometric_equivalent_values_y_increment
        minimap_marker_relative_track_pos_x -= normal_transformed_trigonometric_equivalent_values_x_increment






    if (90 < track_angle <= 180) or (-270 <= track_angle < -180): # THESE TWO ARE IN THE SAME QUADRANT
        if track_angle >= 0: # i.e. if the track angle is positive
            x_y_conversion_multiplier = (track_angle-90)/90 # BECAUSE OTHERWISE x_y_conversion_multiplier and 1-x_y_conversion_multiplier GETS DISTORTED e.g. when they're meant to be 0.5 with 135 degrees as the track angle, they're actually 0.75 or 0.25
        else:
            x_y_conversion_multiplier = ((track_angle+270)/90) # + 90 was such an arbitrary guess

        x_y_conversion_multiplier_for_y = (x_y_conversion_multiplier) # these two get swapped here
        x_y_conversion_multiplier_for_x = (1-x_y_conversion_multiplier) # these two get swapped here



        # calculate negated transformed trigonometric equivalent values first
        negated_transformed_trigonometric_equivalent_values_y_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_y)
        negated_transformed_trigonometric_equivalent_values_x_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_x)

        normal_transformed_trigonometric_equivalent_values_y_increment = -negated_transformed_trigonometric_equivalent_values_y_increment
        normal_transformed_trigonometric_equivalent_values_x_increment = -negated_transformed_trigonometric_equivalent_values_x_increment


        track_pos.y -= negated_transformed_trigonometric_equivalent_values_y_increment # changed from += to -=
        track_pos.x -= negated_transformed_trigonometric_equivalent_values_x_increment

        minimap_marker_relative_track_pos_y -= normal_transformed_trigonometric_equivalent_values_y_increment
        minimap_marker_relative_track_pos_x -= normal_transformed_trigonometric_equivalent_values_x_increment






    if (180 < track_angle <= 270) or (-180 <= track_angle < -90): # THESE TWO ARE IN THE SAME QUADRANT
        if track_angle >= 0: # i.e. if the track angle is positive
            x_y_conversion_multiplier = (track_angle-180)/90
        else:
            x_y_conversion_multiplier = ((track_angle+180)/90)

        x_y_conversion_multiplier_for_y = (1-x_y_conversion_multiplier) # these two get swapped here
        x_y_conversion_multiplier_for_x = (x_y_conversion_multiplier) # these two get swapped here


        # calculate negated transformed trigonometric equivalent values first
        negated_transformed_trigonometric_equivalent_values_y_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_y)
        negated_transformed_trigonometric_equivalent_values_x_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_x)

        normal_transformed_trigonometric_equivalent_values_y_increment = -negated_transformed_trigonometric_equivalent_values_y_increment
        normal_transformed_trigonometric_equivalent_values_x_increment = -negated_transformed_trigonometric_equivalent_values_x_increment


        track_pos.y -= negated_transformed_trigonometric_equivalent_values_y_increment
        track_pos.x += negated_transformed_trigonometric_equivalent_values_x_increment # changed from += to -=

        minimap_marker_relative_track_pos_y -= normal_transformed_trigonometric_equivalent_values_y_increment
        minimap_marker_relative_track_pos_x += normal_transformed_trigonometric_equivalent_values_x_increment







    if (270 < track_angle <= 360) or (-90 <= track_angle < 0): # THESE TWO ARE IN THE SAME QUADRANT
        if track_angle >= 0: # i.e. if the track angle is positive
            x_y_conversion_multiplier = (track_angle-270)/90
        else:
            x_y_conversion_multiplier = ((track_angle+90)/90) # + 90 was such an arbitrary guess

        x_y_conversion_multiplier_for_y = (x_y_conversion_multiplier) # these two get swapped here
        x_y_conversion_multiplier_for_x = (1-x_y_conversion_multiplier) # these two get swapped here


        # calculate negated transformed trigonometric equivalent values first
        negated_transformed_trigonometric_equivalent_values_y_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_y)
        negated_transformed_trigonometric_equivalent_values_x_increment = (track_speed * dt)*(x_y_conversion_multiplier_for_x)

        normal_transformed_trigonometric_equivalent_values_y_increment = -negated_transformed_trigonometric_equivalent_values_y_increment
        normal_transformed_trigonometric_equivalent_values_x_increment = -negated_transformed_trigonometric_equivalent_values_x_increment


        track_pos.y += negated_transformed_trigonometric_equivalent_values_y_increment
        track_pos.x += negated_transformed_trigonometric_equivalent_values_x_increment # changed from += to -=

        minimap_marker_relative_track_pos_y += normal_transformed_trigonometric_equivalent_values_y_increment
        minimap_marker_relative_track_pos_x += normal_transformed_trigonometric_equivalent_values_x_increment





def render_image_then_apply_and_update_offsets(temp_i_value, temp_j_value):
    global image_to_be_blitted, offsetx, offsety, previously_added_track_posy, previously_added_track_posx
    # screen.blit(track_image, track_rect) # displays the current image over itself # i think it might be 'front' buffer # this acts as a 'back buffer' (i learnt the term from ChatGPT but thought up of this method myself) - basically, the previous image gets rendered again on top of itself. this is the back buffer. the new image gets DEFINED (not rendered yet - 'rendered' is when screen.blit() is present) with image_to_be_blitted = track_images[i][j]. then the back buffer gets overwritten and stops getting rendered with screen.blit(track_image, track_rect) many lines down
    image_to_be_blitted = track_images[temp_i_value][temp_j_value]

    # print("YOYOYO", temp_i_value, temp_j_value)

    # screen.blit(track_images[i][j], track_rect)
    offsetx = (half_length_of_each_tile)*temp_j_value
    offsety = (half_length_of_each_tile)*temp_i_value
    # print("NEW QUADRANT:", str(i)+"-"+str(j))

    # here, im subtracting/getting rid of the old offset added (when the game is launched, the previous offsets are initialised to 0)
    track_pos.y = track_pos.y - previously_added_track_posy
    track_pos.x = track_pos.x - previously_added_track_posx

    # then im adding the new offsets which are defined in the if statements above (which arent correct yet but we can do some trial and error)
    track_pos.y = track_pos.y + offsety # DON'T FORGET TO UNCOMMENT THIS YOU TWAT
    track_pos.x = track_pos.x + offsetx # DON'T FORGET TO UNCOMMENT THIS YOU TWAT


    # then im storing the current offsets as 'previously added' for the next iteration when this if statement is entered into again
    previously_added_track_posy = offsety
    previously_added_track_posx = offsetx

    # check_if_new_quadrant_has_been_entered.append(check_if_new_quadrant_has_been_entered[-1]) # COMMENTED OUT FOR OPTIMISATION

    # we can check the offsets are correct by using the big red crosses - when you enter a new quadrant/tile, they should stay in place, and only get cut off. like so: (demonstrated)
    # let's do some trial and error now


player_found = False
def locate_the_player_and_return_i_and_j(): # traverses the ENTIRE map to initially find the player and returns the i and j index
    global player_found, temp_i_value, temp_j_value
    for i in range(i_value): # THESE TWO NEED TO BE CHANGED WHEN YOU RENDER IN A NEW MAP
        for j in range(j_value): # THESE TWO NEED TO BE CHANGED WHEN YOU RENDER IN A NEW MAP
            if (DP_diagonal_y_component-(half_length_of_each_tile*i)+offsety < track_pos.y < DP_y_component-(half_length_of_each_tile*i)+offsety):
                if (DP_diagonal_x_component-(half_length_of_each_tile*j)+offsetx < track_pos.x < DP_x_component-(half_length_of_each_tile*j)+offsetx):
                    # check_if_new_quadrant_has_been_entered.append(str(i)+"-"+str(j)) # we don't want this line here otherwise i and j appends twice. since it appends twice, "if check_if_new_quadrant_has_been_entered[-2] != check_if_new_quadrant_has_been_entered[-1]:" will not trigger on the first frame, meaning it does not render any tile until a new quadrant has been moved into
                    # print("PLAYER LOCATED AT:", i,j)
                    temp_i_value, temp_j_value = i,j
                    player_found = True
                    # print("cool i found bro at:", temp_i_value, temp_j_value)
                    return temp_i_value, temp_j_value


# MAP RENDERING OPTIMISATION:
tile_needs_to_be_changed = False
def search_the_current_tile_and_8_surrounding_tiles(temp_i_value, temp_j_value):
    global tile_needs_to_be_changed
    # print(check_if_new_quadrant_has_been_entered)
    # print("SEARCHING THE 9 SURROUNDING TILES...")
    # CHECK IF YOU ARE STILL IN THE SAME TILE:
    if (DP_diagonal_y_component-(half_length_of_each_tile*temp_i_value)+offsety < track_pos.y < DP_y_component-(half_length_of_each_tile*temp_i_value)+offsety):
        if (DP_diagonal_x_component-(half_length_of_each_tile*temp_j_value)+offsetx < track_pos.x < DP_x_component-(half_length_of_each_tile*temp_j_value)+offsetx):
            # print("SEARCH COMPLETE. PLAYER IS IN THE SAME TILE AT.", temp_i_value, temp_j_value)
            # print("SINCE THE SEARCH IS COMPLETE, THE SEARCH IS NOW TERMINATED.")
            tile_needs_to_be_changed = False
            return temp_i_value, temp_j_value # don't do anything if we're still in the same tile, but we STILL need to return temp_i_value and temp_j_value because we can't return nothing

    # ELSE, IF WE'RE NOT IN THE SAME TILE:
    for i in range(temp_i_value-1, temp_i_value+2): # THESE TWO NEED TO BE CHANGED WHEN YOU RENDER IN A NEW MAP
        for j in range(temp_j_value-1, temp_j_value+2): # THESE TWO NEED TO BE CHANGED WHEN YOU RENDER IN A NEW MAP

            # SKIP THIS SPECIFIC I AND J VALUE CUZ WE ALREADY SEARCHED IT ABOVE
            # ACTUALLY NAH this if statement has to run every iteration of the nested for loop - not worth it (I think?)
            # if (i == temp_i_value) and (j == temp_j_value):
                # pass

            # print(i, j)
            if (DP_diagonal_y_component-(half_length_of_each_tile*i)+offsety < track_pos.y < DP_y_component-(half_length_of_each_tile*i)+offsety):
                if (DP_diagonal_x_component-(half_length_of_each_tile*j)+offsetx < track_pos.x < DP_x_component-(half_length_of_each_tile*j)+offsetx):
                    # print("SEARCH COMPLETE AT:", i,j)
                    temp_i_value, temp_j_value = i,j
                    # print("SINCE THE SEARCH IS COMPLETE, THE SEARCH IS NOW TERMINATED.")
                    tile_needs_to_be_changed = True
                    return temp_i_value, temp_j_value


# MAKE IT SO THAT WHEN YOU ARE RECORDING, THE FRAME COUNTER STARTS FROM 0 CUZ IT MAY JUST CUT INTO THE MIDDLE OF A REPLAY FOR NO REASON
commence_lights_sequence = False
start_time_for_lights_sequence = 0
elapsed_time_for_lights_sequence = 0
time_started_for_lights_sequence = False
def reset_timed_lap():
    # you NEED TO MAKE ALL OF THESE GLOBAL APPARENTLY - ASK CHATGPT FOR MORE DETAILS LATER
    # WHENEVER YOU ADD A NEW VARIABLE HERE, YOU NEED TO SET IT AS GLOBAL FIRST
    global track_speed, rate_of_change_of_speed, track_angle, gear, automatic, wheel_angle, drs_enabled
    global track_pos, previously_added_track_posx, previously_added_track_posy, image_to_be_blitted
    global current_time, minutes_to_seconds, minimap_marker_relative_track_pos_x, minimap_marker_relative_track_pos_y, minimap_marker_start_pos_x, minimap_marker_start_pos_y, attempt_number
    global sector1_colour, sector2_colour, sector3_colour, sector1_passed, sector2_passed, sector3_passed, sector1_time_text, sector2_time_text, sector3_time_text
    global timed_lap_has_started, ers_recharge_mode, energy_store_level, final_lap_time_appended, bot_activated, raycast_bot_up_arrow_activated, commence_lights_sequence, time_started_for_lights_sequence
    global new_time_index_found, artificially_activate_end_game_leaderboard, cooldown_lap, render_no_sector_times
    global off_track_time_penalty, formatted_off_track_time_penalty, elapsed_time_for_off_track_time_penalty_linger

    # track_speed = 1250

    track_speed = 1250

    rate_of_change_of_speed = 0
    
    # track_angle = 110
    track_angle = 270

    # gear = 8
    gear = 8
    automatic = (1==1)
    wheel_angle = 0

    drs_enabled = True

    # track_pos.x, track_pos.y = 1025, 475  # this is just before where the finish line is
    # previously_added_track_posx = 14400.0 # i'm so gassed i figured out you needed these two lines when you needed to reset a timed lap - just use print statements to figure out what this number should be when you spawn in the correct location
    # previously_added_track_posy = 3200.0 # i'm so gassed i figured out you needed these two lines when you needed to reset a timed lap - just use print statements to figure out what this number should be when you spawn in the correct location
    
    track_pos.x, track_pos.y = 838, 500
    previously_added_track_posx = 10400.0
    previously_added_track_posy = 7200.0

    # track_pos.x, track_pos.y = 261, 304
    # previously_added_track_posx = 5160.0
    # previously_added_track_posy = 6020.0
    
    # image_to_be_blitted = track_images[4][19]
    image_to_be_blitted = track_images[9][7] # [9][7] not [9][8] because when you load in the game, the track gets cut off

    current_time = 0
    minutes_to_seconds = 0

    minimap_marker_relative_track_pos_x = 0
    minimap_marker_relative_track_pos_y = 0
    minimap_marker_start_pos_x = 131
    minimap_marker_start_pos_y = 124

    print()
    attempt_number = attempt_number + 1
    print("Attempt", str(attempt_number) + ":")

    sector1_colour = (100, 100, 100)
    sector2_colour = (100, 100, 100)
    sector3_colour = (100, 100, 100)

    sector1_passed = False
    sector2_passed = False
    sector3_passed = False

    # set these back to None so that the try-except block in display_end_game_leaderboard() fails in the 'try' and branches to 'except'
    sector1_time_text = None
    sector2_time_text = None
    sector3_time_text = None

    timed_lap_has_started = False

    ers_recharge_mode = False
    energy_store_level = 68

    final_lap_time_appended = False

    render_image_then_apply_and_update_offsets(9, 8)
    locate_the_player_and_return_i_and_j() # we still need this line for some reason otherwise you get an error: "temp_i_value, temp_j_value = search_the_current_tile_and_8_surrounding_tiles(temp_i_value, temp_j_value) - ypeError: cannot unpack non-iterable NoneType object"

    bot_activated = False

    raycast_bot_up_arrow_activated = True
    
    commence_lights_sequence = True
    time_started_for_lights_sequence = False

    new_time_index_found = False

    artificially_activate_end_game_leaderboard = False

    cooldown_lap = False

    render_no_sector_times = True

    off_track_time_penalty = 0
    formatted_off_track_time_penalty = "00:00.000"
    elapsed_time_for_off_track_time_penalty_linger = 999 # this needs to be some value over 2 seconds so that the penalty isn't lingering anymore (I set the lingering period to be 2 seconds for now)



# MERGE SORT:
def merge_sort_list_into_ascending_order(list):
    # return the list if the list contains 0 or 1 items
    if len(list) <= 1:
        return list

    mid = len(list)//2

    # recursively sort both halves
    left_half = merge_sort_list_into_ascending_order(list[:mid]) # sorts the list from the start index to the mid index
    right_half = merge_sort_list_into_ascending_order(list[mid:]) # sorts the list from the mid index to the end index

    # merge the sorted halves
    sorted_list = merge_phase(left_half, right_half)
    # return the solved halves
    return sorted_list

def merge_phase(left_half, right_half):
    sorted_list = []
    left_index = 0
    right_index = 0

    # merge the two halves whilst maintaining order
    while left_index < len(left_half) and right_index < len(right_half):
        if left_half[left_index] <= right_half[right_index]:
            sorted_list.append(left_half[left_index])
            left_index = left_index + 1
        else:
            sorted_list.append(right_half[right_index])
            right_index = right_index + 1

    # if there are remaining elements in left_half or right_half, add them to sorted_list
    sorted_list.extend(left_half[left_index:]) # .extend() adds the elements of left_half[left_index:] to the sorted_list
    sorted_list.extend(right_half[right_index:]) # .extend() adds the elements of right_half[right_index:] to the sorted_list
    return sorted_list

# END GAME SCREEN LEADERBOARD
LDY = -screen_size_y # leaderboard dropdown y value # LDY should range from screen_size_y (810) to 0

end_game_screen_leaderboard_buttons = []
end_game_screen_leaderboard_restart_button = Button((0, 255, 0), (0, 255, 0), 735, 705, 240, 50, "RESTART >>>", 16, "end_game_screen_leaderboard_restart_button")
end_game_screen_leaderboard_buttons.append(end_game_screen_leaderboard_restart_button)

end_game_screen_leaderboard_scroll_up_button = Button((100, 100, 100), (100, 100, 100), 945, 245, 30, 30, "", 0, "end_game_screen_leaderboard_scroll_up_button")
end_game_screen_leaderboard_buttons.append(end_game_screen_leaderboard_scroll_up_button)

end_game_screen_leaderboard_scroll_down_button = Button((100, 100, 100), (100, 100, 100), 945, 612, 30, 30, "", 0, "end_game_screen_leaderboard_scroll_down_button")
end_game_screen_leaderboard_buttons.append(end_game_screen_leaderboard_scroll_down_button)

scroll_down_arrow_image = pygame.image.load("scroll_down_arrowv1.png").convert_alpha()
scroll_down_arrow_image = pygame.transform.scale(scroll_down_arrow_image, (24, 12))

scroll_up_arrow_image = pygame.transform.rotate(scroll_down_arrow_image, 180)


final_lap_times_list = []

end_screen_finish_line_banner_image = pygame.image.load("end_screen_finish_line_banner.png").convert_alpha()
end_screen_finish_line_banner_image_alpha_value = 150
end_screen_finish_line_banner_fading_out = True
end_screen_finish_line_banner_image.set_alpha(end_screen_finish_line_banner_image_alpha_value)
end_screen_finish_line_banner_image = pygame.transform.scale(end_screen_finish_line_banner_image, (870, 50))

leaderboard_scroll_start_index = 0
new_time_index_found = False

soft_tyre_image = pygame.image.load("loading_wheel_soft_tyrev1.png").convert_alpha()

leaderboard_glow = pygame.image.load("leaderboard_glow.png").convert_alpha()
leaderboard_glow = pygame.transform.scale(leaderboard_glow, (910, 740))

render_no_sector_times = True

def display_end_game_leaderboard(final_lap_time, final_lap_times_list):
    global end_game_screen_leaderboard_buttons, bot_activated, time_started_for_lap_cooldown, start_time_for_lap_cooldown, elapsed_time_for_lap_cooldown, end_screen_finish_line_banner_fading_out, end_screen_finish_line_banner_image_alpha_value, leaderboard_scroll_start_index, leaderboard_scroll_end_index, merge_sorted_final_lap_times_list, new_time_index_found, artificially_activate_end_game_leaderboard, LDY, render_no_sector_times

    if LDY < -0.01: # this if statement exists so that there isn't some 1 pixel adjustment (which is noticeable!) like 10 seconds after the leaderboard comes up
        LDY = LDY*0.92

    end_game_screen_leaderboard_restart_button.button_y_pos = 705+LDY
    end_game_screen_leaderboard_scroll_up_button.button_y_pos = 245+LDY
    end_game_screen_leaderboard_scroll_down_button.button_y_pos = 612+LDY
    
    
    # ----------CLEAN Formula 1 Pixel Racing Leaderboard.txt - VALIDATION INPUT----------
    # - Remove unwanted entries e.g. empty lines, spaces, and NO TIME entries.
    # > This would be in the case of misformatting/unwanted appendages to the leaderboard lap times list.
    # > NO TIME entries only act as placeholders when the player does not have any times on the leaderboard yet.

    # - You cannot use a for loop due to "IndexError: list index out of range" errors when you remove an item from the list using .remove().
    # > it is better to use a linear search using while loops here than if statements that run every frame because this ensures that final_lap_times_list is FULLY cleaned before we use it.

    # - Since these while loops run every frame to ensure no unwanted entries are considered in the leaderboard lap times list,
    # the while loops may raise an IndexError when unwanted entries cannot be found in order to remove them.
    # > therefore, it is preferable to use a try-except block to handle any errors.
    
    try:
        while "NO TIME" in final_lap_times_list: # DO A LINEAR SEARCH HERE USING A WHILE LOOP
            final_lap_times_list.remove("NO TIME")
        while "LAP INVALID" in final_lap_times_list: # DO A LINEAR SEARCH HERE USING A WHILE LOOP
            final_lap_times_list.remove("LAP INVALID")
        while " " in final_lap_times_list: # DO A LINEAR SEARCH HERE USING A WHILE LOOP
            final_lap_times_list.remove(" ")
        while "" in final_lap_times_list: # DO A LINEAR SEARCH HERE USING A WHILE LOOP
            final_lap_times_list.remove("")
    # Print any errors that get raised in order to handle any errors that occur, e.g. IndexError if final_lap_times_list is empty. 
    except Exception as e:
        print("An exception has occurred:", e)

    # Append a NO TIME entry if the player does not have any times in the leaderboard yet
    if len(final_lap_times_list) == 0:
        final_lap_times_list.append("NO TIME")
    # --------------------

    mousex, mousey = pygame.mouse.get_pos() # return the mouse x and y positions every frame

    screen.blit(leaderboard_glow, (85, 35+LDY))
    pygame.draw.rect(screen, (255, 255, 255), (100, 50+LDY, 880, 710)) # white background square
    pygame.draw.rect(screen, (50, 50, 50), (105, 55+LDY, 870, 700)) # grey foreground square
    pygame.draw.rect(screen, (255, 255, 255), (100, 105+LDY, 880, 5)) # white border line

    
    # END SCREEN FINISH LINE BANNNER
    screen.blit(end_screen_finish_line_banner_image, (105,55+LDY))

    if end_screen_finish_line_banner_fading_out:
        end_screen_finish_line_banner_image_alpha_value = end_screen_finish_line_banner_image_alpha_value - 1
        if end_screen_finish_line_banner_image_alpha_value < 15:
            end_screen_finish_line_banner_fading_out = False
    else:
        end_screen_finish_line_banner_image_alpha_value = end_screen_finish_line_banner_image_alpha_value + 1
        if end_screen_finish_line_banner_image_alpha_value > 200:
            end_screen_finish_line_banner_fading_out = True

    end_screen_finish_line_banner_image.set_alpha(end_screen_finish_line_banner_image_alpha_value)

    finished_text = font_size_40.render("FINISH!", True, (255, 255, 255))
    finished_text_rect = finished_text.get_rect()
    finished_text_rect.center = (screen_size_x//2, 83+LDY)
    screen.blit(finished_text, finished_text_rect)



    if (return_minimum_of_list(final_lap_times_list) == final_lap_time) and (final_lap_times_list[0] != "NO TIME"):
        new_track_record_text = font_size_20.render("NEW TRACK RECORD!", True, (0, 255, 0))
        screen.blit(new_track_record_text, (728, 145+LDY))

    # these two if statements can be combined
    if artificially_activate_end_game_leaderboard:
        if off_track_time_penalty == 0:
            full_lap_time_text = font_size_70.render(final_lap_time, True, (255, 255, 255)) # this will display a normal white NO TIME or final lap time
        else:
            full_lap_time_text = font_size_70.render(final_lap_time, True, (255, 0, 0)) # this will show a red LAP INVALID

    if off_track_time_penalty > 0 and not artificially_activate_end_game_leaderboard: # this will activate at the end of the lap
        full_lap_time_text = font_size_70.render(final_lap_time, True, (255, 0, 0))
        lap_time_invalidated_leaderboard_text = font_size_20.render("LAP TIME INVALIDATED", True, (255, 0, 0))
        screen.blit(lap_time_invalidated_leaderboard_text, (125, 145+LDY))

    full_lap_time_text_rect = full_lap_time_text.get_rect() # return Rect() object
    full_lap_time_text_rect.center = (screen_size_x//2, 157+LDY) # set centre position of Rect() object

    screen.blit(full_lap_time_text, full_lap_time_text_rect) # render with new Rect() attributes
    

    pygame.draw.rect(screen, (255, 255, 255), (100, 195+LDY, 880, 5)) # second white border line

    columns_texts = font_size_20.render("POS                 TIME                                    NAME                              TEAM", True, (255, 255, 255))
    screen.blit(columns_texts, (112, 213+LDY))

    pygame.draw.rect(screen, (255, 255, 255), (100, 240+LDY, 880, 5)) # third white border line

    pygame.draw.rect(screen, (255, 255, 255), (100, 642+LDY, 880, 5)) # fourth white border line
    
    # merge sort the final_lap_times_list
    merge_sorted_final_lap_times_list = merge_sort_list_into_ascending_order(final_lap_times_list)


    leaderboard_line_spacing = 57
    leaderboard_scroll_end_index = min(leaderboard_scroll_start_index+7, len(merge_sorted_final_lap_times_list)) # 8 because only 8 entries can fit on the leaderboard screen # min() because if len(merge_sorted_final_lap_times_list) is smaller than leaderboard_scroll_start_index_8 (leaderboard_scroll_start_index is initialised to 0), then we want that because there's less than leaderboard_scroll_start_index+8 entries to display, so the for loop only needs to get up to len(merge_sorted_final_lap_times_list), and not leaderboard_scroll_start_index+8

    # --------------- LEADERBOARD SCROLL INDEX ---------------
    # Find the leaderboard_scroll_start_index in order to render the leaderboard in the correct scroll position when the player.
    # After the player has completed a lap, we want to automatically scroll the leaderboard down to the player's new time.
    # 7 lap time entries can be visible on the leaderboard at any one time, with the player's new time in the centre entry position.
    # > However, there are some exceptions in edge cases where the player's time is at the start or end of the leaderboard lap times list.
    # > There are further exceptions if the leaderboard lap times list has less than 7 entries.
    if not artificially_activate_end_game_leaderboard: # The player can choose to activate the leaderboard before the lap time is completed.
        for i in range(len(merge_sorted_final_lap_times_list)):
            if merge_sorted_final_lap_times_list[i] == final_lap_time: # The new time index equals i - this is the index of the player's new time.
                if not new_time_index_found: 
                    if i >= 3: # The index of the player's new time is more than or equal to 3.
                        # Case 1 (edge case): the user's final lap time is near the start of the list.
                        if len(merge_sorted_final_lap_times_list) <= 7:
                            leaderboard_scroll_start_index = 0
                        if len(merge_sorted_final_lap_times_list) == 8:
                            leaderboard_scroll_start_index = 1
                        if len(merge_sorted_final_lap_times_list) == 9:
                            leaderboard_scroll_start_index = 2

                        # Case 2: the user's final lap time is in the middle of the list and is not near the start or end of the list.
                        if len(merge_sorted_final_lap_times_list) >= 10:
                            leaderboard_scroll_start_index = i-3
                            
                            # Case 3 (edge case): the user's final lap time is near the end of the list
                            if i+1 == len(merge_sorted_final_lap_times_list):
                                leaderboard_scroll_start_index = len(merge_sorted_final_lap_times_list)-7
                            if i+1 == len(merge_sorted_final_lap_times_list)-1:
                                leaderboard_scroll_start_index = len(merge_sorted_final_lap_times_list)-7
                            if i+1 == len(merge_sorted_final_lap_times_list)-2:
                                leaderboard_scroll_start_index = len(merge_sorted_final_lap_times_list)-7

                    else:
                        # FAILURE - YOU FORGOT THIS ELSE STATEMENT
                        # Case 4 (edge case): the user's final lap time is at the start of the list AND the length of the list is less than 7.
                        leaderboard_scroll_start_index = 0
                    
                    new_time_index_found = True

                # Render the NEW TIME text in the correct entry position (i.e. at the player's new time when they have finished a lap).
                if leaderboard_scroll_start_index <= i < leaderboard_scroll_end_index:
                    new_time_text1 = font_size_15.render("NEW", True, (0, 255, 0))
                    new_time_text2 = font_size_15.render("TIME", True, (0, 255, 0))

                    screen.blit(new_time_text1, (390, 257+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)))
                    screen.blit(new_time_text2, (389, 275+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)))

    # If the player has artificially activated the leaderboard:
    else:
        if not new_time_index_found:
            leaderboard_scroll_start_index = 0 # By default, set the leaderboard_scroll_start_index to 0.
            new_time_index_found = True
    # ------------------------------------------------------------


    # print("final calculated scroll indexes", leaderboard_scroll_start_index, leaderboard_scroll_end_index)

    for i in range(leaderboard_scroll_start_index, leaderboard_scroll_end_index):
        lap_times_positions_text = font_size_40.render(str(i+1)+".", True, (255, 255, 255))
        screen.blit(lap_times_positions_text, (120, 254+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)))


        leaderboard_lap_times_text = font_size_40.render(merge_sorted_final_lap_times_list[i], True, (255, 255, 255))
        if final_lap_times_list[0] != "NO TIME":
            screen.blit(leaderboard_lap_times_text, (190, 255+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)))
        else:
            screen.blit(leaderboard_lap_times_text, (197, 255+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)))

        leaderboard_names_text = font_size_30.render("Player", True, (255, 255, 255))
        screen.blit(leaderboard_names_text, (504, 256+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)))


        if len(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][0]) > 20: # if the name of the team exceeds 20 characters, use a smaller font size
            leaderboard_teams_text = font_size_15.render(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][0], True, (255, 255, 255))
            leaderboard_teams_text_rect = leaderboard_teams_text.get_rect()
            leaderboard_teams_text_rect.center = 835+(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][3])*0.2, 271+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)
        else:
            leaderboard_teams_text = font_size_25.render(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][0], True, (255, 255, 255))
            leaderboard_teams_text_rect = leaderboard_teams_text.get_rect()
            leaderboard_teams_text_rect.center = 791+(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][3])*0.2, 273+LDY+(i*leaderboard_line_spacing)-(leaderboard_scroll_start_index*leaderboard_line_spacing)




        screen.blit(leaderboard_teams_text, leaderboard_teams_text_rect)


    for i in range(len(end_game_screen_leaderboard_buttons)):
        end_game_screen_leaderboard_buttons[i].draw_button(screen)
        end_game_screen_leaderboard_buttons[i].check_if_mouse_is_hovering(mousex, mousey)
        end_game_screen_leaderboard_buttons[i].check_if_mouse_clicked(mousex, mousey, event)
        end_game_screen_leaderboard_buttons[i].draw_text_on_button(screen)

    pygame.draw.rect(screen, (150, 150, 150), (945, 275+LDY, 30, 337)) # scroll bar
    screen.blit(scroll_up_arrow_image, (948, 253+LDY))
    screen.blit(scroll_down_arrow_image, (948, 621+LDY))




    try:
        screen.blit(sector1_time_text, (120, 652+LDY))
        screen.blit(formatted_sector1_delta_time_text, (315, 652+LDY))
        render_no_sector_times = False

        screen.blit(sector2_time_text, (120, 687+LDY))
        screen.blit(formatted_sector2_delta_time_text, (315, 687+LDY))

        screen.blit(sector3_time_text, (120, 722+LDY))
        screen.blit(formatted_sector3_delta_time_text, (315, 722+LDY))
    except:
        if render_no_sector_times:
            no_sector_times_text = font_size_30.render("NO SECTOR TIMES", True, (255, 255, 255))
            screen.blit(no_sector_times_text, (154, 687+LDY))


    soft_text = font_size_30.render("SOFT", True, (255, 255, 255))
    screen.blit(soft_text, (493, 686+LDY))

    screen.blit(soft_tyre_image, (583, 663+LDY))

    
    auto_restart = False
    if bot_activated and auto_restart:
        if not time_started_for_lap_cooldown:
            time_started_for_lap_cooldown = True
            start_time_for_lap_cooldown = time.time()
        else:
            elapsed_time_for_lap_cooldown = time.time() - start_time_for_lap_cooldown
            print(elapsed_time_for_lap_cooldown)

        if elapsed_time_for_lap_cooldown > 5:
            time_started_for_lap_cooldown = False
            start_time_for_lap_cooldown = 0
            elapsed_time_for_lap_cooldown = 0
            restart_timed_lap_fade_in_and_out_and_lights_sequence() # restart_timed_lap() is included
    

time_started_for_lap_cooldown = False
start_time_for_lap_cooldown = 0
elapsed_time_for_lap_cooldown = 0


if not disable_splash_screen_sequence:
    display_splash_screen()

if not disable_start_menu:
    display_start_menu()


load_game()

print()
print("Attempt 1:")

time_started_for_ers_lights = False
start_time_for_ers_lights = 0
elapsed_time_for_ers_lights = 0

time_started_for_ers_border_colour = False
start_time_for_ers_border_colour = 0
elapsed_time_for_ers_border_colour = 0
ers_border_colour_red = False

energy_store_level = 68 # energy store (ES) is just the battery # 68 is max

ers_recharge_mode = False
ers_overtake_mode = False

ers_lightning_bolt_image = pygame.image.load("ers_lightning_boltv1.png").convert_alpha()
ers_lightning_bolt_image = pygame.transform.scale(ers_lightning_bolt_image, (20, 28))

ers_lightning_bolt_red_image = pygame.image.load("ers_lightning_bolt_redv1.png").convert_alpha()
ers_lightning_bolt_red_image = pygame.transform.scale(ers_lightning_bolt_red_image, (20, 28))

ers_lightning_bolt_green_image = pygame.image.load("ers_lightning_bolt_greenv1.png").convert_alpha()
ers_lightning_bolt_green_image = pygame.transform.scale(ers_lightning_bolt_green_image, (20, 28))

FPS = new_FPS # DO NOT REMOVE THIS LINE

artificially_activate_end_game_leaderboard = False

final_lap_time_appended = False

cooldown_lap = False


def return_total_leftward_and_rightward_raycast_distances_separately():
    # leftward raycasting:
    leftward_raycast_distance_found = False
    leftward_pixel_colour = None # initialise as None
    leftward_raycast_iterator = 0

    # half leftward raycasting:
    half_leftward_raycast_distance_found = False
    half_leftward_pixel_colour = None # initialise as None
    half_leftward_raycast_iterator = 0

    # rightward raycasting:
    rightward_raycast_distance_found = False
    rightward_pixel_colour = None # initialise as None
    rightward_raycast_iterator = 0

    # half rightward raycasting:
    half_rightward_raycast_distance_found = False
    half_rightward_pixel_colour = None # initialise as None
    half_rightward_raycast_iterator = 0

    # forward raycasting:
    forward_raycast_distance_found = False
    forward_pixel_colour = None # initialise as None
    forward_raycast_iterator = 0

    max_distance = 360

    # main while loop - this means that all raycasting calculations run every single frame
    # it's not "and" - it's "or"
    while (not half_leftward_raycast_distance_found) or (not leftward_raycast_distance_found) or (not half_rightward_raycast_distance_found) or (not rightward_raycast_distance_found) or (not forward_raycast_distance_found):
        
        # leftward raycasting:
        if leftward_pixel_colour != (0, 150, 0) and leftward_pixel_colour != (150, 150, 149): # (150, 150, 149) is the section of road which is the pit lane entry before the marking
            if not leftward_raycast_distance_found:
                leftward_pixel_colour = screen.get_at((540-leftward_raycast_iterator, 360-leftward_raycast_iterator))
                

                pygame.draw.rect(screen, (255, 0, 0), (540-leftward_raycast_iterator, 358-leftward_raycast_iterator, 1, 1))

                leftward_raycast_iterator = leftward_raycast_iterator + 1
                if leftward_raycast_iterator >= max_distance:
                    leftward_raycast_distance_found = True
        else:
            leftward_raycast_distance_found = True



        # half leftward raycasting:
        if half_leftward_pixel_colour != (0, 150, 0) and half_leftward_pixel_colour != (150, 150, 149): # (150, 150, 149) is the section of road which is the pit lane entry before the pit lane marking
            if not half_leftward_raycast_distance_found:
                # validation check: use a try-except block to ensure that screen.get_at() doesn't crash when trying to get pixels which are off screen
                try:
                    half_leftward_pixel_colour = screen.get_at((540-half_leftward_raycast_iterator, 360-(half_leftward_raycast_iterator*2)))
                except IndexError:
                    pass
                
                pygame.draw.rect(screen, (255, 0, 0), (540-half_leftward_raycast_iterator, 358-(half_leftward_raycast_iterator*2), 1, 1))

                half_leftward_raycast_iterator = half_leftward_raycast_iterator + 1
                if half_leftward_raycast_iterator >= max_distance:
                    half_leftward_raycast_distance_found = True
        else:
            half_leftward_raycast_distance_found = True



        # rightward raycasting:
        if rightward_pixel_colour != (0, 150, 0) and rightward_pixel_colour != (150, 150, 149): # (150, 150, 149) is the section of road which is the pit lane entry before the pit lane marking
            if not rightward_raycast_distance_found:
                rightward_pixel_colour = screen.get_at((540+rightward_raycast_iterator, 360-rightward_raycast_iterator))

                pygame.draw.rect(screen, (255, 0, 0), (540+rightward_raycast_iterator, 358-rightward_raycast_iterator, 1, 1))

                rightward_raycast_iterator = rightward_raycast_iterator + 1
                if rightward_raycast_iterator >= max_distance:
                    rightward_raycast_distance_found = True
        else:
            rightward_raycast_distance_found = True



        # half rightward raycasting:
        if half_rightward_pixel_colour != (0, 150, 0) and half_rightward_pixel_colour != (150, 150, 149): # (150, 150, 149) is the section of road which is the pit lane entry before the marking
            if not half_rightward_raycast_distance_found:
                # validation check: use a try-except block to ensure that screen.get_at() doesn't crash when trying to get pixels which are off screen
                try:
                    half_rightward_pixel_colour = screen.get_at((540+half_rightward_raycast_iterator, 360-(half_rightward_raycast_iterator*2)))
                except IndexError:
                    pass
                
                pygame.draw.rect(screen, (255, 0, 0), (540+half_rightward_raycast_iterator, 358-(half_rightward_raycast_iterator*2), 1, 1))

                half_rightward_raycast_iterator = half_rightward_raycast_iterator + 1
                if half_rightward_raycast_iterator >= max_distance:
                    half_rightward_raycast_distance_found = True
        else:
            half_rightward_raycast_distance_found = True



        # forward raycasting
        if forward_pixel_colour != (0, 150, 0) and forward_pixel_colour != (150, 150, 149):
            # (150, 150, 149) is the section of road which is the pit lane entry before the marking
            if not forward_raycast_distance_found:
                # validation check: use a try-except block to ensure that screen.get_at() doesn't crash when trying to get pixels which are off screen
                try:
                    forward_pixel_colour = screen.get_at((540, 357-forward_raycast_iterator))
                except IndexError:
                    pass # don't return a new colour for the forward pixel
                
                pygame.draw.rect(screen, (255, 0, 0), (540, 357-forward_raycast_iterator, 1, 1))

                forward_raycast_iterator = forward_raycast_iterator + 1
                if forward_raycast_iterator >= 366:
                    forward_raycast_distance_found = True
        else:
            forward_raycast_distance_found = True


    half_leftward_raycast_distance, leftward_raycast_distance = half_leftward_raycast_iterator, leftward_raycast_iterator
    half_rightward_raycast_distance, rightward_raycast_distance = half_rightward_raycast_iterator, rightward_raycast_iterator
    forward_raycast_distance = forward_raycast_iterator
    return half_leftward_raycast_distance, leftward_raycast_distance, half_rightward_raycast_distance, rightward_raycast_distance, forward_raycast_distance



raycast_bot_up_arrow_activated = False
raycast_bot_down_arrow_activated = False
raycast_bot_left_arrow_activated = False
raycast_bot_right_arrow_activated = False
raycast_distance_difference = 0
additional_brake_speed = 0

bot_activated = False
def move_ai_bot_via_returning_boolean_flags(half_leftward_raycast_distance, leftward_raycast_distance, half_rightward_raycast_distance, rightward_raycast_distance, forward_raycast_distance):
    global raycast_bot_up_arrow_activated, raycast_bot_down_arrow_activated, raycast_bot_left_arrow_activated, raycast_bot_right_arrow_activated, raycast_distance_difference, additional_brake_speed
    raycast_bot_up_arrow_activated = False
    raycast_bot_down_arrow_activated = False
    raycast_bot_left_arrow_activated = False
    raycast_bot_right_arrow_activated = False

    raycast_distance_difference = 0
    raycast_difference_threshold = 0

    # if total leftward is more than the total rightward, turn left
    if leftward_raycast_distance+half_leftward_raycast_distance > rightward_raycast_distance+half_rightward_raycast_distance:
        raycast_distance_difference = (leftward_raycast_distance+half_leftward_raycast_distance) - (rightward_raycast_distance+half_rightward_raycast_distance)
        if raycast_distance_difference < raycast_difference_threshold: # only activate if the difference between the leftward and rightward raycasting distances is high enough beyond a certain threshold, i.e. you are close enough to either side of the track
            pass
        else:
            if track_speed*track_speed_text_scale_factor < 75:
                raycast_bot_left_arrow_activated = True

    # if total leftward is less than the total rightward, turn right
    if leftward_raycast_distance+half_leftward_raycast_distance < rightward_raycast_distance+half_rightward_raycast_distance:
        raycast_distance_difference = (rightward_raycast_distance+half_rightward_raycast_distance) - (leftward_raycast_distance+half_leftward_raycast_distance)
        if raycast_distance_difference < raycast_difference_threshold: # only activate if the difference between the leftward and rightward raycasting distances is high enough beyond a certain threshold, i.e. you are close enough to either side of the track
            pass
        else:
            raycast_bot_right_arrow_activated = True

    if leftward_raycast_distance+half_leftward_raycast_distance == rightward_raycast_distance+half_rightward_raycast_distance:
        pass # i.e. do nothing. this is ensured as all boolean flags are set to False to begin with anyway
    

    # HARD-CODED ELEMENTS:
    if raycast_distance_difference > 500: # if it's too close to the edge of the track, the larger the raycast_distance_difference, the closer to the edge of the track the car is at
        raycast_bot_up_arrow_activated = False
        raycast_bot_down_arrow_activated = True

    raycast_steering_multiplier = raycast_distance_difference/3 # change the rate of steering

    if 340 < forward_raycast_distance < 365 and 180 < (track_speed*track_speed_text_scale_factor): # remember max is 365 for forward ray casting, as this reaches the edge of the screen
        raycast_bot_up_arrow_activated = False
        additional_brake_speed = forward_raycast_distance*(3/365) # max additional brake speed of 3
    else:
        if track_speed*track_speed_text_scale_factor < 50:
            raycast_bot_up_arrow_activated = True

    return raycast_bot_up_arrow_activated, raycast_bot_down_arrow_activated, raycast_bot_left_arrow_activated, raycast_bot_right_arrow_activated, raycast_distance_difference, additional_brake_speed, raycast_steering_multiplier

black_foreground = pygame.image.load("black_foreground_1080x810.png").convert_alpha()
black_foreground_activated = False
black_foreground_alpha_iterator = 0
def restart_timed_lap_fade_in_and_out_and_lights_sequence():
    global black_foreground_activated, fade_in, black_foreground_alpha_iterator
    black_foreground_activated = True
    fade_in = True
    black_foreground_alpha_iterator = 0

track_speed_text_scale_factor = 0.1

drs_enabled = False

drs_indicator_grey = render_text_once(font_size_30, "DRS", True, (200, 200, 200))
drs_indicator_green = render_text_once(font_size_30, "DRS", True, (0, 255, 0))



# ENGINE SOUND
# --- Init ---
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# --- Load Sound and Setup ---
base_sound = pygame.mixer.Sound("idle.wav")
base_array = pygame.sndarray.array(base_sound)
channel = pygame.mixer.Channel(0)  # Dedicated channel for engine # 0 = channel 1, 1 = channel 2...

# --- Gear/Throttle State ---
current_gear = 0
gear_ratios = [4.4, 3.5, 2.3, 1.8, 1.2, 0.6, 0.4, 0.1]  # 8 gears
rpm_upshift_changes = [3000, 2500, 2250, 2000, 1750, 1500, 1300, 1200]
rpm_downshift_changes = rpm_upshift_changes[::-1]

rpm_text = render_text_once(font_size_20, "RPM", False, (255, 255, 255))

attempt_text = render_text_once(font_size_30, "Attempt ", False, (255, 255, 255))

# RPM - REVOLUTIONS PER MINUTE - UNOFFICIAL DATA
# the variable name "RPM" is a deeper shade of blue than "rpm". use "rpm" to be safe
# IDLE RPM = 4500
rpm = 4500 # maps from speedmaxratio 100
rpm_min = 4000
rpm_max = 14000
throttle_pressed = False

# Sound update timing
last_sound_update = 0
min_sound_interval = 0.06 # 60ms between sound updates

# --- Pitch Shift ---
def change_pitch(sound_array, pitch_factor):
    indices = np.round(np.arange(0, len(sound_array), pitch_factor))
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[indices]

def smooth_pitch(current_pitch, target_pitch, smooth_factor=0.4):
    return current_pitch + (target_pitch - current_pitch) * smooth_factor

def update_volume(rpm, rpm_min, rpm_max):
    # update volume based on RPM, mapped from 0.3 to 1.0
    if rpm < 10200:
        volume = max(0.3, min((rpm - rpm_min) / (rpm_max - rpm_min) * 0.8 + 0.3, 1.0))
    else:
        # After 11000 RPM, apply exponential growth for volume
        volume = 0.6 + (1.0 - 0.3) * ((rpm - 10200) / (rpm_max - 10200)) ** 15
        volume = min(volume, 1.0)  # Cap volume at 1.0

    channel.set_volume(volume)
    # channel.set_volume(0)
    return volume

# --- Loop Control ---
current_pitch = 1.0
current_sound = None

# ENGINE SOUNDS
channel.play(base_sound, loops=-1)

# Create a channel for the second track
# GEAR CHANGES
channel2 = pygame.mixer.Channel(1) # 0 accesses the first channel, 1 accesses the second channel
channel2.set_volume(1)  # Set the volume for the second track

# Create a channel for the third track
# START LIGHTS
channel3 = pygame.mixer.Channel(2) 
channel3.set_volume(1)

# Create a channel for the fourth track
# MAIN SOUNDTRACK
channel4 = pygame.mixer.Channel(3) 
channel4.set_volume(0.275)
channel4.set_volume(0)

channel4.play(pygame.mixer.Sound("flippy bit soundtrack smooth loop.mp3"), loops=-1, fade_ms=1000)
main_soundtrack_enabled = True

# Create a channel for the fifth track
# GRASS SOUNDS
channel5 = pygame.mixer.Channel(4) 
channel5.set_volume(0)  
channel5.play(pygame.mixer.Sound("rustling grassv6.mp3"), loops=-1)

# Create a channel for the sixth track
# WIND SOUNDS
channel6 = pygame.mixer.Channel(5) 
channel6.set_volume(0)
channel6.play(pygame.mixer.Sound("windv2.mp3"), loops=-1)

# Create a channel for the seventh track
# BOTTOMING OUT SOUNDS
channel7 = pygame.mixer.Channel(6) 
channel7.set_volume(0)
channel7.play(pygame.mixer.Sound("bottoming outv1.mp3"), loops=-1)

# Create a channel for the eighth track
# SPLASH SCREEN SEQUENCE ENGINE SOUNDS
# [DEFINED IN SPLASH SCREEN PROCEDURE]


# CLUTCH
clutch_depressed = False


# OFF-TRACK TIME PENALTY GRAPHIC NOTIFICATION
off_track_time_penalty_graphic = pygame.image.load("off-track time penalty graphic.png").convert_alpha()
off_track_time_penalty_graphic = pygame.transform.scale_by(off_track_time_penalty_graphic, 0.25)
off_track_time_penalty = 0.000
formatted_off_track_time_penalty = "00:00.000"
time_started_for_off_track_time_penalty_interval = False
elapsed_time_for_off_track_time_penalty_interval = 0

# OFF-TRACK TIME PENALTY GRAPHIC NOTIFICATION LINGER
start_time_for_off_track_time_penalty_linger = 0

# main game loop
running = True
while running:
    # IMPORTANT: *****YOU MUST MULTIPLY ANY VISUAL MOVING OBJECT/MOVING CALCULATIONS ON SCREEN WITH DT INSIDE THE MAIN WHILE LOOP WHICH GETS EXECUTED EVERY FRAME*****, OTHERWISE THE SPEEDS OF THE MOVING OBJECTS/MOVING CALCULATIONS WILL NOT BE CONSISTENT ACROSS VARYING FRAMERATES
    dt = clock.tick(FPS) / 1000.0 # delta time calculates the amount of time has elapsed since the last frame, and returns that time in milliseconds. / 1000.0 then converts that time from milliseconds to seconds
    current_fps = clock.get_fps()
    current_fps = int(current_fps)
    pygame.display.set_caption(f'Formula 1 Pixel Racing | FPS: {current_fps}') # consider moving these out of the while loop for a slight performance increase?

    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN: # whenever you have this KEYDOWN thing, pygame reads the input once when you press a key down
            if keys[pygame.K_t]:
                restart_timed_lap_fade_in_and_out_and_lights_sequence()


            if advanced_controls_flag:
                if keys[pygame.K_4]: # you cannot put (gear_down_macro_list[frame_counter] == 1 and playing_back) here because this line is not accessed through the while loop every frame
                    if gear > 0:
                        gear = gear - 1
                        # if recording:
                            # gear_down_macro_list[frame_counter] = 1


                if keys[pygame.K_8]: # you cannot put (gear_up_macro_list[frame_counter] == 1 and playing_back) here because this line is not accessed through the while loop every frame
                    if gear < 8:
                        gear = gear + 1
                        # if recording:
                            # gear_up_macro_list[frame_counter] = 1



            if not advanced_controls_flag:
                if not automatic:
                    if keys[pygame.K_1]: # you cannot put (gear_down_macro_list[frame_counter] == 1 and playing_back) here because this line is not accessed through the while loop every frame
                        if gear > 0:
                            gear = gear - 1
                            rpm += rpm_downshift_changes[gear] * 2
                            # if recording:
                                # gear_down_macro_list[frame_counter] = 1

                            
                    if keys[pygame.K_2]: # you cannot put (gear_up_macro_list[frame_counter] == 1 and playing_back) here because this line is not accessed through the while loop every frame
                        if gear < 8:
                            gear = gear + 1
                            rpm -= rpm_upshift_changes[current_gear] * 1.5
                            # if recording:
                                # gear_up_macro_list[frame_counter] = 1


            if keys[pygame.K_z] and timed_lap_has_started:
                automatic = True
            if keys[pygame.K_x]:
                automatic = False

            # ADVANCED CONTROLS: DEACTIVATED INDEFINITELY
            if keys[pygame.K_a] and keys[pygame.K_LCTRL]:
                if not advanced_controls_flag:
                    # FALSE - DEACTIVATED INDEFINITELY
                    advanced_controls_flag = False
                else:
                    # FALSE - DEACTIVATED INDEFINITELY
                    advanced_controls_flag = False

            # RECHARGE MODE
            if keys[pygame.K_g] and timed_lap_has_started:
                ers_recharge_mode = not ers_recharge_mode

            if keys[pygame.K_TAB]:
                LDY = -screen_size_y # leaderboard dropdown y value # LDY should range from screen_size_y (810) to 0
                if artificially_activate_end_game_leaderboard:
                    artificially_activate_end_game_leaderboard = False
                    final_lap_time_appended = False
                else:
                    artificially_activate_end_game_leaderboard = True

            if keys[pygame.K_b]:
                if not bot_activated:
                    bot_activated = True
                else:
                    bot_activated = False
                    raycast_bot_up_arrow_activated = False
                    raycast_bot_down_arrow_activated = False
                    raycast_bot_left_arrow_activated = False
                    raycast_bot_right_arrow_activated = False
    
            if keys[pygame.K_RSHIFT] and timed_lap_has_started:
                drs_enabled = not drs_enabled

            if keys[pygame.K_m]:
                if main_soundtrack_enabled:
                    channel4.set_volume(0)
                    main_soundtrack_enabled = False
                else:
                    channel4.set_volume(0.3)
                    main_soundtrack_enabled = True

    if keys[pygame.K_SPACE]:
        clutch_depressed = True
    else:
        clutch_depressed = False


    # Pitch calculation
    target_pitch = max(0.5, min((rpm - rpm_min) / (rpm_max - rpm_min) * 1.5 + 0.5, 2.0))
    target_pitch *= 4  # Boost overall pitch
    current_pitch = smooth_pitch(current_pitch, target_pitch)

    # Update sound only if pitch has changed significantly and enough time has passed
    current_time = pygame.time.get_ticks() / 1000
    if abs(current_pitch - target_pitch) > 0.00012 and (current_time - last_sound_update) > min_sound_interval:
        new_array = change_pitch(base_array, current_pitch)
        new_sound = pygame.sndarray.make_sound(new_array)
        if channel.get_busy():
            channel.stop()
        channel.play(new_sound, loops=-1)
        last_sound_update = current_time

    volume = update_volume(rpm, rpm_min, rpm_max)


    
    if (gear_up_macro_list[frame_counter] == 1 and playing_back):
        if gear < 8:
            gear = gear + 1

    if (gear_down_macro_list[frame_counter] == 1 and playing_back):
        if gear > 0:
            gear = gear - 1

    # keys = pygame.key.get_pressed()
    
    if keys[pygame.K_0]:
        track_speed = track_speed + 5

    if keys[pygame.K_LSHIFT] and timed_lap_has_started and not ers_recharge_mode:
        ers_overtake_mode = True
    else:
        ers_overtake_mode = False




    if track_speed > 0:
        # WIND NOISES
        # print((track_speed*track_speed_text_scale_factor*0.01*0.15))
        channel6.set_volume((track_speed*track_speed_text_scale_factor*0.01*0.12))

        if track_speed*track_speed_text_scale_factor > 150:
            # BOTTOMING OUT NOISES
            channel7.set_volume((track_speed*track_speed_text_scale_factor*0.01*0.2))
        else:
            channel7.set_volume(0)


    

    screen.fill((0, 150, 0)) # moved screen.fill(100, 100, 100) to way higher before image_to_be_blitted = track_images[i][j] so that the screen SHOULDN’T change before screen.blit() is reached - reduced flickering # NEVERMIND THIS INTERFERES WITH PIXEL CHECKING COLOUR DETECTION - SEE testtrack.pub page 46 # LOL NEVERMIND AGAIN LOL - having screen.fill() near the top of the while loop solved the flickering problem. to fix both the flickering problem, im gonna move to timer_toggle if statement to before the screen.fill() function, both near the top of the while loop

    x_y_conversion(track_angle)



    ers_border_colour_red = False

    # using KEYDOWN may be more efficient for key presses that are being checked every frame. ask ChatGPT
    
    # print(throttle_macro_list[frame_counter], playing_back)
    throttle_pressed = False

    if ((keys[pygame.K_UP] and not wasd_keys_activated and timed_lap_has_started) or (raycast_bot_up_arrow_activated) or (keys[pygame.K_w] and wasd_keys_activated and timed_lap_has_started)) or (advanced_controls_flag and (keys[pygame.K_f] or keys[pygame.K_h])) or (throttle_macro_list[frame_counter] == 1 and playing_back):
        # print(clutch_depressed)
        
        # print("les go")
        # if (throttle_macro_list[frame_counter] == 1 and playing_back):
           # y_intercept = 7.75
        # else:
            # y_intercept = 3

        # if 1 <= gear <= 8:
            # rate_of_change_of_speed = (0.03*track_speed) + 100
        
        """
        Transforming the gear ratios:
        - To stretch a graph on the x-axis, you need to adjust the x-coordinates (track_speed) in the equation.
        - You replace x (track_speed) with x/k (track_speed/gear_ratios_horizontal_stretch_scale_factor), where k is the scale factor.
        """
        throttle_pressed = True

        gear_ratios_horizontal_stretch_scale_factor = 1.5

        if not drs_enabled:
            y_intercept = 6
        else:
            y_intercept = 8

        # print("y_intercept:", y_intercept, "   drs_enabled:", drs_enabled)

        if gear == 1:
            rate_of_change_of_speed = (-0.00048*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**2) + (0.116*(track_speed/gear_ratios_horizontal_stretch_scale_factor)) + y_intercept
        if gear == 2:
            rate_of_change_of_speed = (-0.00000082489*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**3) + (0.000302222*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**2) + y_intercept
        if gear == 3:
            rate_of_change_of_speed = (-0.00000029369*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**3) + (0.000142844*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**2) + y_intercept
        if gear == 4:
            rate_of_change_of_speed = (-0.00000000027277*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**4) + (0.00000016638*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**3) + y_intercept
        if gear == 5:
            rate_of_change_of_speed = (-0.00000000010252*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**4) + (0.000000074521*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**3) + y_intercept
        if gear == 6:
            rate_of_change_of_speed = (-0.000000000000056706*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**5) + (0.000000000047912*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**4) + y_intercept
        if gear == 7:
            rate_of_change_of_speed = (-0.000000000000016639*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**5) + (0.000000000015639*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**4) + y_intercept
        if gear == 8:
            rate_of_change_of_speed = (-0.0000000000000024104*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**5) + (0.0000000000020874*(track_speed/gear_ratios_horizontal_stretch_scale_factor)**4) + y_intercept

        # print(rate_of_change_of_speed)
        # ACCELERATION AMPLIFIER/DAMPENER

        # you CAN put this in the throttle indicator code since it's just the same thing, really


        if gear == 0: # FIXES NEUTRAL PROBLEM WHERE THE SPEED JUST SNAPS TO 0
            pass
        else:
            if not advanced_controls_flag:
                if not ers_overtake_mode or (ers_overtake_mode and energy_store_level <= 0):
                    rate_of_change_of_speed = rate_of_change_of_speed*25

                if ers_overtake_mode and energy_store_level > 0:
                    rate_of_change_of_speed = rate_of_change_of_speed*27.5
                
            else: # if advanced_controls_flag is enabled:
                if keys[pygame.K_f] and keys[pygame.K_h]:
                    rate_of_change_of_speed = rate_of_change_of_speed*25
                if keys[pygame.K_f] != keys[pygame.K_h]: # XOR OPERATION
                    rate_of_change_of_speed = rate_of_change_of_speed*12.5

            # WRONG: THIS ISN'T AN XOR OPERATION: - YOU NEED AN XOR OPERATION FOR THIS
            # if keys[pygame.K_f] or keys[pygame.K_h]:
                # rate_of_change_of_speed = rate_of_change_of_speed*12.5



        if not ers_recharge_mode and ers_overtake_mode and energy_store_level > -1:

            if not time_started_for_ers_border_colour:
                time_started_for_ers_border_colour = True
                start_time_for_ers_border_colour = time.time()
            else:
                elapsed_time_for_ers_border_colour = time.time() - start_time_for_ers_border_colour

            if elapsed_time_for_ers_border_colour < 0.1: # does things between 0 and 0.1 seconds
                ers_border_colour_red = True

            if elapsed_time_for_ers_border_colour > 0.2: # doesn't do anything between 0.1 and 0.2 seconds
                elapsed_time_for_ers_border_colour = 0
                ers_border_colour_red = False

                if track_speed > 0:
                    energy_store_level = energy_store_level - 1
                    
                time_started_for_ers_border_colour = False



    if ((not wasd_keys_activated and not keys[pygame.K_UP]) or (wasd_keys_activated and not keys[pygame.K_w])) and (not raycast_bot_up_arrow_activated) and (not playing_back) and (not keys[pygame.K_f]) and (not keys[pygame.K_h]) and (not (keys[pygame.K_f] != keys[pygame.K_h])):
        if rate_of_change_of_speed > 0:
            if track_speed > -1:
                rate_of_change_of_speed = rate_of_change_of_speed - 7500*dt # -1.5 is the naturally adjusting jerk

    if playing_back:
        if throttle_macro_list[frame_counter] == 0: # i.e. not accelerating
            if rate_of_change_of_speed > 0:
                if track_speed > -1:
                    rate_of_change_of_speed = rate_of_change_of_speed - 7500*dt 


    # print(rate_of_change_of_speed)

    # print(track_speed, rate_of_change_of_speed) # look at these two values in the terminal below in the left bottom corner
    track_speed = track_speed + (rate_of_change_of_speed * dt)


    if track_speed < 0: # these limiters are fine - they do not get stuck at 0
        track_speed = 0
        rate_of_change_of_speed = 0

    if (track_angle >= 360) or (track_angle <= -360):
        track_angle = 0

    down_arrow_depressed = False # fixes automatic downshifting when throttle and brake are applied at the same time - since brake takes priority over throttle, the car slows down
    if ((keys[pygame.K_DOWN] and not wasd_keys_activated and timed_lap_has_started) or (raycast_bot_down_arrow_activated) or (keys[pygame.K_s] and wasd_keys_activated and timed_lap_has_started)) or (advanced_controls_flag and (keys[pygame.K_c] or keys[pygame.K_n])) or (brake_macro_list[frame_counter] == 1 and playing_back):
        down_arrow_depressed = True # fixes automatic downshifting when throttle and brake are applied at the same time - since brake takes priority over throttle, the car slows down
        # rate_of_change_of_speed = rate_of_change_of_speed - 0.2
        drs_enabled = False

        if not advanced_controls_flag:
            if not raycast_bot_down_arrow_activated:
                track_speed = track_speed - 7 # changing track_speed instead of rate_of_change_of_speed is better because when you press throttle and brake, brake now gets prioritised.
            else:
                # track_speed = track_speed - ((track_speed*(6/250))+additional_brake_speed) # 6 is brake speed and 200 is max speed
                track_speed = track_speed - 7
        else:
            if keys[pygame.K_c] and keys[pygame.K_n]:
                track_speed = track_speed - 8
            if keys[pygame.K_c] != keys[pygame.K_n]: # XOR OPERATION
                track_speed = track_speed - 4



    # rate_of_change_of_turning_speed WRITTEN BY CHATGPT - FOR SOME REASON THE rate_of_change_of_turning_speed DIDN'T RETURN TO 0 WHENEVER I WASN'T PRESSING ANYTHING - IT GOT STUCK AT LIKE 0.049999999999 OR SOMETHING - check ChatGPT on 15/06/24
    if ((keys[pygame.K_LEFT] and not wasd_keys_activated and timed_lap_has_started) or (raycast_bot_left_arrow_activated) or (keys[pygame.K_a] and wasd_keys_activated and timed_lap_has_started)) or (advanced_controls_flag and (keys[pygame.K_q] or keys[pygame.K_w])) or (leftward_steering_macro_list[frame_counter] == 1 and playing_back):
        if not advanced_controls_flag:
            if not raycast_bot_left_arrow_activated:
                rotation_speed = 60
            else:
                # rotation_speed = raycast_distance_difference*(70/500)*1 # 70 = rotation speed # look at Teams self-DMs on this date - another graph was made!
                if track_speed*track_speed_text_scale_factor < 75:
                    rotation_speed = 20
                else:
                    rotation_speed = 0
                # print("ROT:", rotation_speed, raycast_distance_difference)
        else:
            if keys[pygame.K_q] and keys[pygame.K_w]:
                rotation_speed = 60
            if keys[pygame.K_q] != keys[pygame.K_w]:
                rotation_speed = 35
        
        rate_of_change_of_turning_speed -= 0.060 # THIS VALUE CAN BE CHANGED - SWINGING
        if rate_of_change_of_turning_speed < -1:  # Limiter
            rate_of_change_of_turning_speed = -1

        if not raycast_bot_left_arrow_activated:
            wheel_angle = wheel_angle + 2

            # WHEEL ANGLE LIMITER
            if wheel_angle > 19:
                wheel_angle = 19

        else:
            wheel_angle = rotation_speed * (19/70)

        # if recording:
            # leftward_steering_macro_list[frame_counter] = 1

    elif ((keys[pygame.K_RIGHT] and not wasd_keys_activated and timed_lap_has_started) or (raycast_bot_right_arrow_activated) or (keys[pygame.K_d] and wasd_keys_activated and timed_lap_has_started)) or (advanced_controls_flag and (keys[pygame.K_o] or keys[pygame.K_p])) or (rightward_steering_macro_list[frame_counter] == 1 and playing_back):
        if not advanced_controls_flag:
            if not raycast_bot_right_arrow_activated:
                rotation_speed = 60
            else:
                # rotation_speed = raycast_distance_difference*(70/500)*1 # 70 = rotation speed # look at Teams self-DMs on this date - another graph was made!
                if track_speed*track_speed_text_scale_factor < 75:
                    rotation_speed = 20
                else:
                    rotation_speed = 60
                # print("ROT:", rotation_speed, raycast_distance_difference)
        else:
            if keys[pygame.K_o] and keys[pygame.K_p]:
                rotation_speed = 60
            if keys[pygame.K_o] != keys[pygame.K_p]:
                rotation_speed = 35
        
        rate_of_change_of_turning_speed += 0.060 # THIS VALUE CAN BE CHANGED - SWINGING
        if rate_of_change_of_turning_speed > 1:  # Limiter
            rate_of_change_of_turning_speed = 1


        if not raycast_bot_right_arrow_activated:
            wheel_angle = wheel_angle - 2

            # WHEEL ANGLE LIMITER
            if wheel_angle < -19:
                wheel_angle = -19

        else:
            wheel_angle = rotation_speed * (19/70)
            wheel_angle = wheel_angle * -1

        # if recording:
            # rightward_steering_macro_list[frame_counter] = 1

    else:
        # NATURALLY ADJUSTING:
        # Naturally adjust turning speed to 0 when no key is pressed
        if rate_of_change_of_turning_speed > 0:
            rate_of_change_of_turning_speed -= 0.20 # THIS VALUE CAN BE CHANGED
            if rate_of_change_of_turning_speed < 0:  # Ensure it doesn't go negative
                rate_of_change_of_turning_speed = 0
        elif rate_of_change_of_turning_speed < 0:
            rate_of_change_of_turning_speed += 0.20 # THIS VALUE CAN BE CHANGED
            if rate_of_change_of_turning_speed > 0:  # Ensure it doesn't go positive
                rate_of_change_of_turning_speed = 0


    # NATURALLY ADJUSTING
    if wheel_angle > 0:
        wheel_angle = wheel_angle - 1
    if wheel_angle < 0:
        wheel_angle = wheel_angle + 1

    if track_speed <= 100:
        steering_pivot_limiter_multiple = track_speed*0.01
    else:
        steering_pivot_limiter_multiple = 1

    track_angle = track_angle + (rotation_speed * rate_of_change_of_turning_speed * steering_pivot_limiter_multiple * dt)

    # print("player_found:", player_found)
    # only activates when you first render in
    if not player_found:
        # the following code correctly runs once:
        # idk why i need the following try-except block:
        try:
            temp_i_value, temp_j_value = locate_the_player_and_return_i_and_j()
        except TypeError:
            print("erm... player not found somehow? rendering image at bitmap[0][0] by default.")
            temp_i_value = 0
            temp_j_value = 0

        render_image_then_apply_and_update_offsets(temp_i_value, temp_j_value)



    """
    USE A TRY-EXCEPT BLOCK TO FIX THIS:
    temp_i_value, temp_j_value = search_the_current_tile_and_8_surrounding_tiles(temp_i_value, temp_j_value) # it takes in an i and j value and outputs a new i and j value
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
    TypeError: cannot unpack non-iterable NoneType object
    """

    temp_i_value, temp_j_value = search_the_current_tile_and_8_surrounding_tiles(temp_i_value, temp_j_value) # it takes in an i and j value and outputs a new i and j value

    # this if statement only runs once when a new quadrant/tile is entered into
    if tile_needs_to_be_changed:
        # FRONT BUFFER:
        # screen.blit(track_image, track_rect) # displays the current image over itself # i think it might be 'front' buffer # this acts as a 'back buffer' (i learnt the term from ChatGPT but thought up of this method myself) - basically, the previous image gets rendered again on top of itself. this is the back buffer. the new image gets DEFINED (not rendered yet - 'rendered' is when screen.blit() is present) with image_to_be_blitted = track_images[i][j]. then the back buffer gets overwritten and stops getting rendered with screen.blit(track_image, track_rect) many lines down
        # print("temp_i_value, temp_j_value:", temp_i_value, temp_j_value)

        # HANDLES NEGATIVE INDEXES - MAKES SURE THAT TILE(S) DON'T DISAPPEAR WHEN EITHER temp_i_value OR temp_j_value BECOMES NEGATIVE AT THE EDGES OF THE MAP
        if (temp_i_value < 0) or (temp_j_value < 0):
            pass
        else:
            # THE FOLLOWING TRY-EXCEPT BLOCK PREVENTS THE GAME FROM CRASHING DUE TO INDEX OUT OF RANGE ISSUES WITH track_images[temp_i_value][temp_j_value]
            try:
                render_image_then_apply_and_update_offsets(temp_i_value, temp_j_value)
            except IndexError:
                pass


    rotated_image_to_be_blitted = pygame.transform.rotate(image_to_be_blitted, track_angle) # .rotozoom() is considerably worse than .rotate()
    offset_rotated = screen_center + (track_pos - screen_center).rotate(-track_angle) # track_pivot was replaced with screen_center here because they were initialised to be the same vector/x and y coordinates
    image_to_be_blitted_rect = rotated_image_to_be_blitted.get_rect(center = offset_rotated)
    

    screen.blit(rotated_image_to_be_blitted, image_to_be_blitted_rect)


    original_car_image_rect = original_car_image.get_rect(center=(screen_size_x//2, (screen_size_y//2)+10)) # THE CAR IS ALWAYS FIXED TO carcentrex AND carcentrey; THE CAR DOES NOT MOVE ON SCREEN
    screen.blit(original_car_image, original_car_image_rect.topleft)


    if timer_toggle:
        # locate_the_player_and_return_i_and_j() # why on Earth did I call locate_the_player_and_return_i_and_j() here in the first place anyway? I think I was mistakenly put it here when I was meant to put it in "if keys[pygame.K_t]:", then I DID put it in "if keys[pygame.K_t]:", then forgot to remove it HERE
        front_wing_pixel_color = screen.get_at((540, 360)) # CHANGED FROM 365 TO 360
        # pygame.draw.rect(screen, (255, 0, 0), (540, 360, 1, 1))
        # print(front_wing_pixel_color)

        left_front_tyre_pixel_colour = screen.get_at((516, 380))
        if left_front_tyre_pixel_colour == (0, 150, 0):
            track_speed = track_speed*0.997 #  this slows down the car
            # print("left front")

        right_front_tyre_pixel_colour = screen.get_at((564, 380))
        if right_front_tyre_pixel_colour == (0, 150, 0):
            track_speed = track_speed*0.997 #  this slows down the car
            # print("right front")

        left_rear_tyre_pixel_colour = screen.get_at((515, 442))
        if left_rear_tyre_pixel_colour == (0, 150, 0):
            track_speed = track_speed*0.997 #  this slows down the car
            # print("left rear")

        right_rear_tyre_pixel_colour = screen.get_at((565, 442))
        if right_rear_tyre_pixel_colour == (0, 150, 0):
            track_speed = track_speed*0.997 #  this slows down the car
            # print("right rear")


        if (left_front_tyre_pixel_colour == (0, 150, 0)) or (right_front_tyre_pixel_colour == (0, 150, 0)) or (left_rear_tyre_pixel_colour == (0, 150, 0)) or (right_rear_tyre_pixel_colour == (0, 150, 0)):
            on_grass = True
        else:
            on_grass = False

        # starting the timed lap at the finish line
        if front_wing_pixel_color == ((254, 254, 254) or (1, 0, 0)) and (not sector1_passed) and (not sector2_passed) and (not sector3_passed):
            start_time = time.time()
            raycast_bot_up_arrow_activated = False
            commence_lights_sequence = False
            timed_lap_has_started = True # this boolean flag fixes the absurd timing number just before a timed lap has started



        # sector 1 complete marking
        elif front_wing_pixel_color == (255, 255, 254) and (not sector1_passed) and (not sector2_passed) and (not sector3_passed):
            sector1_passed = True
            sector1_time = current_formatted_elapsed_time


            # in actual F1 timing telemetry, sector times are not printed as something like 00:14.567. they are printed as 14.567, so do the following:
            if (sector1_time[0] == "0") and (sector1_time[1] == "0"):
                print("SECTOR 1:", sector1_time[3:9])


                sector1_time_text = render_text_once(font_size_30, "S1: "+sector1_time[3:9], True, (255, 255, 255))
            else:
                # i.e. if the current_formatted_elapsed_time/sector1_time starts with 00
                print("SECTOR 1:", sector1_time)
                sector1_time_text = render_text_once(font_size_30, "S1: "+sector1_time, True, (255, 255, 255))



            if len(sector1_times_list) == 0:
                sector1_colour = green_colour
            else:
                previous_best_sector1_time = return_minimum_of_list(sector1_times_list)
                
                if sector1_time <= previous_best_sector1_time: # i.e. if the current, new sector2_time is less than or equal to (faster than or the same as) the previous fastest sector2_time
                    sector1_colour = green_colour
                else:
                    sector1_colour = yellow_colour

                sector1_delta_time = return_difference_between_two_formatted_times_as_a_float(sector1_time, previous_best_sector1_time)
                formatted_sector1_delta_time = format_sector_delta_time(sector1_delta_time)

                if formatted_sector1_delta_time[0] == "-": # i.e. if formatted_sector1_delta_time is negative
                    formatted_sector1_delta_time_text = render_text_once(font_size_30, formatted_sector1_delta_time, True, (0, 255, 0))
                else:
                    formatted_sector1_delta_time_text = render_text_once(font_size_30, formatted_sector1_delta_time, True, yellow_colour)
            
            sector1_times_list.append(sector1_time)

             ##### INSTEAD OF USING APPEND, USE A LINEAR SEARCH TO FIND THE END OF THE LIST AND ADD ON A VALUE THERE #####

            # it works! all we need to do now is set each sector's boolean flag to be false when we cross the finish line too so we can do consecutive timed laps (icl though that would invalidate the lap cuz we get a running start - normally you dont get a running start but whatever)



        # sector 2 complete marking:
        elif front_wing_pixel_color == (255, 254, 254) and (sector1_passed) and (not sector2_passed) and (not sector3_passed):

            sector2_passed = True

            instantaneous_cumulative_formatted_elapsed_time_at_sector2_complete_marking_for_sector3_calculation = current_formatted_elapsed_time
            # sector1_time is now saved as a formatted string instead of a float number
            # you need to do current time - sector1_time

            
            sector2_time = convert_seconds_and_milliseconds_into_formatted_time(return_difference_between_two_formatted_times_as_a_float(current_formatted_elapsed_time, sector1_time))
            # print("S2 ayo?", sector2_time, current_formatted_elapsed_time, sector1_time)
            # in actual F1 timing telemetry, sector times are not printed as something like 00:14.567. they are printed as 14.567, so do the following:
            if (sector2_time[0] == "0") and (sector2_time[1] == "0"):
                print("SECTOR 2:", sector2_time[3:9])
                sector2_time_text = render_text_once(font_size_30, "S2: "+sector2_time[3:9], True, (255, 255, 255))
            else:
                # i.e. if the current_formatted_elapsed_time/sector1_time starts with 00
                print("SECTOR 2:", sector2_time)
                sector2_time_text = render_text_once(font_size_30, "S2: "+sector2_time, True, (255, 255, 255))



            if len(sector2_times_list) == 0:
                sector2_colour = green_colour
            else:
                previous_best_sector2_time = return_minimum_of_list(sector2_times_list)
                
                if sector2_time <= previous_best_sector2_time: # i.e. if the current, new sector2_time is less than or equal to (faster than or the same as) the previous fastest sector2_time
                    sector2_colour = green_colour
                else:
                    sector2_colour = yellow_colour

                sector2_delta_time = return_difference_between_two_formatted_times_as_a_float(sector2_time, previous_best_sector2_time)
                formatted_sector2_delta_time = format_sector_delta_time(sector2_delta_time)

                if formatted_sector2_delta_time[0] == "-": # i.e. if formatted_sector2_delta_time is negative
                    formatted_sector2_delta_time_text = render_text_once(font_size_30, formatted_sector2_delta_time, True, (0, 255, 0))
                else:
                    formatted_sector2_delta_time_text = render_text_once(font_size_30, formatted_sector2_delta_time, True, yellow_colour)
            
            sector2_times_list.append(sector2_time)


        # finish line or sector 3 complete marking:
        elif front_wing_pixel_color == ((254, 254, 254) or (1, 0, 0)) and (sector1_passed) and (sector2_passed) and (not sector3_passed):
            sector3_passed = True

            # sector1_time is now saved as a formatted string instead of a float number
            # you need to do current time - sector1_time

            sector3_time = convert_seconds_and_milliseconds_into_formatted_time(return_difference_between_two_formatted_times_as_a_float(current_formatted_elapsed_time, instantaneous_cumulative_formatted_elapsed_time_at_sector2_complete_marking_for_sector3_calculation)) # THIS IS WHERE THE BUG IS! TRY INPUTTING "00:36.000" - "00:15.000" IN THIS FUNCTION
            # print("S3 ayo?", sector3_time, current_formatted_elapsed_time, instantaneous_cumulative_formatted_elapsed_time_at_sector2_complete_marking_for_sector3_calculation)
            
            # in actual F1 timing telemetry, sector times are not printed as something like 00:14.567. they are printed as 14.567, so do the following:
            if (sector3_time[0] == "0") and (sector3_time[1] == "0"):
                print("SECTOR 3:", sector3_time[3:9])
                sector3_time_text = render_text_once(font_size_30, "S3: "+sector3_time[3:9], True, (255, 255, 255))
            else:
                # i.e. if the current_formatted_elapsed_time/sector1_time starts with 00
                print("SECTOR 3:", sector3_time)
                sector3_time_text = render_text_once(font_size_30, "S3: "+sector3_time, True, (255, 255, 255))



            if len(sector3_times_list) == 0:
                sector3_colour = green_colour
            else:
                previous_best_sector3_time = return_minimum_of_list(sector3_times_list)
                
                if sector3_time <= previous_best_sector3_time: # i.e. if the current, new sector3_time is less than or equal to (faster than or the same as) the previous fastest sector2_time
                    sector3_colour = green_colour
                else:
                    sector3_colour = yellow_colour

                sector3_delta_time = return_difference_between_two_formatted_times_as_a_float(sector3_time, previous_best_sector3_time)
                formatted_sector3_delta_time = format_sector_delta_time(sector3_delta_time)

                if formatted_sector3_delta_time[0] == "-": # i.e. if formatted_sector3_delta_time is negative
                    formatted_sector3_delta_time_text = render_text_once(font_size_30, formatted_sector3_delta_time, True, (0, 255, 0))
                else:
                    formatted_sector3_delta_time_text = render_text_once(font_size_30, formatted_sector3_delta_time, True, yellow_colour)
            
            sector3_times_list.append(sector3_time)
        

            final_lap_time = current_formatted_elapsed_time

            if off_track_time_penalty > 0:
                print("yee", final_lap_time, off_track_time_penalty)

                final_lap_time_seconds_and_milliseconds = convert_formatted_time_into_seconds_and_milliseconds(final_lap_time)
                final_lap_time_seconds_and_milliseconds = final_lap_time_seconds_and_milliseconds + off_track_time_penalty
                final_lap_time = convert_seconds_and_milliseconds_into_formatted_time(final_lap_time_seconds_and_milliseconds)

                print("haw", final_lap_time)

            print("FULL LAP TIME:", final_lap_time) # storing it in another variable cuz why not


    if -9.4 < wheel_angle < 9.4:
        wheel_angle_offset_y = 1
    else:
        wheel_angle_offset_y = 0


    if (wheel_angle > 9.4) or (wheel_angle < -9.4):
        wheel_angle_offset_x = -1
    else:
        wheel_angle_offset_x = 0

    # print(wheel_angle) # it doesn't return to 0 for some reason (gets stuck at 0.5 degrees or something) but that's not an issue cuz it's not the real steering angle of the car - only the visual wheel angle, which 0.5 degrees itself isn't enough to produce a visual change to the angle of the wheels

    center_of_leftfrontwheel = ((screen_size_x//2)-20+wheel_angle_offset_x, (screen_size_y//2)-17+wheel_angle_offset_y)
    rotated_leftfrontwheelimg = pygame.transform.rotate(leftfrontwheelimg, wheel_angle)
    # Get the new rectangle of the rotated image and set its center to the original center
    rotated_leftfrontwheel_rect = leftfrontwheelimg.get_rect(center=center_of_leftfrontwheel)
    # Blit the rotated image onto the screen
    screen.blit(rotated_leftfrontwheelimg, rotated_leftfrontwheel_rect.topleft)

    center_of_rightfrontwheel = ((screen_size_x//2)+20+wheel_angle_offset_x, (screen_size_y//2)-17+wheel_angle_offset_y)
    rotated_rightfrontwheelimg = pygame.transform.rotate(rightfrontwheelimg, wheel_angle)
    # Get the new rectangle of the rotated image and set its center to the original center
    rotated_rightfrontwheel_rect = rightfrontwheelimg.get_rect(center=center_of_rightfrontwheel)
    # Blit the rotated image onto the screen
    screen.blit(rotated_rightfrontwheelimg, rotated_rightfrontwheel_rect.topleft)

    # rear wing DRS flap
    if not drs_enabled:
        screen.blit(team_selection_screen_teams_and_car_images_array[team_selection_array_pointer][4], ((screen_size_x//2)-14, (screen_size_y//2)+57))
        pygame.draw.rect(screen, (200, 200, 200), (252, 760, 80, 40), 3)
        screen.blit(drs_indicator_grey, (259, 767))
    else:
        pygame.draw.rect(screen, (0, 255, 0), (252, 760, 80, 40), 3)
        screen.blit(drs_indicator_green, (259, 767))

    
    # EXHAUST FLAMES
    # exhaust flames - unburnt fuel gets ignited in the exhaust
    if (0 < gear < 9) and (keys[pygame.K_1] or keys[pygame.K_2] or gear_changed_flag) and (track_speed > 100): # can occur during upshifting OR downshifting
        gear_changed_flag = False
        f = 0
        random_chance_for_flame_spitting = random.randint(1,1) # overall 1 in 1 chance for a flame spit
        random_length_of_time_of_flame_spitting = random.randint(1,3)
        if random_length_of_time_of_flame_spitting == 1:
            flame_spitting_frames = flame_spitting_frames1
        if random_length_of_time_of_flame_spitting == 2:
            flame_spitting_frames = flame_spitting_frames2
        if random_length_of_time_of_flame_spitting == 3:
            flame_spitting_frames = flame_spitting_frames3
        flame_spitting = True

    if (flame_spitting) and (random_chance_for_flame_spitting == 1):
        if flame_spitting_frames[f] == True:
            random_exhaust_colour_green_component = random.randint(0, 255)

            random_chance_for_white_or_grey_flame_spitting = random.randint(1,5)
            if random_chance_for_white_or_grey_flame_spitting == 1:
                temp_add_to_red_component = -55
                temp_add_to_green_component = -(random_exhaust_colour_green_component) + 200
                temp_add_to_blue_component = 200
            else:
                temp_add_to_red_component = 0
                temp_add_to_green_component = 0
                temp_add_to_blue_component = 0

            random_positioning_and_size_for_flame_spitting = random.randint(1,4)
            flame_spitting_y_offset = 23


            if random_positioning_and_size_for_flame_spitting == 1: # normal length, symmetrical flame
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-2, carcentrey+80+flame_spitting_y_offset, 5, 7))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-3, carcentrey+82+flame_spitting_y_offset, 7, 2))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-1, carcentrey+84+flame_spitting_y_offset, 3, 12))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2), carcentrey+84+flame_spitting_y_offset, 1, 16))
            if random_positioning_and_size_for_flame_spitting == 2: # normal length, right-sided flame
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-2, carcentrey+80+flame_spitting_y_offset, 5, 7))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-3, carcentrey+83+flame_spitting_y_offset, 7, 2))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-1, carcentrey+84+flame_spitting_y_offset, 3, 12))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)+1, carcentrey+84+flame_spitting_y_offset, 1, 19))
            if random_positioning_and_size_for_flame_spitting == 3: # normal length, left-sided flame
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-2, carcentrey+80+flame_spitting_y_offset, 5, 10))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-3, carcentrey+84+flame_spitting_y_offset, 7, 2))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-1, carcentrey+84+flame_spitting_y_offset, 3, 12))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-1, carcentrey+84+flame_spitting_y_offset, 1, 19))
            if random_positioning_and_size_for_flame_spitting == 4: # long length, symmetrical flame
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-2, carcentrey+80+flame_spitting_y_offset, 5, 13))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-3, carcentrey+82+flame_spitting_y_offset, 7, 2))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-1, carcentrey+84+flame_spitting_y_offset, 3, 25))
                pygame.draw.rect(screen, (255+temp_add_to_red_component, random_exhaust_colour_green_component+temp_add_to_green_component, 0+temp_add_to_blue_component), ((screen_size_x//2)-1, carcentrey+84+flame_spitting_y_offset, 1, 30))

        f = f + 1
        if f == len(flame_spitting_frames):
            flame_spitting = False
    

    # SPEED TEXT
    if track_speed < 0:
        track_speed = 0
    speed_text = font_size_40.render((str(int(track_speed*track_speed_text_scale_factor))), False, (255, 255, 255)) # track_speed*0.45
    screen.blit(speed_text, (screen_size_x - 115, screen_size_y - 80))

    # MPH TEXT
    screen.blit(mph_text, (screen_size_x - 114, screen_size_y - 40))

    # GEAR NUMBER
    if gear != 0:
        gear_text = font_size_75.render((str(gear)), False, (255, 255, 255))
    else:
        gear_text = font_size_75.render("N", False, (255, 255, 255))
    screen.blit(gear_text, (screen_size_x - 100, screen_size_y - 180))

    
    # RPM

    if speedmaxratio > 100:
        speedmaxratio = 100
    # print("SPEEDMAXRATIO:", speedmaxratio) # THE CLOSER YOU ARE TO 1, THE CLOSER YOU ARE TO THE MAX SPEED
    # if speedmaxratio > 0.9:
        # rpm = 5200/(0.2+(0.2*2.72**speedmaxratio)) + 4550
    # else:
        # rpm = (-25000*speedmaxratio) + 31000
    
    # > VERY expensive calculation. you should reconsider using rpm = (-4000*speedmaxratio) + 15800, but this time make a variant of it or something. consult ChatGPT for optimised calculations running every frame

    rpm = (30000/(0.25+2.72**(2*speedmaxratio))) + 4450

    if rpm > 13000:
        rpm = rpm - 25
        if rpm > 13250:
            rpm = rpm - 25
            if rpm > 13500:
                rpm = rpm - 25
                if rpm > 13750:
                    rpm = rpm - 25


    # rpm = (-91*speedmaxratio) + 13500

    # RPM ADDITIONAL RANDOMNISER
    # - this adds 'noise' to the current RPM value if the track_speed is less than 100 
    # > optimisation: less than 100 because we needn't run this if statement at high revs because the RPM is changing too fast anyway
    # - this allows for a more realistic RPM values at lower revs, particularly when the engine is idling
    if track_speed < 100:
        rpm_additional_randomniser = random.randint(-5, 5)
    
    # RPM VALUE TEXT
    actual_rpm_text = font_size_30.render((str(int(rpm+rpm_additional_randomniser))), False, (255, 255, 255))
    screen.blit(actual_rpm_text, (screen_size_x - 272, screen_size_y - 80))

    # RPM TEXT
    screen.blit(rpm_text, (screen_size_x - 272, screen_size_y - 40))

    if bot_activated or cooldown_lap:
        if track_speed*track_speed_text_scale_factor < 50:
            automatic = False
            gear = 3
        bot_activated = True

    # the following if statement needs to come after the track is rendered on screen
    if bot_activated:
        pygame.draw.rect(screen, (75, 75, 75), (10, 215, 225, 75)) # positioning, size

        raycast_self_driving_bot_text = font_size_17.render("RAYCAST SELF-DRIVING", False, (255, 255, 255))
        raycast_self_driving_bot_text2 = font_size_17.render("BOT: ACTIVE", False, (255, 255, 255))
        screen.blit(raycast_self_driving_bot_text, (21, 233))
        screen.blit(raycast_self_driving_bot_text2, (65, 258))

        half_leftward_raycast_distance, leftward_raycast_distance, half_rightward_raycast_distance, rightward_raycast_distance, forward_raycast_distance = return_total_leftward_and_rightward_raycast_distances_separately()
            # print(leftward_raycast_distance, rightward_raycast_distance, frame_counter2)

        raycast_bot_up_arrow_activated, raycast_bot_down_arrow_activated, raycast_bot_left_arrow_activated, raycast_bot_right_arrow_activated, raycast_distance_difference, additional_brake_speed, raycast_steering_multiplier = move_ai_bot_via_returning_boolean_flags(half_leftward_raycast_distance, leftward_raycast_distance, half_rightward_raycast_distance, rightward_raycast_distance, forward_raycast_distance)

    # the following if statement needs to come AFTER the values from move_ai_bot_via_returning_boolean_flags are returned
    # hardcoded breaking points:

    # print(temp_i_value, temp_j_value)

    # HARD CODED STUFF:
    if bot_activated:
        if track_speed*track_speed_text_scale_factor > 50:
            # track_speed = track_speed - 0.5
            pass

        # as soon as the player crosses the finish line:
        if track_speed*track_speed_text_scale_factor > 75:
            raycast_bot_down_arrow_activated = True

        if track_speed*track_speed_text_scale_factor > 25 and (temp_i_value == 10 and (temp_j_value == 15 or temp_j_value == 16)):
            raycast_bot_down_arrow_activated = True

        if track_speed*track_speed_text_scale_factor > 25 and (temp_i_value == 3 and temp_j_value == 14):
            raycast_bot_down_arrow_activated = True

        if track_speed*track_speed_text_scale_factor > 25 and (temp_i_value == 4 and temp_j_value == 26):
            raycast_bot_down_arrow_activated = True

        if track_speed*track_speed_text_scale_factor > 25 and ((temp_i_value == 8 and temp_j_value == 39) or (temp_i_value == 8 and temp_j_value == 40) or (temp_i_value == 9 and temp_j_value == 40)):
            raycast_bot_down_arrow_activated = True

    
    # SECTOR TIMES DISPLAY
    # SECTORS BACKGROUND RECTANGLE
    pygame.draw.rect(screen, (50, 50, 50), (389, 730, 300, 30)) # positioning, size

    # SECTOR 1 RECTANGLE
    pygame.draw.rect(screen, sector1_colour, (389, 730, 100, 30))
    screen.blit(sector1_text, (430, 736))

    # SECTOR 2 RECTANGLE
    pygame.draw.rect(screen, sector2_colour, (489, 730, 100, 30))
    screen.blit(sector2_text, (528, 736))

    # SECTOR 3 RECTANGLE
    pygame.draw.rect(screen, sector3_colour, (589, 730, 100, 30))
    screen.blit(sector3_text, (628, 736))

    # SECTOR BORDERS
    pygame.draw.rect(screen, (255, 255, 255), (389, 730, 300, 2))
    pygame.draw.rect(screen, (255, 255, 255), (389, 758, 300, 2))
    pygame.draw.rect(screen, (255, 255, 255), (389, 730, 2, 30))
    pygame.draw.rect(screen, (255, 255, 255), (689, 730, 2, 30))

    pygame.draw.rect(screen, (255, 255, 255), (489, 730, 2, 30))
    pygame.draw.rect(screen, (255, 255, 255), (589, 730, 2, 30))

    # print(raycast_bot_up_arrow_activated, raycast_bot_down_arrow_activated)

    # INPUT INDICATORS BACKGROUND
    # BLACK OUTLINE
    pygame.draw.rect(screen, (0, 0, 0), (249-200, screen_size_y-92-560, 45, 86))
    pygame.draw.rect(screen, (0, 0, 0), (208-200, screen_size_y-51-560, 127, 45))
    # GREY BOXES
    pygame.draw.rect(screen, (50, 50, 50), (252-200, screen_size_y-89-560, 39, 80))
    pygame.draw.rect(screen, (50, 50, 50), (211-200, screen_size_y-48-560, 121, 39))

    # THROTTLE INDICATOR
    if ((keys[pygame.K_UP] and not wasd_keys_activated and timed_lap_has_started) or (keys[pygame.K_w] and wasd_keys_activated and timed_lap_has_started))  or (raycast_bot_up_arrow_activated) or (throttle_macro_list[frame_counter] == 1 and playing_back):
        # pygame.draw.rect(screen, (0, 255, 0), (10, 150, 30, 30))
        pygame.draw.rect(screen, (0, 255, 0), (254-200, screen_size_y-87-560, 35, 35))


    # ENERGY STORE/BATTERY
    # ENERY STORE BACKGROUND
    pygame.draw.rect(screen, (100, 100, 100), (745, screen_size_y-80, 40, 72)) # background is 72 pixels long including border pixels (border pixel width = 2)
    # ENERGY STORE LEVEL
    pygame.draw.rect(screen, (240, 240, 0), (747, (screen_size_y-78)+(68-energy_store_level), 36, energy_store_level)) # energy store level is at a max of 68 pixels

    # ENERGY STORE BORDERS
    if (not ers_border_colour_red) or (ers_recharge_mode and elapsed_time_for_ers_lights > 0.2):
        # ERS BORDERS AND GREY LIGHTNING BOLT:
        # THIS GREY BOLT IS DRAWN UNDERNEATH THE GREEN BOLT WHEN ERS RECHARGE MODE IS ON - THIS IS INEFFICIENT
        pygame.draw.rect(screen, (200, 200, 200), (756, screen_size_y-84, 18, 4))
        pygame.draw.rect(screen, (200, 200, 200), (745, screen_size_y-80, 40, 72), 3) # border_width is the last parameter
        screen.blit(ers_lightning_bolt_image, (755, screen_size_y-60))


    if ers_border_colour_red and not ers_recharge_mode:
        # ERS BORDERS AND RED LIGHTNING BOLT:
        pygame.draw.rect(screen, (255, 0, 0), (756, screen_size_y-84, 18, 4))
        pygame.draw.rect(screen, (255, 0, 0), (745, screen_size_y-80, 40, 72), 3) # border_width is the last parameter
        screen.blit(ers_lightning_bolt_red_image, (755, screen_size_y-60))


    # BRAKE INDICATOR
    if ((keys[pygame.K_DOWN] and not wasd_keys_activated and timed_lap_has_started) or (keys[pygame.K_s] and wasd_keys_activated and timed_lap_has_started)) or (raycast_bot_down_arrow_activated) or (brake_macro_list[frame_counter] == 1 and playing_back):
        # pygame.draw.rect(screen, (255, 0, 0), (10, 180, 30, 30))
        pygame.draw.rect(screen, (255, 0, 0), (254-200, screen_size_y-46-560, 35, 35))
       
        # ERS (ENERGY RECOVERY SYSTEM)
        if ers_recharge_mode and track_speed > 0:

            if not time_started_for_ers_lights:
                time_started_for_ers_lights = True
                start_time_for_ers_lights = time.time()
            else:
                elapsed_time_for_ers_lights = time.time() - start_time_for_ers_lights

            if elapsed_time_for_ers_lights < 0.1: # renders things between 0 and 0.1 seconds
                pygame.draw.rect(screen, (255, 0, 0), ((screen_size_x//2)-14, carcentrey+100, 6, 1)) # left rear wing light
                pygame.draw.rect(screen, (255, 0, 0), ((screen_size_x//2)-2, carcentrey+101, 5, 2)) # centre light
                pygame.draw.rect(screen, (255, 0, 0), ((screen_size_x//2)+9, carcentrey+100, 6, 1)) # right rear wing light

                # ERS BORDERS AND GREEN LIGHTNING BOLT:
                pygame.draw.rect(screen, (0, 255, 0), (756, screen_size_y-84, 18, 4))
                pygame.draw.rect(screen, (0, 255, 0), (745, screen_size_y-80, 40, 72), 3) # border_width is the last parameter
                screen.blit(ers_lightning_bolt_green_image, (755, screen_size_y-60))

            if elapsed_time_for_ers_lights > 0.2: # doesn't render anything between 0.1 and 0.2 seconds
                elapsed_time_for_ers_lights = 0

                if track_speed > 0:
                    energy_store_level = energy_store_level + 1

                time_started_for_ers_lights = False

    if energy_store_level > 68:
        energy_store_level = 68
    if energy_store_level < -1:
        energy_store_level = 0



    # LEFTWARD STEERING INDICATOR
    if ((keys[pygame.K_LEFT] and not wasd_keys_activated and timed_lap_has_started) or (keys[pygame.K_a] and wasd_keys_activated and timed_lap_has_started)) or (raycast_bot_left_arrow_activated) or (leftward_steering_macro_list[frame_counter] == 1 and playing_back):
        pygame.draw.rect(screen, (255, 255, 255), (213-200, screen_size_y-46-560, 35, 35))

    # RIGHTWARD STEERING INDICATOR
    if ((keys[pygame.K_RIGHT] and not wasd_keys_activated and timed_lap_has_started) or (keys[pygame.K_d] and wasd_keys_activated and timed_lap_has_started)) or (raycast_bot_right_arrow_activated) or (rightward_steering_macro_list[frame_counter] == 1 and playing_back):
        pygame.draw.rect(screen, (255, 255, 255), (295-200, screen_size_y-46-560, 35, 35))

    # ATTEMPT COUNT
    if timer_toggle:
        screen.blit(attempt_text, (10, 10))

        attempt_number_text = font_size_30.render(str(attempt_number), False, (255, 255, 255))
        screen.blit(attempt_number_text, (137, 11))

    # AUTO OR MANUAL TEXT
    if automatic:
        automatic_or_manual_text = font_size_20.render("AUTO", False, (255, 255, 255))
        screen.blit(automatic_or_manual_text, (200, 12))
    if not automatic:
        automatic_or_manual_text = font_size_20.render("MANUAL", False, (255, 255, 255))
        screen.blit(automatic_or_manual_text, (195, 12))

    if ers_recharge_mode:
        ers_recharge_mode_on_or_off_text = font_size_20.render("RECHARGE: ON", False, (255, 255, 255))
        screen.blit(ers_recharge_mode_on_or_off_text, (295, 12))
    if not ers_recharge_mode:
        ers_recharge_mode_on_or_off_text = font_size_20.render("RECHARGE: OFF", False, (255, 255, 255))
        screen.blit(ers_recharge_mode_on_or_off_text, (295, 12))
    

    # SHIFT LIGHTS
    # SHIFT LIGHTS SILHOUETTE METHOD 1: BLITTING JUST THE IMAGE
    # screen.blit(shift_lights_silhouette_image, (347.5, 770))


    # SHIFT LIGHTS SILHOUETTE METHOD 2: DRAWING ALL THE CIRCLES
    # SHIFT LIGHTS BACKGROUND
    pygame.draw.rect(screen, (45, 45, 45), (347.5+13, 770, 360, 30))

    # SHIFT LIGHTS BLACK SILHOUETTE
    for i in range(14):
        pygame.draw.circle(screen, (0, 0, 0), (365+(i*25)+13, 785), 10) # the distance between the centre of each circle is 25

    # SHIFT LIGHTS BORDERS
    pygame.draw.rect(screen, (0, 0, 0), (347.5+13, 769, 360, 32), 2)


    if track_speed == 0:
        speedmaxratio = 100 # speedmaxratio is actually infinite here but we'll just say it's 100 to avoid a division by error issue. it can't be set to 0 otherwise 0 will interfere with the deep-nested if statements
    else:
        speedmaxratio = ((125*gear)+125) / track_speed # why was it 125 again? - 125 is the maximum speed of the first gear, measured in arbitrary units
    # print("SPEEDMAXRATIO:", speedmaxratio) # THE CLOSER YOU ARE TO 1, THE CLOSER YOU ARE TO THE MAX SPEED

    # fixing automatic downshifting
    if rate_of_change_of_speed > 0 or not down_arrow_depressed: # fixes automatic downshifting when throttle and brake are applied at the same time - since brake takes priority over throttle, the car slows down
        accelerating = True
    if rate_of_change_of_speed < 0 or down_arrow_depressed: # fixes automatic downshifting when throttle and brake are applied at the same time - since brake takes priority over throttle, the car slows down
        accelerating = False

    speedmaxratio_offset = -0.500

    if 1.450+speedmaxratio_offset < speedmaxratio < 9999:
        if (automatic and not accelerating and gear > 1) or (on_grass and automatic and gear > 1): # fixes automatic downshifting
            gear = gear - 1
            channel2.play(pygame.mixer.Sound("gear changev3.mp3"))
            gear_changed_flag = True

    # print(accelerating, on_grass)

    # first 10 shift lights which are red
    # print("Redrawing circles now!")
    for i in range(10):
        if speedmaxratio < (1.500-(0.025*i))+speedmaxratio_offset:
            pygame.draw.circle(screen, (255, 0, 0), (365+(25*i)+13, 785), 10)
        else:
            # redrawing circles done! now, we are breaking from the for loop since we don't need to check 
            # ")
            break
    
    # DRS LIGHTS
    if drs_enabled:
        for i in range(4):
            pygame.draw.circle(screen, (0, 255, 0), (365+(25*i)+13, 785), 10)

    if speedmaxratio < (1.250-(0.025*0))+speedmaxratio_offset:
        pygame.draw.circle(screen, (90, 75, 245), (615+13, 785), 10)
        if speedmaxratio < (1.225-(0.025*0))+speedmaxratio_offset:
            pygame.draw.circle(screen, (90, 75, 245), (640+13, 785), 10)
            if speedmaxratio < (1.200-(0.025*0))+speedmaxratio_offset:
                pygame.draw.circle(screen, (90, 75, 245), (665+13, 785), 10)
                if speedmaxratio < (1.175-(0.025*0))+speedmaxratio_offset:
                    pygame.draw.circle(screen, (90, 75, 245), (690+13, 785), 10)

                    if (automatic) and (gear != 8) and (accelerating) and (not on_grass): # gear != 8 ensures that the gear cannot go above 8
                        gear = gear + 1
                        channel2.play(pygame.mixer.Sound("gear changev6.mp3"))
                        gear_changed_flag = True

                    # BLINKING SHIFT LIGHTS; LAST 4 LILAC SHIFT LIGHTS THAT BLINK WHEN REV LIMITER/REDLINE IS HIT 
                    # TIMER THAT ACTIVATES WHEN ALL SHIFT LIGHTS ARE LIT UP - A BOOLEAN FLAG IS REQUIRED TO START THE TIME ONCE WHEN ALL SHIFT LIGHTS ARE LIT UP
                    if not time_started_for_shift_lights:
                        time_started_for_shift_lights = True
                        start_time_for_shift_lights = time.time()
                        # print(start_time_for_shift_lights)
                    else: # if time has started for shift lights
                        elapsed_time_for_shift_lights = time.time() - start_time_for_shift_lights

                    if elapsed_time_for_shift_lights > 0.1:
                        for i in range(4):
                            pygame.draw.circle(screen, (0, 0, 0), (615+(i*25)+13, 785), 10)
                        if elapsed_time_for_shift_lights > 0.2: # this value must be double the value in the above if statement to ensure the shift light timing has equal timing for lilac and black # oh my word this line was genius - i didnt need another timer to state how long the last 4 shift lights were black for - i just used the old elapsed time and waited an additional 0.2 seconds there instead - remove this if statement then unindent the following two lines to see how like the last 4 shift lights blinked black VERY quickly before becoming lilac again
                            elapsed_time_for_shift_lights = 0
                            time_started_for_shift_lights = False


    # print(elapsed_time_for_shift_lights)
    if speedmaxratio > (1.175-(0.025*0))+speedmaxratio_offset:
        time_started_for_shift_lights = False

    # MINIMAP
    mini_map_scale_factor = 0.0117

    screen.blit(canada_minimap_image, (5, 40))
    pygame.draw.circle(screen, (255, 0, 0), (minimap_marker_start_pos_x+(minimap_marker_relative_track_pos_x*mini_map_scale_factor), minimap_marker_start_pos_y+(minimap_marker_relative_track_pos_y*mini_map_scale_factor)), 7)
    # print(track_angle)
    # print(minimap_marker_relative_track_pos_x, minimap_marker_relative_track_pos_y)

    if commence_lights_sequence:
        track_angle = 270 # need to put this here again because apparently it's possible to restart a new timed lap slightly wonky/misaligned
        if not time_started_for_lights_sequence:
            start_time_for_lights_sequence = time.time()
            last_played_time_for_lights_sequence_sound = 0
            time_started_for_lights_sequence = True
        else:
            elapsed_time_for_lights_sequence = time.time() - start_time_for_lights_sequence
            if elapsed_time_for_lights_sequence < 5: # ensures that circles stop rendering after 5 seconds, regardless of whether the player has crossed the start/finish line
                if elapsed_time_for_lights_sequence - last_played_time_for_lights_sequence_sound >= 0.51: # interval = 0.51 seconds, i.e. the lights sequence sound will play every 0.5 seconds # 0.51 seconds to make sure it goes over 2.5 seconds when the lights sequence finish so there isn't an extra beeping sound at the end
                    channel3.play(pygame.mixer.Sound("start light.mp3"))
                    last_played_time_for_lights_sequence_sound = elapsed_time_for_lights_sequence

                if elapsed_time_for_lights_sequence > 0.5:
                    pygame.draw.circle(screen, (0, 0, 0), ((screen_size_x//2)-200, 250), 36)
                    pygame.draw.circle(screen, (255, 0, 0), ((screen_size_x//2)-200, 250), 31)
                    if elapsed_time_for_lights_sequence > 1:
                        pygame.draw.circle(screen, (0, 0, 0), ((screen_size_x//2)-100, 250), 36)
                        pygame.draw.circle(screen, (255, 0, 0), ((screen_size_x//2)-100, 250), 31)
                        if elapsed_time_for_lights_sequence > 1.5:
                            pygame.draw.circle(screen, (0, 0, 0), (screen_size_x//2, 250), 36)
                            pygame.draw.circle(screen, (255, 0, 0), (screen_size_x//2, 250), 31)
                            if elapsed_time_for_lights_sequence > 2:
                                pygame.draw.circle(screen, (0, 0, 0), ((screen_size_x//2)+100, 250), 36)
                                pygame.draw.circle(screen, (255, 0, 0), ((screen_size_x//2)+100, 250), 31)
                                if elapsed_time_for_lights_sequence > 2.5:
                                    pygame.draw.circle(screen, (0, 0, 0), ((screen_size_x//2)+200, 250), 36)
                                    pygame.draw.circle(screen, (255, 0, 0), ((screen_size_x//2)+200, 250), 31)
                                    
            else: # if elapsed_time_for_lights_sequence is more than 5 seconds
                commence_lights_sequence = False # ensures that circles stop rendering after 5 seconds and this entire code block is turned off
                raycast_bot_up_arrow_activated = False

    if timer_toggle:
        if off_track_time_penalty > 0:
            off_track_time_penalty_text_surface_small = font_size_30.render("+"+formatted_off_track_time_penalty, False, (255, 0, 0))
            screen.blit(off_track_time_penalty_text_surface_small, (10, screen_size_y - 90)) # the value but small and in the left bottom corner

            lap_invalidated_text_surface = font_size_25.render("LAP TIME INVALIDATED", False, (255, 0, 0))
            lap_invalidated_text_surface_rect = lap_invalidated_text_surface.get_rect()
            lap_invalidated_text_surface_rect.center = (screen_size_x//2, screen_size_y - 100)
            screen.blit(lap_invalidated_text_surface, lap_invalidated_text_surface_rect) # LAP TIME INVALIDATED

        if ((left_front_tyre_pixel_colour == (0, 150, 0)) and (right_front_tyre_pixel_colour == (0, 150, 0)) and (left_rear_tyre_pixel_colour == (0, 150, 0)) and (right_rear_tyre_pixel_colour == (0, 150, 0))) and timed_lap_has_started:
            off_track_time_penalty_graphic_rect = off_track_time_penalty_graphic.get_rect()
            off_track_time_penalty_graphic_rect.center = (screen_size_x//2, 200)
            screen.blit(off_track_time_penalty_graphic, off_track_time_penalty_graphic_rect) # the graphic
            
            off_track_time_penalty_text_surface = font_size_35.render("+"+formatted_off_track_time_penalty, False, (255, 0, 0))
            off_track_time_penalty_text_surface_rect = off_track_time_penalty_text_surface.get_rect()
            off_track_time_penalty_text_surface_rect.center = (screen_size_x//2, 275)
            screen.blit(off_track_time_penalty_text_surface, off_track_time_penalty_text_surface_rect) # the value

            # NOTIFICATION LINGER
            elapsed_time_for_off_track_time_penalty_linger = 0 # keep resetting to 0 on each frame
            start_time_for_off_track_time_penalty_linger = time.time()

            if not time_started_for_off_track_time_penalty_interval:

                print(off_track_time_penalty, formatted_off_track_time_penalty)

                off_track_time_penalty = convert_formatted_time_into_seconds_and_milliseconds(formatted_off_track_time_penalty)

                print(off_track_time_penalty, formatted_off_track_time_penalty)

                off_track_time_penalty = off_track_time_penalty + 2

                print(off_track_time_penalty, formatted_off_track_time_penalty)

                formatted_off_track_time_penalty = convert_seconds_and_milliseconds_into_formatted_time(off_track_time_penalty)

                print(off_track_time_penalty, formatted_off_track_time_penalty)

                print("QUE PASA\n")




                start_time_for_off_track_time_penalty_interval = time.time()
                time_started_for_off_track_time_penalty_interval = True
            else:
                current_time_for_off_track_time_penalty_interval = time.time()
                elapsed_time_for_off_track_time_penalty_interval = current_time_for_off_track_time_penalty_interval - start_time_for_off_track_time_penalty_interval

            
            if elapsed_time_for_off_track_time_penalty_interval > 0.5:
                
                elapsed_time_for_off_track_time_penalty_interval = 0
                time_started_for_off_track_time_penalty_interval = False

        else:
            time_started_for_off_track_time_penalty_interval = False
            start_time_for_off_track_time_penalty_interval = 0
            current_time_for_off_track_time_penalty_interval = 0
            elapsed_time_for_off_track_time_penalty_interval = 0

            # NOTIFICATION LINGER
            current_time_for_off_track_time_penalty_linger = time.time()
            elapsed_time_for_off_track_time_penalty_linger = current_time_for_off_track_time_penalty_linger - start_time_for_off_track_time_penalty_linger # this line is ALWAYS executing after you get a penalty then come back on the track. this is a small inefficiency
            if elapsed_time_for_off_track_time_penalty_linger < 2 and timed_lap_has_started: # the notification lingers on screen for 2 seconds after the player has come back on the road # "and if timed_lap_has_started" is there so that the notification isn't there before you cross the finish line when the time starts
                off_track_time_penalty_graphic_rect = off_track_time_penalty_graphic.get_rect()

                off_track_time_penalty_graphic_rect.center = (screen_size_x//2, 200)
                screen.blit(off_track_time_penalty_graphic, off_track_time_penalty_graphic_rect) # the graphic
                
                off_track_time_penalty_text_surface = font_size_35.render("+"+formatted_off_track_time_penalty, False, (255, 0, 0))
                off_track_time_penalty_text_surface_rect = off_track_time_penalty_text_surface.get_rect()
                off_track_time_penalty_text_surface_rect.center = (screen_size_x//2, 275)
                screen.blit(off_track_time_penalty_text_surface, off_track_time_penalty_text_surface_rect) # the value


        if not timed_lap_has_started:
            minutes, seconds, milliseconds = 0, 0, 0
        else:
            # print("Track limits not infringed.")
            # TIME ELAPSED:
            current_time = time.time()
            # print(start_time, current_time)
            elapsed_time = current_time - start_time

            # calculate minutes, seconds, and milliseconds
            minutes, seconds = divmod(elapsed_time, 60)
            seconds, milliseconds = divmod(seconds, 1)
            milliseconds = int(milliseconds * 1000)
        current_formatted_elapsed_time = "{:02d}:{:02d}.{:03d}".format(int(minutes), int(seconds), milliseconds) # formatted as minutes:seconds.milliseconds

        # elapsed_time = "Time: {:.3f}".format(elapsed_time) # .format() method # elapsed_time = "Elapsed time: {:.4f} seconds".format(elapsed_time) # this was the old formatting for the timer. it wasn't minutes:seconds.milliseconds - it was just seconds.milliseconds
        

        if (sector1_passed) and (sector2_passed) and (sector3_passed):
            if off_track_time_penalty == 0:
                final_lap_time_text = font_size_40.render(final_lap_time, True, (0, 255, 0))
            else:
                final_lap_time_text = font_size_40.render(final_lap_time, True, (255, 0, 0))
            screen.blit(final_lap_time_text, (10, screen_size_y - 45))

        else:
            if off_track_time_penalty == 0:
                elapsed_time_text = font_size_40.render(str(current_formatted_elapsed_time), True, (255, 255, 255))
            else:
                elapsed_time_text = font_size_40.render(str(current_formatted_elapsed_time), True, (255, 0, 0))
            screen.blit(elapsed_time_text, (10, screen_size_y - 45))




        if (sector1_passed) and (not sector2_passed) and (not sector3_passed):
            screen.blit(sector1_time_text, (10, screen_size_y - 200))
            if len(sector1_times_list) > 1: screen.blit(formatted_sector1_delta_time_text, (205, screen_size_y - 200)) # 1 because we just appended the first sector1_time. but you can't have a delta time when there's only one time. you need to have at least two times to be able to calculate a delta time


        if (sector1_passed) and (sector2_passed) and (not sector3_passed):
            screen.blit(sector1_time_text, (10, screen_size_y - 200))
            if len(sector1_times_list) > 1: screen.blit(formatted_sector1_delta_time_text, (205, screen_size_y - 200))

            screen.blit(sector2_time_text, (10, screen_size_y - 170))
            if len(sector2_times_list) > 1: screen.blit(formatted_sector2_delta_time_text, (205, screen_size_y - 170))


        if (sector1_passed) and (sector2_passed) and (sector3_passed):
            screen.blit(sector1_time_text, (10, screen_size_y - 200))
            if len(sector1_times_list) > 1: screen.blit(formatted_sector1_delta_time_text, (205, screen_size_y - 200))

            screen.blit(sector2_time_text, (10, screen_size_y - 170))
            if len(sector2_times_list) > 1: screen.blit(formatted_sector2_delta_time_text, (205, screen_size_y - 170))

            screen.blit(sector3_time_text, (10, screen_size_y - 140))
            if len(sector3_times_list) > 1: screen.blit(formatted_sector3_delta_time_text, (205, screen_size_y - 140))
    

    # colour detecting pixels on each of the 4 tyres
    # pygame.draw.rect(screen, (255, 0, 0), (516, 380, 1, 1))
    # pygame.draw.rect(screen, (255, 0, 0), (564, 380, 1, 1))
    # pygame.draw.rect(screen, (255, 0, 0), (515, 442, 1, 1))
    # pygame.draw.rect(screen, (255, 0, 0), (565, 442, 1, 1))


    if sector3_passed or artificially_activate_end_game_leaderboard:
        if sector3_passed:
            cooldown_lap = True

        if not final_lap_time_appended:

            # why is there a blank space here lol - what was here before?

            if artificially_activate_end_game_leaderboard:
                if off_track_time_penalty == 0: # doesn't append the time if time penalty is more than 0:
                    final_lap_time = "NO TIME"
                else:
                    final_lap_time = "LAP INVALID"
                final_lap_times_list.append(final_lap_time)
            else:
                final_lap_times_list.append(final_lap_time)

            # USE "file_object" NOT "f"! - "f" is the index number for the flame_spitting_frames array!
            file_object = open("Formula 1 Pixel Racing Leaderboard.txt", "r") 
            length_of_final_lap_times_inside_text_file = len(file_object.readlines())
            file_object.close()

            if length_of_final_lap_times_inside_text_file == 0:
                file_object = open("Formula 1 Pixel Racing Leaderboard.txt", "a") # "a"- APPEND - appends to the end of the file
                file_object.write("\n" + str(final_lap_time))
                file_object.close()
            else:
                file_object = open("Formula 1 Pixel Racing Leaderboard.txt", "a") # "a"- APPEND - appends to the end of the file
                file_object.write(str(final_lap_time))
                file_object.close()

            file_object = open("Formula 1 Pixel Racing Leaderboard.txt", "r") # "r" - READ - reads the file; does not change the content of the file
            final_lap_times_inside_text_file = file_object.read()
            file_object.close()

            # return list of final lap times
            final_lap_times_inside_text_file_list = final_lap_times_inside_text_file.splitlines()

            # merge sort list of final lap times
            merge_sorted_final_lap_times_inside_text_file_list = merge_sort_list_into_ascending_order(final_lap_times_inside_text_file_list)
            # print(merge_sorted_final_lap_times_inside_text_file_list)
        
            # overwrite file with nothing, i.e. emptying the file
            open("Formula 1 Pixel Racing Leaderboard.txt", "w").close() # "w" - WRITE - overwrites any existing content # overwrite with nothing - this effectively empties the file

            # append file with each element of the merge sorted list of final lap times
            file_object = open("Formula 1 Pixel Racing Leaderboard.txt", "a") # "a"- APPEND - appends to the end of the file
            for i in range(len(merge_sorted_final_lap_times_inside_text_file_list)):
                file_object.write(merge_sorted_final_lap_times_inside_text_file_list[i]+"\n")
            file_object.close()

            final_lap_time_appended = True

            # this code runs once dw:
            LDY = -screen_size_y # leaderboard dropdown y value # LDY should range from screen_size_y (810) to 0

        display_end_game_leaderboard(final_lap_time, merge_sorted_final_lap_times_inside_text_file_list) # final_lap_times_list


    if black_foreground_activated:
        black_foreground.set_alpha(black_foreground_alpha_iterator)

        if fade_in:
            channel.fadeout(100)
            black_foreground_alpha_iterator = black_foreground_alpha_iterator + 10
            if black_foreground_alpha_iterator > 300:
                reset_timed_lap()
                timer_toggle = True # you should only enable timer toggle HERE
                fade_in = False # begins fading back out, returning to the normal game screen
                channel.play(base_sound, loops=-1, fade_ms=200)
        else:
            black_foreground_alpha_iterator = black_foreground_alpha_iterator - 20
            if black_foreground_alpha_iterator <= 0:
                black_foreground_activated = False # deactivate the black_foreground so we aren't blitting it when it's not visible (i.e. don't blit the black foreground when alpha value is less than or equal to 0)

        screen.blit(black_foreground, (0, 0))

    pygame.display.flip()

pygame.quit()
