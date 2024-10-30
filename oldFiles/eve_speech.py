import speech_recognition as sr
import pyttsx3
import pygame

pygame.init()
pygame.mixer.init()

engine = pyttsx3.init()
recognizer = sr.Recognizer()

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
    engine.say(text)
    engine.runAndWait()


def recognize_speech():
    with sr.Microphone() as source:
        print("Listening for your command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, there was an issue with the service.")
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
        speak(f"The elevator's currently on level {current_level}.")
        speak(
            "You can ask the elevator to go to a specific level or ask what's on a level."
        )
        speak("Please speak your command after the beep.")
        play_beep()
        command = recognize_speech()
        if command is not None and ("stop" in command or "exit" in command):
            speak("Opening the elevator door.")
        else:
            process_command(command)
        speak("Have a great day.")


elevator_voice_command_system()
# TODO:
# 1. Maybe loop through a container?
