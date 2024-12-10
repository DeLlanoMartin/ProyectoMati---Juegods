import socket
import threading

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()  # O usa la IP del servidor si es remoto
port = 12345
client_socket.connect((host, port))

# Variable para identificar el cliente
client_id = None

# Función para mandar mensajes
def send_message(message):
    if message:  # No permitir enviar mensajes si el juego ha terminado
        client_socket.sendall(message.encode())

# Función para recibir mensajes
def receive_messages():
    global client_id
    # Recibir el ID del cliente asignado por el servidor
    client_id = int(client_socket.recv(1024).decode())
    print(f"Client ID asignado: {client_id}")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Conexión cerrada por el servidor.")
                break

            data = data.decode()
            print(data)
            
            if "Elija cara(1) o seca(2)" in data:
                eleccion = int(input("Elegir: 1 (cara) o 2 (seca): "))
                send_message(f"eleccion:{eleccion}")
            
            elif "Ambos jugadores" in data:
                guess = int(input("Adivina un número entre 1 y 100: "))
                client_socket.sendall(guess.encode())
                
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
    client_socket.close()

# Iniciar un hilo para recibir mensajes del servidor
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()
