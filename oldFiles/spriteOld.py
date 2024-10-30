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
HOST = '127.0.0.1'  # Localhost
PORT = 65432       # Same port as the backend
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

def handle_client(client_socket):
    global is_listening, is_speaking, current_volume

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data.startswith('volume:'):
            try:
                # Extract the volume level from the message
                current_volume = float(data.split(':')[1])
                is_listening = False
                is_speaking = True
            except ValueError:
                current_volume = 0
        elif data == 'listening':
            is_listening = True
            is_speaking = False
            current_volume = 0  # Reset volume when listening
        else:
            is_listening = False
            is_speaking = False
            current_volume = 0  # Reset volume when idle


def animate_spirit():
    global is_listening, is_speaking, current_volume
    spirit_radius = 50
    clock = pygame.time.Clock()

    # Colors for each state
    SPEAKING_COLOR = (0, 255, 200)
    LISTENING_COLOR = (100, 200, 255)
    IDLE_COLOR = (50, 100, 150)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Clear screen
        screen.fill(BLACK)

        # Set color based on state
        if is_speaking:
            spirit_color = SPEAKING_COLOR
            # Dynamically adjust pulse based on the volume level
            pulse_amount = current_volume * 2  # Adjust multiplier for more/less responsiveness
        elif is_listening:
            spirit_color = LISTENING_COLOR
            pulse_amount = 8 * math.sin(pygame.time.get_ticks() * 0.005)
        else:
            spirit_color = IDLE_COLOR
            pulse_amount = 0

        # Draw the spirit with the dynamic pulse
        pygame.draw.circle(screen, spirit_color, (200, 200), spirit_radius + int(pulse_amount))

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
