import keyboard
import socket
import time

def client_program():
    print("Trying to connect to server")
    host = "10.22.32.214"
    port = 5000

    client_socket = socket.socket()
    try:
        client_socket.connect((host, port))
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("Connected to server. Waiting for keyboard input")

    def send_message(message):
        try:
            client_socket.send(message.encode())
        except Exception as e:
            print(f"Error sending message: {e}")

    # Event handlers for key presses
    def on_left_press(event):
        send_message('left')

    def on_left_release(event):
        send_message('l_false')

    def on_right_press(event):
        send_message('right')

    def on_right_release(event):
        send_message('r_false')

    def on_up_press(event):
        send_message('up')

    def on_x_press(event):
        send_message('x')

    # Register event listeners
    keyboard.on_press_key('left', on_left_press)
    keyboard.on_release_key('left', on_left_release)
    keyboard.on_press_key('right', on_right_press)
    keyboard.on_release_key('right', on_right_release)
    keyboard.on_press_key('up', on_up_press)
    keyboard.on_press_key('x', on_x_press)

    try:
        # Keep the program running until 'q' is pressed to quit
        while True:
            if keyboard.is_pressed('q'):
                print("Exiting program")
                break
            time.sleep(0.1)  # Prevent CPU overuse
    finally:
        client_socket.close()
        print("Connection closed")

if __name__ == '__main__':
    client_program()
