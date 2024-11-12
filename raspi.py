import tkinter as tk
from tkinter import ttk
import threading
import time
import serial
import gpiod
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import Adafruit_DHT

GPIO_CHIP = 'gpiochip4'
PUMP_PIN = 17
MOISTURE_THRESHOLD = 300
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO Pin where DHT22 is connected

chip = gpiod.Chip(GPIO_CHIP)
pump_line = chip.get_line(PUMP_PIN)
pump_line.request(consumer="water_pump_control", type=gpiod.LINE_REQ_DIR_OUT)
pump_line.set_value(0)

moisture_data = {"Plant A": []}
temperature_data = {"Plant A": []}
humidity_data = {"Plant A": []}

def water_pump(duration=3):
    if pump_line.get_value() == 0:
        print("Watering Plant A...")
        pump_line.set_value(1)
        time.sleep(duration)
        pump_line.set_value(0)
        print("Watering complete!")
    else:
        print("Pump is already on. Skipping watering.")

def read_from_arduino():
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE)
    while True:
        if arduino.in_waiting > 0:
            data = arduino.readline().decode('utf-8').strip()
            if data:
                try:
                    moisture = int(data)
                    moisture_percent = (1023 - moisture) / 1023 * 100
                    moisture_data["Plant A"].append(moisture_percent)
                    print(f"Received Moisture Data: {moisture_percent}%")

                    if moisture < MOISTURE_THRESHOLD:
                        water_pump()

                    root.after(0, update_graphs)

                except ValueError:
                    print("Invalid data received from Arduino.")
        time.sleep(1)

def read_from_dht22():
    while True:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            temperature_data["Plant A"].append(temperature)
            humidity_data["Plant A"].append(humidity)
            print(f"Temperature: {temperature}°C  Humidity: {humidity}%")
        else:
            print("Failed to retrieve data from DHT22 sensor.")
        time.sleep(5)

def show_moisture_graph(canvas_frame):
    data = moisture_data["Plant A"]

    for widget in canvas_frame.winfo_children():
        widget.destroy()

    short_term_data = data[-10:]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(short_term_data, marker='o', color='g')
    ax.set_title("Soil Moisture Levels (Short-Term)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Moisture Level (%)")

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    plt.close(fig)

def show_long_term_graph(canvas_frame):
    data = moisture_data["Plant A"]

    for widget in canvas_frame.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(data, label="Plant A", marker='o', color='g')
    ax.set_title("Long-Term Soil Moisture Levels")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Moisture Level (%)")

    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    plt.close(fig)

def show_temperature_and_humidity():
    temperature = temperature_data["Plant A"][-1] if temperature_data["Plant A"] else "N/A"
    humidity = humidity_data["Plant A"][-1] if humidity_data["Plant A"] else "N/A"

    temp_label.config(text=f"Temperature: {temperature}°C")
    humidity_label.config(text=f"Humidity: {humidity}%")

def update_graphs():
    show_moisture_graph(canvas_frame_1)
    show_long_term_graph(canvas_frame_2)
    show_temperature_and_humidity()

def setup_gui():
    global root, canvas_frame_1, canvas_frame_2, temp_label, humidity_label

    root = tk.Tk()
    root.title("Smart Plant Monitoring System")
    root.geometry("1000x600")
    root.configure(bg="#d4f1f4")

    title_label = tk.Label(root, text="Plant Monitoring System", font=("Arial", 16, "bold"), bg="#75e6da", fg="white")
    title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")

    plant_var = tk.StringVar()
    plant_menu = ttk.Combobox(root, textvariable=plant_var, values=["Plant A"], font=("Arial", 12), width=12)
    plant_menu.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    plant_menu.current(0)

    canvas_frame_1 = tk.Frame(root, bg="#d4f1f4")
    canvas_frame_1.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
    canvas_frame_1.grid_rowconfigure(0, weight=1)
    canvas_frame_1.grid_columnconfigure(0, weight=1)

    canvas_frame_2 = tk.Frame(root, bg="#d4f1f4")
    canvas_frame_2.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
    canvas_frame_2.grid_rowconfigure(0, weight=1)
    canvas_frame_2.grid_columnconfigure(0, weight=1)

    temp_label = tk.Label(root, font=("Arial", 14), bg="#d4f1f4")
    temp_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    humidity_label = tk.Label(root, font=("Arial", 14), bg="#d4f1f4")
    humidity_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    update_graphs()

    root.mainloop()

def start_background_tasks():
    threading.Thread(target=read_from_arduino, daemon=True).start()
    threading.Thread(target=read_from_dht22, daemon=True).start()

if name == "main":
    start_background_tasks()
    setup_gui()
