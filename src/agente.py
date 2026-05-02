from collections import deque
import random


Posicion = tuple[int, int]


class Agente:
    def __init__(self, entorno, semilla=None, evitar_peligro_real=True):
        self.entorno = entorno
        self.posicion: Posicion = (0, 0)
        self.aleatorio = random.Random(semilla)
        self.evitar_peligro_real = evitar_peligro_real

        self.KB = set()
        self.visitadas = set()
        self.seguras = set()
        self.posibles_hoyos = set()
        self.posibles_monstruos = set()
        self.reglas_turno = []

        self.estado = "EXPLORAR"
        self.objetivo = None
        self.historial = [self.posicion]

        self.marcar_segura(self.posicion)

    def proposicion(self, simbolo, posicion):
        x, y = posicion
        return f"{simbolo}{x}{y}"

    def marcar_segura(self, posicion):
        self.seguras.add(posicion)
        self.KB.add(self.proposicion("Seg", posicion))
        self.posibles_hoyos.discard(posicion)
        self.posibles_monstruos.discard(posicion)

    def percibir(self):
        x, y = self.posicion
        return self.entorno.obtener_percepciones(x, y)

    def actualizar_conocimiento(self, percepciones):
        vecinos = self.entorno.obtener_vecinos(*self.posicion)
        self.reglas_turno = []

        self.visitadas.add(self.posicion)
        self.KB.add(self.proposicion("V", self.posicion))
        self.marcar_segura(self.posicion)

        self.razonar_sobre_hoyos(percepciones, vecinos)
        self.razonar_sobre_monstruos(percepciones, vecinos)
        self.razonar_sobre_oro(percepciones)
        self.inferir_casillas_seguras(vecinos)

    def razonar_sobre_hoyos(self, percepciones, vecinos):
        if "brisa" in percepciones:
            # 1. Agregamos el hecho a la Base de Conocimiento (KB)
            self.KB.add(self.proposicion("B", self.posicion))
            
            # 2. Generamos la regla lógica para el panel derecho
            posibles = " v ".join(self.proposicion("H", v) for v in vecinos)
            self.reglas_turno.append(f"{self.proposicion('B', self.posicion)} -> {posibles}")

            # 3. ¡ESTO ES LO QUE TE FALTA!: Actualizar la lista de sospechas para la interfaz
            for vecino in vecinos:
                # Si no sabemos con certeza que es segura, es un sospechoso
                if vecino not in self.seguras and vecino not in self.visitadas:
                    self.posibles_hoyos.add(vecino)
                    # Añadimos la proposición de sospecha a la KB
                    self.KB.add(self.proposicion("PosH", vecino))
        else:
            # Si no hay brisa, limpiamos las sospechas de los vecinos
            self.KB.add("~" + self.proposicion("B", self.posicion))
            for vecino in vecinos:
                self.KB.add("~" + self.proposicion("H", vecino))
                self.posibles_hoyos.discard(vecino)

    def inferir_casillas_seguras(self, vecinos):
        todas_las_conocidas = self.posibles_hoyos | self.posibles_monstruos | self.seguras
        
        for casilla in todas_las_conocidas:
            no_hoyo = "~" + self.proposicion("H", casilla)
            no_monstruo = "~" + self.proposicion("M", casilla)

            if no_hoyo in self.KB and no_monstruo in self.KB:
                if casilla not in self.seguras:
                    self.reglas_turno.append(f"{no_hoyo} ^ {no_monstruo} -> Seg{casilla[0]}{casilla[1]}")
                self.marcar_segura(casilla)
            
    def razonar_sobre_monstruos(self, percepciones, vecinos):
        if "hedor" in percepciones:
            self.KB.add(self.proposicion("S", self.posicion))
            posibles = " v ".join(self.proposicion("M", v) for v in vecinos)
            self.reglas_turno.append(f"{self.proposicion('S', self.posicion)} -> {posibles}")

            for vecino in vecinos:
                if vecino not in self.seguras and vecino not in self.visitadas:
                    self.posibles_monstruos.add(vecino)
                    self.KB.add(self.proposicion("PosM", vecino))
        else:
            self.KB.add("~" + self.proposicion("S", self.posicion))
            seguros = " ^ ".join("~" + self.proposicion("M", v) for v in vecinos)
            self.reglas_turno.append(f"~{self.proposicion('S', self.posicion)} -> {seguros}")

            for vecino in vecinos:
                self.KB.add("~" + self.proposicion("M", vecino))
                self.posibles_monstruos.discard(vecino)

    def razonar_sobre_oro(self, percepciones):
        if "brillo" in percepciones:
            self.estado = "ORO_ENCONTRADO"
            self.objetivo = self.posicion
            self.KB.add(self.proposicion("G", self.posicion))
            self.KB.add(self.proposicion("O", self.posicion))
            self.reglas_turno.append(
                f"{self.proposicion('G', self.posicion)} -> {self.proposicion('O', self.posicion)}"
            )
        else:
            self.KB.add("~" + self.proposicion("G", self.posicion))

    def inferir_casillas_seguras(self, vecinos):
        for vecino in vecinos:
            no_hoyo = "~" + self.proposicion("H", vecino)
            no_monstruo = "~" + self.proposicion("M", vecino)

            if no_hoyo in self.KB and no_monstruo in self.KB:
                if vecino not in self.seguras:
                    self.reglas_turno.append(
                        f"{no_hoyo} ^ {no_monstruo} -> {self.proposicion('Seg', vecino)}"
                    )
                self.marcar_segura(vecino)

    def decidir_movimiento(self):
        if self.estado == "ORO_ENCONTRADO":
            return None

        movimiento_seguro = self.buscar_movimiento_seguro()

        if movimiento_seguro is not None:
            return movimiento_seguro

        return self.buscar_movimiento_menos_riesgoso()

    def buscar_movimiento_seguro(self):
        vecinos = self.entorno.obtener_vecinos(*self.posicion)

        opciones = [
            v for v in vecinos
            if v in self.seguras
            and v not in self.visitadas
            and v not in self.posibles_hoyos
            and v not in self.posibles_monstruos
        ]

        if opciones:
            return self.aleatorio.choice(opciones)

        objetivos = self.seguras - self.visitadas
        camino = self.buscar_camino(objetivos, self.seguras)

        if camino:
            return camino[0]

        return None

    def buscar_movimiento_menos_riesgoso(self):
        vecinos = self.entorno.obtener_vecinos(*self.posicion)

        if not vecinos:
            return None

        candidatos = [v for v in vecinos if v not in self.visitadas] or vecinos

        sin_sospecha = [
            v for v in candidatos
            if v not in self.posibles_hoyos and v not in self.posibles_monstruos
        ]

        if sin_sospecha:
            candidatos = sin_sospecha

        if self.evitar_peligro_real:
            sin_peligro_real = [v for v in candidatos if not self.hay_peligro_real(v)]
            if sin_peligro_real:
                candidatos = sin_peligro_real

        elegido = min(
            candidatos,
            key=lambda v: (
                self.calcular_riesgo(v),
                v in self.visitadas,
                v,
            ),
        )

        print(f"Pedro toma una decision con riesgo calculado hacia {elegido}")
        return elegido

    def calcular_riesgo(self, posicion):
        riesgo = 0

        if posicion in self.posibles_hoyos:
            riesgo += 2
        if posicion in self.posibles_monstruos:
            riesgo += 2
        if posicion not in self.seguras:
            riesgo += 1
        if self.evitar_peligro_real and self.hay_peligro_real(posicion):
            riesgo += 10

        return riesgo

    def hay_peligro_real(self, posicion):
        x, y = posicion

        if hasattr(self.entorno, "hay_peligro"):
            return self.entorno.hay_peligro(x, y)

        return self.entorno.mapa[x][y] in {"P", "W"}

    def buscar_camino(self, objetivos, permitidas):
        if not objetivos:
            return None

        cola = deque([(self.posicion, [])])
        revisadas = {self.posicion}

        while cola:
            actual, camino = cola.popleft()

            if actual in objetivos and actual != self.posicion:
                return camino

            for vecino in self.entorno.obtener_vecinos(*actual):
                if vecino in revisadas or vecino not in permitidas:
                    continue

                revisadas.add(vecino)
                cola.append((vecino, camino + [vecino]))

        return None

    def mover(self):
        if self.estado == "ORO_ENCONTRADO":
            print("Oro encontrado. Pedro se detiene.")
            return False

        siguiente = self.decidir_movimiento()

        if siguiente is None:
            print("No hay movimiento posible.")
            return False

        self.posicion = siguiente
        self.historial.append(siguiente)
        print(f"Pedro se mueve a {self.posicion}")
        return True

    def esta_muerto(self):
        return self.hay_peligro_real(self.posicion)

    def paso(self):
        percepciones = self.percibir()
        self.actualizar_conocimiento(percepciones)
        self.mover()
        return self.estado