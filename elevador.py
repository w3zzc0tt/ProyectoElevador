class Elevador:
    def __init__(self, max_area=9):
        self.max_area = max_area          # Área máxima que puede ocupar
        self.area_ocupada = 0             # Área actualmente ocupada
        self.personas_dentro = []         # Lista de personas dentro del elevador

    def puede_entrar(self, persona):
        """Verifica si la persona cabe en el elevador según su espacio."""
        return self.area_ocupada + persona.espacio <= self.max_area

    def entrar_persona(self, persona):
        """Intenta subir a la persona si hay espacio disponible."""
        if self.puede_entrar(persona):
            self.personas_dentro.append(persona)
            self.area_ocupada += persona.espacio
            return True
        return False

    def limpiar(self):
        """Vacía el elevador completamente (útil después de llegar al último piso)."""
        self.personas_dentro.clear()
        self.area_ocupada = 0
