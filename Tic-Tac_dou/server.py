import socket
import threading

class Game:
    def __init__(self):
        self.board = [None] * 9
        self.turn = 1
        self.game_over = False
        self.clients = {}  # Almacena los sockets de los jugadores (máximo 2)
        self.winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]

    def check_winner(self):
        # Verifica si alguien ganó
        for combination in self.winning_combinations:
            a, b, c = combination
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] is not None:
                return 1 if self.board[a] == "X" else 2
        return None

    def handle_client(self, client_socket, client_id):
        print("se ejecuta handle_client")
        while not self.game_over:
            print("se ejecuta el while")
            try:
                print("se ejecuta el try")
                # Espera a recibir datos del cliente
                data = client_socket.recv(1024)
                if not data or self.game_over:
                    break

                # Procesa los datos recibidos
                button_index, player_turn = map(int, data.decode().split(','))
                print("recibe los datos")
                if player_turn != self.turn:
                    continue  # Si no es su turno, ignora el movimiento

                print("actualiza el tablero")

                # Actualiza el tablero con el movimiento
                self.board[button_index - 1] = "X" if player_turn == 1 else "O"

                print("antes de reenviar el movimiento")

                # Reenvía el movimiento a todos los clientes
                for cid, c in self.clients.items():
                    c.send(data)  # Envía el movimiento
                
                print("después de haber enviado el movimiento")

                # Verifica si hay un ganador
                winner = self.check_winner()
                if winner:
                    self.notify_winner(winner)
                    break

                # Cambia el turno
                self.turn = 1 if self.turn == 2 else 2

            except ConnectionResetError:
                print(f"Cliente {client_id} desconectado inesperadamente.")
                self.clients.pop(client_id, None)
                break

        client_socket.close()

    def notify_winner(self, winner_id):
        self.game_over = True
        message = f"winner,{winner_id}"
        for cid, c in self.clients.items():
            c.send(message.encode())

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.games = {}  # Almacena las instancias de los juegos
        self.current_game_id = 1

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Servidor esperando conexiones...")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print("Cliente conectado desde:", client_address)

            # Crea una nueva sala cada vez que hay 2 clientes en una sala existente
            if self.current_game_id not in self.games or len(self.games[self.current_game_id].clients) >= 2:
                self.games[self.current_game_id] = Game()
                self.current_game_id += 1

            # Obtiene el juego actual y asigna el cliente
            game = self.games[self.current_game_id - 1]
            client_id = len(game.clients) + 1
            game.clients[client_id] = client_socket

            # Envia el id del cliente
            client_socket.send(str(client_id).encode())

            # Inicia un hilo para manejar al cliente dentro de su instancia de juego
            threading.Thread(target=game.handle_client, args=(client_socket, client_id)).start()

# Configuración del servidor
host = socket.gethostname()
port = 12345
server = Server(host, port)
server.start()