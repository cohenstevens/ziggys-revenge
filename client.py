import keyboard
import socket
import time


def client_program():
    print("trying to connect to server")
    host = "10.34.10.44"
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    print("waiting for keyboard input")
    while keyboard.read_key() != 'q':

        if keyboard.on_press('left'):
            client_socket.send('left'.encode())  # send message
            time.sleep(0.1)
        if keyboard.on_release('left'):
            client_socket.send('l_false'.encode())
            time.sleep(0.1)
        if keyboard.on_press('right'):
            client_socket.send('right'.encode())  # send message
            time.sleep(0.1)
        if keyboard.on_release('right'):
            client_socket.send('r_false'.encode())
            time.sleep(0.1)
        if keyboard.on_press('up'):
            client_socket.send('up'.encode())  # send message
            time.sleep(0.1)
        if keyboard.on_press('x'):
            client_socket.send('x'.encode())  # send message
            time.sleep(0.1)

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()