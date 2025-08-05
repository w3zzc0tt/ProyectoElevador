class Elevador:
    def __init__(self, capacidad_area=9):  # Máximo 9 áreas
        self.capacidad_area = capacidad_area
        self.area_ocupada = 0
        self.personas_dentro = []

    def puede_entrar(self, persona):
        """Verifica si una persona puede entrar al elevador"""
        return (self.area_ocupada + persona.area_ocupada) <= self.capacidad_area

    def entrar_persona(self, persona):
        """Agrega una persona al elevador"""
        if self.puede_entrar(persona):
            self.personas_dentro.append(persona)
            self.area_ocupada += persona.area_ocupada
            return True
        return False

    def salir_persona(self, persona):
        """Saca una persona del elevador"""
        if persona in self.personas_dentro:
            self.personas_dentro.remove(persona)
            self.area_ocupada -= persona.area_ocupada
            return True
        return False
