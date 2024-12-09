import socket
import threading
import time
import random
import os
import signal

class WordleServer:
    def __init__(self, host, port, max_clients=5):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Diccionario para rastrear clientes conectados
        self.client_id_counter = 0
        self.mysterious_word = str(self.elegir_palabra())
        self.winners = []
        self.game_over = False

    @staticmethod
    def elegir_palabra():
        try:
            palabras = [
                "chizito" , "abaco"     , "abeja"     , "abismo"  , "abogado"     , "acerca"    , "acuerdo" , "afecto"      , "agosto"  , "alcoba"  ,
                "amigo"   , "anaranjado", "apoyo"     , "arco"    , "avion"       , "banco"     , "bicho"   , "bomba"       , "banco"   , "cable"   ,
                "cielo"   , "camino"    , "clavo"     , "correr"  , "cosecha"     , "dado"      , "dientes" , "duro"        , "duda"    , "enlace"  ,
                "espejo"  , "espera"    , "estrella"  , "fuego"   , "feliz"       , "freno"     , "flor"    , "gato"        , "grande"  , "hermano" ,
                "hombre"  , "hoja"      , "huevo"     , "idea"    , "huevo"       , "jarabe"    , "jugar"   , "juez"        , "luna"    , "lucha"   ,
                "libro"   , "limon"     , "mango"     , "mesa"    , "mujer"       , "nube"      , "noche"   , "nene"        , "niña"    , "oceano"  ,
                "olla"    , "pueblo"    , "plaza"     , "pirámide", "rojo"        , "rosa"      , "roca"    , "silla"       , "sol"     , "sueño"   ,
                "sal"     , "superficie", "taza"      , "tigre"   , "tierra"      , "tunel"     , "uno"     , "viento"      , "vacio"   , "valle"   ,
                "vaca"    , "silla"     , "sombra"    , "luz"     , "granada"     , "iman"      , "tiburon" , "programacion", "negro"   , "mansion" ,
                "pelotudo", "matias"    , "fascinante", "codigo"  , "testosterona", "trolazo"   , "vehiculo", "ojo"         , "lago"    , "alivio"
            ]

            # Elegir una palabra aleatoria
            if palabras:
                return random.choice(palabras).lower()  # Convertir a mayúsculas (opcional)
            else:
                raise ValueError("El archivo de palabras está vacío.")
        except FileNotFoundError:
            print("Error: No se encontró el archivo 'palabras.txt'.")
            return "DEFAULT"  # Palabra por defecto

    def start(self):
        """Inicia el servidor y escucha conexiones entrantes."""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print(f"Servidor escuchando en {self.host}:{self.port}")

        while True:
            client, client_address = self.server_socket.accept()
            print(f"Cliente conectado desde: {client_address}")

            # Verificar si el máximo de clientes ha sido alcanzado
            if len(self.clients) >= self.max_clients:
                print("Máximo de clientes alcanzado. Desconectando al nuevo cliente.")
                client.send("Servidor: No se permiten más de 5 clientes. Conexión cerrada.".encode())
                client.close()
                continue
            
            # Asignar un ID único al cliente
            self.client_id_counter += 1
            client_id = self.client_id_counter
            self.clients[client_id] = client
            

            # Iniciar un hilo para manejar al cliente
            client_thread = threading.Thread(target=self.handle_client, args=(client, client_id), daemon=True)
            client_thread.start()

    def handle_client(self, client, client_id):
        """Maneja la comunicación con un cliente."""
        self.send_message(client, f"ID:{client_id}")  # Enviar ID del cliente
        time.sleep(0.1)  # Pausa breve para evitar que los mensajes se solapen
        self.send_message(client, f"WORD:{len(self.mysterious_word)}")  # Enviar longitud de la palabra


        try:
            while True:
                data = client.recv(1024).decode()
                print(data)
                if not data:
                    break

                if data.startswith("TRY"):
                    _, move, attempts = data.split(":")
                    result = self.process_word(move, self.mysterious_word)
                    self.send_message(client, f"RESULT:{result}")
                    if move == self.mysterious_word:
                        self.add_winner(client_id, attempts, client)
                elif data =="DISCONNECT":
                    print(f"Cliente {client_id} ha desconectado.")
                    self.clients.remove(client)
                    client.close()
                    if len(self.clients)==0:
                        self.server_socket.close()
                        return
                    break

        except ConnectionResetError:
            print(f"Cliente {client_id} cerró la conexión inesperadamente.")
        finally:
            self.clients.pop(client_id, None)
            client.close()

    def send_message(self, client, message):
        """Envía un mensaje codificado a un cliente."""
        client.sendall(message.encode())

    def process_word(self, word, mysterious_word):
        """Procesa el intento del cliente y devuelve los resultados."""
        word = list(word)
        mysterious_word = list(mysterious_word)
        results = []

        for i, letra in enumerate(word):
            if i < len(mysterious_word):
                if letra == mysterious_word[i]:
                    results.append(f"CORRECT")
                elif letra in mysterious_word:
                    results.append(f"DIFF")
                else:
                    results.append(f"NO")
                
        return ",".join(results)  # Unir los resultados en una cadena separada por comas
    
    def add_winner(self, client_id, attempts, client):
        """Registra al ganador y envía la posición a cada cliente cuando todos terminen."""
        # Agregar el jugador actual a la lista de ganadores
        self.winners.append((client_id, int(attempts), client))  # Guardar también el objeto cliente
        self.send_message(client, "WIN")  # Confirmación de victoria al jugador actual

        # Si todos los clientes ganaron, calcular posiciones
        if len(self.winners) == len(self.clients):
            time.sleep(0.1)
            self.win()

    def win(self):
        """Calcula posiciones y las envía a todos los jugadores ganadores."""
        # Ordenar los ganadores por intentos (menor a mayor)
        sorted_winners = sorted(self.winners, key=lambda x: x[1])  # (client_id, attempts, client)
            
        # Enviar posición a cada cliente
        for idx, (player_id, attempts, client_obj) in enumerate(sorted_winners, start=1):
            position_message = f"POSITION:{idx}"
            self.send_message(client_obj, position_message)
        
        # Reiniciar el juego
        self.restart_game()

    def restart_game(self):
        """Reinicia todas las variables y comienza un nuevo juego."""
        self.mysterious_word = self.elegir_palabra()  # Elige una nueva palabra aleatoria
        self.winners = []  # Vaciar la lista de ganadores
        self.clients = {}  # Vaciar la lista de clientes
        self.client_id_counter = 0  # Reiniciar el contador de ID de clientes
        self.game_over = False  # Reiniciar el estado de "juego terminado"
        print("El juego ha sido reiniciado.")

    def shutdown(self):
        """Cierra el servidor de manera segura."""
        print("Servidor cerrado.")
        self.server_socket.close()


# Ejecución del servidor
if __name__ == "__main__":
    host = socket.gethostname()  # Obtener el nombre del host
    port = 5000
    server = WordleServer(host, port)
    
    # Manejo de cierre limpio
    def sigint_handler(signal, frame):
        server.shutdown()
        os._exit(0)
    
    signal.signal(signal.SIGINT, sigint_handler)  # Capturar SIGINT (Ctrl+C)
    
    server.start()