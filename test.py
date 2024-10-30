import speech_recognition as sr
import pyttsx3
import pygame
import socket
import time

pygame.init()
pygame.mixer.init()

engine = pyttsx3.init()
recognizer = sr.Recognizer()

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
level_info = {}


def play_beep():
    try:
        pygame.mixer.music.load("beep.mp3")
        pygame.mixer.music.set_volume(0.08)
        pygame.mixer.music.play()
    except pygame.error:
        speak("Beep sound file is missing or there was an error playing it.")


def speak(text):
    client_socket.sendall(b"speaking")
    engine.say(text)
    engine.runAndWait()
    client_socket.sendall(b"idle")


def recognize_speech():
    client_socket.sendall(b"listening")
    with sr.Microphone() as source:
        print("Listening for your command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            client_socket.sendall(b"idle")
            return command.lower()
        except sr.UnknownValueError:
            client_socket.sendall(b"idle")
            return None
        except sr.RequestError:
            speak("Sorry, there was an issue with the service.")
            client_socket.sendall(b"idle")
            return None


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
        if any(phrase in command for phrase in level_move_phrases):
            try:
                input_num = command.split()[-1]
                level_value = int(input_num) if input_num.isdigit() else num_dict.get(input_num, None)
                if level_value and level_value in level_info:
                    if level_value == current_level:
                        speak(f"Cannot go to {level_value} as the elevator is already there.")
                    else:
                        speak(f"Taking you to level {level_value}.")
                        current_level = level_value
                else:
                    speak(f"Level {level_value} is not available.")
            except ValueError:
                speak("Sorry, I didn't catch the level number.")

        elif any(phrase in command for phrase in level_info_phrases):
            input_num = command.split()[-1]
            level_value = int(input_num) if input_num.isdigit() else num_dict.get(input_num, None)
            if level_value and level_value in level_info:
                speak(f"Level {level_value} has the {level_info[level_value]}.")
            else:
                speak(f"I don't have information about level {level_value}.")
        else:
            speak("Sorry, I can only take you to a specific level or tell you what's on a level.")


def get_building_information():
    print("How many floors are there in the building?")
    num_floors = input("Enter the number of floors: ")

    if num_floors.isdigit():
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
    else:
        speak("Sorry, I didn't understand the number of floors. Let's try again.")
        get_building_information()


def standby_mode():
    """Waits in standby mode until Enter key is pressed or 'assist' is recognized."""
    print("Waiting in standby mode... Press Enter or say 'assist' to start.")
    
    # Reinitialize the pygame display to ensure keyboard capture
    pygame.display.quit()
    pygame.display.init()
    screen = pygame.display.set_mode((100, 100))  # Minimal display for event capture

    while True:
        # Process events to capture the Enter key press
        pygame.event.pump()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Changed from K_SPACE to K_RETURN
                    speak("Welcome! How may I assist you?")
                    play_beep()
                    return  # Exit standby and begin assistance

        # Check for "assist" voice command to initiate assistance with help prompt
        command = recognize_speech()
        if command and "assist" in command:
            speak("What do you need help with? Speak after the beep.")
            play_beep()  # Play beep directly
            return  # Exit standby and begin assistance



def elevator_voice_command_system():
    get_building_information()

    while True:
        # Wait in standby until activated by spacebar or voice command
        standby_mode()
        
        # Process one command and then return to standby
        command = recognize_speech()
        process_command(command)
        
        # Notify the user that the system is returning to standby
        speak("If you need further assistance, please say 'assist' again.")



# Start the system
elevator_voice_command_system()
