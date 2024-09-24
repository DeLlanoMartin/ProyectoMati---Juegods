import socket
import threading
import customtkinter

# Crear un array para almacenar las referencias a los botones
buttons = []

app = customtkinter.CTk()

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
client_socket.connect((host, port))

# Variable para identificar el cliente
client_id = None

# Función para mandar mensajes
def send_message(message):
    if message:
        client_socket.send(message.encode())

# Función para recibir mensajes
def receive_messages():
    global client_id
    # Recibir el ID del cliente asignado por el servidor
    client_id = int(client_socket.recv(1024).decode())
    print(f"Client ID asignado: {client_id}")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Conexión cerrada por el servidor.")
                break

            # Recibe el botón que el otro jugador presionó y su ID, luego lo separa en 2 variables
            button_index, player = data.decode().split(',')
            button_index = int(button_index) - 1
            
            # Actualizar el botón según el jugador
            if player == "1":
                buttons[button_index].configure(text="X", state="disabled", fg_color="red")
            elif player == "2":
                buttons[button_index].configure(text="O", state="disabled", fg_color="blue")
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
    client_socket.close()

board = [None] * 9  # None indica que ese botón no ha sido presionado

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


# Función para verificar si hay un ganador
def check_winner():

    for combination in winning_combinations:
        a, b, c = combination
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a]  # Devuelve "X" o "O", dependiendo del ganador
    return None  # No hay ganador aún

# Variable global para verificar si hay un ganador
game_over = False

# Función para ganar
def win():
    global game_over
    game_over = True  # Marcar que el juego ha terminado
    for button in buttons:
        button.configure(state="disabled")  # Desactivar todos los botones
    print(f"¡El jugador {client_id} ha ganado!")

# Actualizar el estado del tablero cuando un botón es presionado
def button_callback(i):
    global board, game_over
    print(f"Botón {i} presionado")
    print(game_over)

    if not game_over and board[i-1] is None:  # Solo permitir si no hay ganador
        if client_id == 1:
            buttons[i-1].configure(text="X", state="disabled", fg_color="red")  # Jugador 1 usa "X"
            board[i-1] = "X"
        elif client_id == 2:
            buttons[i-1].configure(text="O", state="disabled", fg_color="blue")  # Jugador 2 usa "O"
            board[i-1] = "O"
        
        # Enviar el movimiento al servidor
        send_message(f"{i},{client_id}")

        # Comprobar si hay un ganador después del movimiento
        winner = check_winner()
        if winner:
            win()  # Llama a la función para manejar el ganador

# Crear botones
for i in range(9):
    button = customtkinter.CTkButton(
        app, 
        text="", 
        command=lambda i=i: button_callback(i+1),
        height=100, 
        width=100
    )
    
    # Crea una grilla
    button.grid(
        # La fila de cada botón es el resultado entero de la división de su número por 3
        row=i // 3,
        # La fila es el resto de la división de su numero por 3
        column=i % 3,
        # Padding que settea los márgenes
        padx=10, 
        pady=10)
    buttons.append(button)

# Iniciar un hilo para recibir mensajes del servidor
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Iniciar la interfaz gráfica
app.mainloop()
