import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
import bcrypt

# Conexión a MongoDB
client = MongoClient("mongodb://Ricardo:root2023@localhost:27017/?authMechanism=DEFAULT")
db = client["Arduino"]
users = db["Usuarios"]

# Función para registrar usuarios (solo para pruebas)
def registrar_usuario():
    username = entry_user.get()
    password = entry_pass.get()

    if username == "" or password == "":
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    # Hashear contraseña
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    users.insert_one({
        "usuario": username,
        "password": hashed
    })

    messagebox.showinfo("OK", "Usuario registrado correctamente")

# Función de login
def login():
    username = entry_user.get()
    password = entry_pass.get()

    user = users.find_one({"usuario": username})

    if user:
        if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            messagebox.showinfo("Correcto", f"Bienvenido {username}")
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
    else:
        messagebox.showerror("Error", "Usuario no encontrado")

# ---------------- Tkinter UI ----------------

root = tk.Tk()
root.title("Login MongoDB")
root.geometry("350x250")

tk.Label(root, text="Usuario:").pack(pady=5)
entry_user = tk.Entry(root, width=30)
entry_user.pack()

tk.Label(root, text="Contraseña:").pack(pady=5)
entry_pass = tk.Entry(root, width=30, show="*")
entry_pass.pack()

btn_login = tk.Button(root, text="Iniciar Sesión", command=login, bg="#6af")
btn_login.pack(pady=10)

btn_register = tk.Button(root, text="Registrar Usuario", command=registrar_usuario, bg="#7f7")
btn_register.pack(pady=5)

root.mainloop()