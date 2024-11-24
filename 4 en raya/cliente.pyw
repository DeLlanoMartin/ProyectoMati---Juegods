import socket
import threading
import customtkinter as ctk
import ast

# Inicializar la app
app = ctk.CTk()
app.title("4 en Raya")
app.geometry("405x475")

# Crear el socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
client_socket.connect((host, port))

# Variables globales
client_id = None  # ID del cliente asignado por el servidor
turno = 1  # Indica si es el turno del cliente
tablero = [[0 for _ in range(7)] for _ in range(6)]  # Estado del tablero
game_over = False

jugador_label = ctk.CTkLabel(app, text="Esperando ID...", font=("Arial", 18))
jugador_label.grid(row=0, column=0, columnspan=7, pady=10, sticky="n")

# Función para actualizar la grilla visual
def actualizar_grilla():
    colores = {0: "white", 1: "red", 2: "#98FB98"}
    for fila in range(6):
        for columna in range(7):
            etiquetas[fila][columna].configure(fg_color=colores[tablero[fila][columna]])

# Función para manejar mensajes del servidor
def recibir_mensajes():
    global turno, tablero, game_over, client_id
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break

            mensaje = data.decode()
            
            if mensaje.startswith("ID:"):
                client_id = int(mensaje.split(":")[1])
                color = "red" if client_id == 1 else "#98FB98"
                jugador_label.configure(
                    text=f"Eres el Jugador {client_id}",
                    text_color=color
                )
            if mensaje.startswith("TABLERO:"):
                # Extraer el tablero y actualizarlo
                tablero = ast.literal_eval(mensaje[len("TABLERO:"):])
                actualizar_grilla()
            elif mensaje.startswith("Ganador"):
                message_label.configure(text=mensaje)
                game_over = True
            elif mensaje.startswith("Espera"):
                message_label.configure(text=mensaje)
            elif mensaje.startswith("Columna llena"):
                message_label.configure(text=mensaje)
            elif mensaje.startswith("turno:"):
                turno = int(mensaje.split(":")[1])
                print("Turno recibido:", turno)
                message_label.configure(text="Tu turno" if turno == client_id else "Esperando turno...")
                
        except Exception as e:
            print("Error al recibir mensaje:", e)
            break

# Crear la grilla visual
etiquetas = [[None for _ in range(7)] for _ in range(6)]
for fila in range(6):
    for columna in range(7):
        # Crear cada etiqueta con más redondez
        etiqueta = ctk.CTkLabel(
            app,
            text="",
            width=50,              # Ancho de cada celda
            height=50,             # Alto de cada celda
            fg_color="white",      # Fondo blanco de la celda
            corner_radius=25,      # Aumentar el radio para mayor redondeo
        )
        etiqueta.grid(row=fila+1, column=columna, padx=3, pady=3)  # Aumenté el espacio entre celdas
        etiquetas[fila][columna] = etiqueta


def enviar_movimiento(columna):
    print("cliente ID: ", client_id)
    print("turno: ", turno)
    if not game_over and turno == client_id:
        client_socket.send(str(columna).encode())

# Crear botones para seleccionar columna
for columna in range(7):
    boton = ctk.CTkButton(
        app, 
        text=str(columna + 1), 
        command=lambda c=columna: enviar_movimiento(c+1), 
        height=40, 
        width=50
        )
    boton.grid(
        row=6 + 1, 
        column=columna, 
        padx=2, 
        pady=2
        )
    


# Etiqueta para mensajes
message_label = ctk.CTkLabel(app, text="Esperando inicio...", font=("Arial", 16))
message_label.grid(row=7+1, column=0, columnspan=7, pady=10)

# Iniciar el hilo de recepción
threading.Thread(target=recibir_mensajes, daemon=True).start()

# Ejecutar la app
app.mainloop()
