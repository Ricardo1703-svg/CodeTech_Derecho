import tkinter as tk
from tkinter import ttk
import serial

# --- CONFIGURAR PUERTO COM DEL ARDUINO ---
# Cambia COM5 por el puerto que uses
ser = serial.Serial('COM5', 9600, timeout=1)

# --- FUNCIÓN PARA LEER EL SENSOR ---
def leer_sensor():
    try:
        linea = ser.readline().decode().strip()

        if linea:
            # Suponiendo que el Arduino manda "24.5,60.2"
            partes = linea.split(",")

            if len(partes) == 2:
                temp.set(f"{partes[0]} °C")
                hum.set(f"{partes[1]} %")

        # Actualiza cada 1 segundo
        root.after(1000, leer_sensor)

    except Exception as e:
        temp.set("Error")
        hum.set("Error")

# --- INTERFAZ TKINTER ---
root = tk.Tk()
root.title("Monitor de Sensor Arduino")
root.geometry("350x250")
root.resizable(False, False)

titulo = ttk.Label(root, text="Sensor Arduino", font=("Arial", 18))
titulo.pack(pady=10)

# Variables
temp = tk.StringVar(value="Esperando...")
hum = tk.StringVar(value="Esperando...")

ttk.Label(root, text="Temperatura:", font=("Arial", 14)).pack()
lbl_temp = ttk.Label(root, textvariable=temp, font=("Arial", 16))
lbl_temp.pack(pady=5)

ttk.Label(root, text="Humedad:", font=("Arial", 14)).pack()
lbl_hum = ttk.Label(root, textvariable=hum, font=("Arial", 16))
lbl_hum.pack(pady=5)

# Inicia lectura del sensor
leer_sensor()

root.mainloop()
