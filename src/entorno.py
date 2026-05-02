"""Entorno tipo Wumpus para el agente Pedro."""

import random


Posicion = tuple[int, int]


class Entorno:
    def __init__(
        self,
        tamano: int = 10,
        cantidad_hoyos: int = 10,
        cantidad_monstruos: int = 1,
        cantidad_oro: int = 1,
        semilla: int | None = None,
    ) -> None:
        self.tamano = tamano
        self.inicio: Posicion = (0, 0)
        self.aleatorio = random.Random(semilla)

        # Matriz del mundo
        self.mapa = [["" for _ in range(tamano)] for _ in range(tamano)]

        self.colocar_elementos(cantidad_hoyos, cantidad_monstruos, cantidad_oro)

    # --------------------
    # GENERACION DEL MUNDO
    # --------------------
    def colocar_elementos(
        self,
        cantidad_hoyos: int,
        cantidad_monstruos: int,
        cantidad_oro: int,
    ) -> None:
        self.colocar_objetos("P", cantidad_hoyos)      # hoyos
        self.colocar_objetos("W", cantidad_monstruos)  # monstruos
        self.colocar_objetos("G", cantidad_oro)        # oro

    def colocar_objetos(self, tipo: str, cantidad: int) -> None:
        colocados = 0

        while colocados < cantidad:
            x = self.aleatorio.randint(0, self.tamano - 1)
            y = self.aleatorio.randint(0, self.tamano - 1)

            # Evitar la posicion inicial
            if (x, y) == self.inicio:
                continue

            # Evitar sobrescribir otro objeto
            if self.mapa[x][y] == "":
                self.mapa[x][y] = tipo
                colocados += 1

    # --------------------
    # VECINOS
    # --------------------
    def obtener_vecinos(self, x: int, y: int) -> list[Posicion]:
        vecinos: list[Posicion] = []

        # Solo Arriba, Abajo, Izquierda, Derecha
        # No debe haber ninguna combinación de (x+1, y+1)
        direcciones = [
            (x - 1, y), # Norte
            (x + 1, y), # Sur
            (x, y - 1), # Oeste
            (x, y + 1)  # Este
        ]

        for nx, ny in direcciones:
            if 0 <= nx < self.tamano and 0 <= ny < self.tamano:
                vecinos.append((nx, ny))

        return vecinos
    def obtener_percepciones(self, x: int, y: int) -> list[str]:
        percepciones = []

        if self.hay_brisa(x, y):
            percepciones.append("brisa")

        if self.hay_hedor(x, y):
            percepciones.append("hedor")

        if self.mapa[x][y] == "G":
            percepciones.append("brillo")

        return percepciones

    def hay_peligro(self, x: int, y: int) -> bool:
        return self.mapa[x][y] in {"P", "W"}

    # --------------------
    # DEBUG VISUAL
    # --------------------
    def mostrar_mapa(self) -> None:
        for fila in self.mapa:
            print(fila)
    
    def hay_brisa(self, x: int, y: int) -> bool:
        for vx, vy in self.obtener_vecinos(x, y):
            if self.mapa[vx][vy] == "P":
                return True
        return False


    def hay_hedor(self, x: int, y: int) -> bool:
        for vx, vy in self.obtener_vecinos(x, y):
            if self.mapa[vx][vy] == "W":
                return True
        return False
