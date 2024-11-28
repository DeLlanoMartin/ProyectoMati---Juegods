import socket
import threading
import customtkinter as ctk


class GameClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.client_gui = None
        self.current_game = None

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
                if not message:
                    break
                self.client_gui.display_message(message)
                if message == "GAME_OVER":
                    self.client_gui.enable_menu()  # Habilitar el menú después del fin del juego
        except Exception as e:
            print(f"Error al escuchar el servidor: {e}")

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
    def __init__(self, master, socket):
        super().__init__(master)
        self.master = master
        self.socket = socket

        # Título del juego
        ctk.CTkLabel(self, text="Juego 1", font=("Arial", 20)).pack(pady=20)

        # Crear un subframe para la grilla
        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(pady=10)

        # Lista para almacenar los botones de la grilla
        self.buttons = []

        # Crear la grilla de botones
        self.crear_botones()

        # Botón para salir al menú principal
        ctk.CTkButton(self, text="Volver al Menú", command=master.show_menu).pack(pady=20)

    def crear_botones(self):
        """Crear una grilla de botones dentro del subframe."""
        for i in range(9):
            button = ctk.CTkButton(
                self.grid_frame,  # Usamos el subframe para colocar la grilla
                text="", 
                command=lambda i=i: self.process_action(f"Button_{i+1}"),  # Identificador único
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

    def process_action(self, action):
        """Procesar las acciones del Juego 1."""
        print(f"Acción del botón: {action}")  # Mensaje en la consola para pruebas

        # Enviar acción al servidor
        try:
            self.socket.sendall(action.encode())
        except Exception as e:
            print(f"Error al enviar acción: {e}")


# Clase para el Juego 2
class Game2Client(ctk.CTkFrame):
    def __init__(self, master, socket):
        super().__init__(master)
        self.master = master
        self.socket = socket

        # Título del juego
        ctk.CTkLabel(self, text="Juego 2", font=("Arial", 20)).pack(pady=20)

        # Área de interacción
        self.info_label = ctk.CTkLabel(self, text="Bienvenido al Juego 2.")
        self.info_label.pack(pady=10)

        # Botones para enviar acciones
        ctk.CTkButton(self, text="Mover", command=lambda: self.process_action("Move")).pack(pady=5)

        # Botón para salir al menú principal
        ctk.CTkButton(self, text="Volver al Menú", command=master.show_menu).pack(pady=20)

    def process_action(self, action):
        """Procesar las acciones del Juego 2."""
        self.socket.sendall(action.encode())


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
            self.client.current_game.destroy()
            self.client.current_game = None
        self.menu_frame.pack(fill="both", expand=True)

    def select_game1(self):
        """Selecciona Juego 1."""
        self.geometry("500x500")
        self.client.current_game = Game1Client(self, self.client.socket)
        self.switch_to_game(self.client.current_game)

    def select_game2(self):
        """Selecciona Juego 2."""
        self.client.current_game = Game2Client(self, self.client.socket)
        self.switch_to_game(self.client.current_game)

    def select_game3(self):
        """Selecciona Juego 3."""
        self.client.current_game = Game3Client(self, self.client.socket)
        self.switch_to_game(self.client.current_game)

    def switch_to_game(self, game_frame):
        """Cambia al frame del juego seleccionado."""
        self.menu_frame.pack_forget()
        game_frame.pack(fill="both", expand=True)

    def display_message(self, message):
        """Mostrar mensajes recibidos del servidor."""
        print(f"Mensaje del servidor: {message}")

    def exit_client(self):
        """Salir del cliente."""
        self.client.disconnect()
        self.quit()


if __name__ == "__main__":
    client = GameClient()
    client.connect_to_server()

    gui = GameClientGUI(client)
    gui.mainloop()
