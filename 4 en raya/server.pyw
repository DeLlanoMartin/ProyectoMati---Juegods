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

# Función para verificar si hay un ganador
def verificar_ganador():
    # Verificar horizontal, vertical y diagonal
    for fila in range(6):
        for columna in range(7):
            if tablero[fila][columna] == 0:
                continue
            # Horizontal
            if columna + 3 < 7 and all(tablero[fila][columna + i] == tablero[fila][columna] for i in range(4)):
                return tablero[fila][columna]
            # Vertical
            if fila + 3 < 6 and all(tablero[fila + i][columna] == tablero[fila][columna] for i in range(4)):
                return tablero[fila][columna]
            # Diagonal derecha
            if fila + 3 < 6 and columna + 3 < 7 and all(tablero[fila + i][columna + i] == tablero[fila][columna] for i in range(4)):
                return tablero[fila][columna]
            # Diagonal izquierda
            if fila + 3 < 6 and columna - 3 >= 0 and all(tablero[fila + i][columna - i] == tablero[fila][columna] for i in range(4)):
                return tablero[fila][columna]
    return 0  # No hay ganador aún

# Función para manejar cada cliente
def manejar_cliente(socket_cliente, client_id):
    global turno, game_over

    try:
        while True:
            if game_over:
                socket_cliente.send("El juego ha terminado.".encode())
                break
            
            # Recibir el movimiento del cliente
            data = socket_cliente.recv(1024)
            if not data:
                print(f"Cliente {client_id} se desconectó.")
                break
            else:
                print(f"Datos recibidos de Cliente {client_id}: {data}")

            columna = int(data.decode()) - 1  # Convertir columna a índice (de 1 a 0)

            print("columna presionada: ", columna+1)

            # Verificar si es el turno del cliente
            if client_id != turno:
                socket_cliente.send("Espera tu turno.".encode())
                continue

            print("turno: ", turno)

            # Encontrar la fila más baja disponible en la columna
            for fila in range(5, -1, -1):
                if tablero[fila][columna] == 0:
                    tablero[fila][columna] = client_id  # Asignar el movimiento del jugador
                    break
            else:
                socket_cliente.send("Columna llena.".encode())
                continue

            # Verificar si hay un ganador
            ganador = verificar_ganador()
            if ganador:
                game_over = True
                for client in clients.values():
                    
                    client.send(f"TABLERO:{tablero}".encode())
                    client.send(f"Ganador: Jugador {ganador}".encode())
                break

            # Alternar el turno
            turno = 1 if turno == 2 else 2

            print("turno cambiado: ", turno)

            # Enviar el estado del tablero actualizado a todos los clientes
            for client in clients.values():
                client.send(f"TABLERO:{tablero}".encode())

            # Enviar el turno a todos los jugadores
            for client in clients.values():
                client.send(f"turno:{turno}".encode())
                
    except Exception as e:
        print(f"Error con Cliente {client_id}: {e}")
    finally:
        socket_cliente.close()

# Configurar y escuchar el servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((host, port))
servidor.listen(2)  # Solo se permiten dos jugadores

print("Servidor iniciado. Esperando conexiones...")

# Aceptar dos clientes
client_id_counter = 1
while len(clients) < 2:
    socket_cliente, direccion = servidor.accept()
    print(f"Cliente conectado desde: {direccion}")
    clients[client_id_counter] = socket_cliente
    socket_cliente.send((f"ID:{client_id_counter}").encode())  # Enviar ID del cliente
    threading.Thread(target=manejar_cliente, args=(socket_cliente, client_id_counter)).start()
    client_id_counter += 1

print("Dos jugadores conectados. ¡Inicia el juego!")