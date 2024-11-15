import keyboard
import socket
import time

def client_program():
    print("Trying to connect to server")
    host = "10.27.10.121"
    port = 5000

    client_socket = socket.socket()
    try:
        client_socket.connect((host, port))
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("Connected to server. Waiting for keyboard input")

    # Function to send messages to the server
    def send_message(message):
        try:
            client_socket.send(message.encode())
            print(f"Sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    # Event handlers for key presses and releases
    def on_left_press(event):
        send_message('left')
        time.sleep(0.1)
    
    def on_left_release(event):
        send_message('l_false')
        time.sleep(0.1)

    def on_right_press(event):
        send_message('right')
        time.sleep(0.1)
    
    def on_right_release(event):
        send_message('r_false')
        time.sleep(0.1)

    def on_up_press(event):
        send_message('up')
        time.sleep(0.1)

    def on_x_press(event):
        send_message('x')
        time.sleep(0.1)

    # Register event listeners for specific keys
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
            time.sleep(0.1)  # Reduce CPU usage
    finally:
        client_socket.close()
        print("Connection closed")

if __name__ == '__main__':
    client_program()
