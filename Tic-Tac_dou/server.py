import socket
import threading
# import customtkinter

# Lista para almacenar los clientes conectados
clients = {}
connection_order = []

# Función para manejar las conexiones de los clientes
def handle_client(client_socket, client_id):
    while True:
        try:
            # Recibir datos del cliente
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Mensaje recibido del cliente {client_id}: {data.decode()}")

            # Reenviar el mensaje a todos los clientes conectados excepto al que lo envió
            for cid, c in clients.items():
                if cid != client_id:
                    c.send(data)

            if data.decode() == "no me da":
                print(f"Cliente {client_id} cerró la conexión.")
                # Remover el socket del cliente de la lista de clientes
                clients.pop(client_id, None)
                connection_order.remove(client_id)
                client_socket.close()
                return
        except ConnectionResetError:
            print(f"Cliente {client_id} cerró la conexión inesperadamente.")
            clients.pop(client_id, None)
            connection_order.remove(client_id)
            client_socket.close()
            return

# Crear un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Elegir el puerto
host = socket.gethostname()
port = 12345

# Enlazar el socket con el puerto
server_socket.bind((host, port))

# Escuchar conexiones entrantes
server_socket.listen()

print("Esperando conexiones entrantes...")

client_id_counter = 1

while True:
    # Aceptar una nueva conexión
    client_socket, client_address = server_socket.accept()
    print("Cliente conectado desde:", client_address)
    
    # Verificar si hay más de 2 clientes conectados
    if len(clients) >= 2:
        print("Máximo de clientes alcanzado. Desconectando al nuevo cliente.")
        message = ("Servidor: No se permiten más de 2 clientes. Conexión cerrada.")
        client_socket.send(message.encode())
        client_socket.close()
        continue    #saltea el codigo para ir al siguiente ciclo

    # Asignar un ID único al cliente
    client_id = client_id_counter
    client_id_counter += 1
    
    # Agregar el cliente a la lista de clientes
    clients[client_id] = client_socket
    connection_order.append(client_id)
    
    # Iniciar un nuevo hilo para manejar la conexión del cliente
    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
    client_handler.start()
