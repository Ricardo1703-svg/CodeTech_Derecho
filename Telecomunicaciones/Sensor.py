import tkinter as tk
from tkinter import messagebox, ttk
from pymongo import MongoClient
from time import strftime, time
import serial
import smtplib
from email.mime.text import MIMEText
import locale

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except locale.Error:
        print("Advertencia: No se pudo configurar el locale a español. El día puede aparecer en inglés.")

temp_actual = "N/A"
hum_actual = "N/A"
ultimo_guardado_timestamp = time()

email_timer_counter = 0


# ------------------ CONFIGURACIÓN SERIAL ------------------
# Asegúrate de que el puerto COM y el baudrate sean correctos
try:
    ser = serial.Serial('COM12', 9600)
except serial.SerialException as e:
    # Manejar el error si el puerto serial no se puede abrir
    messagebox.showerror("Error Serial", f"No se pudo abrir el puerto serial 'COM12':\n{e}")
    ser = None


# ------------------ CONFIGURACIÓN MONGODB ------------------
MONGO_URI = "mongodb://Ricardo:root2023@localhost:27017/?authMechanism=DEFAULT"
DB_NAME = "sensores"
COLLECTION_NAME = "dht11"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command('ping') # Prueba la conexión
    MONGO_READY = True
except Exception as e:
    messagebox.showerror("Error MongoDB", f"No se pudo conectar a MongoDB:\n{e}")
    MONGO_READY = False

# ------------------ CONFIGURACIÓN EMAIL Y REPORTE AUTOMÁTICO ------------------
EMAIL_USER = "richdevtest17@gmail.com"
EMAIL_PASSWORD = "LA QUE CREE JEJEJEJEJJEJEJEJEJ"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Correo fijo para reportes automáticos
EMAIL_REPORTE_FIJO = "ralvares961@gmail.com"

# ------------------ TKINTER SETUP ------------------
root = tk.Tk()
root.title("Monitor de Datos de Arduino")

# Centrar la ventana
window_width = 700
window_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width/2) - (window_width/2)
y_coordinate = (screen_height/2) - (window_height/2)
root.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")

# Configuración de la rejilla (grid) principal
for i in range(2):
    root.grid_columnconfigure(i, weight=1)
    
# ------------------ ETIQUETAS DE DÍA Y HORA ------------------

etiqueta_fecha = tk.Label(root, text="Día", font=('calibri', 14, 'bold'), background='black', foreground='white')
etiqueta_fecha.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="ew")

etiqueta_hora = tk.Label(root, text="Hora", font=('calibri', 14, 'bold'), background='black', foreground='white')
etiqueta_hora.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="ew")

# ------------------ ETIQUETAS DE TEMPERATURA Y HUMEDAD ------------------

etiqueta_temp = tk.Label(root, text="Temperatura (°C): Esperando...", font=('calibri', 12),
                        background='#ff8282', foreground='black', padx=10, pady=5)
etiqueta_temp.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

etiqueta_hum = tk.Label(root, text="Humedad (%): Esperando...", font=('calibri', 12),
                       background='#82c6ff', foreground='black', padx=10, pady=5)
etiqueta_hum.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# ------------------ TABLA (Treeview) ------------------

columnas_tabla = ("Temperatura", "Humedad", "Fecha", "Hora")
tabla = ttk.Treeview(root, columns=columnas_tabla, show="headings", height=10)

tabla.heading("Temperatura", text="Temperatura (°C)")
tabla.heading("Humedad", text="Humedad (%)")
tabla.heading("Fecha", text="Fecha")
tabla.heading("Hora", text="Hora")

tabla.column("Temperatura", width=100, anchor="center")
tabla.column("Humedad", width=100, anchor="center")
tabla.column("Fecha", width=80, anchor="center")
tabla.column("Hora", width=80, anchor="center")

tk.Label(root, text="Registros de la base de datos", font=('calibri', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=(10, 0))

tabla.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

# ------------------ FUNCIONES DE DATOS Y ACTUALIZACIÓN ------------------

def actualizar_hora():
    """Actualiza las etiquetas de hora y fecha, mostrando el día en español."""
    etiqueta_hora.config(text=strftime('%H:%M:%S %p'))
    etiqueta_fecha.config(text=strftime('%A, %d/%m/%Y').capitalize()) 
    root.after(1000, actualizar_hora)

def leer_y_mostrar_datos():
    """Lee datos del serial y actualiza las etiquetas de T/H (cada segundo)."""
    global temp_actual, hum_actual
    
    if ser and ser.is_open:
        try:
            linea = ser.readline().decode('utf-8').rstrip()
            
            if ',' in linea:
                temp_str, hum_str = linea.split(',')
                
                temp_actual = temp_str.strip()
                hum_actual = hum_str.strip()
                
                etiqueta_temp.config(text=f"Temperatura (°C): {temp_actual}")
                etiqueta_hum.config(text=f"Humedad (%): {hum_actual}")
            else:
                etiqueta_temp.config(text="Temperatura (°C): Error de formato")
                etiqueta_hum.config(text="Humedad (%): Error de formato")

        except serial.SerialTimeoutException:
            pass
        except ValueError:
            print("Error de conversión de datos a float.")
        except Exception as e:
            print(f"Error de lectura serial: {e}")
            etiqueta_temp.config(text="Temperatura (°C): Error")
            etiqueta_hum.config(text="Humedad (%): Error")
    else:
        etiqueta_temp.config(text="Temperatura (°C): SERIAL CERRADO")
        etiqueta_hum.config(text="Humedad (%): SERIAL CERRADO")
        
    root.after(1000, leer_y_mostrar_datos)

def cargar_tabla():
    """Carga los registros de MongoDB en la tabla Treeview."""
    if not MONGO_READY:
        return
        
    tabla.delete(*tabla.get_children())
    try:
        for doc in collection.find().sort([("_id", -1)]).limit(100):
            temp = doc.get("Temperatura", "N/A")
            hum = doc.get("Humedad", "N/A")
            fecha = doc.get("Fecha", "N/A")
            hora = doc.get("Hora", "N/A")
            tabla.insert("", "end", values=(temp, hum, fecha, hora))
    except Exception as e:
        messagebox.showerror("Error de Carga", f"Error al cargar datos de MongoDB:\n{e}")


def guardar_datos(manual=True):
    """
    Guarda la última lectura de T/H en MongoDB.
    Si se llama manualmente (por botón), muestra un messagebox.
    """
    if not MONGO_READY:
        if manual:
            messagebox.showwarning("Advertencia", "No hay conexión a MongoDB. No se puede guardar.")
        return
        
    if temp_actual == "N/A" or hum_actual == "N/A":
        if manual:
            messagebox.showwarning("Advertencia", "Aún no se han recibido datos válidos del serial.")
        return

    datos_hora = strftime('%H:%M:%S %p')
    datos_fecha = strftime('%d/%m/%Y')
    
    documento = {
        "Temperatura": temp_actual, 
        "Humedad": hum_actual, 
        "Fecha": datos_fecha, 
        "Hora": datos_hora
    }

    try:
        result = collection.insert_one(documento)
        if manual:
            messagebox.showinfo("Genial", f"Registro insertado:\nTemperatura: {temp_actual}°C\nHumedad: {hum_actual}%\nID: {result.inserted_id}")
        
        cargar_tabla()
    except Exception as e:
        if manual:
            messagebox.showerror("Error", f"No se pudo guardar en MongoDB:\n{e}")

# ------------------ FUNCIÓN DE ENVÍO DE REPORTE AUTOMÁTICO (Cada 2 Minutos) ------------------
def enviar_reporte_automatico():
    """Envía un reporte periódico con la última lectura al correo fijo."""
    
    if temp_actual == "N/A" or hum_actual == "N/A":
        return

    # 1. Preparar el contenido del correo
    asunto = "Reporte Automático T/H"
    
    contenido = "Este es un reporte automático de las condiciones ambientales actuales:\n\n"
    contenido += f"Temperatura: {temp_actual}°C\n"
    contenido += f"Humedad: {hum_actual}%\n"
    contenido += f"Fecha y Hora del reporte: {strftime('%d/%m/%Y')} - {strftime('%H:%M:%S %p')}\n"

    try:
        # 2. Configurar y enviar el mensaje
        mensaje = MIMEText(contenido)
        mensaje["Subject"] = asunto
        mensaje["From"] = EMAIL_USER
        mensaje["To"] = EMAIL_REPORTE_FIJO # Usar la variable renombrada

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, EMAIL_REPORTE_FIJO, mensaje.as_string())
        server.quit()
        
        print(f"Reporte automático enviado correctamente a {EMAIL_REPORTE_FIJO}.")

    except Exception as e:
        print(f"Error al enviar el reporte automático: {e}")
        # No mostrar messagebox para no interrumpir el flujo automático


# ------------------ TAREAS PERIÓDICAS (GUARDADO Y REPORTE) ------------------
def ejecutar_tareas_periodicas():
    """
    Ejecuta el guardado en MongoDB cada 1 minuto.
    Y el Reporte Automático cada 2 minutos (usando el contador).
    """
    global email_timer_counter
    
    # 1. Guardar en MongoDB (Cada 1 minuto)
    guardar_datos(manual=False)
    
    # 2. Verificar si es momento de enviar el reporte (Cada 2 minutos = 2 iteraciones de 1 minuto)
    email_timer_counter += 1
    if email_timer_counter >= 2: 
        enviar_reporte_automatico()
        email_timer_counter = 0 # Reiniciar el contador
    
    # Programar la próxima ejecución en 60 segundos (1 minuto)
    root.after(60000, ejecutar_tareas_periodicas)


# ------------------ FUNCIÓN DE ENVÍO DE CORREO (INTERNA) ------------------
# Esta función se mantiene para el envío manual (por el botón).
def _enviar_correo_final(destino_email, ventana_correo):
    """Lógica que ejecuta el envío real del correo."""
    if not MONGO_READY:
        messagebox.showwarning("Advertencia", "No hay conexión a MongoDB para obtener el último registro.")
        return

    if not destino_email or "@" not in destino_email or "." not in destino_email:
        messagebox.showerror("Error", "Por favor, introduce una dirección de correo válida.")
        return

    try:
        # Obtener el último registro de MongoDB
        ultimo = collection.find_one(sort=[("_id", -1)])

        if not ultimo:
             messagebox.showwarning("Advertencia", "No hay registros guardados en la base de datos.")
             return

        contenido = "Último registro Arduino:\n\n"
        contenido += f"Temperatura: {ultimo.get('Temperatura', 'N/A')}°C\n"
        contenido += f"Humedad: {ultimo.get('Humedad', 'N/A')}%\n"
        contenido += f"Fecha: {ultimo.get('Fecha', 'N/A')}\n"
        contenido += f"Hora: {ultimo.get('Hora', 'N/A')}\n"

        mensaje = MIMEText(contenido)
        mensaje["Subject"] = "Datos de Temperatura y Humedad (Arduino)"
        mensaje["From"] = EMAIL_USER
        mensaje["To"] = destino_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, destino_email, mensaje.as_string())
        server.quit()
        
        ventana_correo.destroy()
        messagebox.showinfo("Correo", "Correo enviado correctamente a: " + destino_email)

    except Exception as e:
        messagebox.showerror("Error de Envío", f"No se pudo enviar el correo. Revise la configuración o la App Password:\n{e}")

# ------------------ FUNCIÓN PARA ABRIR VENTANA DE CORREO ------------------
def abrir_ventana_correo():
    """Abre una nueva ventana Toplevel para que el usuario introduzca el correo de destino."""
    
    ventana_correo = tk.Toplevel(root)
    ventana_correo.title("Destinatario de Correo")
    ventana_correo.geometry("350x150")
    ventana_correo.resizable(False, False)
    
    tk.Label(ventana_correo, text="Correo de Destino:", font=('calibri', 12)).pack(pady=10, padx=20)
    
    email_entry = tk.Entry(ventana_correo, width=40, font=('calibri', 10))
    email_entry.pack(pady=5, padx=20)
    
    btn_enviar = tk.Button(ventana_correo, text="Enviar Datos", 
                           command=lambda: _enviar_correo_final(email_entry.get(), ventana_correo),
                           bg="#ffd966", font=("Arial Black", 11))
    btn_enviar.pack(pady=15)
    
    ventana_correo.grab_set()
    root.wait_window(ventana_correo)


# ------------------ BOTONES ------------------

# Botón "Guardar Registro" (llama a guardar_datos manualmente)
btn_guardar = tk.Button(root, text="Guardar Registro", command=lambda: guardar_datos(manual=True),
                        bg="#8bff82", font=("Arial Black", 11))
btn_guardar.grid(row=3, column=0, padx=5, pady=20, sticky="ew")

# Botón "Enviar por Correo" (llama a la ventana de input)
btn_correo = tk.Button(root, text="Enviar por Correo", command=abrir_ventana_correo,
                         bg="#ffd966", font=("Arial Black", 11))
btn_correo.grid(row=3, column=1, padx=5, pady=20, sticky="ew")


# ------------------ CERRAR VENTANA ------------------
def cerrar_ventana():
    """Cierra el puerto serial y la ventana de la aplicación."""
    if ser and ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", cerrar_ventana)

# ------------------ INICIO DE LA APLICACIÓN ------------------
actualizar_hora()
leer_y_mostrar_datos()
ejecutar_tareas_periodicas()
cargar_tabla()

# Iniciar el bucle principal de Tkinter
root.mainloop()