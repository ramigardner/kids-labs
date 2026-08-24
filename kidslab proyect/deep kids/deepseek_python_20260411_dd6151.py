import os
import sys
import io
import contextlib
import traceback

CHALLENGE_FILES_DIR = "challenge_files"

class ChallengeManager:
    def __init__(self):
        self.challenges = {
            "buho_fix": {
                "title": "Arreglar al Búho 🦉",
                "description": "El Búho siempre reporta latencia 0.8. Modifica la función 'reportar' para que devuelva un valor más cercano a la realidad (que es 0.3).",
                "animal": "buho",
                "file": "buho.py",
                "test_cases": [
                    {"input": None, "expected": 0.3, "tolerance": 0.1}
                ]
            },
            "zorro_speed": {
                "title": "Acelerar al Zorro 🦊",
                "description": "El Zorro es lento. Cambia la función 'latencia' para que devuelva un valor menor a 0.2.",
                "animal": "zorro",
                "file": "zorro.py",
                "test_cases": [
                    {"input": None, "expected": 0.15, "tolerance": 0.1}
                ]
            }
        }

    def run_challenge(self, animal, code, challenge_id):
        """Ejecuta el código del niño en un entorno controlado"""
        # Guardar el código en el archivo correspondiente
        if challenge_id not in self.challenges:
            return {"success": False, "message": "Desafío desconocido"}

        challenge = self.challenges[challenge_id]
        file_path = os.path.join(CHALLENGE_FILES_DIR, challenge["file"])

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Importar dinámicamente el módulo
            import importlib.util
            spec = importlib.util.spec_from_file_location(challenge["animal"], file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Ejecutar casos de prueba
            if not hasattr(module, "reportar"):
                return {"success": False, "message": "La función 'reportar' no existe"}

            func = module.reportar
            for test in challenge["test_cases"]:
                # Redirigir stdout para evitar prints en el servidor
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    result = func() if test["input"] is None else func(test["input"])

                if abs(result - test["expected"]) > test["tolerance"]:
                    return {
                        "success": False,
                        "message": f"Se esperaba ~{test['expected']} pero se obtuvo {result}"
                    }

            # Calcular nuevo karma basado en el resultado (simplificado)
            new_karma = 0.8 + (0.2 if result < 0.2 else 0)
            return {
                "success": True,
                "message": f"¡Bien hecho! El {animal} ahora reporta {result:.2f}. Karma mejorado.",
                "new_karma": min(1.0, new_karma)
            }

        except Exception as e:
            return {"success": False, "message": f"Error en el código: {traceback.format_exc()}"}