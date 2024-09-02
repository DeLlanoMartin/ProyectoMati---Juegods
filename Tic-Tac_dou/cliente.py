import socket
import threading

# Función para enviar mensajes al servidor
def send_message():
    while True:
        message = input()
        client_socket.send(message.encode())
        if message == "no me da":
            client_socket.close()
            break

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Elegir el host y puerto al que conectar (el host y puerto del servidor)
host = socket.gethostname()  # Este debería ser el nombre de host o la dirección IP del servidor
port = 12345

# Conectar el socket al servidor
client_socket.connect((host, port))

# Iniciar un hilo para enviar mensajes al servidor
send_thread = threading.Thread(target=send_message)
send_thread.start()

# Recibir mensajes del servidor
while True:
    data = client_socket.recv(1024)
    print("Mensaje del otro jugador:", data.decode())