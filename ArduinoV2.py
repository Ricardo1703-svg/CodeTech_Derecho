import tkinter as tk
import serial
from time import sleep

ser = serial.Serial('COM13', 9600)
sleep(2)

def leer_datos():
    try:
        linea = ser.readline().decode('utf-8').rstrip()
        temp, hum = linea.split(",")

        etiqueta.config(text=f"Temperatura: {temp}°C\nHumedad: {hum}%")

    except:
        etiqueta.config(text="Esperando datos...")

    root.after(1000, leer_datos)

root = tk.Tk()
root.title("Lectura DHT11")

etiqueta = tk.Label(root, text="Iniciando...", font=("Arial", 18))
etiqueta.pack(pady=20)

root.after(1000, leer_datos)
root.mainloop()
