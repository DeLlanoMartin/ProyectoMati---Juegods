import socket
import threading

# Lista para almacenar los clientes conectados
clients = {}
connection_order = []

def handle_client(client_socket, client_id):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            
            print(f"Mensaje recibido del cliente {client_id}: {data.decode()}")

            # Reenviar el mensaje a todos los clientes conectados
            for cid, c in clients.items():
                if cid != client_id:
                    c.send(data)  # Envía el número del botón presionado y el cliente que lo presionó

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

    if len(clients) >= 2:
        print("Máximo de clientes alcanzado. Desconectando al nuevo cliente.")
        message = ("Servidor: No se permiten más de 2 clientes. Conexión cerrada.")
        client_socket.send(message.encode())
        client_socket.close()
        continue

    # Asignar un ID único al cliente
    clients[client_id_counter] = client_socket
    threading.Thread(target=handle_client, args=(client_socket, client_id_counter)).start()
    client_id_counter += 1
