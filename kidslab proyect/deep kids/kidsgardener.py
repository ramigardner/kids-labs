import tkinter as tk
import requests
import threading
import time
import random

# -----------------------------
# CONFIG
# -----------------------------
BASE_URLS = [
    "http://desktop-be9om4d.tail2e4caf.ts.net:7771/api/state",
    "https://desktop-be9om4d.tail2e4caf.ts.net:7771/api/state"
]

REFRESH_INTERVAL = 5
TIMEOUT = 10  # más tolerante

devices = {}
last_devices = {}
current_url = None
running = True

# -----------------------------
# DETECTAR URL FUNCIONAL
# -----------------------------
def resolve_url():
    global current_url

    for url in BASE_URLS:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                current_url = url
                print("Conectado a:", url)
                return
        except:
            continue

    current_url = None

# -----------------------------
# FETCH
# -----------------------------
def fetch_data():
    global devices, last_devices

    resolve_url()

    while running:
        if not current_url:
            root.after(0, show_status, "Sin conexión al nodo")
            time.sleep(REFRESH_INTERVAL)
            resolve_url()
            continue

        try:
            res = requests.get(current_url, timeout=TIMEOUT)
            data = res.json()

            new_devices = {}

            for node in data.get("nodes", []):
                for d in node.get("monitored_devices", []):
                    name = f"{d['tipo']} ({d['ip']})"

                    new_devices[name] = {
                        "latency": 1 - d.get("karma_avg", 0.5),
                        "karma": d.get("karma_avg", 0.5),
                        "obs": d.get("observations", 0)
                    }

            if new_devices:
                devices = new_devices
                last_devices = new_devices

            root.after(0, update_view, "OK")

        except Exception as e:
            print("timeout/error:", e)

            # usar último estado válido
            if last_devices:
                devices.update(last_devices)
                root.after(0, update_view, "⚠ usando datos previos")
            else:
                root.after(0, show_status, "Esperando datos del nodo...")

        time.sleep(REFRESH_INTERVAL)

# -----------------------------
# LOGICA
# -----------------------------
def estimate_reality():
    if not devices:
        return 0
    return sum(d["latency"] for d in devices.values()) / len(devices)

# -----------------------------
# UI
# -----------------------------
def update_view(status_msg):
    output.delete("1.0", tk.END)

    if not devices:
        output.insert(tk.END, "Sin datos...\n")
        return

    reality = estimate_reality()

    output.insert(tk.END, f"Estado: {status_msg}\n")
    output.insert(tk.END, f"Realidad: {round(reality,3)}\n")

    matches = sum(1 for d in devices.values() if abs(d["latency"] - reality) < 0.1)
    output.insert(tk.END, f"Coincidencias: {matches}/{len(devices)}\n\n")

    for name, data in devices.items():
        error = abs(data["latency"] - reality)

        if error < 0.1:
            status = "✔"
            reason = ""
        else:
            status = "🚨"
            reason = f"   difiere {round(error,3)}\n"

        output.insert(
            tk.END,
            f"{name}\n"
            f"  lat: {round(data['latency'],3)} | karma: {round(data['karma'],3)}\n"
            f"  estado: {status}\n"
            f"{reason}\n"
        )

def show_status(msg):
    output.delete("1.0", tk.END)
    output.insert(tk.END, msg + "\n")

# -----------------------------
# EXPERIMENTOS
# -----------------------------
def add_noise():
    if devices:
        k = random.choice(list(devices.keys()))
        devices[k]["latency"] = random.uniform(0.7, 1.0)
        update_view("ruido manual")

def ignore_bad():
    global devices
    if devices:
        reality = estimate_reality()
        devices = {
            k: v for k, v in devices.items()
            if abs(v["latency"] - reality) < 0.2
        }
        update_view("filtrado")

def randomize_all():
    if devices:
        for d in devices.values():
            d["latency"] = random.uniform(0.1, 1.0)
        update_view("aleatorio")

# -----------------------------
# APP
# -----------------------------
root = tk.Tk()
root.title("ASPR - Realidad vs Datos")

output = tk.Text(root, height=28, width=75)
output.pack()

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Ruido", command=add_noise).grid(row=0, column=0)
tk.Button(btn_frame, text="Filtrar", command=ignore_bad).grid(row=0, column=1)
tk.Button(btn_frame, text="Aleatorio", command=randomize_all).grid(row=0, column=2)

threading.Thread(target=fetch_data, daemon=True).start()

root.mainloop()
