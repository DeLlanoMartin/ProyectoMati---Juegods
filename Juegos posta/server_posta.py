import socket
import threading

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
                    self.handle_game_action(client, data)
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

        # Informar a ambos clientes que el juego comienza
        for c in client_pair:
            c.sendall(f"START_GAME:{game_name}".encode())

    def handle_game_action(self, client, data):
        # Buscar la partida activa del cliente
        for client_pair, game in self.games.items():
            if client in client_pair:
                game.process_action(client, data)
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

    def process_action(self, client, data):
        if data.startswith("MOVE"):
            _, move = data.split(":")


        elif data == "END_GAME":
            for c in self.client_pair:
                c.sendall("GAME_OVER".encode())


# Clase Juego 2
class Game2:
    def __init__(self, client_pair, server):
        self.client_pair = client_pair  # Par de clientes en la partida
        self.server = server  # Referencia al servidor
        self.state = {"player_turn": 0, "board": []}  # Estado inicial del juego

    def process_action(self, client, data):
        if data.startswith("MOVE"):
            _, move = data.split(":")
            self.state["board"].append(move)
            self.state["player_turn"] = (self.state["player_turn"] + 1) % 2

            # Enviar actualizaciones a ambos jugadores
            for c in self.client_pair:
                c.sendall(f"UPDATE:{self.state}".encode())

        elif data == "END_GAME":
            for c in self.client_pair:
                c.sendall("GAME_OVER".encode())


# Clase Juego 2
class Game3:
    def __init__(self, client_pair, server):
        self.client_pair = client_pair  # Par de clientes en la partida
        self.server = server  # Referencia al servidor
        self.state = {"player_turn": 0, "board": []}  # Estado inicial del juego

    def process_action(self, client, data):
        if data.startswith("MOVE"):
            _, move = data.split(":")
            self.state["board"].append(move)
            self.state["player_turn"] = (self.state["player_turn"] + 1) % 2

            # Enviar actualizaciones a ambos jugadores
            for c in self.client_pair:
                c.sendall(f"UPDATE:{self.state}".encode())

        elif data == "END_GAME":
            for c in self.client_pair:
                c.sendall("GAME_OVER".encode())


if __name__ == "__main__":
    server = GameServer()
    server.start()