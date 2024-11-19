import socket
import threading
import customtkinter as ctk

# Inicializar la app
app = ctk.CTk()
app.title("4 en Raya")
app.geometry("375x450")

# Crear el socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
client_socket.connect((host, port))

# Variables globales
client_id = None  # ID del cliente asignado por el servidor
turn = None  # Turno actual
game_over = False  # Indica si el juego ha terminado
filas = 6
columnas = 7  # Tamaño del tablero int
tablero = [[0 for _ in range(columnas)] for _ in range(filas)]  # Estado del tablero

# Crear la grilla visual
etiquetas = [[None for _ in range(columnas)] for _ in range(filas)]

def enviar_mensaje(mensaje):
    if mensaje and not game_over:  # No permitir enviar mensajes si el juego ha terminado
        mensaje = str(mensaje).encode()
        client_socket.send(mensaje)

# Función para recibir mensajes del servidor
def recibir_mensajes():
    global client_id, turn, game_over, tablero

    # Recibir el ID del cliente asignado por el servidor
    client_id = client_socket.recv(1024).decode()
    print(f"ID del cliente asignado: {client_id}")

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("Conexión cerrada por el servidor.")
                break

            mensaje = data.decode()

        except ConnectionResetError:
            print("Conexión perdida con el servidor.")
            break
    client_socket.close()

# Crear la grilla de etiquetas
for fila in range(filas):
    for columna in range(columnas):
        etiqueta = ctk.CTkLabel(
            app, 
            text="", 
            width=50, 
            height=50, 
            fg_color="white",  # Color inicial
            corner_radius=10
        )
        etiqueta.grid(
            row=fila, 
            column=columna, 
            padx=2, 
            pady=5)
        etiquetas[fila][columna] = etiqueta

def button_callback(boton):
    enviar_mensaje(boton)

# Crear los botones para seleccionar columnas
for columna in range(columnas):
    boton = ctk.CTkButton(
        app,
        text = columna + 1,
        command=lambda c=columna: button_callback(c+1),
        height=40,
        width=50,       
    )

    boton.grid(
        row=filas, 
        column=columna, 
        padx=0, 
        pady=0)

# Crear un Label para mostrar mensajes (ganador, turno, etc.)
message_label = ctk.CTkLabel(app, text="Esperando inicio...", font=("Arial", 16))
message_label.grid(row=filas + 1, column=0, columnspan=columnas, pady=10)

# Iniciar hilo para recibir mensajes
hilo_receptor = threading.Thread(target=recibir_mensajes, daemon=True)
hilo_receptor.start()

# Ejecutar la app
app.mainloop()