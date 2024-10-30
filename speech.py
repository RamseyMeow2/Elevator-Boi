import speech_recognition as sr
import pyttsx3
import pygame
import socket
import time

pygame.init()
pygame.mixer.init()

engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Socket setup for sending state updates
HOST = "127.0.0.1"
PORT = 65432
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((HOST, PORT))
    print("Connected to the frontend animation.")
except socket.error as e:
    print(f"Failed to connect to frontend: {e}")

num_dict = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

current_level = 1
level_value = 0
level_info = {}


def play_beep():  # Loads in beep sound
    try:
        pygame.mixer.music.load("beep.mp3")
        pygame.mixer.music.set_volume(0.08)
        pygame.mixer.music.play()
    except pygame.error:
        speak("Beep sound file is missing or there was an error playing it.")


def speak(text):
    client_socket.sendall(b"speaking")  # Notify frontend that we're speaking
    engine.say(text)
    engine.runAndWait()
    client_socket.sendall(b"idle")  # Switch back to idle after speaking


def recognize_speech():
    client_socket.sendall(b"listening")  # Notify frontend that we're listening
    with sr.Microphone() as source:
        print("Listening for your command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            client_socket.sendall(b"idle")  # Done listening
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            client_socket.sendall(b"idle")
            return None
        except sr.RequestError:
            speak("Sorry, there was an issue with the service.")
            client_socket.sendall(b"idle")
            return None


# Phrases
level_move_phrases = [
    "take me to level",
    "go to level",
    "bring me to level",
    "move to level",
    "take me to floor",
    "go to floor",
    "bring me to floor",
    "move to floor",
]
level_info_phrases = ["what's on level", "what is on level", "is on level"]


def process_command(command):
    global current_level
    if command:
        found_phrase = None
        level_value = None

        # Check for movement phrases
        for phrase in level_move_phrases:
            if phrase in command:
                found_phrase = phrase
                break

        # Check for info phrases if no movement phrase was found
        if not found_phrase:
            for phrase in level_info_phrases:
                if phrase in command:
                    found_phrase = phrase
                    break

        if found_phrase:
            # Try to find the word directly after the found phrase
            try:
                phrase_index = command.index(found_phrase) + len(found_phrase)
                input_num = (
                    command[phrase_index:].strip().split()[0]
                )  # Gets the word right after the phrase

                try:
                    level_value = int(input_num)
                except ValueError:
                    if input_num in num_dict:
                        level_value = num_dict[input_num]
                    else:
                        speak(f"Sorry, {input_num} is not a recognized number.")
                        return

                # Handle level movement
                if found_phrase in level_move_phrases:
                    if level_value in level_info:
                        if level_value == current_level:
                            speak(
                                f"Cannot go to {level_value} as the elevator is already there."
                            )
                        else:
                            speak(f"Taking you to level {level_value}.")
                            current_level = level_value
                    else:
                        speak(f"Level {level_value} is not available.")

                # Handle level info request
                elif found_phrase in level_info_phrases:
                    if level_value in level_info:
                        speak(f"Level {level_value} has the {level_info[level_value]}.")
                    else:
                        speak(f"I don't have information about level {level_value}.")
            except (ValueError, IndexError):
                speak("Sorry, I didn't catch the level number.")
        else:
            speak(
                "Sorry, I can only take you to a specific level or tell you what's on a level."
            )


def get_building_information():
    while True:
        input_num = input("Enter the number of levels in the building: ")
        try:
            num_floors = int(input_num)
            break
        except ValueError:
            if input_num in num_dict:
                num_floors = num_dict[input_num]
                break
            else:
                print(f"Sorry, {input_num} is not a recognized number.")

    print(f"Great! There are {num_floors} floors.")
    for i in range(1, int(num_floors) + 1):
        print(f"Please tell me what is on floor {i}.")
        floor_info = input(f"What is on floor {i}? ")
        if floor_info:
            level_info[i] = floor_info
            print(f"Got it! Floor {i} has the {floor_info}.")
    print("\nBuilding Information:")
    for floor, info in level_info.items():
        print(f"{floor}: {info}")


def elevator_voice_command_system():
    get_building_information()

    while True:
        speak(f"The elevator's currently on level {current_level}.")
        speak(
            "You can ask the elevator to go to a specific level or ask what's on a level."
        )
        speak("Please speak your command after the beep.")
        play_beep()
        command = recognize_speech()
        if command is not None and ("stop" in command or "exit" in command):
            speak("Opening the elevator door.")
            break
        else:
            process_command(command)
        speak("Have a great day.")


# Start the system
elevator_voice_command_system()

# TO DO
# 1. Do the button thing where u get into the elevator and it asks if u need assisstance
# 1.a. Space bar ain't working
# 2. Make the phrases into lists

# Things to test
# - Test out differnt levels/floors like a normal person
# - Go to/ask about a level that doesn't exist
# - Say things after saying the phrase "take me to level two PLEASE THANK YOU"
# - Try exit/stop
