import pygame
import socket
from threading import Thread
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Elevator Spirit Animation")

# Colors
BLUE = (100, 200, 255)
BLACK = (0, 0, 0)

# Animation States
is_listening = False
is_speaking = False

# Socket setup
HOST = "127.0.0.1"  # Localhost
PORT = 65432  # Same port as the backend
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)


def handle_client(client_socket):
    global is_listening, is_speaking

    while True:
        data = client_socket.recv(1024).decode("utf-8")
        if data == "listening":
            is_listening = True
            is_speaking = False
        elif data == "speaking":
            is_listening = False
            is_speaking = True
        else:
            is_listening = False
            is_speaking = False


def animate_spirit():
    global is_listening, is_speaking
    spirit_radius = 50
    clock = pygame.time.Clock()
    current_pulse = 0  # Track the current pulse amount for smooth transitions

    # Colors for each state
    SPEAKING_COLOR = (0, 255, 200)  # Bright cyan for speaking
    LISTENING_COLOR = (100, 200, 255)  # Light blue for listening
    IDLE_COLOR = (50, 100, 150)  # Dark blue for idle

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Clear screen
        screen.fill(BLACK)

        # Determine target pulse amount based on state
        if is_speaking:
            target_pulse = 10 * math.sin(pygame.time.get_ticks() * 0.01)
            spirit_color = SPEAKING_COLOR  # Set color for speaking
        elif is_listening:
            target_pulse = 8 * math.sin(pygame.time.get_ticks() * 0.005)
            spirit_color = LISTENING_COLOR  # Set color for listening
        else:
            target_pulse = 0  # No pulsing when idle
            spirit_color = IDLE_COLOR  # Set color for idle

        # Smoothly transition to the target pulse
        current_pulse += (target_pulse - current_pulse) * 0.1

        # Draw the spirit with the appropriate color and pulse
        pygame.draw.circle(
            screen, spirit_color, (200, 200), spirit_radius + int(current_pulse)
        )

        # Update display
        pygame.display.flip()
        clock.tick(60)


def main():
    client_socket, addr = server_socket.accept()
    print(f"Connected to backend: {addr}")

    # Start animation and communication
    Thread(target=handle_client, args=(client_socket,)).start()
    animate_spirit()


if __name__ == "__main__":
    main()
