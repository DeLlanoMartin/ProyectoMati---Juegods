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

def send_message(message):
    if message:
        client_socket.send(message.encode())

def receive_messages():
    global client_id
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Conexión cerrada por el servidor.")
                break
            
            # Separar el índice del botón y el jugador
            button_index, player = data.decode().split(',')
            button_index = int(button_index) - 1
            
            # Actualizar el botón según el jugador
            if player == "1":
                buttons[button_index].configure(text="X", state="disabled")
            elif player == "2":
                buttons[button_index].configure(text="O", state="disabled")
        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
    client_socket.close()

def button_callback(i):
    print(f"botón {i} presionado")
    if client_id==1:
        buttons[i-1].configure(text="X", state="disabled",fg_color="red")  # Deshabilitar el botón en esta interfaz
    else:
        buttons[i-1].configure(text="O", state="disabled",fg_color="red")
    send_message(f"{i},{client_id}")

# Crear botones
for i in range(9):
    button = customtkinter.CTkButton(
        app, 
        text="", 
        command=lambda i=i: button_callback(i+1),
        height=100, 
        width=100
    )
    button.grid(row=i // 3, column=i % 3, padx=10, pady=10)
    buttons.append(button)

# Iniciar un hilo para recibir mensajes del servidor
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Iniciar la interfaz gráfica
app.mainloop()
