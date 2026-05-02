from src.interfaz import InterfazGrafica


if __name__ == "__main__":
    app = InterfazGrafica(tamano=10, max_intentos=500, semilla=None)
    app.ejecutar()