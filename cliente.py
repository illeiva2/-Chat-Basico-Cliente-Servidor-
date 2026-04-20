import socket

# Configuración de la conexión al servidor
HOST = 'localhost'
PORT = 5000


# Conectar al servidor y enviar mensajes hasta que el usuario escriba "éxito"
def iniciar_cliente():
    """Conecta al servidor y permite enviar múltiples mensajes en una sesión."""
    try:
        # Crear el socket TCP/IP del cliente
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((HOST, PORT))
        print(f"[Cliente] Conectado al servidor {HOST}:{PORT}")
        print("[Cliente] Escribe un mensaje y presiona Enter para enviarlo.")
        print("[Cliente] Escribe 'éxito' para salir.\n")

        with cliente_socket:
            while True:
                # Solicitar mensaje al usuario
                mensaje = input("Tú: ").strip()

                if not mensaje:
                    continue

                # Verificar condición de salida ANTES de enviar
                if mensaje.lower() == 'éxito':
                    print("[Cliente] Sesión finalizada.")
                    break

                # Enviar el mensaje al servidor
                cliente_socket.sendall(mensaje.encode('utf-8'))

                # Recibir y mostrar la respuesta del servidor
                respuesta = cliente_socket.recv(1024).decode('utf-8')
                print(f"Servidor: {respuesta}\n")

    except ConnectionRefusedError:
        print(f"[Cliente] No se pudo conectar al servidor en {HOST}:{PORT}. "
              "Asegúrate de que el servidor esté corriendo.")
    except OSError as e:
        print(f"[Cliente] Error de conexión: {e}")
    except KeyboardInterrupt:
        print("\n[Cliente] Conexión interrumpida por el usuario.")


# Punto de entrada principal
if __name__ == '__main__':
    iniciar_cliente()
