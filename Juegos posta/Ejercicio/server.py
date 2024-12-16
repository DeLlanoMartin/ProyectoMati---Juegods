import socket
import threading
import random
import time

clients = {}
elecciones = []
adivinanzas = {}
secret_number = random.randint(1, 100)
empate = False
turn = None

# Enviar un mensaje a todos los clientes
def send_to_clients(message):
    for client_socket in clients.values():
        client_socket.sendall(message.encode())

def handle_client(client_socket, client_id):
    global elecciones, secret_number, adivinanzas, empate, turn

    client_socket.sendall("Elija cara (1) o seca (2)".encode())

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            print(f"Mensaje recibido del cliente {client_id}: {data}")

            # Procesar elección inicial (cara o seca)
            if data.startswith("eleccion"):
                eleccion = int(data.split(":")[1])
                elecciones.append((eleccion, client_id))

                if len(elecciones) == 2:  # Cuando ambos jugadores hayan elegido
                    if elecciones[0][0] == elecciones[1][0]:  # Si hay empate
                        empate = True
                        send_to_clients("Ambos jugadores eligieron lo mismo. Adivinen un número entre 1 y 100.")
                    else:  # No hay empate, decidir ganador
                        # Lanzar la moneda
                        resultado_moneda = random.randint(1, 2)
                        print(f"Resultado de la moneda: {'cara' if resultado_moneda == 1 else 'seca'} (valor: {resultado_moneda})")

                        # Identificar quién eligió qué
                        jugador_1 = elecciones[0]
                        jugador_2 = elecciones[1]

                        # Determinar ganador
                        if jugador_1[0] == resultado_moneda:
                            ganador = jugador_1[1]
                            perdedor = jugador_2[1]
                        else:
                            ganador = jugador_2[1]
                            perdedor = jugador_1[1]

                        # Anunciar resultado
                        send_to_clients(f"Salió {'cara' if resultado_moneda == 1 else 'seca'}. Gana el jugador {ganador}!")

                        # Reiniciar variables para la siguiente ronda
                        elecciones.clear()
                        secret_number = random.randint(1, 100)
                        turn = None
                        time.sleep(0.1)
                        send_to_clients("Elija cara (1) o seca (2)")
            
            # Procesar adivinanzas en caso de empate
            elif data.isdigit() and empate:
                adivinanzas[client_id] = int(data)
                if len(adivinanzas) == 2:  # Ambos jugadores adivinaron
                    jugador_1, jugador_2 = list(adivinanzas.items())
                    diff_1 = abs(secret_number - jugador_1[1])
                    diff_2 = abs(secret_number - jugador_2[1])

                    if diff_1 < diff_2:
                        turn = jugador_1[0]
                    elif diff_2 < diff_1:  
                        turn = jugador_2[0]
                    else:
                        turn = random.choice([jugador_1[0], jugador_2[0]])

                    send_to_clients(f"El número secreto era {secret_number}. El jugador {turn} elige primero.")
                    empate = False
                    adivinanzas.clear()

            # Procesar elección final del jugador que ganó  
            elif data.startswith("final"):
                final_eleccion = int(data.split(":")[1])
                other_client = [cid for cid in clients if cid != client_id][0]
                send_to_clients(f"El jugador {client_id} eligió {'cara' if final_eleccion == 1 else 'seca'}.")
                time.sleep(0.1)
                clients[other_client].sendall(f"Te toca {'seca' if final_eleccion == 1 else 'cara'}.".encode())
                elecciones.clear()

                moneda = random.randint(1,2)
                print(moneda)

                if moneda == final_eleccion:
                    send_to_clients(f"Salió {'cara' if moneda == 1 else 'seca'}. Gana el jugador {client_id}!")
                else:
                    send_to_clients(f"Salió {'cara' if moneda == 1 else 'seca'}. Gana el jugador {other_client}!")

                # Reiniciar para la siguiente ronda
                elecciones.clear()
                secret_number = random.randint(1, 100)
                turn = None
                empate = False
                send_to_clients("Elija cara (1) o seca (2)")

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
