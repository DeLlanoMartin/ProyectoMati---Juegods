import socket
import threading
import customtkinter as ctk


class GameClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.client_gui = GameClientGUI(self)
        self.current_game = None
        self.client_id = None
        self.turn = 1
        self.winner = None

    def connect_to_server(self):
        """Conectar al servidor."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Conectado al servidor en {self.host}:{self.port}")

        # Iniciar hilo para escuchar mensajes del servidor
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def listen_to_server(self):
        """Escuchar mensajes del servidor en un hilo separado."""
        try:
            while True:
                message = self.socket.recv(1024).decode()
                print(f"mensaje: {message}")
                if not message:
                    break
                elif not self.client_gui:
                    print("self.client_gui no está inicializado.")
                if message == "GAME_OVER":
                    self.client_gui.enable_menu()  # Habilitar el menú después del fin del juego
                elif message.startswith("ID:"):
                    print(message)
                    self.client_id = message.split(":")[1]
                elif message.startswith("TURN:"):
                    self.turn = int(message.split(":")[1])
                elif message.startswith("WINNER"):
                    print("se recibe mensaje de ganador")
                    self.winner = message.split(":")[1]
                    print(f"Ganador: {self.winner}")
                elif message.startswith("MOVE"):
                    _, move, player_id = message.split(":")
                    self.current_game.process_action(int(move), int(player_id))
                

        except Exception as e:
            print(f"Error al escuchar el servidor: {e}")
            print(f"mensaje intentado: {message}") 

    def send_message(self, message):
        """Enviar un mensaje al servidor."""
        try:
            self.socket.sendall(message.encode())
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")

    def disconnect(self):
        """Desconectar del servidor."""
        self.send_message("DISCONNECT")
        self.socket.close()


# Clase para el Juego 1
class Game1Client(ctk.CTkFrame):
    def __init__(self, master, client, socket):
        super().__init__(master)
        self.master = master
        self.client = client  # Instancia completa de GameClient
        self.socket = socket
        self.client_id = int(self.client.client_id)
        self.winner = None

        # Mostrar el ID del cliente como ejemplo
        ctk.CTkLabel(self, text=f"Tu ID: {self.client_id}", font=("Arial", 20)).pack(pady=20)

        # Crear un subframe para la grilla
        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(pady=10)

        self.buttons = []  # Lista para almacenar los botones de la grilla
        self.board = [None] * 9  # None indica que ese botón no ha sido presionado
        
        # Crear la grilla de botones
        self.crear_botones()

        # Informar al servidor que este cliente seleccionó el juego
        self.socket.sendall("GAME_SELECTION:Game1".encode())

        # Botón para volver al menú principal
        ctk.CTkButton(self, text="Volver al Menú", command=master.show_menu).pack(pady=20)

    def show_winner_label(self, winner):
        """Mostrar un Label en el centro de la pantalla como una barra horizontal al ganar."""
        winner_text = f"¡Jugador {winner} ha ganado!"
        self.winner_label = ctk.CTkLabel(
            self,
            text=winner_text,
            font=("Arial", 24, "bold"),  # Texto en negrita
            fg_color="#FF69B4",         # Color melón
            text_color="white",         # Texto blanco
            corner_radius=10,           # Bordes redondeados
            width=self.winfo_width(),   # Ancho del Label igual al de la pantalla
            height=50                   # Altura de la barra
        )
        # Posicionar el Label como una barra horizontal en el medio
        self.winner_label.place(relx=0.5, rely=0.5, anchor="center")


    def crear_botones(self):
        """Crear una grilla de botones dentro del subframe."""
        for i in range(9):
            button = ctk.CTkButton(
                self.grid_frame,  # Usamos el subframe para colocar la grilla
                text="", 
                command=lambda i=i: self.update_game(i),  # Identificador único
                height=100, 
                width=100
            )
            # Colocar el botón en la grilla
            button.grid(
                row=i // 3,  # Determina la fila
                column=i % 3,  # Determina la columna
                padx=10, 
                pady=10
            )
            self.buttons.append(button)  # Agregar el botón a la lista

    def process_action(self, move, player):
        print("entra a process action")
        index = int(move)
        if self.board[index] is None:  # Si el botón no ha sido presionado
            # Actualizar visualización del botón
            self.board[index] = "X" if player == 1 else "O"
            self.buttons[index].configure(
                text=self.board[index], 
                state="disabled", 
                fg_color="red" if player == 1 else "blue", 
                font=("Arial", 30)
                )

        if self.client.winner != None:
            self.show_winner_label(self.client.winner)
            for button in self.buttons:
                print(f"Deshabilitando botón: {button}")
                button.configure(state="disabled")
            ctk.CTkLabel(self, text=f"Tu ID: {self.client_id}", font=("Arial", 20)).pack(pady=20)

    def update_game(self, action):
        print(f"se presiona el botón: {action}")
        if self.client.turn != self.client_id:
            return
        try:                                                                                
            self.socket.sendall(f"MOVE:{action}".encode())
        except Exception as e:
            print(f"Error al enviar el movimiento: {e}")

# Clase para el Juego 2
class Game2Client(ctk.CTkFrame):
    def __init__(self, master, client, socket):
        super().__init__(master)
        self.master = master
        self.client = client  # Instancia completa de GameClient
        self.socket = socket
        self.client_id = int(self.client.client_id)
        self.winner = None

        # Array de arrays para guardar la grilla visual
        self.etiquetas = [[None for _ in range(7)] for _ in range(6)]
        
        # Array de arrays para guardar la grilla de botones
        self.board = [[0 for _ in range(7)] for _ in range(6)] 
        
        # Mostrar el ID del cliente como ejemplo
        ctk.CTkLabel(self, text=f"Tu ID: {self.client_id}", font=("Arial", 20)).pack(pady=20)

        # Crear un subframe para la grilla
        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(pady=10)
        
        # Crear la grilla de botones
        self.crear_botones()

        # Informar al servidor que este cliente seleccionó el juego
        self.socket.sendall("GAME_SELECTION:Game2".encode())

        # Botón para volver al menú principal
        ctk.CTkButton(self, text="Volver al Menú", command=master.show_menu).pack(pady=20)

    def show_winner_label(self, winner):
        """Mostrar un Label en el centro de la pantalla como una barra horizontal al ganar."""
        winner_text = f"¡Jugador {winner} ha ganado!"
        self.winner_label = ctk.CTkLabel(
            self,
            text=winner_text,
            font=("Arial", 24, "bold"),  # Texto en negrita
            fg_color="#FF69B4",         # Color melón
            text_color="white",         # Texto blanco
            corner_radius=10,           # Bordes redondeados
            width=self.winfo_width(),   # Ancho del Label igual al de la pantalla
            height=50                   # Altura de la barra
        )
        # Posicionar el Label como una barra horizontal en el medio
        self.winner_label.place(relx=0.5, rely=0.5, anchor="center")

    def crear_botones(self):
        """Crear una grilla de botones dentro del subframe."""
        for columna in range(7):
            boton = ctk.CTkButton(
                self.grid_frame,  # Cambiado a self.grid_frame
                text=str(columna + 1), 
                command=lambda c=columna: self.update_game(c),
                height=40, 
                width=50
            )
            boton.grid(
                row=6,  # Fila para los botones (debajo de la grilla)
                column=columna, 
                padx=2, 
                pady=2
            )
        for fila in range(6):
            for columna in range(7):
                # Crear cada etiqueta con más redondez
                etiqueta = ctk.CTkLabel(
                    self.grid_frame,  # Cambiado a self.grid_frame
                    text="",
                    width=50,              # Ancho de cada celda
                    height=50,             # Alto de cada celda
                    fg_color="white",      # Fondo blanco de la celda
                    corner_radius=25,      # Aumentar el radio para mayor redondeo
                )
                etiqueta.grid(row=fila, column=columna, padx=3, pady=3)  # Aumenté el espacio entre celdas
                self.etiquetas[fila][columna] = etiqueta

    def process_action(self, move, player):
        for fila in range(5, -1, -1):
            if self.board[fila][move] == 0:
                self.board[fila][move] = player  # Asignar el movimiento del jugador
                break

        colores = {0: "white", 1: "red", 2: "#98FB98"}
        for fila in range(6):
            for columna in range(7):
                etiqueta = self.etiquetas[fila][columna]  # Asegúrate de acceder a cada etiqueta
                etiqueta.configure(fg_color=colores[self.board[fila][columna]])               
        print("color actualizado")

        if self.client.winner:
            self.show_winner_label(self.client.winner)
            for fila in self.etiquetas:
                for etiqueta in fila:  # Recorrer cada etiqueta individualmente
                    etiqueta.configure(state="disabled")


    def update_game(self, action):
        if self.client.turn != self.client_id:
            return
        
        try:
            self.socket.sendall(f"MOVE:{action}".encode())
        except Exception as e:
            print(f"Error al enviar el movimiento: {e}")



# Clase para el Juego 3
class Game3Client(ctk.CTkFrame):
    def __init__(self, master, socket):
        super().__init__(master)
        self.master = master
        self.socket = socket

        # Título del juego
        ctk.CTkLabel(self, text="Juego 3", font=("Arial", 20)).pack(pady=20)

        # Área de interacción
        self.info_label = ctk.CTkLabel(self, text="Acción especial del Juego 3.")
        self.info_label.pack(pady=10)

        # Botones para enviar acciones
        ctk.CTkButton(self, text="Especial", command=lambda: self.process_action("Special")).pack(pady=5)

        # Botón para salir al menú principal
        ctk.CTkButton(self, text="Volver al Menú", command=master.show_menu).pack(pady=20)

    def process_action(self, action):
        """Procesar las acciones del Juego 3."""
        self.socket.sendall(action.encode())


# Clase GUI que maneja la interfaz del cliente
class GameClientGUI(ctk.CTk):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.client.client_gui = self

        self.title("Cliente de Juegos")
        self.geometry("400x300")

        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.pack(fill="both", expand=True)

        # Etiqueta principal
        self.label = ctk.CTkLabel(self.menu_frame, text="Menú Principal", font=("Arial", 20))
        self.label.pack(pady=20)

        # Botones para seleccionar el juego
        self.game1_button = ctk.CTkButton(self.menu_frame, text="Jugar Juego 1", command=self.select_game1)
        self.game1_button.pack(pady=10)

        self.game2_button = ctk.CTkButton(self.menu_frame, text="Jugar Juego 2", command=self.select_game2)
        self.game2_button.pack(pady=10)

        self.game3_button = ctk.CTkButton(self.menu_frame, text="Jugar Juego 3", command=self.select_game3)
        self.game3_button.pack(pady=10)

        # Botón para salir
        self.exit_button = ctk.CTkButton(self.menu_frame, text="Salir", command=self.exit_client)
        self.exit_button.pack(pady=10)

    def show_menu(self):
        """Volver al menú principal."""
        self.geometry("400x300")
        if self.client.current_game:
            self.client.current_game.destroy()  # Destruir el frame actual del juego
            self.client.current_game = None
        self.menu_frame.pack(fill="both", expand=True)

    def select_game1(self):
        """Selecciona Juego 1."""
        self.geometry("500x500")
        self.client.turn = 1  # Reinicia el turno global
        self.client.winner = None  # Reinicia el ganador
        self.client.current_game = Game1Client(self, self.client, self.client.socket)  # Nueva instancia
        self.switch_to_game(self.client.current_game)


    def select_game2(self):
        """Selecciona Juego 2."""
        self.geometry("405x525")
        self.client.turn = 1  # Reinicia el turno global
        self.client.winner = None  # Reinicia el ganador
        self.client.current_game = Game2Client(self, self.client, self.client.socket)
        self.switch_to_game(self.client.current_game)

    def select_game3(self):
        """Selecciona Juego 3."""
        self.client.current_game = Game3Client(self, self.client.socket, self.client.client_id)
        self.switch_to_game(self.client.current_game)

    def switch_to_game(self, game_frame):
        """Cambia al frame del juego seleccionado."""
        self.menu_frame.pack_forget()
        game_frame.pack(fill="both", expand=True)

    def exit_client(self):
        """Salir del cliente."""
        self.client.disconnect()
        self.quit()


if __name__ == "__main__":
    client = GameClient()
    client.connect_to_server()

    gui = GameClientGUI(client)
    gui.mainloop()