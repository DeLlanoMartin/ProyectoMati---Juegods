import socket
import threading

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()  # O usa la IP del servidor si es remoto
port = 12345
client_socket.connect((host, port))
puntaje = 0

# Variable para identificar el cliente
client_id = None

# Función para mandar mensajes
def send_message(message):
    if message:  # Enviar solo si el mensaje no está vacío
        client_socket.sendall(message.encode())

# Función para recibir mensajes
def receive_messages():
    global client_id, puntaje
    client_id = int(client_socket.recv(1024).decode())  # Recibir el ID del cliente
    print(f"ID asignado: Cliente {client_id}")

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                print("Conexión cerrada por el servidor.")
                break

            print(data)

            if "Elija cara" in data:
                eleccion = input("Elija: ")
                while eleccion not in ["1", "2"]:
                    print("Opción inválida. Intente de nuevo.")
                    eleccion = input("Elija: ")
                send_message(f"eleccion:{eleccion}")

            elif "Adivinen un número" in data:
                guess = input("Adivine un número entre 1 y 100: ")
                while not guess.isdigit() or not (1 <= int(guess) <= 100):
                    print("Entrada inválida. Debe ser un número entre 1 y 100.")
                    guess = input("Adivine un número entre 1 y 100: ")
                send_message(guess)

            elif "Elijan" in data:
                eleccion = input("Elija cara (1) o seca (2)")
                while eleccion not in ["1", "2"]:
                    print("Opción inválida. Intente de nuevo.")
                    eleccion = input("Elija cara (1) o seca (2)")
                send_message(f"eleccion:{eleccion}")

            elif "El jugador" in data and "elige primero" in data:
                if f" {client_id} " in data:
                    print("Te toca elegir primero.")
                    eleccion_final = input("Elija cara (1) o seca (2): ")
                    while eleccion_final not in ["1", "2"]:
                        print("Opción inválida. Intente de nuevo.")
                        eleccion_final = input("Elija cara (1) o seca (2): ")
                    send_message(f"final:{eleccion_final}")
                else:
                    print("Espera a que el otro jugador elija.")
            
            elif "Gana el jugador " in data:
                if f" {client_id}" in data:
                    puntaje =+ 1
                print(f"puntaje del jugador {client_id}: {puntaje}")
        

            elif "Te toca" in data:
                print(data)  # Mostrar la elección que queda para el cliente

        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break

    client_socket.close()

# Iniciar un hilo para recibir mensajes del servidor
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()