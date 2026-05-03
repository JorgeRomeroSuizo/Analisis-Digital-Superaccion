from customtkinter import *
import psutil as ps
import os
import sqlite3
import pywinctl as pwc
import threading as th
import time
#from datetime import *
#conexion = sqlite3.connect("prueba.db")
#cursor = conexion.cursor()


activo=False
tiempoinicio=time.time()
tiempoapertura = time.ctime()


def monitor():
    global activo
    while True:
        while activo:
            global tiempoinicio
            global tiempoapertura
            conexion = sqlite3.connect("prueba.db")
            cursor = conexion.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS datosenbruto(tiempodeapertura , nombre, tiempodeuso)")
            ventanaactiva=pwc.getActiveWindowTitle()
            time.sleep(2)
            ventanacomparacion=pwc.getActiveWindowTitle()
            if ventanaactiva!=ventanacomparacion:
                tiempodeuso=round(time.time()-tiempoinicio, 3)
                filaainsertar=(tiempoapertura, ventanaactiva,tiempodeuso)
                cursor.execute("INSERT INTO datosenbruto VALUES (?, ?, ?)", filaainsertar)
                conexion.commit()
                tiempoinicio=time.time()
                tiempoapertura = time.ctime()
                conexion.close()

thread = th.Thread(target=monitor, daemon=True)
thread.start()

class VentanaPrueba(CTk):
    def __init__(self):
        super().__init__()
        self.title("Ventana Prueba")
        self.geometry("600x600")
        CTkButton(self, text="Iniciar Monitoreo", command=self.activar).pack()
        CTkButton(self, text="Pausar Monitoreo", command=self.desactivar).pack()
        self.estaactivo=CTkLabel(self, text="Monitor: Desactivado")
        self.estaactivo.pack()
    def activar(self):
        global activo
        global tiempoinicio
        global tiempoapertura
        tiempoinicio = time.time()
        tiempoapertura = time.ctime()
        activo=True
        #thread.start()
        self.estaactivo.configure(text="Monitor: Activado")
    def desactivar(self):
        global activo
        activo=False
        self.estaactivo.configure(text="Monitor: Desactivado")

VentanaPrueba().mainloop()
