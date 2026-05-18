#Se planea implementar filtros para la tabla y falta hacer el analizador.
#Por favor perdondar faltas de ortografia y malos comentarios. En mi vida eh comentado el codigo entonces no se como se debe de hacer.

    from customtkinter import * #En vez de tkinter por que se ve mas bonito
    import sqlite3 #Para bases de datos
    import pywinctl as pwc #Para obtener la ventana activa
    import time #Para el tiempo. Puede que se cambie despues
    from tkinter import ttk, messagebox #Lastimosamente el CutomCtk no tiene el ttk.tree que hace la vida mas facil para mostrar la tabla.   Al parecer tampoco tiene yesorno
    import datetime
    from ctk_date_picker import CTkDatePicker
class VentanaPrueba(CTk):
    def __init__(self):
        super().__init__()
        self.filas=0 #Guarda la ultima rowid dibujada de la tabla para que asi actualizarla sea mas facil. # Esto probablemente se pueda sacar de aquí pero no quiero arriesgarme ahorita.
                     #Se empieza en 0 para que la primera vez que dibuje dibuje en 1, la primera fila.
        self.conexion = sqlite3.connect("db1_distraido.db") #Inicializa conexion con la base de datos o la crea si no existe.
        self.cursor = self.conexion.cursor() #Crea el cursor de la base de datos.
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS datosenbruto(tiempodeapertura , nombre, tiempodeuso)")
        self.title("Pruebas superaccion")
        self.geometry("600x600")
        self.activo = False #Esta variable se encarga de ver si el monitor de actividad esta activo o no. El monitor de actividad registra que ventana esta activa.
        self.tiempoinicio = time.time() #Crea un tiempo inicial no legible para humanos con fin de calculos.
        self.tiempoapertura = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Crea un tiempo inicial legible para humanos.

        self.CATEGORIAS = { #Obviamente faltan aplicaciones por definir, pero esto se ira añadiendo por los usuarios a lo largo del tiempo.
            "productivo": ["vscode", "word", "excel", "pycharm", "notion",
                           "libreoffice", "code", "writer"],
            "distraccion": ["youtube", "netflix", "twitter", "instagram",
                            "facebook", "tiktok", "twitch", "reddit"],
            "comunicacion": ["whatsapp", "telegram", "discord", "slack", "zoom"],
            "neutral": ["chrome", "firefox", "explorer"]
        }
        self.FEEDBACK = { #Es el feedback que darle a la persona segun cada patrón
            "alto_distraccion": {
                "causa": "Usaste mas del 60% de tu tiempo en distracciones. Esto se debe a que la tarea genera gran estres, por lo cual se recurre impulsivamente a distracciones (Steel, 2007).",
                "tip": "Se recomienda usar el metodo pomodoro, consistente en 25 min trabajo y 5 min descanso. El compromiso corto reduce la aversión, lo cual lleva a completar tareas."
            },
            "hiperactividad_digital": {
                "causa": "Sesiones muy cortas indican dificultad de atención. Recuperar el foco toma ~23 min por interrupción (Mark et al., 2005).",
                "tip": "Intenta tener una sola app visible a la vez, esto incrementara tu atención"
            },
            "social_dominante": {
                "causa": "Tu tiempo en redes sociales supera tu tiempo de trabajo. El contacto social es más gratificante a corto plazo que el trabajo (Pychyl, 2013).",
                "tip": "Puedes revisar mensajes solo a horas fijas: 9am, 1pm, 6pm."
            },
            "muy_productivo": {
                "causa": "Menos del 20% en distracción. Tienes un enfoque muy bueno. (Steel, 2007).",
                "tip": "Anota qué condiciones te ayudaron hoy a mejorar y trata de repetirlas"
            },
            "equilibrado": {
                "causa": "Eres balanceado entre distraerte y ser productivo.",
                "tip": "Reducir distracción un 10% por semana puede tener gran impacto cuando se acumula."
            },
            "apps_no_clasificadas": {
                "causa": "Gran parte del tiempo lo usas en apps no reconocidas por el programa. El análisis puede ser incompleto.",
                "tip": "Agrega tus apps frecuentes a nuestra calificación para hacernos mejorar :D."
            },
            "patron_manana": {
                "causa": "Alta distracción antes de las 12pm. El inicio del dia es el momento mas vulnerable para un adolescente (Rozental & Carlbring, 2014).",
                "tip": "Trata de evitar el uso de dispositivos electronicos en la mañana, esto mejorara tu concentración a lo largo del dia"
            },
            "patron_tarde": {
                "causa": "Alta distracción después de las 3pm. El autocontrol se agota durante el día (Baumeister, 2002).",
                "tip": "Reserva tareas difíciles para la mañana donde tu mente es mas activa, y deja lo facil para la tarde, donde la mente es un poco mas rezagada"
            }
        }


        #Pestanas
        tabs=CTkTabview(self) #Vista en pestanas como navegador.
        tabs.pack(fill="both", expand=True)
        tabs.add("Estado monitor") #Se anaden las dos usadas.
        tabs.add("Dibujo tabla")
        tabs.add("Análisis")
        #------------------------

        #Botones monitor
        CTkButton(tabs.tab("Estado monitor"), text="Iniciar Monitoreo", command=self.activar).pack()
        CTkButton(tabs.tab("Estado monitor"), text="Pausar Monitoreo", command=self.desactivar).pack()
        #------------------------

        self.estaactivo=CTkLabel(tabs.tab("Estado monitor"), text="Monitor: Desactivado")
        self.estaactivo.pack()
        self.monitor()

        #Botones tabla
        botonActualizar=CTkButton(tabs.tab("Dibujo tabla"), text="Actualizar Tabla", command=self.tabla) #Este boton actualiza la tabla
        botonActualizar.pack()
        CTkButton(tabs.tab("Dibujo tabla"), text="limpiar", command=self.limpiar).pack()
        #------------------------

        #Tabla
        self.tree = ttk.Treeview(tabs.tab("Dibujo tabla"), columns=("col1", "col2", "col3"), show="headings") #treeview se usa porque hace mas facil la vida al hacer tablas
        self.tree.heading("col1", text="Tiempo de apertura") #Se les ponen titulos a las columnas
        self.tree.heading("col2", text="Aplicacion")
        self.tree.heading("col3", text="Tiempo de uso")
        self.tree.pack(fill="both", expand=True)

        tablaSlider=CTkTabview(tabs.tab("Dibujo tabla"))
        tablaSlider.pack()
        tablaSlider.add("Fecha inicial")
        tablaSlider.add("Fecha final")
        self.fInicial=CTkDatePicker(tablaSlider.tab("Fecha inicial"))
        self.fInicial.set_date_format("%Y-%m-%d")
        self.fInicial.pack()
        self.fFinal=CTkDatePicker(tablaSlider.tab("Fecha final"))
        self.fFinal.set_date_format("%Y-%m-%d")
        self.fFinal.pack()

        #Botones Analisis
        self.botonanalisis=CTkButton(tabs.tab("Análisis"), text="Analizar", command=self.analuzis)
        self.botonanalisis.pack()
        #Texto analisis
        self.textoAnalisis = CTkTextbox(tabs.tab("Análisis"))
        self.textoAnalisis.pack(fill="both", expand=True)
        #------------------------
        botonActualizar.invoke() #Se llama al boton una vez para que aparezca dibujada al iniciar el programa.
        CTkButton(tabs.tab("Dibujo tabla"), text="Filtrar tabla", command=self.filtrarTabla).pack() #Este boton actualiza la tabla


    def activar(self): #Esta funcion activa el monitor
        self.tiempoinicio = time.time()
        self.tiempoapertura = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            tiempodeuso = round(time.time() - self.tiempoinicio, 3)
            filaainsertar = (self.tiempoapertura, self.ventanaactiva, tiempodeuso)
            self.cursor.execute("INSERT INTO datosenbruto VALUES (?, ?, ?)", filaainsertar)
            self.conexion.commit()
            self.tiempoinicio = time.time()
            self.tiempoapertura = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.after(0, self.monitor)

    def tabla(self): #Esta funcion inserta los datos de la tabla de sql en la tabla dibujada por ttk.treeview.
        self.cursor.execute("SELECT * FROM datosenbruto WHERE rowid > ?", (self.filas,)) #Dibuja solo desde donde no se a dibujado para ahorrar recursos.
        filasainsertar = self.cursor.fetchall()
        self.escribirTabla(filasainsertar)
        self.cursor.execute("SELECT MAX(rowid) FROM datosenbruto")
        resultado = self.cursor.fetchone()[0]
        self.filas = resultado if resultado is not None else 0

    def filtrarTabla(self):
        self.filtrar(self.fInicial.get_date(), self.fFinal.get_date())
        self.limpiar(a=False)
        filasainsertar = self.cursor.fetchall()
        self.escribirTabla(filasainsertar)

    def escribirTabla(self, filasainsertar):
        for i in filasainsertar:
            self.tree.insert("", "end", values=i)

    def limpiar(self, a=True):
        if a:
            confirmacion=messagebox.askyesno("Confirmacion", "Esto eliminara todos los datos almacenados para su analisis, esta seguro de querer continuar?")
            if confirmacion:
                self.cursor.execute("DELETE FROM datosenbruto")
                self.conexion.commit()
                for i in self.tree.get_children():
                    self.tree.delete(i)
                self.filas=0
                self.tabla()
        else:
            for i in self.tree.get_children():
                self.tree.delete(i)

    def filtrar(self, tmpi, tmpf):
        self.cursor.execute("SELECT * FROM datosenbruto WHERE tiempodeapertura BETWEEN ? AND ?", (tmpi, tmpf))

    def oDatos(self): #Devuelve la tabla entera para analizarla luego
        self.cursor.execute("SELECT * FROM datosenbruto")
        return self.cursor.fetchall()

    def clasificar(self, nombreVentana): #Hace un for que recorre tanto la llave como la entrada del diccionario, y luego obtiene a que categoria pertenece
        nombre = nombreVentana.lower()
        for categoria, llaves in self.CATEGORIAS.items():
            for llave in llaves: #Obtiene solo las diferentes aplicaciones de una categoria
                if llave in nombre: #Determina si esa aplicación esta en el nombre de la aplicación que uso el usuario
                    return categoria
        return "desconocido" #Si no esta devuelve desconocido

    def calculaRatio(self, filas): #Indica el tiempo en cada aplicación
        totales = {"productivo": 0, "distraccion": 0,
                   "comunicacion": 0, "neutral": 0, "desconocido": 0}
        for apertura, nombre, uso in filas:
            cat = self.clasificar(nombre)
            totales[cat] += uso #esto le suma tiempo a la categoria segun la aplicación
        total = sum(totales.values()) #Suma todoo
        if total == 0:
            return totales, 0
        return totales, totales["distraccion"] / total #Retorna todos los totales y el radio de distracción

    def calculaCambios(self, filas): #Calcula el promedio de tiempo usado en cada aplicaciópn
        if len(filas) == 0:
            return 0
        totalTiempo=0
        for fila in filas:
            totalTiempo+=fila[2]
        return totalTiempo / len(filas)

    def calculaHoraPico(self, filas): #Calcula que hora se estuvo mas distraido
        horas = []
        for i in range(24):
            horas.append(0)
        for apertura, nombre, uso in filas:
            if self.clasificar(nombre) == "distraccion":
                horas[datetime.datetime.strptime(apertura, "%Y-%m-%d %H:%M:%S").hour] += uso #Suma a la hora correspondiente el tiempo de uso de la aplicación a esa hora
        return horas.index(max(horas)) #Retorna la hora con mas tiempo de distracción

    def calculaAppMasUsada(self, filas):
        apps = {}
        for apertura, nombre, uso in filas:
            if nombre in apps:
                apps[nombre] += uso #Si ya lo encuentra le añade el uso
            else:
                apps[nombre] = uso #Si es nuevo le añade el primer uso
        if not apps: #AJSJASSDAs al parecer un diccionario vacio evaluado como bool retorna false y si tiene algo true
            return "ninguna"
        return max(apps, key=apps.get) #Retorna el maximo VALOR, para eso esta el apps.get, si no retornaria alfabetico, un dolor de cabeza esta cosa

    def detectaPatrones(self, totales, tasa, ratio, ratioManana=0, ratioTarde=0): #Usa las demas funciones para identificar patrones, en la siguiente funcion van a ver
        patrones = []
        if ratio > 0.6:    #Ya me da hueva explicar que hace cada cosa, ehhh se va a explicar en la presentación si quieren :D
            patrones.append("alto_distraccion") #Se pueden basar de los mensajes para ver que es cada cosa
        if tasa < 30:
            patrones.append("hiperactividad_digital")
        if totales["comunicacion"] > totales["productivo"]:
            patrones.append("social_dominante")
        if ratio < 0.2:
            patrones.append("muy_productivo")
        if totales["desconocido"] > totales["productivo"]:
            patrones.append("apps_no_clasificadas")
        if ratioManana > 0.6:
            patrones.append("patron_manana")
        if ratioTarde > 0.6:
            patrones.append("patron_tarde")
        if len(patrones) == 0:
            patrones.append("equilibrado")
        return patrones

    def analuzis(self): #la función que usa tooooodo lo demas
        filas = self.oDatos()

        if len(filas) == 0:  #Se explica solo
            self.textoAnalisis.delete("1.0", "end")
            self.textoAnalisis.insert("1.0", "No hay datos. Inicia el monitor primero.")
            return

        totales, ratio = self.calculaRatio(filas)
        tasa = self.calculaCambios(filas)
        horaPico = self.calculaHoraPico(filas)
        appTop = self.calculaAppMasUsada(filas)

        filasManana = []
        for f in filas:
            hora = datetime.datetime.strptime(f[0], "%Y-%m-%d %H:%M:%S").hour
            if hora < 12:
                filasManana.append(f)

        filasTarde = []
        for f in filas:
            hora = datetime.datetime.strptime(f[0], "%Y-%m-%d %H:%M:%S").hour
            if hora >= 15:
                filasTarde.append(f)

        _, ratioManana = self.calculaRatio(filasManana) if filasManana else (None, 0)
        _, ratioTarde  = self.calculaRatio(filasTarde)  if filasTarde  else (None, 0)

        patrones = self.detectaPatrones(totales, tasa, ratio, ratioManana, ratioTarde)

        textoFeedback = ""
        for patron in patrones:
            if patron in self.FEEDBACK:
                textoFeedback += f"\n -{self.FEEDBACK[patron]['causa']}\n"
                textoFeedback += f"  ----{self.FEEDBACK[patron]['tip']}\n"

        def aMinutos(segundos):
            return round(segundos / 60, 1)
#Las triples comillas son increibles, no hay que escdibir \ņ \ņ \ņ \ņ \ņ \ņ a cada rato para cada nueva linea. Por cierto las multiplicaciones por 100 son para que sea porcentaje
        #Por cierto, usar el {'─' * 40} tambien es bendición. Es mas facil que escribir -------------------------, pajoc si esta leyendo esto ahi nos enseña a usarlo que esta increible
        texto = f"""
ANÁLISIS DE ACTIVIDAD
{'─' * 40}

Distracción:      {ratio * 100:.1f}% 
Sesión promedio:  {tasa:.1f} seg
Hora pico:        {horaPico:02d}:00
App más usada:    {appTop}
Patrones:         {', '.join(patrones)}

TIEMPO POR CATEGORÍA
{'─' * 40}
  Productivo:     {aMinutos(totales['productivo'])} min
  Distracción:    {aMinutos(totales['distraccion'])} min
  Comunicación:   {aMinutos(totales['comunicacion'])} min
  Neutral:        {aMinutos(totales['neutral'])} min
  Sin clasificar: {aMinutos(totales['desconocido'])} min

DIAGNÓSTICO
{'─' * 40}
{textoFeedback}
FUENTES
{'─' * 40}
  · Steel (2007). Psychological Bulletin
  · Mark et al. (2005). CHI Conference
  · Pychyl (2013). Procrastination Puzzle
  · Rozental & Carlbring (2014). Frontiers in Psychology
  · Baumeister (2002). Ego Depletion
        """

        self.textoAnalisis.delete("1.0", "end")
        self.textoAnalisis.insert("1.0", texto)
#POR FIN SE INICIA EL PROGRAMAAAAAAA
VentanaPrueba().mainloop()
