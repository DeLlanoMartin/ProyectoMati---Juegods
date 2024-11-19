import socket
import threading

# Configuración del servidor
host = socket.gethostname()
port = 12345

# Variables globales
clients = {}  # Diccionario para almacenar clientes
tablero = [[0 for _ in range(7)] for _ in range(6)]  # Tablero de 6 filas x 7 columnas
turno = 1  # Turno actual: jugador 1 o 2
game_over = False  # Indica si el juego ha terminado

# Función para manejar cada cliente
def manejar_cliente(socket_cliente, client_id):
    global turno, game_over

    while True:
        try:
            data = socket_cliente.recv(1024)
            if not data:
                break

            mensaje = data.decode()
            print(f"Mensaje recibido de Cliente {client_id}: {mensaje}")

            print(mensaje)

            if game_over or client_id != turno:
                continue  # Ignorar si el juego terminó o no es su turno
            
        except Exception as e:
            print(f"Error con Cliente {client_id}: {e}")
            break

    socket_cliente.close()


# Configurar y escuchar el servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((host, port))
servidor.listen(2)  # Solo se permiten dos jugadores

print("Servidor iniciado. Esperando conexiones...")

client_id_counter = 1
while len(clients) < 2:  # Aceptar solo dos clientes
    socket_cliente, direccion = servidor.accept()
    print(f"Cliente conectado desde: {direccion}")

    # Asignar ID al cliente y notificarle
    clients[client_id_counter] = socket_cliente
    socket_cliente.send(str(client_id_counter).encode())  # Enviar solo el ID del cliente

    # Crear un hilo para manejar al cliente
    threading.Thread(target=manejar_cliente, args=(socket_cliente, client_id_counter)).start()
    client_id_counter += 1

print("Dos jugadores conectados. ¡Inicia el juego!")
