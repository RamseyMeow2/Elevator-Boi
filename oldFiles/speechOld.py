import speech_recognition as sr
import pyttsx3
import pygame
import socket
import time
import numpy as np
import pyaudio

pygame.init()
pygame.mixer.init()

engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Socket setup for sending state updates
HOST = '127.0.0.1'  # Localhost
PORT = 65432       # Port to match the frontend's listening port
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Initialize pyaudio globally to avoid reopening the stream multiple times
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

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

def play_beep():
    try:
        pygame.mixer.music.load("beep.mp3")  # Load your beep sound file
        pygame.mixer.music.set_volume(0.08)
        pygame.mixer.music.play()
    except pygame.error:
        speak("Beep sound file is missing or there was an error playing it.")

def speak(text):
    client_socket.sendall(b'speaking')  # Notify frontend that we're speaking
    
    # Start the speech engine and monitor volume
    engine.say(text)
    
    # While the speech engine is running, monitor and send the volume level
    while engine.isBusy():
        volume = get_microphone_volume()
        client_socket.sendall(f'volume:{volume}'.encode('utf-8'))
        time.sleep(0.1)  # Adjust sleep duration to control how often you send updates
    
    engine.runAndWait()
    client_socket.sendall(b'idle')  # Switch back to idle after speaking

def recognize_speech():
    client_socket.sendall(b'listening')  # Notify frontend that we're listening
    with sr.Microphone() as source:
        print("Listening for your command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            client_socket.sendall(b'idle')  # Done listening
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            client_socket.sendall(b'idle')
            return None
        except sr.RequestError:
            speak("Sorry, there was an issue with the service.")
            client_socket.sendall(b'idle')
            return None

def process_command(command):
    global current_level
    if command:
        if "take me to level" in command or "go to level" in command:
            try:
                input_num = command.split()[-1]
                try:
                    level_value = int(input_num)
                except ValueError:
                    if input_num in num_dict:
                        level_value = num_dict[input_num]
                    else:
                        speak("Not a recognized number word")
                        return
                if level_value in level_info:
                    if level_value == current_level:
                        speak(f"Cannot go to {level_value} as the Elevator's already there.")
                    else:
                        speak(f"Taking you to level {level_value}.")
                        current_level = level_value
                else:
                    speak(f"Level {level_value} is not available.")
            except ValueError:
                speak("Sorry, I didn't catch the level number.")

        elif (
            "what's on level" in command
            or "what is on level" in command
            or "is on level" in command
        ):
            try:
                input_num = command.split()[-1]
                try:
                    level_value = int(input_num)
                except ValueError:
                    if input_num in num_dict:
                        level_value = num_dict[input_num]
                    else:
                        speak("Not a recognized number word")
                        return

                if level_value in level_info:
                    speak(f"Level {level_value} has the {level_info[level_value]}.")
                else:
                    speak(f"I don't have information about level {level_value}.")
            except ValueError:
                speak("Sorry, I didn't catch the level number.")
        else:
            speak(
                "Sorry, I can only take you to a specific level or tell you what's on a level."
            )

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

def elevator_voice_command_system():
    get_building_information()

    while True:
        # Give instructions and wait for a valid command
        speak(f"The elevator's currently on level {current_level}.")
        speak(
            "You can ask the elevator to go to a specific level or ask what's on a level."
        )
        speak("Please speak your command after the beep.")
        play_beep()

        # Wait for a valid voice command
        command = recognize_speech()
        if command is None:
            # If no command was recognized, ask again
            speak("I didn't catch that. Please try again.")
            continue

        if "stop" in command or "exit" in command:
            speak("Opening the elevator door.")
            break
        else:
            process_command(command)
        
        # Give an option to exit or continue
        speak("Would you like to give another command? Say 'yes' to continue or 'no' to stop.")
        play_beep()
        response = recognize_speech()
        if response and ("no" in response or "stop" in response or "exit" in response):
            speak("Thank you! Have a great day.")
            break



def get_microphone_volume():
    # Read the audio data
    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
    volume_level = np.linalg.norm(data) / 1024  # Compute the amplitude
    return volume_level

def cleanup_audio():
    stream.stop_stream()
    stream.close()
    p.terminate()


# Start the system
elevator_voice_command_system()
