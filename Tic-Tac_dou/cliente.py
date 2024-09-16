import socket
import threading
import customtkinter

# Creamos un array para almacenar las referencias a los botones
buttons = []

app = customtkinter.CTk()

# Función para enviar mensajes al servidor
def send_message():
    while True:
        message = input()
        client_socket.send(message.encode())
        if message == "no me da":
            client_socket.close()
            break

# Función para recibir mensajes del servidor
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Conexión cerrada por el servidor.")
                break
            print("Mensaje de otro jugador:", data.decode())
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
    client_socket.close()

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Elegir el host y puerto al que conectar
host = socket.gethostname()
port = 12345

# Conectar el socket al servidor
client_socket.connect((host, port))

# Iniciar un hilo para enviar mensajes al servidor
send_thread = threading.Thread(target=send_message)
send_thread.start()

# Iniciar un hilo para recibir mensajes del servidor sin bloquear la interfaz
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Lista de información para los botones
buttons_info = [
    {"text": "", "row": 0, "column": 0},
    {"text": "", "row": 0, "column": 1},
    {"text": "", "row": 0, "column": 2},
    {"text": "", "row": 1, "column": 0},
    {"text": "", "row": 1, "column": 1},
    {"text": "", "row": 1, "column": 2},
    {"text": "", "row": 2, "column": 0},
    {"text": "", "row": 2, "column": 1},
    {"text": "", "row": 2, "column": 2},
]

# Callback para los botones
def button_callback(i):
    print(f"botón {i} presionado")

# Creación de los botones y almacenamiento de referencia
for i, button_info in enumerate(buttons_info):
    button = customtkinter.CTkButton(
        app, 
        text=button_info["text"], 
        command=lambda i=i: button_callback(i+1),  # Pasamos 'i' al callback
        height=100, 
        width=100
    )
    button.grid(row=button_info["row"], column=button_info["column"], padx=10, pady=10)
    buttons.append(button)  # Almacenar cada botón en la lista

# Cambiar el texto del tercer botón (índice 2)
def change_button_text():
    buttons[2].configure(text="Nuevo Texto")

# Iniciar la interfaz gráfica
app.mainloop()
