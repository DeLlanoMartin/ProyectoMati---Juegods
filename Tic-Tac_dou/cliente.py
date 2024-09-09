import socket
import threading

def send_message():
    while True:
        message = input()
        client_socket.send(message.encode())
        if message == "no me da":
            client_socket.close()
            break

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Elegir el host y puerto al que conectar
host = socket.gethostname()
port = 12345

# Conectar el socket al servidor
client_socket.connect((host, port))

# Iniciar un hilo para enviar mensajes al servidor
send_thread = threading.Thread(target=send_message)
send_thread.start()

# Recibir mensajes del servidor
while True:
    try:
        data = client_socket.recv(1024)
        if not data:
            print("Conexión cerrada por el servidor.")
            break
        print("Mensaje de otro jugador:", data.decode())
    except ConnectionResetError:
        print("Conexión perdida con el servidor.")
        break
client_socket.close()
