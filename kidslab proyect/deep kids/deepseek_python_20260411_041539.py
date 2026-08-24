import random

class GardenState:
    def __init__(self):
        self.animals = {
            "buho": {"karma": 0.8, "latency": 0.1, "history": [], "name": "Búho 🦉"},
            "zorro": {"karma": 0.7, "latency": 0.2, "history": [], "name": "Zorro 🦊"},
            "topo": {"karma": 0.5, "latency": 0.6, "history": [], "name": "Topo 🐭"},
            "abeja": {"karma": 0.9, "latency": 0.05, "history": [], "name": "Abeja 🐝"}
        }
        self.external_temp = 22.0  # "Anclaje externo" simulado

    def get_all_karma(self):
        return {name: data["karma"] for name, data in self.animals.items()}

    def get_animal_karma(self, animal):
        if animal in self.animals:
            return {animal: self.animals[animal]["karma"]}
        return {}

    def get_full_state(self):
        return {
            "animals": self.animals,
            "external_temp": self.external_temp,
            "reality": self._calculate_reality()
        }

    def _calculate_reality(self):
        """Calcula la 'realidad' como promedio de latencias"""
        latencies = [data["latency"] for data in self.animals.values()]
        return sum(latencies) / len(latencies) if latencies else 0.5

    def simulate_round(self):
        """Cada animal reporta un valor, se compara con realidad y se ajusta Karma"""
        reality = self._calculate_reality()
        # Cambiar ligeramente el anclaje externo
        self.external_temp += random.uniform(-0.5, 0.5)

        for name, data in self.animals.items():
            # Cada animal tiene un "reporte" basado en su latencia + ruido
            report = data["latency"] + random.uniform(-0.1, 0.2)
            error = abs(report - reality)

            # Ajuste de karma según error
            if error < 0.1:
                data["karma"] = min(1.0, data["karma"] + 0.05)
            elif error > 0.3:
                data["karma"] = max(0.1, data["karma"] - 0.03)
            else:
                # Decaimiento suave
                data["karma"] *= 0.99

            data["history"].append({
                "report": round(report, 3),
                "error": round(error, 3),
                "karma": round(data["karma"], 3)
            })
            # Mantener historial limitado
            if len(data["history"]) > 20:
                data["history"].pop(0)

    def update_animal_logic(self, animal, new_karma):
        """Actualiza el karma de un animal manualmente (desde desafío)"""
        if animal in self.animals:
            self.animals[animal]["karma"] = max(0.1, min(1.0, new_karma))
            self.animals[animal]["latency"] = 1.0 - self.animals[animal]["karma"]  # relación inversa simple