import socket
import threading

# Lista para almacenar los clientes conectados
clients = []

# Función para manejar las conexiones de los clientes
def handle_client(client_socket, client_id):
    global counter
    while True:
        # Recibir datos del cliente
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Mensaje recibido del cliente {client_id}: {data.decode()}")
            
            # Reenviar el mensaje a todos los clientes conectados (incluido el cliente que lo envió)
            for c in clients:
                c.send(data)
            if data.decode() == "no me da":
                print(f"Cliente {client_id} cerró la conexión.")
                # Remover el socket del cliente de la lista de clientes
                clients.remove(client_socket)
                client_socket.close()
                return
        except ConnectionResetError:
            print(f"Cliente {client_id} cagoneó.")
            print(f"Contador: {counter}")
            # Remover el socket del cliente de la lista de clientes
            clients.remove(client_socket)
            client_socket.close()
            return

# Crear un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Elegir el puerto
host = socket.gethostname()
port = 12345

# Enlazar el socket con el puerto
server_socket.bind((host, port))

# Escuchar conexiones entrantes, 2 es el número máximo de conexiones que puede tener el servidor
server_socket.listen()

print("Esperando conexiones entrantes...")

client_id_counter = 1

while True:
    # Aceptar una nueva conexión
    client_socket, client_address = server_socket.accept()
    print("Cliente conectado desde:", client_address)
    
    # Asignar un ID único al cliente
    client_id = client_id_counter
    client_id_counter += 1
    
    # Agregar el cliente a la lista de clientes
    clients.append(client_socket)
    
    # Iniciar un nuevo hilo para manejar la conexión del cliente
    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
    client_handler.start()