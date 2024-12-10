import socket
import threading
import random

clients = {}
connection_order = []
elecciones = []
secret_number = random.randint(1, 100)
moneda = 

def handle_client(client_socket, client_id):
    global elecciones, secret_number
    message = "Elija cara(1) o seca(2)"
    client_socket.sendall(message.encode())

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            data = data.decode()
            print(f"Mensaje recibido del cliente {client_id}: {data}")

            if data.startswith("eleccion"):
                eleccion = data.split(":")[1]
                elecciones.append((int(eleccion), client_id))  

            if len(elecciones) == 2:
                for cid, c in clients.items():
                    c.sendall("Los jugadores eligieron cosas distintas.".encode())
                
                if elecciones[client_id] == moneda

            else:
                print("Esperando el movimiento del otro jugador...")

        except ConnectionResetError:
            print(f"Cliente {client_id} cerró la conexión inesperadamente.")
            clients.pop(client_id, None)
            break

# Crear un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
server_socket.bind((host, port))
server_socket.listen()

print("Esperando conexiones entrantes...")

client_id_counter = 1

while True:
    client_socket, client_address = server_socket.accept()
    print("Cliente conectado desde:", client_address)

    clients[client_id_counter] = client_socket
    client_socket.sendall(str(client_id_counter).encode())  # Enviar el ID al cliente
    threading.Thread(target=handle_client, args=(client_socket, client_id_counter)).start()
    client_id_counter += 1