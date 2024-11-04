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
turn = None  # Variable para controlar el turno
game_over = False  # Para saber si el juego ha terminado

# Función para mandar mensajes
def send_message(message):
    if message and not game_over:  # No permitir enviar mensajes si el juego ha terminado
        client_socket.send(message.encode())

# Función para recibir mensajes
def receive_messages():
    global client_id, turn, game_over
    # Recibir el ID del cliente asignado por el servidor
    client_id = int(client_socket.recv(1024).decode())
    print(f"Client ID asignado: {client_id}")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Conexión cerrada por el servidor.")
                break

            message = data.decode()

            # Verificar si el mensaje es el fin del juego
            if "winner" in message:
                winner_id = message.split(',')[1]
                handle_game_over(winner_id)
                break  # Salir del bucle una vez que el juego ha terminado

            # Recibe el botón que el otro jugador presionó y su ID
            button_index, player = message.split(',')
            button_index = int(button_index) - 1
            
            # Actualizar el botón según el jugador
            if player == "1":
                buttons[button_index].configure(text="X", state="disabled", fg_color="red")
            elif player == "2":
                buttons[button_index].configure(text="O", state="disabled", fg_color="blue")

            # Alternar turno
            turn = 1 if player == "2" else 2

            # Comprobar si es su turno
            if client_id == turn and not game_over:
                enable_buttons()
            else:
                disable_buttons()
                
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
    client_socket.close()

# Función para manejar el fin del juego
def handle_game_over(winner_id):
    global game_over
    game_over = True  # Marcar que el juego ha terminado
    for button in buttons:
        button.configure(state="disabled")  # Desactivar todos los botones
    print(f"¡El jugador {winner_id} ha ganado!")

def disable_buttons():
    for button in buttons:
        button.configure(state="disabled")

def enable_buttons():
    for button in buttons:
        # Solo habilitar botones vacíos si el juego no ha terminado
        if button.cget("text") == "" and not game_over:
            button.configure(state="normal")

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

# Función para ganar
def win():
    send_message(f"winner,{client_id}")  # Notificar al servidor del ganador

# Actualizar el estado del tablero cuando un botón es presionado
def button_callback(i):
    global board, game_over
    print(f"Botón {i} presionado")

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
        else:
            disable_buttons()  # Desactivar los botones hasta el próximo turno

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
        row=i // 3,
        column=i % 3,
        padx=10, 
        pady=10)
    buttons.append(button)

# Iniciar un hilo para recibir mensajes del servidor
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Iniciar la interfaz gráfica
app.mainloop()