#Se planea implementar filtros para la tabla y falta hacer el analizador.
#Por favor perdondar faltas de ortografia y malos comentarios. En mi vida eh comentado el codigo entonces no se como se debe de hacer.
from customtkinter import * #En vez de tkinter por que se ve mas bonito
#import psutil as ps
#import os
import sqlite3 #Para bases de datos
import pywinctl as pwc #Para obtener la ventana activa
import time #Para el tiempo. Puede que se cambie despues
from tkinter import ttk #Lastimosamente el CutomCtk no tiene el ttk.tree que hace la vida mas facil para mostrar la tabla.
#from datetime import *
#conexion = sqlite3.connect("prueba.db")
#cursor = conexion.cursor()
class VentanaPrueba(CTk):
    def __init__(self):
        super().__init__()
        self.filas=0 #Guarda la ultima rowid dibujada de la tabla para que asi actualizarla sea mas facil.
                     #Se empieza en 0 para que la primera vez que dibuje dibuje en 1, la primera fila.
        self.conexion = sqlite3.connect("prueba.db") #Inicializa conexion con la base de datos o la crea si no existe.
        self.cursor = self.conexion.cursor() #Crea el cursor de la base de datos.
        self.title("Pruebas superaccion")
        self.geometry("600x600")
        self.activo = False #Esta variable se encarga de ver si el monitor de actividad esta activo o no. El monitor de actividad registra que ventana esta activa.
        self.tiempoinicio = time.time() #Crea un tiempo inicial no legible para humanos con fin de calculos.
        self.tiempoapertura = time.ctime() #Crea un tiempo inicial legible para humanos.
        tabs=CTkTabview(self) #Vista en pestanas como navegador.
        tabs.pack(fill="both", expand=True)
        tabs.add("Estado monitor") #Se anaden las dos usadas.
        tabs.add("Dibujo tabla")
        CTkButton(tabs.tab("Estado monitor"), text="Iniciar Monitoreo", command=self.activar).pack()
        CTkButton(tabs.tab("Estado monitor"), text="Pausar Monitoreo", command=self.desactivar).pack()
        self.estaactivo=CTkLabel(tabs.tab("Estado monitor"), text="Monitor: Desactivado")
        self.estaactivo.pack()
        self.monitor()
        botonActualizar=CTkButton(tabs.tab("Dibujo tabla"), text="Actualizar Tabla", command=self.tabla) #Este boton actualiza la tabla
        botonActualizar.pack()
        #scroll=CTkScrollableFrame(tabs.tab("Dibujo tabla"))
        #scroll.pack(fill="both", expand=True)
        # CTkLabel(scroll, text="Tiempo de apertura").pack(padx=10, pady=10, side="left")
        # CTkLabel(scroll, text="Aplicacion").pack(padx=10, pady=10, side="left")
        # CTkLabel(scroll, text="Tiempo de uso").pack(padx=10, pady=10, side="right")
        self.tree = ttk.Treeview(tabs.tab("Dibujo tabla"), columns=("col1", "col2", "col3"), show="headings") #treeview se usa porque hace mas facil la vida al hacer tablas
        self.tree.heading("col1", text="Tiempo de apertura") #Se les ponen titulos a las columnas
        self.tree.heading("col2", text="Aplicacion")
        self.tree.heading("col3", text="Tiempo de uso")
        self.tree.pack(fill="both", expand=True)
        botonActualizar.invoke() #Se llama al boton una vez para que aparezca dibujada al iniciar el programa.

    def activar(self): #Esta funcion activa el monitor
        self.tiempoinicio = time.time()
        self.tiempoapertura = time.ctime()
        self.activo=True
        self.estaactivo.configure(text="Monitor: Activado")
    def desactivar(self): #Esta funcion desactiva el monitor
        self.activo=False
        self.estaactivo.configure(text="Monitor: Desactivado")
    def monitor(self): #Esta funcion consigue la ventana activa y espera 2 segundos para comparar (llamando a la funcion comparar).
                       #Esta funcion solo llama a comparar si se define el monitor como activo. Si no esta activo solo espera 100 ms para llamarse a si misma.
            if self.activo:
                self.ventanaactiva = pwc.getActiveWindowTitle()
                self.after(2000, self.comparar)
            else:
                self.after(100, self.monitor)
    def comparar(self): #Esta funcion encuentra si se cambia de ventana. Si si, crea la tabla de sql si no existe y guarda los datos de la ventana anterior. NO LA ACTUAL.
                        #Redefine cual es la ventana activa actual y vuelve a llamar a monitor (que llama esta misma funcion).
        ventanacomparacion = pwc.getActiveWindowTitle()
        if self.ventanaactiva != ventanacomparacion:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS datosenbruto(tiempodeapertura , nombre, tiempodeuso)") #Esto probablemente se pueda sacar de aquí pero no quiero arriesgarme ahorita.
            tiempodeuso = round(time.time() - self.tiempoinicio, 3)
            filaainsertar = (self.tiempoapertura, self.ventanaactiva, tiempodeuso)
            self.cursor.execute("INSERT INTO datosenbruto VALUES (?, ?, ?)", filaainsertar)
            self.conexion.commit()
            self.tiempoinicio = time.time()
            self.tiempoapertura = time.ctime()
            #self.conexion.close()
        self.after(0, self.monitor)
    def tabla(self): #Esta funcion inserta los datos de la tabla de sql en la tabla dibujada por ttk.treeview.
        self.cursor.execute("SELECT * FROM datosenbruto WHERE rowid > ?", (self.filas,)) #Dibuja solo desde donde no se a dibujado para ahorrar recursos.
        filasainsertar = self.cursor.fetchall()
        for i in filasainsertar:
            self.tree.insert("", "end", values=i)
        self.cursor.execute("SELECT MAX(rowid) FROM datosenbruto")
        self.filas=self.cursor.fetchone()[0] #Redefine desde donde se tiene que insertar.
VentanaPrueba().mainloop()