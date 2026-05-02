import tkinter as tk
from tkinter import messagebox, font
from src.agente import Agente
from src.entorno import Entorno

class InterfazGrafica:
    def __init__(self, tamano=10, max_intentos=500, semilla=None):
        self.tamano = tamano
        self.max_intentos = max_intentos
        self.semilla = semilla
        self.turno = 1
        self.juego_terminado = False
        self.percepciones = ["ninguna"]

        self.entorno = self.crear_entorno()
        self.agente = self.crear_agente()

        self.ventana = tk.Tk()
        self.ventana.title("🕹️ Pedro's Quest: Wumpus World")
        self.ventana.geometry("1100x750")
        self.ventana.configure(bg="#F0F2F5") # Fondo gris azulado moderno

        # --- PALETA DE COLORES ---
        self.colores = {
            "fondo": "#F0F2F5",
            "panel": "#FFFFFF",
            "texto": "#2D3436",
            "pedro": "#3498DB",      # Azul brillante
            "visitada": "#A2D9A1",   # Verde suave
            "segura": "#E8F5E9",     # Verde muy claro
            "peligro": "#FF7675",    # Rojo coral
            "wumpus": "#A29BFE",     # Morado suave
            "oro": "#FDCB6E",        # Dorado
            "desconocido": "#DFE6E9",# Gris claro
            "borde": "#B2BEC3"
        }

        self.tamano_celda = 55 # Un poco más grande para mejor visibilidad
        self.mostrar_real = tk.BooleanVar(value=False)

        self.crear_componentes()
        self.actualizar_pantalla()

    def crear_entorno(self):
        try: return Entorno(tamano=self.tamano, semilla=self.semilla)
        except TypeError: return Entorno(tamano=self.tamano)

    def crear_agente(self):
        try: return Agente(self.entorno, semilla=self.semilla)
        except TypeError: return Agente(self.entorno)

    def crear_componentes(self):
        # Contenedor Principal con sombreado simulado
        contenedor = tk.Frame(self.ventana, bg=self.colores["fondo"], padx=20, pady=20)
        contenedor.pack(fill="both", expand=True)

        # SECCIÓN IZQUIERDA (MAPA)
        izquierda = tk.Frame(contenedor, bg=self.colores["fondo"])
        izquierda.pack(side="left", padx=(0, 20))

        # El Canvas ahora tiene un borde más redondeado visualmente
        self.canvas = tk.Canvas(
            izquierda,
            width=self.tamano * self.tamano_celda,
            height=self.tamano * self.tamano_celda,
            bg="white",
            highlightthickness=2,
            highlightbackground=self.colores["borde"]
        )
        self.canvas.pack(pady=10)

        # Leyenda Estilizada
        leyenda = tk.Label(
            izquierda,
            text=(
                "👤 A: Pedro  |  ✅ V: Visitada  |  🛡️ S: Segura  |  ❓ ?: Desconocida\n"
                "🕳️ H?: Hoyo  |  👾 M?: Monstruo  |  ⚠️ !: Doble Riesgo\n"
                "Mapa Real: 🕳️ P  |  👾 W  |  💰 G  |  🍃 B  |  🤢 O"
            ),
            justify="center",
            bg=self.colores["fondo"],
            fg="#636E72",
            font=("Segoe UI", 10, "italic"),
        )
        leyenda.pack(fill="x")

        # SECCIÓN DERECHA (INFO)
        derecha = tk.Frame(contenedor, bg=self.colores["panel"], padx=20, pady=20, relief="flat")
        derecha.pack(side="right", fill="both", expand=True)

        tk.Label(
            derecha,
            text="PEDRO'S QUEST",
            font=("Segoe UI Black", 20),
            bg=self.colores["panel"],
            fg=self.colores["texto"]
        ).pack(anchor="w")

        # Panel de Información con fuente limpia
        self.info = tk.Label(
            derecha,
            text="",
            justify="left",
            anchor="w",
            bg=self.colores["panel"],
            fg="#2D3436",
            font=("Segoe UI", 11),
            pady=10
        )
        self.info.pack(fill="x")

        tk.Label(
            derecha,
            text="LOG DE RAZONAMIENTO",
            font=("Segoe UI", 10, "bold"),
            bg=self.colores["panel"],
            fg="#B2BEC3"
        ).pack(anchor="w", pady=(10, 0))

        self.texto_reglas = tk.Text(
            derecha,
            height=12,
            font=("Consolas", 10),
            bg="#F8F9FA",
            fg="#2D3436",
            relief="flat",
            padx=10,
            pady=10
        )
        self.texto_reglas.pack(fill="both", expand=True, pady=10)

        # Botones Estilizados
        botones = tk.Frame(derecha, bg=self.colores["panel"])
        botones.pack(fill="x", pady=10)

        btn_style = {"font": ("Segoe UI Bold", 10), "relief": "flat", "cursor": "hand2", "pady": 8}
        
        self.btn_next = tk.Button(
            botones, text="PRÓXIMO PASO ➡️", command=self.siguiente_turno,
            bg=self.colores["pedro"], fg="white", activebackground="#2980B9", **btn_style
        )
        self.btn_next.pack(side="left", fill="x", expand=True, padx=5)

        tk.Button(
            botones, text="REINICIAR 🔄", command=self.reiniciar,
            bg="#E17055", fg="white", activebackground="#D63031", **btn_style
        ).pack(side="left", fill="x", expand=True, padx=5)

        tk.Checkbutton(
            derecha, text="Revelar Mapa Real (Debug)", variable=self.mostrar_real,
            command=self.actualizar_pantalla, bg=self.colores["panel"], font=("Segoe UI", 9)
        ).pack(anchor="w")

    # --- Los métodos de lógica se mantienen intactos ---
    def siguiente_turno(self):
        if self.juego_terminado: return
        if self.turno > self.max_intentos:
            self.finalizar("Pedro alcanzó el límite de intentos.")
            return

        percepciones_reales = self.agente.percibir()
        self.percepciones = percepciones_reales or ["ninguna"]
        self.agente.actualizar_conocimiento(percepciones_reales)

        if "brillo" in percepciones_reales:
            self.actualizar_pantalla()
            self.finalizar("✨ ¡Pedro encontró el oro! ✨")
            return

        se_movio = self.agente.mover()
        self.actualizar_pantalla()

        if se_movio is False:
            self.finalizar("Pedro no pudo moverse.")
            return

        if self.agente.esta_muerto():
            self.actualizar_pantalla()
            self.finalizar("💀 Pedro ha caído.")
            return

        self.turno += 1

    def actualizar_pantalla(self):
        self.dibujar_mapa()
        self.mostrar_info()
        self.mostrar_reglas()

    def dibujar_mapa(self):
        self.canvas.delete("all")
        for x in range(self.tamano):
            for y in range(self.tamano):
                pos = (x, y)
                x1, y1 = y * self.tamano_celda, x * self.tamano_celda
                x2, y2 = x1 + self.tamano_celda, y1 + self.tamano_celda

                # Dibujar fondo de la celda
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=self.color_celda(pos),
                    outline="#FFFFFF", width=2
                )

                # Dibujar Iconos/Texto
                txt = self.texto_celda(pos)
                emoji_map = {"A": "👤", "P": "🕳️", "W": "👾", "G": "💰", "V": "✅", "S": "🛡️", "H?": "❓", "M?": "❓", "!": "⚠️"}
                display_txt = emoji_map.get(txt, txt)
                
                self.canvas.create_text(
                    (x1 + x2) // 2, (y1 + y2) // 2,
                    text=display_txt,
                    font=("Segoe UI", 12, "bold") if txt != "?" else ("Segoe UI", 10),
                    fill="#2D3436" if txt != "A" else "white"
                )

    # --- Ajuste de Colores Estéticos ---
    def color_celda(self, posicion):
        if posicion == self.agente.posicion: return self.colores["pedro"]
        if self.mostrar_real.get():
            el = self.obtener_elemento_real(posicion)
            if el == "P": return self.colores["peligro"]
            if el == "W": return self.colores["wumpus"]
            if el == "G": return self.colores["oro"]
            
            b, o = self.hay_brisa_en(posicion), self.hay_olor_en(posicion)
            if b and o: return "#FFEAA7"
            if b: return "#FAB1A0"
            if o: return "#D63031" # Un tono suave de rojo/púrpura

        if posicion in self.agente.visitadas: return self.colores["visitada"]
        if posicion in self.agente.seguras: return self.colores["segura"]
        if self.es_doble_sospecha(posicion): return "#FF7675"
        if posicion in self.obtener_posibles_hoyos(): return "#FFADAD"
        if posicion in self.obtener_posibles_monstruos(): return "#D7D1E9"
        
        return self.colores["desconocido"]

    # Los demás métodos (obtener_elemento_real, hay_brisa_en, etc.) 
    # se mantienen igual que en tu código original para no romper la lógica.
    def texto_celda(self, posicion):
        if posicion == self.agente.posicion: return "A"
        if self.mostrar_real.get():
            elemento = self.obtener_elemento_real(posicion)
            if elemento: return elemento
            brisa, olor = self.hay_brisa_en(posicion), self.hay_olor_en(posicion)
            if brisa and olor: return "B/O"
            if brisa: return "B"
            if olor: return "O"
        if self.es_doble_sospecha(posicion): return "!"
        if posicion in self.obtener_posibles_hoyos(): return "H?"
        if posicion in self.obtener_posibles_monstruos(): return "M?"
        if posicion in self.agente.visitadas: return "V"
        if posicion in self.agente.seguras: return "S"
        return "?"

    def obtener_elemento_real(self, posicion):
        x, y = posicion
        return self.entorno.mapa[x][y]

    def hay_brisa_en(self, posicion):
        x, y = posicion
        for vx, vy in self.entorno.obtener_vecinos(x, y):
            if self.entorno.mapa[vx][vy] == "P": return True
        return False

    def hay_olor_en(self, posicion):
        x, y = posicion
        for vx, vy in self.entorno.obtener_vecinos(x, y):
            if self.entorno.mapa[vx][vy] == "W": return True
        return False

    def obtener_posibles_hoyos(self):
        if hasattr(self.agente, "posibles_hoyos"): return self.agente.posibles_hoyos
        return getattr(self.agente, "posibles_peligros", set())

    def obtener_posibles_monstruos(self):
        return getattr(self.agente, "posibles_monstruos", set())

    def es_doble_sospecha(self, posicion):
        return (posicion in self.obtener_posibles_hoyos() and posicion in self.obtener_posibles_monstruos())

    def mostrar_info(self):
        kb = getattr(self.agente, "KB", set())
        texto = (
            f"📅 TURNO: {self.turno} | 📍 POSICIÓN: {self.agente.posicion}\n"
            f"🧠 ESTADO: {self.agente.estado}\n"
            f"📡 PERCEPCIÓN: {', '.join(self.percepciones).upper()}\n"
            "--------------------------------------------------\n"
            f"📌 Visitadas: {len(self.agente.visitadas)}  |  🛡️ Seguras: {len(self.agente.seguras)}\n"
            f"⚠️ Sospechas: {len(self.obtener_posibles_hoyos())} Hoyos / {len(self.obtener_posibles_monstruos())} Wumpus\n"
            f"📚 Hechos en Memoria: {len(kb)}"
        )
        self.info.config(text=texto)

    def mostrar_reglas(self):
        self.texto_reglas.delete("1.0", tk.END)
        reglas = getattr(self.agente, "reglas_turno", [])
        if not reglas:
            self.texto_reglas.insert(tk.END, "> Esperando datos del Agente...")
            return
        for regla in reglas:
            self.texto_reglas.insert(tk.END, f"⊢ {regla}\n")

    def finalizar(self, mensaje):
        self.juego_terminado = True
        messagebox.showinfo("FIN DE LA PARTIDA", mensaje)

    def reiniciar(self):
        self.turno = 1
        self.juego_terminado = False
        self.entorno = self.crear_entorno()
        self.agente = self.crear_agente()
        self.percepciones = ["ninguna"]
        self.actualizar_pantalla()

    def ejecutar(self):
        self.ventana.mainloop()