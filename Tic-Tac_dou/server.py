import socket
import threading

clients = {}
connection_order = []
turn = 1  # Control de turnos, empieza con el jugador 1
game_over = False  # Variable para saber si el juego ha terminado
board = [None] * 9  # Estado del tablero

# Combinaciones ganadoras
winning_combinations = [
    [0, 1, 2],  # Fila 1
    [3, 4, 5],  # Fila 2
    [6, 7, 8],  # Fila 3
    [0, 3, 6],  # Columna 1
    [1, 4, 7],  # Columna 2
    [2, 5, 8],  # Columna 3
    [0, 4, 8],  # Diagonal principal
    [2, 4, 6]   # Diagonal secundaria
]

def handle_client(client_socket, client_id):
    global turn, game_over  # Hacer que turn y game_over sean accesibles aquí

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            if game_over:  # Si el juego ha terminado, no permitir más acciones
                continue

            # Asegurarse de que es el turno correcto
            player_turn = int(data.decode().split(',')[1])
            if player_turn != turn:
                continue  # Si no es el turno, ignorar


            print(f"Mensaje recibido del cliente {client_id}: {data.decode()}")

            # Procesar el movimiento
            button_index = int(data.decode().split(',')[0]) - 1
            board[button_index] = "X" if player_turn == 1 else "O"


            # Reenviar el mensaje a todos los clientes conectados
            for cid, c in clients.items():
                c.send(data)  # Envía el movimiento y el cliente que lo hizo

            # Verificar si hay un ganador
            winner = check_winner()
            if winner:
                notify_winner(winner)  # Notificar al ganador
                break  # Salir del bucle si hay un ganador

            # Cambiar el turno
            turn = 1 if turn == 2 else 2

        except ConnectionResetError:
            print(f"Cliente {client_id} cerró la conexión inesperadamente.")
            clients.pop(client_id, None)
            break

# Función para manejar el fin del juego
def notify_winner(winner_id):
    global game_over
    game_over = True  # Marcar que el juego ha terminado
    message = f"winner,{winner_id}"  # Crear mensaje para enviar
    for cid, c in clients.items():
        c.send(message.encode())  # Notificar a todos los clientes sobre el ganador

# Función para verificar si hay un ganador
def check_winner():
    for combination in winning_combinations:
        a, b, c = combination
        if board[a] == board[b] == board[c] and board[a] is not None:
            return 1 if board[a] == "X" else 2  # Devuelve 1 o 2, dependiendo del ganador
    return None  # No hay ganador aún

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

    clients[client_id_counter] = client_socket
    client_socket.send(str(client_id_counter).encode())  # Enviar el ID al cliente
    threading.Thread(target=handle_client, args=(client_socket, client_id_counter)).start()
    client_id_counter += 1
