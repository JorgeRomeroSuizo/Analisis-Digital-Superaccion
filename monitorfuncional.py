from customtkinter import *
#import psutil as ps
#import os
import sqlite3
import pywinctl as pwc
import time
#from datetime import *
#conexion = sqlite3.connect("prueba.db")
#cursor = conexion.cursor()
class VentanaPrueba(CTk):
    def __init__(self):
        super().__init__()
        self.conexion = sqlite3.connect("prueba.db")
        self.cursor = self.conexion.cursor()
        self.title("Pruebas superaccion")
        self.geometry("600x600")
        self.activo = False
        self.tiempoinicio = time.time()
        self.tiempoapertura = time.ctime()
        tabs=CTkTabview(self)
        tabs.pack(fill="both", expand=True)
        tabs.add("Estado monitor")
        tabs.add("Dibujo tabla")
        CTkButton(tabs.tab("Estado monitor"), text="Iniciar Monitoreo", command=self.activar).pack()
        CTkButton(tabs.tab("Estado monitor"), text="Pausar Monitoreo", command=self.desactivar).pack()
        self.estaactivo=CTkLabel(tabs.tab("Estado monitor"), text="Monitor: Desactivado")
        self.estaactivo.pack()
        self.monitor()

    def activar(self):
        self.tiempoinicio = time.time()
        self.tiempoapertura = time.ctime()
        self.activo=True
        #thread.start()
        self.estaactivo.configure(text="Monitor: Activado")
    def desactivar(self):
        self.activo=False
        self.estaactivo.configure(text="Monitor: Desactivado")
    def monitor(self):
            if self.activo:
                self.ventanaactiva = pwc.getActiveWindowTitle()
                self.after(2000, self.prueba)
            else:
                self.after(100, self.monitor)
    def prueba(self):
        ventanacomparacion = pwc.getActiveWindowTitle()
        if self.ventanaactiva != ventanacomparacion:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS datosenbruto(tiempodeapertura , nombre, tiempodeuso)")
            tiempodeuso = round(time.time() - self.tiempoinicio, 3)
            filaainsertar = (self.tiempoapertura, self.ventanaactiva, tiempodeuso)
            self.cursor.execute("INSERT INTO datosenbruto VALUES (?, ?, ?)", filaainsertar)
            self.conexion.commit()
            self.tiempoinicio = time.time()
            self.tiempoapertura = time.ctime()
            #self.conexion.close()
        self.after(0, self.monitor)

VentanaPrueba().mainloop()