import socket
import threading
from cryptography.fernet import Fernet

# Lista para armazenar clientes conectados, chaves e seus nomes
clients = []
usernames = {}
client_keys = {}  

# Função para enviar a chave Fernet para o cliente
def send_key(client):
    key = Fernet.generate_key()
    client_keys[client] = Fernet(key) 
    client.send(key)

# Envia a lista de usuários online para todos os clientes
def send_user_list():
    user_list = "Usuários online: " + ", ".join(usernames.values())
    broadcast(user_list.encode('utf-8'), None)

# Função para enviar mensagens criptografadas para todos os clientes
def broadcast(message, current_client):
    for client in clients:
        if client != current_client:
            try:
                cipher = client_keys[client]  # Pega a chave de criptografia do cliente
                encrypted_message = cipher.encrypt(message)
                client.send(encrypted_message)
            except Exception as e:
                print(f"Erro ao enviar para o cliente {client}: {e}")
                if client in clients:
                    clients.remove(client)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break

            print(f"Mensagem criptografada recebida: {message}")

            cipher = client_keys[client]
            decrypted_message = cipher.decrypt(message).decode('utf-8')

            print(f"Mensagem descriptografada: {decrypted_message}")

            # Reenvia a mensagem para os outros clientes descrptografada
            broadcast(decrypted_message.encode('utf-8'), client)
        except Exception as e:
            print(f"Erro ao lidar com o cliente: {e}")
            if client in clients:
                clients.remove(client)
            break

    # Remove o cliente da lista ao desconectar
    if client in clients:
        clients.remove(client)
    username = usernames.pop(client, None)
    client_keys.pop(client, None)  
    print(f"{username} desconectou.")
    send_user_list()

# Função principal para iniciar o servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen()

    print("Servidor iniciado...")

    while True:
        client, address = server.accept()
        print(f"Conexão estabelecida com {address}")

        # Envia uma chave de criptografia exclusiva para o cliente
        send_key(client)

        # Adiciona o cliente e seu nome de usuário
        clients.append(client)
        username = client.recv(1024).decode('utf-8')  # Espera que o cliente envie seu nome
        usernames[client] = username
        send_user_list()  

        # Inicia uma nova thread para lidar com o cliente
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    start_server()
