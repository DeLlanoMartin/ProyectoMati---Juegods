import socket
import threading
import customtkinter

# Creamos un array para almacenar las referencias a los botones
buttons = []

print("CLIENTE")

app = customtkinter.CTk()

# Crear un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Elegir el host y puerto al que conectar
host = socket.gethostname()
port = 12345

# Conectar el socket al servidor
client_socket.connect((host, port))

# Función para enviar mensajes al servidor desde la entrada de texto
def send_message():
    message = entry.get()  # Obtener el texto del campo de entrada
    client_socket.send(message.encode())
    if message == "no me da":
        client_socket.close()
    entry.delete(0, customtkinter.END)  # Limpiar el campo de entrada después de enviar el mensaje

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

# Iniciar un hilo para recibir mensajes del servidor
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

# Campo de entrada para enviar mensajes
entry = customtkinter.CTkEntry(app, width=300)
entry.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Botón para enviar mensajes
send_button = customtkinter.CTkButton(app, text="Enviar", command=send_message)
send_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Iniciar la interfaz gráfica
app.mainloop()
