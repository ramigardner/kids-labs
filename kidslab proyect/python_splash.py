#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║          PYTHON SPLASH  —  Aprende Python Jugando            ║
║          Estética: Kinder Splash / Burbujas / Color          ║
║          Motor: pygame  |  100% offline                      ║
║          Versión: 1.0   |  Actualizable por JSON             ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import json
import os
import math
import time
import random
import threading
from array import array

# ─────────────────────────── VENTANA ───────────────────────────
W, H = 980, 660
FPS  = 60

# ─────────────────────────── PALETA KINDER SPLASH ──────────────
SKY        = (210, 245, 255)   # fondo celeste suave
PANEL_BG   = (255, 255, 255)   # paneles blancos
CORAL      = (255, 111, 97)    # rojo coral
MINT       = (78,  205, 196)   # verde menta
LEMON      = (255, 230, 80)    # amarillo limón
LAVENDER   = (180, 151, 231)   # violeta
PEACH      = (255, 179, 128)   # durazno
SKY_BLUE   = (100, 180, 255)   # azul cielo
HOT_PINK   = (255, 105, 180)   # rosa fuerte
GRASS      = (120, 210, 90)    # verde pasto
DARK_TXT   = (50,  50,  70)    # texto oscuro
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
SHADOW     = (0,   0,   0,  60)

MODULE_PALETTE = [CORAL, MINT, LEMON, LAVENDER, PEACH, SKY_BLUE, HOT_PINK]

# ─────────────────────────── ARCHIVOS ──────────────────────────
SAVE_FILE    = "splash_save.json"
RANKING_FILE = "splash_ranking.json"
CONTENT_FILE = "contenido.json"   # actualizaciones por email

# ════════════════════════════════════════════════════════════════
#  FIGURAS PIXEL ART (8×8, 3 colores: 0=vacío 1=principal 2=detalle)
# ════════════════════════════════════════════════════════════════
FIGURES = {
    "serpiente": {
        "pixels": [
            [0,0,1,1,1,1,0,0],
            [0,1,2,2,2,2,1,0],
            [1,2,2,1,1,2,2,1],
            [1,2,2,2,2,2,2,1],
            [0,1,2,2,2,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,0,0,0,0],
        ],
        "colors": {1: (100,180,80), 2: (60,140,50)},
        "name": "🐍 Serpiente Python"
    },
    "robot": {
        "pixels": [
            [0,1,1,1,1,1,1,0],
            [1,2,1,1,1,1,2,1],
            [1,1,2,1,1,2,1,1],
            [1,1,1,1,1,1,1,1],
            [0,1,1,1,1,1,1,0],
            [0,1,0,1,1,0,1,0],
            [0,1,1,0,0,1,1,0],
            [0,0,1,1,1,1,0,0],
        ],
        "colors": {1: (100,180,255), 2: (255,230,80)},
        "name": "🤖 Robot"
    },
    "cohete": {
        "pixels": [
            [0,0,0,1,1,0,0,0],
            [0,0,1,2,2,1,0,0],
            [0,0,1,2,2,1,0,0],
            [0,1,1,2,2,1,1,0],
            [1,1,2,2,2,2,1,1],
            [0,0,1,2,2,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,1,2,2,1,0,0],
        ],
        "colors": {1: (255,111,97), 2: (255,200,80)},
        "name": "🚀 Cohete"
    },
    "estrella": {
        "pixels": [
            [0,0,0,1,1,0,0,0],
            [0,0,0,1,1,0,0,0],
            [1,1,1,2,2,1,1,1],
            [1,2,2,2,2,2,2,1],
            [1,2,2,2,2,2,2,1],
            [1,1,1,2,2,1,1,1],
            [0,0,1,1,1,1,0,0],
            [0,1,1,0,0,1,1,0],
        ],
        "colors": {1: (255,230,80), 2: (255,180,20)},
        "name": "⭐ Estrella"
    },
    "corazon": {
        "pixels": [
            [0,1,1,0,0,1,1,0],
            [1,2,2,1,1,2,2,1],
            [1,2,2,2,2,2,2,1],
            [1,2,2,2,2,2,2,1],
            [0,1,2,2,2,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,0,1,1,0,0,0],
            [0,0,0,0,0,0,0,0],
        ],
        "colors": {1: (255,105,180), 2: (200,50,120)},
        "name": "💖 Corazón"
    },
    "flor": {
        "pixels": [
            [0,0,1,1,1,1,0,0],
            [0,1,2,2,2,2,1,0],
            [1,2,2,1,1,2,2,1],
            [1,2,1,2,2,1,2,1],
            [1,2,1,2,2,1,2,1],
            [1,2,2,1,1,2,2,1],
            [0,1,2,2,2,2,1,0],
            [0,0,1,1,1,1,0,0],
        ],
        "colors": {1: (120,210,90), 2: (255,179,128)},
        "name": "🌸 Flor"
    },
    "diamante": {
        "pixels": [
            [0,0,0,1,1,0,0,0],
            [0,0,1,2,2,1,0,0],
            [0,1,2,1,1,2,1,0],
            [1,2,1,2,2,1,2,1],
            [1,2,2,2,2,2,2,1],
            [0,1,2,2,2,2,1,0],
            [0,0,1,2,2,1,0,0],
            [0,0,0,1,1,0,0,0],
        ],
        "colors": {1: (180,151,231), 2: (140,100,200)},
        "name": "💎 Diamante"
    },
}

FIGURE_ORDER = ["serpiente","robot","cohete","estrella","corazon","flor","diamante"]

# ════════════════════════════════════════════════════════════════
#  CONTENIDO — MÓDULOS Y RETOS (cargable desde JSON externo)
# ════════════════════════════════════════════════════════════════
BUILTIN_MODULES = [
    {
        "name": "Variables",
        "emoji": "📦",
        "tip": "Las variables son cajas donde guardamos información.",
        "challenges": [
            {"desc": "Crea una variable llamada 'nombre' que guarde tu nombre.",
             "code": "___ = \"Ana\"", "expected": "nombre", "hint": "n-o-m-b-r-e",
             "explain": "'nombre' es el identificador de tu variable."},
            {"desc": "Asigna el número 42 a la variable 'respuesta'.",
             "code": "___ = 42", "expected": "respuesta", "hint": "r-e-s-p-u-e-s-t-a",
             "explain": "42 es un entero (int). La variable lo guarda en memoria."},
            {"desc": "Declara 'precio' con valor 19.99 (número decimal).",
             "code": "___ = 19.99", "expected": "precio", "hint": "p-r-e-c-i-o",
             "explain": "19.99 es float (número con punto decimal)."},
            {"desc": "Crea 'activo' con valor True (booleano).",
             "code": "___ = True", "expected": "activo", "hint": "a-c-t-i-v-o",
             "explain": "True/False son los dos únicos valores booleanos."},
            {"desc": "Intercambia valores: a=5, b=10. Completa la línea.",
             "code": "a, b = b, ___", "expected": "a", "hint": "a",
             "explain": "Python permite intercambio directo sin variable temporal."},
        ],
        "syntax": "nombre = \"Juan\"\nedad = 25\nprecio = 99.99\nactivo = True",
        "figure": "serpiente"
    },
    {
        "name": "Condicionales",
        "emoji": "🔀",
        "tip": "Los condicionales permiten tomar decisiones en el código.",
        "challenges": [
            {"desc": "Escribe la palabra clave para 'si se cumple la condición'.",
             "code": "___ x > 10:\n    print(\"mayor\")", "expected": "if", "hint": "i-f",
             "explain": "'if' evalúa si la condición es True para ejecutar el bloque."},
            {"desc": "Completa el 'si no' (caso contrario).",
             "code": "if x > 10:\n    print(\"mayor\")\n___:\n    print(\"menor\")",
             "expected": "else", "hint": "e-l-s-e",
             "explain": "'else' se ejecuta cuando el 'if' es False."},
            {"desc": "Añade 'sino si' para x == 10.",
             "code": "if x > 10:\n    print(\"mayor\")\n___ x == 10:\n    print(\"igual\")",
             "expected": "elif", "hint": "e-l-i-f",
             "explain": "'elif' = else + if. Evalúa otra condición si la anterior falló."},
            {"desc": "Operador lógico 'y': ambas condiciones deben ser True.",
             "code": "if x > 0 ___ y < 100:\n    print(\"ok\")",
             "expected": "and", "hint": "a-n-d",
             "explain": "'and' requiere que AMBAS condiciones sean verdaderas."},
            {"desc": "Operador 'o': basta con que una sea True.",
             "code": "if dia == \"sabado\" ___ dia == \"domingo\":\n    print(\"finde\")",
             "expected": "or", "hint": "o-r",
             "explain": "'or' es True si AL MENOS UNA condición es verdadera."},
        ],
        "syntax": "if edad >= 18:\n    print(\"mayor de edad\")\nelif edad == 17:\n    print(\"casi!\")\nelse:\n    print(\"menor de edad\")",
        "figure": "robot"
    },
    {
        "name": "Bucles",
        "emoji": "🔁",
        "tip": "Los bucles repiten acciones automáticamente.",
        "challenges": [
            {"desc": "Bucle que repite para cada 'i' en un rango.",
             "code": "___ i in range(5):\n    print(i)", "expected": "for", "hint": "f-o-r",
             "explain": "'for' itera sobre una secuencia. range(5) genera 0,1,2,3,4."},
            {"desc": "Bucle que continúa MIENTRAS se cumpla la condición.",
             "code": "cont = 0\n___ cont < 3:\n    print(cont)\n    cont += 1",
             "expected": "while", "hint": "w-h-i-l-e",
             "explain": "'while' repite mientras la condición sea True."},
            {"desc": "range() desde 2 hasta 6 (inclusive). ¿Qué va en el hueco?",
             "code": "for i in range(2, ___):\n    print(i)", "expected": "7", "hint": "7",
             "explain": "range(2,7) genera 2,3,4,5,6. El límite superior no se incluye."},
            {"desc": "Palabra para SALIR del bucle inmediatamente.",
             "code": "for i in range(10):\n    if i == 5:\n        ___",
             "expected": "break", "hint": "b-r-e-a-k",
             "explain": "'break' termina el bucle en ese instante."},
            {"desc": "Palabra para SALTAR a la siguiente iteración.",
             "code": "for i in range(5):\n    if i == 2:\n        ___\n    print(i)",
             "expected": "continue", "hint": "c-o-n-t-i-n-u-e",
             "explain": "'continue' salta el resto del cuerpo y va al siguiente ciclo."},
        ],
        "syntax": "for i in range(5):\n    print(i)\n\ncont = 0\nwhile cont < 3:\n    print(cont)\n    cont += 1",
        "figure": "cohete"
    },
    {
        "name": "Funciones",
        "emoji": "⚙️",
        "tip": "Las funciones son bloques de código reutilizables.",
        "challenges": [
            {"desc": "Palabra clave para DEFINIR una función.",
             "code": "___ saludar():\n    print(\"Hola\")", "expected": "def", "hint": "d-e-f",
             "explain": "'def' declara una función. El nombre la identifica."},
            {"desc": "Agrega el parámetro 'nombre' a la función.",
             "code": "def saludar(___):\n    print(\"Hola\", nombre)",
             "expected": "nombre", "hint": "n-o-m-b-r-e",
             "explain": "Los parámetros son variables locales de la función."},
            {"desc": "La función debe DEVOLVER el doble de x.",
             "code": "def doble(x):\n    ___ x * 2",
             "expected": "return", "hint": "r-e-t-u-r-n",
             "explain": "'return' devuelve un valor al lugar donde se llamó la función."},
            {"desc": "LLAMA a la función saludar con argumento 'Ana'.",
             "code": "___(\"Ana\")", "expected": "saludar", "hint": "s-a-l-u-d-a-r",
             "explain": "Llamar = escribir el nombre de la función con argumentos."},
            {"desc": "Función lambda: suma dos números. Completa.",
             "code": "suma = lambda a, b: a ___ b",
             "expected": "+", "hint": "+",
             "explain": "Lambda es una función corta en una sola línea."},
        ],
        "syntax": "def suma(a, b):\n    return a + b\n\nresultado = suma(3, 4)\nprint(resultado)  # 7",
        "figure": "estrella"
    },
    {
        "name": "Listas",
        "emoji": "📋",
        "tip": "Las listas guardan múltiples valores en orden.",
        "challenges": [
            {"desc": "Crea una lista VACÍA llamada 'datos'.",
             "code": "datos = ___", "expected": "[]", "hint": "[ ]",
             "explain": "[] es una lista vacía. Las listas usan corchetes."},
            {"desc": "AGREGA el número 5 al final de la lista.",
             "code": "datos.___(5)", "expected": "append", "hint": "a-p-p-e-n-d",
             "explain": "append() agrega un elemento al final de la lista."},
            {"desc": "Accede al PRIMER elemento (índice cero).",
             "code": "primero = colores[___]", "expected": "0", "hint": "0",
             "explain": "Los índices empiezan en 0, no en 1."},
            {"desc": "Obtén la LONGITUD (cantidad de elementos) de 'items'.",
             "code": "largo = ___(items)", "expected": "len", "hint": "l-e-n",
             "explain": "len() es una función incorporada que cuenta elementos."},
            {"desc": "ELIMINA el elemento en el índice 2.",
             "code": "del items[___]", "expected": "2", "hint": "2",
             "explain": "'del' elimina el elemento en la posición indicada."},
        ],
        "syntax": "frutas = [\"manzana\", \"pera\"]\nfrutas.append(\"naranja\")\nprint(len(frutas))  # 3\nprint(frutas[0])    # manzana",
        "figure": "corazon"
    },
    {
        "name": "Diccionarios",
        "emoji": "📖",
        "tip": "Los diccionarios guardan pares clave-valor, como un índice.",
        "challenges": [
            {"desc": "Crea un diccionario VACÍO 'usuario'.",
             "code": "usuario = ___", "expected": "{}", "hint": "{ }",
             "explain": "{} es un diccionario vacío. Usa llaves."},
            {"desc": "Asigna la clave 'nombre' con valor 'Luis'.",
             "code": "usuario[___] = \"Luis\"", "expected": "\"nombre\"", "hint": "'nombre'",
             "explain": "La clave va entre comillas porque es un string."},
            {"desc": "Obtén el valor de la clave 'edad' de forma segura.",
             "code": "edad = usuario.___(\"edad\")", "expected": "get", "hint": "g-e-t",
             "explain": "get() no da error si la clave no existe."},
            {"desc": "Verifica si existe la clave 'email'.",
             "code": "if ___ in usuario:", "expected": "\"email\"", "hint": "'email'",
             "explain": "'in' verifica si una clave existe en el diccionario."},
            {"desc": "ELIMINA la clave 'temp' del diccionario.",
             "code": "___ usuario[\"temp\"]", "expected": "del", "hint": "d-e-l",
             "explain": "'del' elimina una clave y su valor del diccionario."},
        ],
        "syntax": "persona = {\"nombre\": \"Ana\", \"edad\": 30}\nprint(persona[\"nombre\"])\npersona[\"ciudad\"] = \"Madrid\"\ndel persona[\"edad\"]",
        "figure": "flor"
    },
    {
        "name": "Archivos",
        "emoji": "💾",
        "tip": "Python puede leer y escribir archivos del sistema operativo.",
        "challenges": [
            {"desc": "Abre el archivo 'datos.txt' en modo LECTURA.",
             "code": "archivo = ___(\"datos.txt\", \"r\")", "expected": "open", "hint": "o-p-e-n",
             "explain": "open() es la función para abrir archivos. 'r' = read."},
            {"desc": "LEE todo el contenido del archivo.",
             "code": "contenido = archivo.___()", "expected": "read", "hint": "r-e-a-d",
             "explain": "read() devuelve el contenido completo como string."},
            {"desc": "Modo de apertura para ESCRITURA (crea o sobreescribe).",
             "code": "with open(\"out.txt\", \"___\") as f:\n    f.write(\"hola\")",
             "expected": "w", "hint": "w",
             "explain": "'w' = write. Crea el archivo si no existe."},
            {"desc": "CIERRA el archivo después de usarlo.",
             "code": "archivo.___()", "expected": "close", "hint": "c-l-o-s-e",
             "explain": "Siempre hay que cerrar los archivos para liberar recursos."},
            {"desc": "Usa 'with' para abrir sin necesidad de cerrar manualmente.",
             "code": "___ open(\"archivo.txt\", \"r\") as f:\n    datos = f.read()",
             "expected": "with", "hint": "w-i-t-h",
             "explain": "'with' cierra el archivo automáticamente al salir del bloque."},
        ],
        "syntax": "with open(\"ejemplo.txt\", \"w\") as f:\n    f.write(\"hola mundo\")\n\nwith open(\"ejemplo.txt\", \"r\") as f:\n    print(f.read())",
        "figure": "diamante"
    },
]

# Proyecto final que se muestra al completar todos los módulos
FINAL_PROJECT = """# ═══════════════════════════════════════════
#   Tu primer programa Python completo 🎉
#   Combina TODO lo que aprendiste
# ═══════════════════════════════════════════

# 1. VARIABLES — guardamos configuración
nombre_archivo = "notas.txt"
notas = []

# 2. FUNCIÓN — procesar datos
def procesar_notas(lista):
    if len(lista) == 0:
        return {"total": 0, "promedio": 0}
    
    total = 0
    for nota in lista:       # BUCLE
        total += nota
    
    promedio = total / len(lista)
    return {"total": total, "promedio": promedio}  # DICCIONARIO

# 3. LISTAS — cargar datos
notas.append(8.5)
notas.append(9.0)
notas.append(7.5)

# 4. CONDICIONALES — evaluar resultado
resultado = procesar_notas(notas)
if resultado["promedio"] >= 7:
    estado = "Aprobado ✅"
else:
    estado = "Recuperar ⚠️"

# 5. ARCHIVOS — guardar resultado
with open(nombre_archivo, "w") as f:
    f.write(f"Promedio: {resultado['promedio']:.1f}\\n")
    f.write(f"Estado: {estado}\\n")

print("¡Programa ejecutado con éxito!")
print(f"Estado: {estado}")
"""

FINAL_OUTPUT = """
>>> Ejecutando tu programa...

✅ Variables inicializadas
✅ Función 'procesar_notas' definida
✅ 3 notas agregadas a la lista: [8.5, 9.0, 7.5]
✅ Promedio calculado: 8.33
✅ Condición evaluada: Aprobado ✅
✅ Archivo 'notas.txt' creado correctamente

¡Programa ejecutado con éxito!
Estado: Aprobado ✅

Conceptos usados: variables, funciones, bucles,
condicionales, listas, diccionarios y archivos.
¡Eso es Python real! 🐍
"""

def load_modules():
    """Carga módulos desde JSON externo si existe, sino usa los incorporados."""
    if os.path.exists(CONTENT_FILE):
        try:
            with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[Contenido actualizado cargado desde {CONTENT_FILE}]")
            return data.get("modules", BUILTIN_MODULES)
        except Exception as e:
            print(f"[Error al cargar {CONTENT_FILE}: {e}. Usando contenido interno.]")
    return BUILTIN_MODULES

MODULES = load_modules()

# ════════════════════════════════════════════════════════════════
#  GUARDADO Y RANKING
# ════════════════════════════════════════════════════════════════
def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

def save_game(state_dict):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(state_dict, f, indent=2)
    except:
        pass

def clear_save():
    if os.path.exists(SAVE_FILE):
        try: os.remove(SAVE_FILE)
        except: pass

def load_ranking():
    if os.path.exists(RANKING_FILE):
        try:
            with open(RANKING_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def update_ranking(name, stars):
    ranking = load_ranking()
    found = False
    for e in ranking:
        if e["name"] == name:
            if stars > e["stars"]:
                e["stars"] = stars
            found = True
            break
    if not found:
        ranking.append({"name": name, "stars": stars})
    ranking.sort(key=lambda x: x["stars"], reverse=True)
    ranking = ranking[:10]
    try:
        with open(RANKING_FILE, 'w') as f:
            json.dump(ranking, f, indent=2)
    except:
        pass
    return ranking

# ════════════════════════════════════════════════════════════════
#  SONIDO RETRO (sin archivos externos)
# ════════════════════════════════════════════════════════════════
class SplashSound:
    def __init__(self):
        self.ok = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.ok = True
        except:
            pass

    def _play(self, freq, dur_ms, wave='sine', vol=0.3):
        if not self.ok:
            return
        try:
            import numpy as np
            sr = 44100
            n  = int(sr * dur_ms / 1000)
            t  = __import__('numpy').linspace(0, dur_ms/1000, n, endpoint=False)
            if wave == 'square':
                w = __import__('numpy').where((t * freq) % 1 < 0.5, 1.0, -1.0)
            elif wave == 'triangle':
                w = 2 * __import__('numpy').abs((t * freq) % 1 - 0.5) - 1
            else:
                w = __import__('numpy').sin(2 * math.pi * freq * t)
            fade = min(int(n * 0.1), 500)
            env  = __import__('numpy').ones(n)
            env[:fade]  = __import__('numpy').linspace(0, 1, fade)
            env[-fade:] = __import__('numpy').linspace(1, 0, fade)
            w = (w * env * vol * 32767).astype(__import__('numpy').int16)
            pygame.sndarray.make_sound(w).play()
        except:
            pass

    def correct(self):
        def _seq():
            self._play(523, 80, 'sine', 0.25)
            time.sleep(0.07)
            self._play(784, 120, 'sine', 0.3)
        threading.Thread(target=_seq, daemon=True).start()

    def error(self):
        self._play(220, 180, 'square', 0.2)

    def levelup(self):
        def _seq():
            for f in [523, 659, 784, 1047]:
                self._play(f, 100, 'sine', 0.3)
                time.sleep(0.09)
        threading.Thread(target=_seq, daemon=True).start()

    def hint(self):
        self._play(880, 80, 'triangle', 0.15)

    def startup(self):
        def _seq():
            for f in [330, 415, 523, 659]:
                self._play(f, 120, 'sine', 0.2)
                time.sleep(0.1)
        threading.Thread(target=_seq, daemon=True).start()

    def gameover(self):
        def _seq():
            for f in [523, 415, 330, 262]:
                self._play(f, 150, 'square', 0.2)
                time.sleep(0.13)
        threading.Thread(target=_seq, daemon=True).start()

    def complete_all(self):
        def _seq():
            melody = [523,659,784,659,784,1047,784,1047,1319]
            for f in melody:
                self._play(f, 130, 'sine', 0.3)
                time.sleep(0.11)
        threading.Thread(target=_seq, daemon=True).start()

# ════════════════════════════════════════════════════════════════
#  BURBUJA (decoración de fondo)
# ════════════════════════════════════════════════════════════════
class Bubble:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.reset()

    def reset(self):
        self.x   = random.randint(30, self.w - 30)
        self.y   = self.h + random.randint(20, 200)
        self.r   = random.randint(8, 28)
        self.spd = random.uniform(0.4, 1.2)
        self.wobble = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.06)
        self.color = random.choice([CORAL, MINT, LEMON, LAVENDER, PEACH, SKY_BLUE, HOT_PINK])
        self.alpha = random.randint(60, 130)

    def update(self):
        self.y -= self.spd
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.5
        if self.y < -self.r * 2:
            self.reset()

    def draw(self, surf):
        s = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        c = (*self.color, self.alpha)
        pygame.draw.circle(s, c, (self.r+1, self.r+1), self.r)
        # brillo
        pygame.draw.circle(s, (255,255,255,80), (self.r-self.r//3, self.r-self.r//3), self.r//3)
        surf.blit(s, (int(self.x - self.r), int(self.y - self.r)))

# ════════════════════════════════════════════════════════════════
#  WIDGETS UI
# ════════════════════════════════════════════════════════════════
class Button:
    def __init__(self, rect, text, color, callback, emoji=""):
        self.rect      = pygame.Rect(rect)
        self.text      = text
        self.emoji     = emoji
        self.color     = color
        self.callback  = callback
        self.hovered   = False
        self.scale     = 1.0
        self.target_sc = 1.0

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(ev.pos)
            self.target_sc = 1.05 if self.hovered else 1.0
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                self.callback()

    def update(self, dt):
        self.scale += (self.target_sc - self.scale) * 0.25

    def draw(self, surf, font):
        sc = self.scale
        rx = self.rect.x - int((self.rect.w*(sc-1))/2)
        ry = self.rect.y - int((self.rect.h*(sc-1))/2)
        rw = int(self.rect.w * sc)
        rh = int(self.rect.h * sc)
        r  = pygame.Rect(rx, ry, rw, rh)

        # sombra
        sh = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,50), (3,3,rw-3,rh-3), border_radius=14)
        surf.blit(sh, (rx, ry))

        # cuerpo
        pygame.draw.rect(surf, self.color, r, border_radius=14)
        # borde blanco
        pygame.draw.rect(surf, WHITE, r, 3, border_radius=14)

        label = f"{self.emoji} {self.text}" if self.emoji else self.text
        txt   = font.render(label, True, DARK_TXT)
        surf.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))


class InputBox:
    def __init__(self, rect, font):
        self.rect   = pygame.Rect(rect)
        self.font   = font
        self.text   = ""
        self.active = True
        self.cursor_timer = 0

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and self.active:
            if ev.key == pygame.K_RETURN:
                return True
            elif ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if ev.unicode.isprintable():
                    self.text += ev.unicode
        return False

    def update(self, dt):
        self.cursor_timer += dt

    def draw(self, surf, label="Tu respuesta:"):
        # etiqueta
        lbl = self.font.render(label, True, DARK_TXT)
        surf.blit(lbl, (self.rect.x, self.rect.y - 22))
        # caja
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=10)
        pygame.draw.rect(surf, MINT,  self.rect, 3, border_radius=10)
        # texto
        txt = self.font.render(self.text, True, DARK_TXT)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + 8))
        # cursor
        if int(self.cursor_timer * 2) % 2 == 0:
            cx = self.rect.x + 10 + txt.get_width()
            pygame.draw.line(surf, DARK_TXT,
                             (cx, self.rect.y + 8),
                             (cx, self.rect.y + self.rect.h - 8), 2)

# ════════════════════════════════════════════════════════════════
#  PIXEL ART RENDERER
# ════════════════════════════════════════════════════════════════
def draw_pixel_figure(surf, fig_key, revealed_pct, x, y, cell=22):
    """Dibuja la figura con revelado progresivo (0.0 a 1.0)."""
    fig   = FIGURES.get(fig_key, FIGURES["serpiente"])
    grid  = fig["pixels"]
    cols  = fig["colors"]
    rows  = len(grid)
    c_cnt = len(grid[0])

    # contar píxeles activos
    active = [(r, c) for r in range(rows) for c in range(c_cnt) if grid[r][c] != 0]
    total  = len(active)
    show   = int(total * min(revealed_pct, 1.0))

    # fondo del área
    area_w = c_cnt * cell + 10
    area_h = rows  * cell + 10
    bg = pygame.Surface((area_w, area_h), pygame.SRCALPHA)
    pygame.draw.rect(bg, (255,255,255,180), (0,0,area_w,area_h), border_radius=12)
    surf.blit(bg, (x-5, y-5))
    pygame.draw.rect(surf, MINT, (x-5, y-5, area_w, area_h), 3, border_radius=12)

    idx = 0
    for r in range(rows):
        for c in range(c_cnt):
            v = grid[r][c]
            if v == 0:
                continue
            px = x + c * cell
            py = y + r * cell
            if idx < show:
                col = cols[v]
                pygame.draw.rect(surf, col, (px+1, py+1, cell-2, cell-2), border_radius=4)
            else:
                # pixel oculto: gris claro
                pygame.draw.rect(surf, (210,220,230), (px+1, py+1, cell-2, cell-2), border_radius=4)
            idx += 1

    return fig["name"]

# ════════════════════════════════════════════════════════════════
#  MAIN GAME CLASS
# ════════════════════════════════════════════════════════════════
class PythonSplash:
    # ── estados: login | playing | gameover | finished | project ──
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("🐍 Python Splash — Aprende Python Jugando")
        self.clock  = pygame.time.Clock()

        # fuentes
        self.f_title = pygame.font.SysFont("comicsansms",   30, bold=True)
        self.f_big   = pygame.font.SysFont("comicsansms",   22, bold=True)
        self.f_mid   = pygame.font.SysFont("couriernew",    17, bold=True)
        self.f_sm    = pygame.font.SysFont("couriernew",    14)
        self.f_hint  = pygame.font.SysFont("comicsansms",   14)

        self.sound   = SplashSound()
        self.bubbles = [Bubble(W, H) for _ in range(22)]

        # estado del juego
        self.state            = "login"
        self.name             = ""
        self.current_module   = 0
        self.current_challenge= 0
        self.lives            = 5          # corazones
        self.max_lives        = 5
        self.revealed_pct     = 0.0        # 0.0 → 1.0 por módulo
        self.total_stars      = 0          # acumulado global
        self.checkpoint_mod   = 0          # checkpoint guardado
        self.checkpoint_ch    = 0
        self.msg              = ""
        self.msg_timer        = 0.0
        self.msg_color        = CORAL
        self.hint_letters     = 0          # pista progresiva
        self.showing_hint     = False
        self.name_text        = ""
        self.cursor_timer     = 0.0
        self.module_buttons   = []
        self.input_box        = None
        self.ranking_list     = load_ranking()
        self.flash            = 0.0        # flash blanco en acierto
        self.final_mode       = "code"     # "code" o "output"
        self.last_explain     = ""         # explicación del último acierto
        self.explain_timer    = 0.0

        # intentar cargar
        self._load_progress()
        self._build_module_buttons()
        self.sound.startup()

    # ── SAVE / LOAD ────────────────────────────────────────────
    def _load_progress(self):
        saved = load_save()
        if saved:
            self.name             = saved.get("name", "")
            self.name_text        = self.name
            self.current_module   = saved.get("module", 0)
            self.current_challenge= saved.get("challenge", 0)
            self.lives            = saved.get("lives", 5)
            self.revealed_pct     = saved.get("revealed", 0.0)
            self.total_stars      = saved.get("stars", 0)
            self.checkpoint_mod   = saved.get("cp_mod", 0)
            self.checkpoint_ch    = saved.get("cp_ch", 0)

    def _save_progress(self):
        save_game({
            "name":       self.name,
            "module":     self.current_module,
            "challenge":  self.current_challenge,
            "lives":      self.lives,
            "revealed":   self.revealed_pct,
            "stars":      self.total_stars,
            "cp_mod":     self.checkpoint_mod,
            "cp_ch":      self.checkpoint_ch,
        })

    def _checkpoint(self):
        self.checkpoint_mod = self.current_module
        self.checkpoint_ch  = self.current_challenge
        self._save_progress()

    # ── MÓDULO BUTTONS ──────────────────────────────────────────
    def _build_module_buttons(self):
        self.module_buttons = []
        bw, bh = 200, 44
        cols   = 3
        start_x= (W - (bw + 18)*cols) // 2
        start_y= 310
        for i, mod in enumerate(MODULES):
            row = i // cols
            col = i % cols
            x   = start_x + col * (bw + 18)
            y   = start_y + row * (bh + 12)
            color = MODULE_PALETTE[i % len(MODULE_PALETTE)]
            idx = i
            btn = Button((x, y, bw, bh), mod["name"], color,
                         callback=lambda m=idx: self._start_module(m),
                         emoji=mod["emoji"])
            self.module_buttons.append(btn)

    def _start_module(self, idx):
        self.current_module    = idx
        self.current_challenge = 0
        self.lives             = self.max_lives
        self.revealed_pct      = 0.0
        self.hint_letters      = 0
        self.showing_hint      = False
        self.state             = "playing"
        self.input_box         = InputBox((W//2 - 180, H - 70, 360, 40), self.f_mid)
        self._checkpoint()
        self.msg       = f"¡Módulo {MODULES[idx]['emoji']} {MODULES[idx]['name']} iniciado!"
        self.msg_timer = 2.5
        self.msg_color = MINT

    def _restart_from_checkpoint(self):
        self.current_module    = self.checkpoint_mod
        self.current_challenge = self.checkpoint_ch
        self.lives             = self.max_lives
        self.showing_hint      = False
        self.hint_letters      = 0
        self.msg       = "Volviste al checkpoint 📍 ¡Podés lograrlo!"
        self.msg_timer = 2.5
        self.msg_color = PEACH
        self.state     = "playing"
        self.input_box = InputBox((W//2 - 180, H - 70, 360, 40), self.f_mid)

    # ── LÓGICA DE RESPUESTA ─────────────────────────────────────
    def _check_answer(self, user_input):
        ch  = MODULES[self.current_module]["challenges"][self.current_challenge]
        exp = ch["expected"].strip()
        usr = user_input.strip()

        # Comparación exacta (case-insensitive)
        if usr.lower() == exp.lower():
            return True

        # Aceptar con/sin comillas simples o dobles
        # ej: expected='"nombre"' y usuario escribe 'nombre' o "'nombre'"
        usr_bare = usr.strip('"\'')
        exp_bare = exp.strip('"\'')
        if usr_bare and exp_bare and usr_bare.lower() == exp_bare.lower():
            return True

        return False

    def _process_answer(self, user_input):
        if not user_input.strip():
            return  # ignorar enter vacío

        if self._check_answer(user_input):
            self.sound.correct()
            self.flash = 0.3
            # avanzar revelado
            total_ch  = len(MODULES[self.current_module]["challenges"])
            self.revealed_pct = min(1.0, (self.current_challenge + 1) / total_ch)
            # guardar explicación para mostrarla
            ch  = MODULES[self.current_module]["challenges"][self.current_challenge]
            self.last_explain  = ch.get("explain", "")
            self.explain_timer = 3.5   # segundos que se muestra
            self.msg       = "✅  ¡Correcto!"
            self.msg_timer = 3.5
            self.msg_color = GRASS
            self.hint_letters  = 0
            self.showing_hint  = False
            self.current_challenge += 1
            self.total_stars += 1

            # checkpoint cada 3 retos
            if self.current_challenge % 3 == 0:
                self._checkpoint()

            if self.current_challenge >= total_ch:
                self._module_complete()
            else:
                self._save_progress()
        else:
            self.sound.error()
            self.lives -= 1
            ch = MODULES[self.current_module]["challenges"][self.current_challenge]
            # revelar letras de pista una a una (hint tiene formato "l-e-t-r-a")
            raw_hint = ch["hint"].replace("-", "")  # quitar guiones para contar chars
            self.hint_letters = min(self.hint_letters + 1, len(raw_hint))
            self.showing_hint = True
            hint_show = raw_hint[:self.hint_letters]  # revelar letra a letra
            if self.lives <= 0:
                self.sound.gameover()
                self.state     = "gameover"
                self.msg       = "¡Sin vidas! Volvés al checkpoint 📍"
                self.msg_timer = 3.0
                self.msg_color = CORAL
            else:
                self.msg       = f"❌ Incorrecto  —  Pista: {hint_show}"
                self.msg_timer = 2.8
                self.msg_color = CORAL
                self._save_progress()

    def _module_complete(self):
        self.sound.levelup()
        self.total_stars += 3  # bonus módulo
        self.ranking_list = update_ranking(self.name, self.total_stars)
        next_mod = self.current_module + 1
        if next_mod < len(MODULES):
            self.current_module    = next_mod
            self.current_challenge = 0
            self.lives             = self.max_lives
            self.revealed_pct      = 0.0
            self.hint_letters      = 0
            self.showing_hint      = False
            self._checkpoint()
            mod = MODULES[next_mod]
            self.msg       = f"🎉 ¡Módulo completo! Desbloqueado: {mod['emoji']} {mod['name']}"
            self.msg_timer = 3.5
            self.msg_color = LEMON
            self.input_box = InputBox((W//2 - 180, H - 70, 360, 40), self.f_mid)
        else:
            # ¡COMPLETÓ TODO!
            self.sound.complete_all()
            clear_save()
            self.state      = "finished"
            self.final_mode = "code"
            self.msg        = ""

    # ── EVENTOS ────────────────────────────────────────────────
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if self.state == "login":
                # input nombre
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        n = self.name_text.strip()
                        if n:
                            self.name = n
                            self._build_module_buttons()
                            # si hay save del mismo nombre, cargar
                            saved = load_save()
                            if saved and saved.get("name","") == self.name:
                                self._load_progress()
                                self.state     = "playing"
                                self.input_box = InputBox((W//2-180, H-70, 360, 40), self.f_mid)
                                self.msg       = f"¡Bienvenido de nuevo, {self.name}! 👋"
                                self.msg_timer = 2.5
                                self.msg_color = MINT
                        else:
                            self.msg       = "Escribí tu nombre primero 😊"
                            self.msg_timer = 2.0
                            self.msg_color = CORAL
                    elif ev.key == pygame.K_BACKSPACE:
                        self.name_text = self.name_text[:-1]
                    else:
                        if ev.unicode.isprintable() and len(self.name_text) < 20:
                            self.name_text += ev.unicode
                for btn in self.module_buttons:
                    if self.name_text.strip():
                        btn.handle_event(ev)
                    else:
                        # necesita nombre primero
                        if ev.type == pygame.MOUSEBUTTONDOWN:
                            self.msg       = "Primero escribí tu nombre 😊"
                            self.msg_timer = 2.0
                            self.msg_color = CORAL

            elif self.state == "playing":
                if self.input_box:
                    if self.input_box.handle_event(ev):
                        ans = self.input_box.text
                        self.input_box.text = ""
                        self._process_answer(ans)

                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_F1:
                        # pista de emergencia (cuesta 1 vida)
                        ch = MODULES[self.current_module]["challenges"][self.current_challenge]
                        self.hint_letters = len(ch["hint"])
                        self.showing_hint = True
                        self.lives = max(0, self.lives - 1)
                        self.sound.hint()
                        self.msg       = f"💡 Pista completa: {ch['hint']}  (−1 vida)"
                        self.msg_timer = 3.0
                        self.msg_color = PEACH

            elif self.state == "gameover":
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN or ev.key == pygame.K_r:
                        self._restart_from_checkpoint()

            elif self.state == "finished":
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        self.final_mode = "output" if self.final_mode == "code" else "code"
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

            for btn in (self.module_buttons if self.state == "login" else []):
                btn.handle_event(ev)

    # ── UPDATE ─────────────────────────────────────────────────
    def update(self, dt):
        self.cursor_timer += dt
        self.flash = max(0.0, self.flash - dt * 2)
        if self.msg_timer > 0:
            self.msg_timer -= dt
        if self.explain_timer > 0:
            self.explain_timer -= dt
        for b in self.bubbles:
            b.update()
        if self.input_box:
            self.input_box.update(dt)
        for btn in self.module_buttons:
            btn.update(dt)

    # ── DRAW HELPERS ───────────────────────────────────────────
    def _draw_bg(self):
        self.screen.fill(SKY)
        for b in self.bubbles:
            b.draw(self.screen)

    def _draw_hearts(self, x, y):
        for i in range(self.max_lives):
            col = CORAL if i < self.lives else (210, 210, 220)
            # corazón simple con dos círculos + triángulo
            s = pygame.Surface((24, 22), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (7, 7), 7)
            pygame.draw.circle(s, col, (17, 7), 7)
            pygame.draw.polygon(s, col, [(0,10),(12,22),(24,10)])
            self.screen.blit(s, (x + i*30, y))

    def _draw_stars_badge(self, x, y):
        badge = self.f_big.render(f"⭐ {self.total_stars}", True, DARK_TXT)
        self.screen.blit(badge, (x, y))

    def _draw_msg(self):
        if self.msg_timer > 0 and self.msg:
            alpha = min(255, int(self.msg_timer * 200))
            surf  = self.f_mid.render(self.msg[:80], True, self.msg_color)
            bg    = pygame.Surface((surf.get_width()+20, surf.get_height()+10), pygame.SRCALPHA)
            pygame.draw.rect(bg, (255,255,255,180), bg.get_rect(), border_radius=8)
            bx = W//2 - (surf.get_width()+20)//2
            self.screen.blit(bg,   (bx, H-50))
            self.screen.blit(surf, (bx+10, H-45))

    def _draw_flash(self):
        if self.flash > 0:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((255,255,255, int(self.flash*180)))
            self.screen.blit(s,(0,0))

    def _panel(self, x, y, w, h, color=(255,255,255), alpha=220):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0,0,w,h), border_radius=16)
        pygame.draw.rect(s, (*MINT, 200), (0,0,w,h), 3, border_radius=16)
        self.screen.blit(s, (x, y))

    def _draw_code_block(self, text, x, y, w):
        lines = text.split("\n")
        lh    = 19
        bh    = len(lines)*lh + 14
        self._panel(x, y, w, bh, (230,240,255), 240)
        for i, line in enumerate(lines):
            # colorear ___ en rojo
            parts = line.split("___")
            cx = x + 8
            cy = y + 7 + i*lh
            for j, part in enumerate(parts):
                surf = self.f_mid.render(part, True, (40,60,100))
                self.screen.blit(surf, (cx, cy))
                cx += surf.get_width()
                if j < len(parts)-1:
                    blank = self.f_mid.render("___", True, CORAL)
                    self.screen.blit(blank, (cx, cy))
                    cx += blank.get_width()

    def _draw_syntax_block(self, text, x, y, w):
        lines = text.split("\n")
        lh    = 17
        bh    = len(lines)*lh + 20
        self._panel(x, y, w, bh, (240,250,240), 220)
        title = self.f_hint.render("📖 Ejemplo de sintaxis:", True, (80,130,80))
        self.screen.blit(title, (x+8, y+4))
        for i, line in enumerate(lines):
            surf = self.f_sm.render(line, True, (50,90,50))
            self.screen.blit(surf, (x+10, y+20+i*lh))

    # ── PANTALLA LOGIN ──────────────────────────────────────────
    def draw_login(self):
        self._draw_bg()

        # título
        title = self.f_title.render("🐍 Python Splash", True, DARK_TXT)
        sub   = self.f_big.render("¡Aprende Python descubriendo figuras secretas!", True, (80,80,120))
        self.screen.blit(title, (W//2 - title.get_width()//2, 22))
        self.screen.blit(sub,   (W//2 - sub.get_width()//2,   62))

        # caja nombre
        self._panel(W//2-200, 105, 400, 55, WHITE, 230)
        lbl  = self.f_hint.render("¿Cómo te llamás?  (Enter para continuar)", True, (100,100,140))
        self.screen.blit(lbl, (W//2-185, 112))
        # texto
        display = self.name_text + ("|" if int(self.cursor_timer*2)%2==0 else "")
        ntxt = self.f_big.render(display if display else "Escribí tu nombre...", True,
                                  DARK_TXT if self.name_text else (180,180,200))
        self.screen.blit(ntxt, (W//2-185, 133))

        # instrucción módulos
        inst = self.f_hint.render("Elegí un módulo para empezar:", True, (80,80,120))
        self.screen.blit(inst, (W//2 - inst.get_width()//2, 286))

        for btn in self.module_buttons:
            btn.draw(self.screen, self.f_hint)

        # ranking pequeño
        rx = W - 200
        self._panel(rx, 100, 185, 200, WHITE, 200)
        rt = self.f_hint.render("🏆 Ranking", True, DARK_TXT)
        self.screen.blit(rt, (rx+10, 108))
        for i, e in enumerate(self.ranking_list[:7]):
            line = self.f_sm.render(f"{i+1}. {e['name'][:10]}  ⭐{e['stars']}", True, DARK_TXT)
            self.screen.blit(line, (rx+10, 130+i*24))

        # tip F1
        tip = self.f_sm.render("F1 = pista de emergencia (−1 vida)", True, (140,140,170))
        self.screen.blit(tip, (10, H-20))

        self._draw_msg()

    # ── PANTALLA PLAYING ────────────────────────────────────────
    def draw_playing(self):
        self._draw_bg()
        mod = MODULES[self.current_module]
        ch  = mod["challenges"][self.current_challenge]

        # ── Panel izquierdo: figura + HUD ──
        PX, PY = 18, 80
        fig_name = draw_pixel_figure(
            self.screen, mod["figure"], self.revealed_pct, PX, PY, cell=24)

        # nombre figura
        fn = self.f_hint.render(fig_name, True, DARK_TXT)
        self.screen.blit(fn, (PX, PY + 8*24 + 14))

        # vidas
        lbl_v = self.f_hint.render("Vidas:", True, DARK_TXT)
        self.screen.blit(lbl_v, (PX, PY + 8*24 + 40))
        self._draw_hearts(PX + 52, PY + 8*24 + 36)

        # estrellas
        self._draw_stars_badge(PX, PY + 8*24 + 68)

        # progreso módulo
        total_ch = len(mod["challenges"])
        prog_pct = self.current_challenge / total_ch
        bw = 200
        pygame.draw.rect(self.screen, (200,220,230), (PX, PY+8*24+96, bw, 12), border_radius=6)
        pygame.draw.rect(self.screen, MINT, (PX, PY+8*24+96, int(bw*prog_pct), 12), border_radius=6)
        prog_lbl = self.f_sm.render(f"Reto {self.current_challenge+1}/{total_ch}", True, DARK_TXT)
        self.screen.blit(prog_lbl, (PX, PY+8*24+112))

        # nombre módulo
        mod_lbl = self.f_big.render(f"{mod['emoji']} {mod['name']}", True, MODULE_PALETTE[self.current_module % len(MODULE_PALETTE)])
        self.screen.blit(mod_lbl, (PX, 40))

        # tip del módulo
        tip_surf = self.f_sm.render(mod["tip"], True, (80,80,120))
        self.screen.blit(tip_surf, (PX, 62))

        # ── Panel derecho: reto ──
        RX = 240
        self._panel(RX, 30, W-RX-10, H-44, WHITE, 200)

        # descripción
        desc_lines = ch["desc"].split("\n")
        dy = 44
        for dl in desc_lines:
            ds = self.f_mid.render(dl, True, DARK_TXT)
            self.screen.blit(ds, (RX+12, dy))
            dy += 24

        # instrucción clara de qué escribir
        instr = self.f_hint.render("✏️  Escribí SOLO la palabra que va en el lugar de  ___", True, LAVENDER)
        self.screen.blit(instr, (RX+12, dy))
        dy += 20

        # código con huecos
        self._draw_code_block(ch["code"], RX+12, dy+4, W-RX-30)
        dy += len(ch["code"].split("\n"))*19 + 26

        # pista progresiva — letra a letra (sin guiones)
        if self.showing_hint:
            raw_hint = ch["hint"].replace("-", "")
            hint_show = raw_hint[:self.hint_letters]
            hs = self.f_hint.render(f"💡 Pista: {hint_show}", True, PEACH)
            self.screen.blit(hs, (RX+12, dy))
            dy += 26

        # sintaxis de ejemplo
        self._draw_syntax_block(mod["syntax"], RX+12, dy+4, W-RX-30)

        # panel explicación (aparece tras acierto)
        if self.explain_timer > 0 and self.last_explain:
            self._panel(RX+12, H-130, W-RX-30, 48, (220,255,220), 230)
            ex = self.f_hint.render(f"💡 {self.last_explain}", True, (40,120,40))
            self.screen.blit(ex, (RX+22, H-118))

        # input
        if self.input_box:
            self.input_box.draw(self.screen, "✏️  Tu respuesta (Enter para confirmar):")

        self._draw_flash()
        self._draw_msg()

    # ── PANTALLA GAMEOVER ───────────────────────────────────────
    def draw_gameover(self):
        self._draw_bg()
        self._panel(W//2-280, 80, 560, 380, WHITE, 230)

        t1 = self.f_title.render("💔 ¡Sin vidas!", True, CORAL)
        self.screen.blit(t1, (W//2 - t1.get_width()//2, 100))

        t2 = self.f_big.render("Volvés al último checkpoint guardado 📍", True, DARK_TXT)
        self.screen.blit(t2, (W//2 - t2.get_width()//2, 148))

        cp = MODULES[self.checkpoint_mod]
        t3 = self.f_mid.render(f"Checkpoint: Módulo '{cp['name']}' — Reto {self.checkpoint_ch+1}", True, (80,80,120))
        self.screen.blit(t3, (W//2 - t3.get_width()//2, 182))

        t4 = self.f_big.render("⭐ Estrellas acumuladas: " + str(self.total_stars), True, LEMON)
        self.screen.blit(t4, (W//2 - t4.get_width()//2, 220))

        t5 = self.f_hint.render("Presioná ENTER o R para continuar desde el checkpoint", True, MINT)
        self.screen.blit(t5, (W//2 - t5.get_width()//2, 268))

        # ranking
        ry = 310
        rt = self.f_hint.render("🏆 Ranking:", True, DARK_TXT)
        self.screen.blit(rt, (W//2 - 140, ry))
        for i, e in enumerate(self.ranking_list[:5]):
            ls = self.f_sm.render(f"{i+1}. {e['name'][:14]}  ⭐{e['stars']}", True, DARK_TXT)
            self.screen.blit(ls, (W//2 - 140, ry+22+i*20))

    # ── PANTALLA FINISHED (proyecto final) ──────────────────────
    def draw_finished(self):
        self._draw_bg()

        # confetti simple: burbujas van más rápido en esta pantalla
        self._panel(50, 20, W-100, H-40, WHITE, 220)

        t1 = self.f_title.render("🎉 ¡Felicitaciones, " + self.name + "!", True, CORAL)
        self.screen.blit(t1, (W//2 - t1.get_width()//2, 32))

        t2 = self.f_big.render("Completaste todos los módulos de Python Splash 🐍", True, (80,80,120))
        self.screen.blit(t2, (W//2 - t2.get_width()//2, 72))

        t3 = self.f_hint.render(f"⭐ Total de estrellas: {self.total_stars}   |   ESPACIO = ver código/salida   |   ESC = salir", True, DARK_TXT)
        self.screen.blit(t3, (W//2 - t3.get_width()//2, 100))

        # proyecto final
        self._panel(60, 120, W-120, H-160, (245,250,255), 240)

        if self.final_mode == "code":
            tab = self.f_hint.render("[ 📄 CÓDIGO ]   [ salida ]   ← ESPACIO para alternar", True, MINT)
            self.screen.blit(tab, (80, 126))
            lines = FINAL_PROJECT.strip().split("\n")
            for i, line in enumerate(lines[:26]):
                col = (40,80,160) if line.strip().startswith("#") else (30,50,30)
                surf = self.f_sm.render(line, True, col)
                self.screen.blit(surf, (78, 148+i*17))
        else:
            tab = self.f_hint.render("[ código ]   [ 💻 SALIDA ]   ← ESPACIO para alternar", True, CORAL)
            self.screen.blit(tab, (80, 126))
            lines = FINAL_OUTPUT.strip().split("\n")
            for i, line in enumerate(lines):
                col = GRASS if line.startswith("✅") else (CORAL if ">>>" in line else DARK_TXT)
                surf = self.f_sm.render(line, True, col)
                self.screen.blit(surf, (78, 148+i*19))

        enc = self.f_hint.render("¿Querés un nuevo módulo? ¡Pedíselo a tu profe! 📧", True, LAVENDER)
        self.screen.blit(enc, (W//2 - enc.get_width()//2, H-30))

    # ── DRAW DISPATCH ───────────────────────────────────────────
    def draw(self):
        if   self.state == "login":    self.draw_login()
        elif self.state == "playing":  self.draw_playing()
        elif self.state == "gameover": self.draw_gameover()
        elif self.state == "finished": self.draw_finished()
        pygame.display.flip()

    # ── MAIN LOOP ───────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    game = PythonSplash()
    game.run()
