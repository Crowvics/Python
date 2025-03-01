import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from cryptography.fernet import Fernet
import datetime
from PIL import Image, ImageTk

client = None
cipher = None
user_name = None
root = None

# Função para conectar ao servidor e receber a chave de criptografia


def connect_to_server():
    global client, cipher

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 5555))
        # Recebe a chave de criptografia do servidor
        key = client.recv(1024)
        cipher = Fernet(key)

        # Inicia a thread de recebimento de mensagens
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()

        # Solicita o nome do usuário após a conexão ser estabelecida
        ask_for_username()
    except Exception as e:
        messagebox.showerror(
            "Erro de Conexão", f"Não foi possível conectar ao servidor:\n{e}")
        root.quit()

# Função para receber e desencriptar mensagens do servidor


def receive_messages():
    while True:
        try:
            message = client.recv(1024)
            if not message:  
                break
            decrypted_message = cipher.decrypt(message).decode('utf-8')
            if decrypted_message.startswith("Usuários online:"):
                update_user_list(decrypted_message)
            else:
                show_message(decrypted_message)
        except Exception as e:
            print("Erro ao receber a mensagem:", e)
            client.close()
            break

# Função para atualizar a lista de usuários online


def update_user_list(message):
    user_list = message.replace("Usuários online: ", "")
    user_list_area.config(state=tk.NORMAL)
    user_list_area.delete(1.0, tk.END)  
    user_list_area.insert(tk.END, user_list)
    user_list_area.config(state=tk.DISABLED)

# Função para enviar mensagens para o servidor


def send_message():
    message = message_entry.get()
    message_entry.delete(0, tk.END)

    if message:
        # Obtém a data e a hora atuais
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"{user_name} [{timestamp}]: {message}"
        encrypted_message = cipher.encrypt(formatted_message.encode('utf-8'))
        try:
            client.send(encrypted_message)
            show_message(f"Você [{timestamp}]: {message}")
        except Exception as e:
            show_message(f"Erro ao enviar a mensagem: {e}")

# Função para exibir mensagens no chat


def show_message(message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"{message}\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

# Função para solicitar o nome do usuário


def ask_for_username():
    global user_name
    user_name = simpledialog.askstring(
        "Nome de Usuário", "Por favor, insira seu nome:", parent=root)
    if not user_name:
        user_name = "Anônimo"
    root.title(f"Sala de Chat Criptografada - {user_name}")
    client.send(user_name.encode('utf-8'))

# Função para encerrar a conexão ao sair
def on_closing():
    if messagebox.askokcancel("Sair", "Você realmente deseja sair do chat?"):
        client.close()
        root.quit()

# Função para iniciar a GUI


def start_gui():
    global message_entry, chat_area, user_list_area, root

    # Cria a janela principal
    root = tk.Tk()
    root.geometry("1920x1080")

    # Carregar a imagem de fundo
    bg_image = Image.open("background.jpg")
    bg_image = bg_image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Canvas para inserir a imagem de fundo
    canvas = tk.Canvas(root, width=1920, height=1080)
    canvas.pack(fill="both", expand=True)

    # Coloca a imagem no canvas
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Frame para a lista de usuários online
    user_frame = tk.Frame(canvas, bg="#f2f2f2", bd=0)
    canvas.create_window(240, 300, window=user_frame, anchor="center")

    # Título para a lista de usuários online
    online_label = tk.Label(user_frame, text="Pessoas Online", font=(
        "Arial", 14, "bold"), bg="#f2f2f2")
    online_label.pack(pady=10)

    # Lista de usuarios online
    user_list_area = scrolledtext.ScrolledText(
        user_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, width=30, bg="#e0e0e0", fg="#000000")
    user_list_area.pack(padx=10, pady=10)
    user_list_area.config(borderwidth=5, relief="groove")

    # Frame para a entrada de mensagens
    message_frame = tk.Frame(canvas, bg="#f2f2f2", bd=0)
    canvas.create_window(240, 580, window=message_frame, anchor="center")

    # Caixa de entrada de texto para enviar mensagens
    message_entry = tk.Entry(message_frame, width=30, font=("Arial", 12))
    message_entry.pack(side=tk.LEFT, padx=10, pady=5)
    message_entry.config(borderwidth=5, relief="groove")

    # Botão de enviar
    send_button = tk.Button(message_frame, text="Enviar",
                            command=send_message, bg="black", fg="white", font=("Arial", 12))
    send_button.pack(side=tk.LEFT, padx=5)
    send_button.config(borderwidth=5, relief="groove")

    # Frame para o chat
    chat_frame = tk.Frame(canvas, bg="#f2f2f2", bd=0)
    canvas.create_window(960, 300, window=chat_frame, anchor="center")

    # Título do chat
    title_label = tk.Label(chat_frame, text="Chat Criptografado", font=(
        "Arial", 16, "bold"), bg="#f2f2f2")
    title_label.pack(pady=10)

    # Área de texto para o chat
    chat_area = scrolledtext.ScrolledText(
        chat_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, width=75, bg="#e0e0e0", fg="#000000")
    chat_area.pack(padx=10, pady=10)
    chat_area.config(borderwidth=5, relief="groove")

    # evento de fechamento
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Conectar ao servidor
    connect_to_server()

    # Inicia a interface
    root.mainloop()


if __name__ == "__main__":
    start_gui()
