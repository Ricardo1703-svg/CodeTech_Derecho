import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
from time import strftime
import serial

ser = serial.Serial('COM5', 9600)

client = MongoClient("mongodb://Ricardo:root2023@localhost:27017/?authMechanism=DEFAULT")
db = client["Arduino"]
collection = db["TemperaturayHumedad"]

def actualizar_etiqueta():
    data = ser.readline().decode('utf-8').rstrip()
    etiqueta.config(text="Dato recibido: " + data)
    root.after(1000, actualizar_etiqueta)

def actualizar_hora():
    string_hora = strftime('%H:%M:%S %p')
    etiqueta_hora.config(text=string_hora)
    string_fecha = strftime('%d/%m/%Y')
    etiqueta_fecha.config(text=string_fecha)
    root.after(1000, actualizar_hora)

def guardar_datos():
    datos_arduino = ser.readline().decode('utf-8').rstrip()
    datos_hora = strftime('%H:%M:%S %p')
    datos_fecha = strftime('%d/%m/%Y')
    documento = {"Datos": datos_arduino, "Fecha": datos_fecha, "Hora": datos_hora}
    result = collection.insert_one(documento)
    messagebox.showinfo("Genial", f"Documento insertado con id: {result.inserted_id}!")

root = tk.Tk()
root.title("Datos desde Arduino")

window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width/2) - (window_width/2)
y_coordinate = (screen_height/2) - (window_height/2)
root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

etiqueta_hora = tk.Label(root, font=('calibri', 10, 'bold'), background='black', foreground='white')
etiqueta_hora.pack(anchor='center')

etiqueta_fecha = tk.Label(root, font=('calibri', 10, 'bold'), background='red', foreground='black')
etiqueta_fecha.pack(anchor='center')

etiqueta = tk.Label(root, text="Esperando datos...", font=('calibri', 10, 'bold'), background='black', foreground='white')
etiqueta.pack(pady=10)

# Actualización de los datos
actualizar_etiqueta()
actualizar_hora()

# Botón para guardar datos
insertar_button = tk.Button(root, text="Guardar", command=guardar_datos, bg="#8bff82", font=("Arial Black", 11))
insertar_button.place(x=10, y=100)

# Cerrar la conexión serial al cerrar la ventana
def cerrar_ventana():
    ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", cerrar_ventana)

# Iniciar el bucle principal de Tkinter
root.mainloop()