import socket
import sqlite3
import datetime

# Configuración general del servidor
HOST = 'localhost'
PORT = 5000
DB_NAME = 'mensajes.db'


# Inicialización de la base de datos SQLite
def inicializar_db():
    """Crea la tabla de mensajes si no existe."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("[DB] Base de datos inicializada correctamente.")
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"[DB] No se pudo acceder a la base de datos: {e}")


# Guardar un mensaje en la base de datos
def guardar_mensaje(contenido, ip_cliente):
    """Guarda el mensaje recibido junto con la IP del cliente y la fecha/hora."""
    fecha_envio = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO mensajes (contenido, fecha_envio, ip_cliente) VALUES (?, ?, ?)',
            (contenido, fecha_envio, ip_cliente)
        )
        conn.commit()
        conn.close()
        print(f"[DB] Mensaje guardado de {ip_cliente}: '{contenido}'")
    except sqlite3.OperationalError as e:
        print(f"[DB] Error al guardar el mensaje: {e}")
        return None
    return fecha_envio


# Inicialización del socket TCP/IP
def inicializar_socket():
    """Crea y configura el socket del servidor en HOST:PORT."""
    try:
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar la dirección inmediatamente después de cerrar el servidor
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor_socket.bind((HOST, PORT))
        servidor_socket.listen(5)
        print(f"[Servidor] Escuchando en {HOST}:{PORT}...")
        return servidor_socket
    except OSError as e:
        raise RuntimeError(f"[Servidor] No se pudo iniciar el socket: {e}")


# Aceptar conexiones y recibir mensajes
def aceptar_conexiones(servidor_socket):
    """Acepta clientes en bucle y maneja los mensajes recibidos."""
    while True:
        try:
            cliente_socket, direccion = servidor_socket.accept()
            ip_cliente = direccion[0]
            print(f"[Servidor] Conexión aceptada de {ip_cliente}:{direccion[1]}")

            # Manejar mensajes del cliente en la misma conexión
            with cliente_socket:
                while True:
                    datos = cliente_socket.recv(1024)
                    if not datos:
                        print(f"[Servidor] Cliente {ip_cliente} desconectado.")
                        break

                    mensaje = datos.decode('utf-8').strip()
                    print(f"[Servidor] Mensaje recibido de {ip_cliente}: '{mensaje}'")

                    # Guardar el mensaje en la base de datos
                    timestamp = guardar_mensaje(mensaje, ip_cliente)

                    # Responder al cliente con confirmación y timestamp
                    if timestamp:
                        respuesta = f"Mensaje recibido: {timestamp}"
                    else:
                        respuesta = f"Mensaje recibido (error al guardar en DB): {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    cliente_socket.sendall(respuesta.encode('utf-8'))

        except KeyboardInterrupt:
            print("\n[Servidor] Servidor detenido por el usuario.")
            break
        except OSError as e:
            print(f"[Servidor] Error de conexión: {e}")
            break


# Punto de entrada principal
def main():
    inicializar_db()
    servidor_socket = inicializar_socket()
    try:
        aceptar_conexiones(servidor_socket)
    finally:
        servidor_socket.close()
        print("[Servidor] Socket cerrado.")


if __name__ == '__main__':
    main()
