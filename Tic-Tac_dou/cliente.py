import socket
import threading
import customtkinter

def tic_tac_tou(client_socket):
    buttons = []
    tictac_pantalla = customtkinter.CTk()
    client_id = None
    turn = None
    game_over = False
    board = [None] * 9  # Representación del tablero en el cliente

    def send_message(message):
        print("enviar mensaje ejecutado")
        if message and not game_over:
            client_socket.send(message.encode())

    def receive_messages():
        nonlocal client_id, turn, game_over
        client_id = int(client_socket.recv(1024).decode())  # Recibe el ID del cliente
        print(f"Client ID asignado: {client_id}")

        while not game_over:
            try:

                #ESTA LÍNEA NO SE EJECUTA
                data = client_socket.recv(1024)
                print("mensaje recibido")
                if not data:
                    print("Conexión cerrada por el servidor.")
                    break

                message = data.decode()

                # Manejar mensaje de ganador
                if "winner" in message:
                    winner_id = message.split(',')[1]
                    handle_game_over(winner_id)
                    break


                # Obtener índice de botón y jugador
                button_index, player = map(int, message.split(','))
                update_button(button_index - 1, player)

                
                
                # Cambiar el turno
                turn = 1 if player == 2 else 2

            except ConnectionResetError:
                print("Conexión perdida con el servidor.")
                break

        client_socket.close()

    def update_button(index, player):
        # Actualiza el botón en la interfaz gráfica
        if player == 1:
            buttons[index].configure(text="X", state="disabled", fg_color="red")
            board[index] = "X"
        elif player == 2:
            buttons[index].configure(text="O", state="disabled", fg_color="blue")
            board[index] = "O"
        disable_buttons() if turn != client_id else enable_buttons()  # Habilita botones en su turno

    def handle_game_over(winner_id):
        nonlocal game_over
        game_over = True
        disable_buttons()
        print(f"¡El jugador {winner_id} ha ganado!")

    def disable_buttons():
        for button in buttons:
            button.configure(state="disabled")

    def enable_buttons():
        for button in buttons:
            if button.cget("text") == "" and not game_over:
                button.configure(state="normal")

    def button_callback(i):
        print("button callback ejecutado")
        nonlocal board, game_over
        print(f"Botón {i} presionado")

        # Solo permite interacción si es el turno del cliente y la posición está vacía
        print(game_over, board[i - 1], client_id, turn)
        if not game_over and board[i - 1] is None and client_id == turn:
            print("ejecutado el if del button callback")
            if client_id == 1:
                buttons[i - 1].configure(text="X", state="disabled", fg_color="red")
                board[i - 1] = "X"
            elif client_id == 2:
                buttons[i - 1].configure(text="O", state="disabled", fg_color="blue")
                board[i - 1] = "O"

            send_message(f"{i},{client_id}")
            disable_buttons()

    # Crear botones de la cuadrícula del juego
    for i in range(9):
        button = customtkinter.CTkButton(
            tictac_pantalla,
            text="",
            command=lambda i=i: button_callback(i + 1),
            height=100,
            width=100
        )
        button.grid(row=i // 3, column=i % 3, padx=10, pady=10)
        buttons.append(button)
    print("botones creados")

    # Iniciar hilo para recibir mensajes
    threading.Thread(target=receive_messages).start()
    tictac_pantalla.mainloop()

# Configuración del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
client_socket.connect((host, port))

tic_tac_tou(client_socket)
