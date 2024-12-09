import socket
import threading
import customtkinter as ctk

class ClientApp(ctk.CTk):
    def __init__(self, host, port):
        super().__init__()
        self.title("Cliente de Adivina la Palabra")
        self.geometry(f"450x250")
        self.attempts = 0
        self.running = True
        
        # Configuración de la conexión con el servidor
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        
        self.client_id = None
        self.mysterious_word_length = 0
        
        # Interfaz gráfica
        self.build_gui()
        
        # Iniciar un hilo para recibir mensajes del servidor
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def build_gui(self):
        # Etiqueta para mostrar el ID del jugador
        self.jugador_label = ctk.CTkLabel(self, text="Esperando ID...", font=("Arial", 18))
        self.jugador_label.pack(pady=10)
        
        # Campo para que el jugador ingrese su intento
        self.word_entry = ctk.CTkEntry(self, placeholder_text="Escribe tu intento aquí")
        self.word_entry.pack(pady=10)
        
        # Botón para enviar el intento
        self.send_button = ctk.CTkButton(self, text="Enviar", command=self.process_attempt)
        self.send_button.pack(pady=10)

        self.exit_button = ctk.CTkButton(self, text="Salir", command=self.exit_game)
        self.exit_button.pack(side="bottom", pady=10)
        
        # TextBox para mostrar mensajes adicionales
        self.result_text = ctk.CTkLabel(self, text="", width=400, height=10)
        self.result_text.pack(pady=10)
    
    def exit_game(self):
        self.running = False
        self.client_socket.sendall("DISCONNECT".encode())  # Enviar un mensaje para informar que el cliente se desconectará
        self.client_socket.close()
        self.destroy()


    def process_attempt(self):
        """Procesa el intento del jugador y lo envía al servidor."""
        self.attempt = self.word_entry.get().strip().lower()
        if len(self.attempt) != self.mysterious_word_length:
            self.result_text.configure(self, text= f"El intento debe tener la misma cantidad de letras que la palabra misteriosa.\n ({self.mysterious_word_length})")
            return
        elif not self.attempt.isalpha():
            self.result_text.configure(self, text="No se permiten símbolos, sólo letras")
            return
        
        if self.attempts==10:
            self.result_text.configure(self, text=f"Límite de {self.attempts} intentos alcanzado")
            self.send_button.configure(state="disabled")
            return
        self.attempts += 1

        self.client_socket.send(f"TRY:{self.attempt}:{self.attempts}".encode())
        self.word_entry.delete(0, "end")  # Limpiar el campo de entrada

    def receive_messages(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    print("Conexión cerrada por el servidor.")
                    break
                
                message = data.decode()
                print(message)
                if message.startswith("ID"):
                    self.client_id = message.split(":")[1]
                    self.jugador_label.configure(text=f"Eres el Jugador {self.client_id}")
                    print(f"ID: {self.client_id}")
                
                elif message.startswith("WORD"):
                    self.mysterious_word_length = int(message.split(":")[1])
                    self.result_text.configure(self, text=f"La palabra tiene {self.mysterious_word_length} caracteres")
                
                elif message.startswith("RESULT"):
                    result = message.split(":")[1].split(",")
                    self.update_hidden_word(result)
                
                elif message.startswith("WIN"):
                    self.result_text.configure(text= f"¡Felicidades, adivinaste la palabra con {self.attempts} intentos!")
                    self.send_button.configure(state="disabled")
                
                elif message.startswith("POSITION"):
                    position = message.split(":")[1]

                    self.result_text.configure(text=f"¡Felicidades, quedaste en la posición {position} con {self.attempts} intentos!")
                
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
        finally:
            self.client_socket.close()

    def update_hidden_word(self, result):
        display_word = []
        self.attempt = list(self.attempt)

        for res in result:
            if res == "CORRECT":
                display_word.append("C")  # Verde para la letra correcta
            elif res == "DIFF":
                display_word.append("D")  # Amarillo para la letra correcta pero en otra posición
            elif res == "NO":
                display_word.append("N")  # Gris para la letra incorrecta
            else:
                display_word.append("_")  # En caso de que algo no se haya procesado correctamente

        # Crear un contenedor Frame para las letras
        self.letters_frame = ctk.CTkFrame(self)
        self.letters_frame.pack(pady=5)  # Usamos pack para colocar el Frame
        self.geometry(f"450x{self.attempts*44 + 250}")

        # Ahora también añadimos los colores correspondientes a cada letra en el Frame
        for i, res in enumerate(result):
            letter = self.attempt[i].upper()  # La letra correspondiente de la palabra intentada
            if res == "CORRECT":
                color = "green"  # Si la letra es correcta y está en la posición correcta
            elif res == "DIFF":
                color = "yellow"  # Si la letra está en la palabra pero en una posición incorrecta
            elif res == "NO":
                color = "gray"  # Si la letra no está en la palabra
            else:
                color = "lightblue"  # Color predeterminado para letras no procesadas
            
            # Crear una nueva etiqueta para cada letra con el color correspondiente
            letter_label = ctk.CTkLabel(self.letters_frame, text=letter, font=("Arial", 20), width=30, height=30, fg_color=color, text_color="black")
            
            # Colocar la etiqueta en el grid en la columna correspondiente
            letter_label.grid(row=0, column=i, padx=2, pady=2)



# Configuración del cliente
if __name__ == "__main__":
    host = socket.gethostname()
    port = 5000
    app = ClientApp(host, port)
    app.mainloop()