import socket
import threading
import time

class GameServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.clients = []  # Lista de clientes conectados
        self.games = {}  # Diccionario para gestionar partidas {client_pair: game_instance}

    def handle_client(self, client, address):
        client_id = len(self.clients)
        client.sendall(f"ID:{client_id}".encode())
        print(f"Cliente conectado desde {address}")
        try:
            while True:
                data = client.recv(1024).decode()
                if data == "DISCONNECT":
                    print(f"Cliente {address} desconectado.")
                    self.remove_client(client)
                    break

                if data.startswith("GAME_SELECTION"):
                    _, game_name = data.split(":")
                    self.assign_game(client, game_name)
                else:
                    self.handle_game_action(client, data, client_id)
        except Exception as e:
            print(f"Error con el cliente {address}: {e}")
            self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            # Eliminar el cliente de cualquier partida activa
            for client_pair, game in list(self.games.items()):
                if client in client_pair:
                    del self.games[client_pair]
                    break
            client.close()

    def assign_game(self, client, game_name):
        if len(self.clients) < 2:
            client.sendall("WAITING_FOR_PLAYER".encode())
            return
        
        # Encontrar el otro cliente conectado
        other_client = [c for c in self.clients if c != client][0]
        
        # Crear una nueva partida y asignarla a ambos clientes
        client_pair = (client, other_client)

        if game_name == "Game1":
            self.games[client_pair] = Game1(client_pair, self)
        elif game_name == "Game2":
            self.games[client_pair] = Game2(client_pair, self)
        elif game_name == "Game3":
            self.games[client_pair] = Game3(client_pair, self)

    def handle_game_action(self, client, data, client_id):
        # Buscar la partida activa del cliente
        for client_pair, game in self.games.items():
            if client in client_pair:
                game.process_action(client, data, client_id)
                break

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(2)  # Solo permitimos 2 clientes
        print(f"Servidor iniciado en {self.host}:{self.port}")
        while True:
            client, address = server.accept()
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client, address)).start()

# Clase Juego 1
class Game1:
    def __init__(self, client_pair, server):
        self.client_pair = client_pair  # Par de clientes en la partida
        self.server = server  # Referencia al servidor
        self.turn = 1 # Estado inicial del juego
        self.winner = None

        self.winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
            [0, 4, 8], [2, 4, 6]              # Diagonales
        ]

        self.board = [None] * 9  # None indica que ese botón no ha sido presionado

    def check_winner(self):
        for combination in self.winning_combinations:
            a, b, c = combination
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] is not None:
                return self.board[a]  # Devuelve "X" o "O", dependiendo del ganador
        return None  # No hay ganador aún

    def process_action(self, client, data, client_id):
        if data.startswith("MOVE"):
            move = int(data.split(":")[1])
            self.board[move] = "X" if int(client_id) == 1 else "O"
            winner = self.check_winner()

            if winner:
                for client in self.client_pair:
                    client.sendall(f"WINNER:{client_id}".encode())
            
            for client in self.client_pair:
                client.sendall(f"MOVE:{move}:{client_id}".encode())
            
            if not winner:
                if self.turn == 1:
                    self.turn =2
                elif self.turn == 2:
                    self.turn =1

                for c in self.client_pair:
                    c.sendall(f"TURN:{self.turn}".encode())
                    print(f"turno enviado: {self.turn} ")

            # Cambiar el turno después de una jugada
        elif data == "END_GAME":
            for c in self.client_pair:
                c.sendall("GAME_OVER".encode())
                self.winner= None


# Clase Juego 2
class Game2:
    def __init__(self, client_pair, server):
        self.client_pair = client_pair  # Par de clientes en la partida
        self.server = server  # Referencia al servidor
        self.board = [[0 for _ in range(7)] for _ in range(6)]
        self.turn = 1
        self.winner = None
        print(self.winner)

    def check_winner(self):
    # Verificar horizontal, vertical y diagonal
        print(self.board)
        for fila in range(6):
            for columna in range(7):
                jugador = self.board[fila][columna]
                if jugador == 0:
                    continue  # Saltar celdas vacías

                # Horizontal
                if columna + 3 < 7 and all(self.board[fila][columna + i] == jugador for i in range(4)):
                    return jugador

                # Vertical
                if fila + 3 < 6 and all(self.board[fila + i][columna] == jugador for i in range(4)):
                    return jugador

                # Diagonal derecha
                if fila + 3 < 6 and columna + 3 < 7 and all(self.board[fila + i][columna + i] == jugador for i in range(4)):
                    return jugador

                # Diagonal izquierda
                if fila + 3 < 6 and columna - 3 >= 0 and all(self.board[fila + i][columna - i] == jugador for i in range(4)):
                    return jugador

        return 0  # No hay ganador aún


    def process_action(self, client, data, client_id):
        if data.startswith("MOVE"):

            move = int(data.split(":")[1])

            for fila in range(5, -1, -1):
                if self.board[fila][move] == 0:
                    self.board[fila][move] = client_id  # Asignar el movimiento del jugador
                    break
                    
            self.winner = self.check_winner()

            if self.winner:
                for client in self.client_pair:
                    client.sendall(f"WINNER:{client_id}".encode())
            
            for client in self.client_pair:
                client.sendall(f"MOVE:{move}:{client_id}".encode())
            
            if not self.winner:
                self.turn = 1 if self.turn == 2 else 2

                for c in self.client_pair:
                    c.sendall(f"TURN:{self.turn}".encode())
                    print(f"turno enviado: {self.turn} ")

            # Cambiar el turno después de una jugada
        elif data == "END_GAME":
            for c in self.client_pair:
                c.sendall("GAME_OVER".encode())
                self.winner= None


# Clase Juego 2
class Game3:
    def __init__(self, client_pair, server):
        self.client_pair = client_pair  # Par de clientes en la partida
        self.server = server  # Referencia al servidor
        self.player_moves = {}  # Almacena los movimientos de los jugadores {player_id: move}
        self.rules = {
            "piedra": ["tijera", "lagarto"],
            "papel": ["piedra", "spock"],
            "tijera": ["papel", "lagarto"],
            "lagarto": ["spock", "papel"],
            "spock": ["piedra", "tijera"]
        }
        self.scores = {1: 0, 2: 0}  # Puntajes de los jugadores {player_id: score}
        self.round = 1  # Contador de rondas


    def process_action(self, client, move, player_id,):
        move = move.split(":")[1]

        # Guardar el movimiento del jugador
        self.player_moves[player_id] = move

        # Verificar si ambos jugadores han enviado sus movimientos
        if len(self.player_moves) == 2:
            # Obtener los movimientos de ambos jugadores
            int
            players = list(self.player_moves.keys())
            move1 = self.player_moves[players[0]]
            move2 = self.player_moves[players[1]]

            print(f"movimiento 1: {move1}")
            print(f"movimiento 2: {move2}")

            # Determinar el resultado
            if move1 == move2:
                result = 0
            elif move2 in self.rules[move1]:
                result = players[0]
                self.scores[players[0]] += 1
            else:
                result = players[1]
                self.scores[players[1]] += 1
            print(f"resultado: {result}")

            # Verificar si ya hay un ganador del mejor de 3
            if self.scores[players[0]] == 2:
                for c in self.client_pair:
                    c.sendall(f"WINNER:{players[0]}".encode())
                self.reset_game()
            elif self.scores[players[1]] == 2:
                for c in self.client_pair:
                    c.sendall(f"WINNER:{players[1]}".encode())
                self.reset_game()
            else:
                # Continuar a la siguiente ronda
                if result!=0:
                    self.round += 1
                    self.player_moves.clear()
                    print(self.scores)
            for c in self.client_pair:
                c.sendall(f"WIN_ROUND:{result}".encode())
                time.sleep(0.1)
                c.sendall(f"CHANGE_ROUND:{self.round}".encode())
        else:
            # Esperar el movimiento del otro jugador
            print("Esperando el movimiento del otro jugador...")

    def reset_game(self):
        """Reiniciar el juego para comenzar otra partida."""
        self.player_moves.clear()
        self.scores = {1: 0, 2: 0}

if __name__ == "__main__":
    server = GameServer()
    server.start()