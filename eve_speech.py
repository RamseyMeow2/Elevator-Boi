import speech_recognition as sr
import pyttsx3

# Initialize the speech engine
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Floor information dictionary (you can expand it with more details)
floor_info = {
    "1": "Lobby",
    "one": "Lobby",
    "2": "Office space",
    "two": "Office space",
    "3": "Gym",
    "three": "Gym",
    "4": "Conference rooms",
    "four": "Conference rooms",
    "5": "Cafeteria",
    "five": "Cafeteria",
    "6": "Roof garden",
    "six": "Roof garden"
}


# Function to speak output
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize voice input
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

# Function to process the elevator command
def process_command(command):
    if command:
        if "take me to floor " in command:
            try:
                floor_number = command.split()[-1]
                if floor_number in floor_info:
                    speak(f"Taking you to floor {floor_number}.")
                else:
                    speak(f"Floor {floor_number} is not available.")
            except ValueError:
                speak("Sorry, I didn't catch the floor number.")
                
        elif "what's on floor " in command or "what is on floor " in command:
            try:
                floor_number = command.split()[-1]
                if floor_number in floor_info:
                    speak(f"Floor {floor_number} has the {floor_info[floor_number]}.")
                else:
                    speak(f"I don't have information about floor {floor_number}.")
            except ValueError:
                speak("Sorry, I didn't catch the floor number.")       
        else:
            speak("Sorry, I can only take you to a specific floor or tell you what's on a floor.")

# Main loop to continuously listen for commands
def elevator_voice_command_system():
    speak("Hello! How can I assist you?")
    while True:
        command = recognize_speech()
        if command is not None and "stop" in command or "exit" in command:
            speak("Stopping elevator.")
            break
        process_command(command)

# Run the elevator system
elevator_voice_command_system()
