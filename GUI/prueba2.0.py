#!/usr/bin/env python3
import tkinter as tk

from tkinter import *
from tkinter import filedialog
from tkinter import Button
from PIL import Image, ImageTk

import webbrowser

import re
import os
import sys
import pexpect
import time
import threading
import subprocess
import json
import base64

Pin_1 =  [116, 188]
tooltips_text = {
    'lineas': 'mostrar/ocultar lineas',
    'imagen': 'Cargar imagen',
    'path': 'Cargar path a QEMU',
    'velocidad': 'Ajustar velocidad consultas',
    'elf': 'Cargar solo kernel',
    'carga': 'Cargar items',
    'qemu': 'Reiniciar QEMU',
    'limpia': 'Limpiar items',
    'guarda': 'Guardar items',
    'boton': 'Agregar boton',
    'led': 'Agregar led',
    'rasp': 'Clic derecho apra mas información'
}
gpio_pinOut = {
        3: 2, 5: 3, 7: 4, 8: 14, 10: 15,
        11: 17, 12: 18, 13: 27, 15: 22, 16: 23,
        18: 24, 19: 10, 21: 9, 22: 25, 23: 11,
        24: 8, 26: 7, 27: 0, 28: 1, 29: 5,
        31: 6, 32: 12, 33: 13, 35: 19, 36: 16,
        37: 26, 38: 20, 40: 21
    }
# ---MUTEX---
mutex_gpio = threading.Lock() 
mutex_sleep = threading.Lock() 
mutex = threading.Lock() 

# ---RUTAS FICHEROS---
absolute_path = os.path.dirname(__file__)
relative_path_UI = "IMG/"
aarch64_path = "/build/qemu-system-aarch64"
# ---IMAGENES---
full_path_LedON = os.path.join(absolute_path, relative_path_UI+ "ledON.png")
full_path_LedOFF = os.path.join(absolute_path, relative_path_UI + "ledOFF.png")
full_path_Boton = os.path.join(absolute_path, relative_path_UI + "boton.png")
full_path_Raspi = os.path.join(absolute_path, relative_path_UI + "raspi.png")
full_path_Guarda = os.path.join(absolute_path, relative_path_UI + "guarda.png")
full_path_Carga = os.path.join(absolute_path, relative_path_UI + "import.png")
full_path_kernel = os.path.join(absolute_path, relative_path_UI + "kernel.png")
full_path_limpiar = os.path.join(absolute_path, relative_path_UI + "limpiar.png")
full_path_ojo = os.path.join(absolute_path, relative_path_UI + "ojo.png")
full_path_imagen= os.path.join(absolute_path, relative_path_UI + "OS.png")
full_path_recarga = os.path.join(absolute_path, relative_path_UI + "recarga.png")
full_path_velocidad = os.path.join(absolute_path, relative_path_UI + "velocidad.png")
full_path_qemu = os.path.join(absolute_path, relative_path_UI + "qemu.png")

# ---DIRECCIONES RASPBERRY PI 3B---
SOCK_PATH="/tmp/tmp-gpio.sock"
GPIO_RANGE=[0x3f200000, 0x3f200fff]
IC_RANGE  =[0x3f00b200, 0x3f00b3ff]

GPIO_SET_OFFSET=0x1c
GPIO_RESET_OFFSET=0x28
GPIO_READ_OFFSET=0x34

# ---DICCIONARIOS---
imagenes_mostradas = {} # Dado el tag te da la imagen
imagenes_mostradas_aux = {}
identificadores = {} 	# Dado el tag da el ID
conexiones = {} 	    # Dado el tag dice a que GPIO esta conectado
tag_a_tipo = {} 	    # Dado el tag devuelve el si es "led" o "boton"
estado_leds = {} 	    # Dado el tag del led, te dice si deberia estar encendido o apagado
GPIO_usado = {} 	    # Dice si un GPIO esta asignado TODO:MEJORAR
config_GPIO = {}        # Dado un pin de GPIO dice si es "input" o "output" 
etiquetas = {}		    # Dado un tag da el ID de canvas de la etiqueta
AUX_pos = {}            # Guarda posiciones antes de realizar un borrado, util para cargar mejor
lineas = {}

# ---VARIABLES GLOBALES---
elementos = 1           # Sirve para asignar TAG a los elementos de Canvas e identificarlos mejor
stop = 0                # Para pausar el trhead de las consultas
delay = 0               # Delay actual para las consultas
global archivo ,qemu_path, archivo_kernel, archivo_img, archivo_dbt,proceso_qemu,mostrando_lineas
proceso_qemu = None
qemu_path = ""
archivo = ""
archivo_kernel = ""
archivo_img = ""
archivo_dbt = ""
mostrando_lineas = True

data = {
    "identificadores": identificadores,
    "conexiones": conexiones,
    "tag_a_tipo": tag_a_tipo,
    "estado_leds": estado_leds,
    "GPIO_usado": GPIO_usado,
    "etiquetas": etiquetas,
    "posiciones": AUX_pos
}


class VGPIOManager(object):
    fd = None
    def __init__(self, spath=SOCK_PATH):
        self.load(spath)

    def load(self, spath=SOCK_PATH):
        if os.path.exists(SOCK_PATH):
            os.unlink(SOCK_PATH)

        self.fd = pexpect.spawn("socat - UNIX-LISTEN:{}".format(SOCK_PATH))

    def validate_address(self, address):
        if address < GPIO_RANGE[0] or address > GPIO_RANGE[1]:
            return False
        return True

    def writel(self, address, value):
        self._sendline('writel 0x{:x} 0x{:x}'.format(address, value))
        return self._read()

    def readl(self, address):
        self._sendline('readl 0x{:x}'.format(address))
        return self._read()

    def read(self, address, size):
        self._sendline('read 0x{:x} 0x{:x}'.format(address, size))
        return self._read()

    def _sendline(self, s):
        return self.fd.sendline(s)

    def _read(self):
        # Cancel echo
        self.fd.readline()
        return self.fd.readline()

    def read_entire_gpio_area(self):
        v = self.read(GPIO_RANGE[0], 0x1000)
        return v
    def read_all_gpio(self):
        v = self.readl(GPIO_RANGE[0] + GPIO_READ_OFFSET)
        return v

    def close(self):
        self.fd.close()

    def help(self):
        s  = "[ ] Virtual GPIO manager\n"
        s += "    Usage:\n"
        s += "    help                     -- this help message\n"
        s += "    get <gpionum>            -- read a specific gpio\n"
        s += "    set <gpionum> <value>    -- Set a gpio to a specific value\n"
        s += "    toggle <gpionum>         -- change the value of the gpio\n"
        s += "    read-area                -- read entire gpio area\n"
        s += "    read-ic                  -- read entire interrupt controller area\n"
        s += "    readl <address>          -- read 32 bit from address\n"
        s += "    writel <address> <value> -- read 32 bit from address\n"
        s += "    exit                     -- exit from program\n"
        s += "    reload                   -- restart the initialization\n"
        return s

    def read_ic_area(self):
        v = self.read(IC_RANGE[0], 0x200)
        return v

    def get_gpio_location(self, num):
        if num > 54 or num < 0:
            return 0
        return GPIO_RANGE[0] + int(num / 32)

    def set(self, gpionum, value):
        m = self.get_gpio_location(gpionum)
        if value:
            m += GPIO_SET_OFFSET
        else:
            m += GPIO_RESET_OFFSET
        gpio = 1 << (gpionum % 32)
        return self.writel(m, gpio)

    def get(self, gpionum):
        m = self.get_gpio_location(gpionum) + GPIO_READ_OFFSET
        v = int(self.readl(m).split()[1], 0)
        gpio = 1 << (gpionum % 32)
        return str((v & gpio)!=0)
    
    def get_GPIO_Val(self, gpionum,data):
        gpio = 1 << (gpionum % 32)
        return str((data & gpio)!=0)
    
    def carga_estado_GPIO(self):
        try:

            valor= int(vgpio.readl(GPIO_RANGE[0]).split()[1],0)
            valor2 = int(vgpio.readl(GPIO_RANGE[0] + 0x4).split()[1],0)
            valor3 = int(vgpio.readl(GPIO_RANGE[0] + 0x8).split()[1],0)
            for i in range(28):
            # Desplazamos el registro a la derecha para posicionar los bits del GPIO a extraer en la posición más baja
                gpio_a_consutar = i %10
                gpio_aux = {}
                gpio_aux[0] = 1 << ((gpio_a_consutar*3) )
                gpio_aux[1] = 1 << (((gpio_a_consutar*3) + 1 ))
                gpio_aux[2] = 1 << (((gpio_a_consutar*3) + 2 ))

                status = ''
                if(i <= 9):
                    status =  '1' if  valor & gpio_aux[2] != 0 else '0'
                    status +=  '1' if valor & gpio_aux[1] != 0 else '0'
                    status +=  '1' if valor & gpio_aux[0] != 0 else '0'
                    config_GPIO[i] = status
                elif(i <= 19):
                    status =  '1' if  valor2 & gpio_aux[2] != 0 else '0'
                    status +=  '1' if valor2 & gpio_aux[1] != 0 else '0'
                    status +=  '1' if valor2 & gpio_aux[0] != 0 else '0'
                    config_GPIO[i] = status
                elif(i <= 27):
                    status =  '1' if  valor3 & gpio_aux[2] != 0 else '0'
                    status +=  '1' if valor3 & gpio_aux[1] != 0 else '0'
                    status +=  '1' if valor3 & gpio_aux[0] != 0 else '0'
                    config_GPIO[i] = status

        except:
            print("No se pudo cargar el estado de los pines")

    def toggle(self, gpionum):
        v = self.get(gpionum)
        print("value: {}".format(v))
        return self.set(gpionum, not v)

    def parse(self, s):
        s = s.split(' ')
        c = s[0]

        if c == 'help':
            return self.help()
        elif c == 'get':
            if len(s) < 2:
                return "Error: get requires 1 argument"
            return self.get(int(s[1], 0))
        elif c == 'set':
            if len(s) < 3:
                return "Error: set requires 2 arguments"
            return self.set(int(s[1], 0), int(s[2], 0))
        elif c == 'read-area':
            return self.read_entire_gpio_area()
        elif c == 'read-ic':
            return self.read_ic_area()
        elif c == 'readl':
            if len(s) < 2:
                return "Error: read requires 1 argument"
            return self.readl(int(s[1], 0))
        elif c == 'writel':
            if len(s) < 3:
                return "Error: write requires 2 arguments"
            return self.writel(int(s[1], 0), int(s[2],0))
        elif c == 'exit':
            self.close()
            sys.exit(0)
        elif c == 'toggle':
            if len(s) < 2:
                return "Error: toggle requires 1 argument"
            return self.toggle(int(s[1]))
        elif c == 'reload':
            return self.load()
        return ""


def on_clic_item(tipo, imagen, on_motion_func, on_hold_func=None, on_release_func=None):
    global elementos
    global identificadores
    global imagenes_mostradas
    global estado_leds

    imagenes_mostradas[elementos] = ImageTk.PhotoImage(file=imagen)

    x = 20 + (elementos % 5) * 100  # 5 es el número máximo de elementos por fila
    y = 100 + (elementos // 5) * 50 

    identificadores[elementos] = canvas.create_image(x, y, image=imagenes_mostradas[elementos], tag=elementos)
    tag_a_tipo[elementos] = tipo
    id = identificadores[elementos]
    tag = elementos

    canvas.tag_bind(id, "<B1-Motion>", lambda event: on_motion_func(event, tag))
    canvas.tag_bind(id, "<Button-3>", lambda event: show_popup(event, tag))
    canvas.tag_bind(id, "<Button-2>", lambda event: delete_item(event, tag))
    if on_hold_func:
        canvas.tag_bind(id, "<ButtonPress-1>", lambda event: on_hold_func(event, tag))

    if on_release_func:
        canvas.tag_bind(id, "<ButtonRelease-1>", lambda event: on_release_func(event, tag))
    estado_leds[tag] = "False"
    elementos += 1
    return tag
        

def delete_item(event, tag):
   
        unbind_item(identificadores[int(tag)],tag)
        canvas.delete(identificadores[int(tag)])
        if(tag in etiquetas):
            canvas.delete(etiquetas[tag])
            del etiquetas[tag]
        if(tag in conexiones and conexiones[tag]in GPIO_usado and GPIO_usado[conexiones[tag]]  == 1):
            del GPIO_usado[conexiones[tag]]
        elif(tag in conexiones and conexiones[tag]in GPIO_usado):
            GPIO_usado[conexiones[tag]]-=1
        if(tag in imagenes_mostradas):
            del imagenes_mostradas[tag]
        if(tag in identificadores):
            del identificadores[int(tag)]
        if(tag in conexiones):	
            del conexiones[tag]	
        if(tag in tag_a_tipo):	
            del tag_a_tipo[tag]	
        if(tag in estado_leds):
            del estado_leds[tag] 	
        if(tag in lineas):
            canvas.delete(lineas[tag])
            del lineas[tag] 


def unbind_item(id,tag):

    if(tag_a_tipo[tag]	== 'led'):
        canvas.tag_unbind(id, "<B1-Motion>")
        canvas.tag_unbind(id, "<Button-3>")
        canvas.tag_unbind(id, "<Button-2>")
    else:
        canvas.tag_unbind(id,"<B1-Motion>")
        canvas.tag_unbind(id,"<ButtonPress-1>")
        canvas.tag_unbind(id,"<ButtonRelease-1>")
        canvas.tag_unbind(id,"<Button-3>")
        canvas.tag_unbind(id, "<Button-2>")


def on_clic_led(event):
    with mutex:
        on_clic_item("led", full_path_LedOFF, on_motion)


def on_clic_boton(event):
    with mutex:
        resize = Image.open(full_path_Boton)
        on_clic_item("boton", full_path_Boton, on_motion, on_hold_boton, on_release_boton)


def on_release_boton(event,tag):

    if proceso_qemu is not None and proceso_qemu.poll() != None:
        if(tag in conexiones):
            gpio =  conexiones[tag]
            with mutex_gpio:
                vgpio.parse("set " + str(gpio) + " 0")
                print("set " + str(gpio) + " 0")
    
    
def on_hold_boton(event,tag):
    with mutex_gpio:
        if proceso_qemu is not None and proceso_qemu.poll() != None:
            if(tag in conexiones):
                gpio =  conexiones[tag]
                vgpio.parse("set " + str(gpio) + " 1")
                print("set " + str(gpio) + " 1")

def coordenadas_gpio(gpio):
    for clave, val in gpio_pinOut.items():
        if val == int(gpio):
            num_pin = clave
    x = Pin_1[0]
    y = Pin_1[1]
    if(num_pin % 2 == 0):
        y -= 9
        x -= 9
    x += (9 * int((num_pin/2))) + int((num_pin/2) - 1)
    if(num_pin > 20): x -=3
    return x,y
def on_motion(event, tag):
    x = event.x
    y = event.y
   # if(tag in identificadores):
    with mutex:
        if check_place(x, y, identificadores[int(tag)]):

            canvas.coords(identificadores[int(tag)],event.x,event.y)

            # Actualizar la posición de la etiqueta
            etiqueta = etiquetas.get(tag)
            if etiqueta is not None:
                etiqueta = etiquetas[tag]
                canvas.coords(etiqueta, x, y + 30)
            linea = lineas.get(tag)
            if linea is not None:
                linea = lineas[tag]
                pin = coordenadas_gpio(conexiones[tag])
                canvas.coords(linea, x, y + 15, pin[0], pin[1])


def check_place(x, y, id):
    empty = True
    
    for clave in identificadores:
        if identificadores[clave] != id:
            coords = canvas.coords(identificadores[clave])
            if abs(x - coords[0]) + abs(y - coords[1]) < 50:
                empty = False
                break
    
    return empty


def clic_aceptar(event, tag):
    with mutex:
        texto = entry.get()
        if texto.isdigit() and  int(texto) < 28:
            if (tag in conexiones):
                if (GPIO_usado[conexiones[tag]] == 1):
                    del GPIO_usado[conexiones[tag]]
                else:
                    GPIO_usado[conexiones[tag]] -= 1
                del conexiones[tag]
                if(tag in etiquetas):
                    canvas.delete(etiquetas[tag])
                    del etiquetas[tag]
                print("Unbind")
            conexiones[tag] = texto
            if (texto in GPIO_usado):
                GPIO_usado[texto] += 1
            else:
                GPIO_usado[texto] = 1

            coords = canvas.coords(identificadores[int(tag)])
            if coords:
                etiquetas[tag] = canvas.create_text(coords[0], coords[1] + 30, text="", fill="white", font=("Arial", 10), anchor="n", tags=("etiqueta",))
                canvas.itemconfig(etiquetas[tag], text="GPIO " + texto)
                if tag in lineas: canvas.delete(lineas[tag])
                global mostrando_lineas
                if mostrando_lineas:
                    pin = coordenadas_gpio(conexiones[tag])
                    lineas[tag] = canvas.create_line(coords[0], coords[1]+15,  pin[0], pin[1], fill="red", width=2)
                print("Asignado el nuevo")
            pop.destroy()

        else:
            print("Valor no válido, GPIO de 0 a 27")
        

        
def show_popup(event,tag):
    x = event.x_root
    y = event.y_root
    
    global pop
    if('pop'in globals()):
        pop.destroy()
        
    pop = Toplevel(root)
    pop.title("Conexión")
    pop.config(bg = "#191818")

    frame = tk.Frame(pop,bg = "#191818")
    frame.pack(pady=10)

     # Create a label
    label = tk.Label(frame, text="Conectar al GPIO número:",bg = "#191818",fg="white")
    label.grid(row=0, column=0)
    
    # Create a text box
    global entry
    entry = tk.Entry(frame)
    entry.grid(row=1, column=0)
    
    # Create a label below the text box
    below_label = tk.Label(frame, text="Aceptar",bg = "#191818",fg="white")
    below_label.grid(row=2, column=0)
    below_label.bind("<Button-1>",lambda event: clic_aceptar(event,tag))

    pop.geometry(f"+{x}+{y}")



def popup_GPIO(event): #Codigo duplicado!!!!!!!!!!!!!!
    with mutex:
        if proceso_qemu is not None and proceso_qemu.poll() != None:
            x = event.x_root
            y = event.y_root
            global pop_GPIO
            if('pop_GPIO'in globals()):
                pop_GPIO.destroy()
            pop_GPIO = Toplevel(root)
            pop_GPIO.title("Resumen GPIO")
            pop_GPIO.config(bg = "#191818")

            frame = tk.Frame(pop_GPIO,bg = "#191818")
            frame.pack(pady=10)

            with mutex_gpio:
                vgpio.carga_estado_GPIO()

            for columna  in range(1, 41):
                if columna % 2 == 0:
                    texto = "error"
                    if(columna == 2 or columna == 4 ):
                        texto = "Power"
                    elif(columna == 6 or columna == 14 or columna == 20 or columna == 30 or columna == 34):
                        texto = "Ground"
                    else:
                        if(config_GPIO[gpio_pinOut[columna]] == "001"): texto ="Gpio " + str(gpio_pinOut[columna])+ " Output"
                        elif(config_GPIO[gpio_pinOut[columna]] == "000"): texto ="Gpio " + str(gpio_pinOut[columna])+ " Input" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "100"): texto ="Gpio " + str(gpio_pinOut[columna])+ " Alt-1" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "110"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-2" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "111"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-3" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "011"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-4" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "010"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-5" 
                            
                    valor = tk.Label(frame, text=str(texto), borderwidth=1, relief="solid", bg = "#191818",fg="white")
                    valor.grid(row=0, column=columna, padx=5, pady=5)

            for columna in range(1, 41):
                if columna % 2 == 0:
                    valor = tk.Label(frame, text=str(columna), borderwidth=1, relief="solid", bg = "#191818",fg="white")
                    valor.grid(row=1, column=columna, padx=5, pady=5)

            for columna in range(1, 41):
                 if columna % 2 != 0:
                    valor = tk.Label(frame, text=str(columna), borderwidth=1, relief="solid", bg = "#191818",fg="white")
                    valor.grid(row=2, column=columna + 1, padx=10, pady=5)

            for columna  in range(1, 41):
                if columna % 2 == 1:
                    texto = "error"
                    if(columna == 1 or columna == 17 ):
                        texto = "Power"
                    elif(columna == 9 or columna == 25 or columna == 39):
                        texto = "Ground"
                    else:
                        if(config_GPIO[gpio_pinOut[columna]] == "001"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Output"
                        elif(config_GPIO[gpio_pinOut[columna]] == "000"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Input" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "100"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-0" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "101"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-1" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "110"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-2" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "111"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-3" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "011"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-4" 
                        elif (config_GPIO[gpio_pinOut[columna]] == "010"): texto = "Gpio " + str(gpio_pinOut[columna])+ " Alt-5" 

                    valor = tk.Label(frame, text=str(texto), borderwidth=1, relief="solid", bg = "#191818",fg="white")
                    valor.grid(row=3, column=columna+ 1, padx=5, pady=5)

            valor = tk.Label(frame, text="Para más detalle clicar aquí", borderwidth=1, relief="solid", bg="#191818", fg="blue")
            valor.grid(row=4, column=20, padx=5, pady=5)
            valor.bind("<Button-1>", abrir_enlace)

def abrir_enlace(event):
    webbrowser.open("https://pinout.xyz/pinout/pin27_gpio0#")

def get(self, gpionum):
    m = self.get_gpio_location(gpionum) + GPIO_READ_OFFSET
    v = int(self.readl(m).split()[1], 0)
    gpio = 1 << (gpionum % 32)
    return str((v & gpio)!=0)


def actualiza_led(estado,tag):
    if(tag in imagenes_mostradas):
        if(estado == "True"):
            imagenes_mostradas[int(tag)] = ImageTk.PhotoImage(file=full_path_LedON)
            canvas.itemconfig(identificadores[int(tag)] ,image=imagenes_mostradas[int(tag)])
        else:
            imagenes_mostradas[int(tag)] = ImageTk.PhotoImage(file=full_path_LedOFF)
            canvas.itemconfig(identificadores[int(tag)] ,image=imagenes_mostradas[int(tag)])


def delete(event = None):
    with mutex:    
        global identificadores, elementos
        ids = list(identificadores.keys())

        for tag in ids:
            if tag != "raspi":
                delete_item(None, tag)

        elementos = 1


def reboot(event = None):
    global vgpio, command_thread, stop, archivo, qemu_path
    if len(qemu_path)>0 and len(archivo) > 0 and  os.path.exists(qemu_path) and os.path.exists(archivo):
        recargar_qemu(False)
    elif len(qemu_path)>0 and os.path.exists(qemu_path)  and len(archivo_kernel) > 0 and os.path.exists(archivo_kernel) and len(archivo_img) > 0 and os.path.exists(archivo_img) and len(archivo_dbt) > 0 and os.path.exists(archivo_dbt):
        recargar_qemu(True)
            

def guardar_estado(event = None):
    with mutex:
        coord = []
        for clave in identificadores:
            coords = canvas.coords(identificadores[clave])
            AUX_pos[clave] = coords
        with open(absolute_path + "datos.json", "w") as json_file:
            json.dump(data, json_file)

        print(json.dumps(data, indent=4))


def cargar_estado(event = None):
    global identificadores, conexiones, tag_a_tipo, estado_leds, GPIO_usado, config_GPIO, etiquetas, elementos
    
    if (elementos != 1):
        delete()

    with mutex:
        with open(absolute_path + "datos.json", "r") as json_file:
            data = json.load(json_file)

        print(json.dumps(data, indent=4))

        identificadores_aux = data.get('identificadores', {})
        conexiones_aux = data.get('conexiones', {})
        tag_a_tipo_aux = data.get('tag_a_tipo', {})
        etiquetas_aux = data.get('etiquetas', {})
        coords_aux = data.get('posiciones', {})

        for tag_anterior in identificadores_aux:
            if(tag_a_tipo_aux[tag_anterior] == "led"):
                tag_actual = on_clic_item("led", full_path_LedOFF, on_motion)
            else:
                resize = Image.open(full_path_Boton)
                tag_actual = on_clic_item("boton", full_path_Boton, on_motion, on_hold_boton, on_release_boton)
            canvas.coords(identificadores[tag_actual],coords_aux[tag_anterior][0],coords_aux[tag_anterior][1])
            if(tag_anterior in conexiones_aux):
                conexiones[tag_actual] = conexiones_aux[tag_anterior]
                if(tag_anterior in etiquetas_aux):
                    coords = canvas.coords(identificadores[int(tag_actual)])
                    if coords:

                        etiquetas[tag_actual] = canvas.create_text(coords[0], coords[1] + 30, text="", fill="white", font=("Arial", 10), anchor="n", tags=("etiqueta",))
                        canvas.itemconfig(etiquetas[tag_actual], text="GPIO " + conexiones_aux[tag_anterior])
                        global mostrando_lineas
                        if mostrando_lineas:
                            pin = coordenadas_gpio(conexiones[tag_actual])
                            lineas[tag_actual] = canvas.create_line(coords[0], coords[1]+15, pin[0], pin[1], fill="red", width=2)

                if (conexiones[tag_actual]  in GPIO_usado):
                    GPIO_usado[conexiones[tag_actual] ] += 1
                else:
                    GPIO_usado[conexiones[tag_actual] ] = 1


def cargar_baremetal(event = None):
    global  archivo, qemu_path

    archivo = filedialog.askopenfilename(filetypes=[("Archivos ELF e IMG", "*.elf *.img")],title="Selecciona un kernel (.elf o .img)")

    if  len(archivo) == 0:
        archivo = "" 
    if  len(qemu_path) == 0:
        qemu_path = "" 

    
    if len(archivo) > 0 and os.path.exists(archivo):
        if(len(qemu_path)>0 and os.path.exists(qemu_path)):
           recargar_qemu(False) 
        else:
           print("Kernel cargado, el path a QEMU no se ha asignado aún")
    else:
        print("No existe el path indicado,debes introducir un correcto para poder iniciar o reiniciar")
        archivo = "" 

def cargar_imagen(event = None):
    global  qemu_path, archivo_kernel, archivo_img, archivo_dbt
    archivo_kernel = filedialog.askopenfilename(filetypes=[("Archivos IMG" , "*.img")],title="Selecciona un kernel")

    if  len(archivo_kernel) == 0:
        archivo_kernel = "" 
    if  len(qemu_path) == 0:
        qemu_path = "" 

    if len(archivo_kernel) > 0 and os.path.exists(archivo_kernel):
        archivo_img = filedialog.askopenfilename(filetypes=[("Archivos IMG" , "*.img")],title="Selecciona un SO")
        if  len(archivo_img) == 0:
            archivo_img = "" 

        if len(archivo_img) > 0 and os.path.exists(archivo_img):
            archivo_dbt = filedialog.askopenfilename(filetypes=[("Archivos DTB" , "*.dtb")],title="Selecciona el dtb")
            if  len(archivo_dbt) == 0:
                archivo_dbt = "" 

            if len(archivo_dbt) > 0 and os.path.exists(archivo_dbt):
                if(len(qemu_path)>0 and os.path.exists(qemu_path)):
                    recargar_qemu(True) 
                else:
                    print("Ficheros cargados, el path a QEMU no se ha asignado aún")
            else:
                print("El fichero dtb seleccionado no existe")
        else:
            print("La imagen del SO seleccionado no existe")
    else:
        print("El kernel seleccionado no existe")



def cambiar_path(event = None):
    global  archivo ,qemu_path, archivo_kernel, archivo_img, archivo_dbt

    qemu_path_aux = filedialog.askdirectory( title="Busca tu carpeta de QEMU") # Si no existe se pregunta
    
    if  len(archivo) == 0:
        archivo = "" 
    if  len(qemu_path_aux) == 0:
        qemu_path_aux = "" 
    else:
        qemu_path_aux += aarch64_path

    if(len(qemu_path_aux)>0 and os.path.exists(qemu_path_aux)):
        qemu_path = qemu_path_aux
        guardar_path_qemu(qemu_path)
        if len(archivo) > 0 and os.path.exists(archivo):
            recargar_qemu(False)
        elif len(archivo_kernel) > 0 and os.path.exists(archivo_kernel) and len(archivo_img) > 0 and os.path.exists(archivo_img) and len(archivo_dbt) > 0 and os.path.exists(archivo_dbt):
            recargar_qemu(True)
        else:
            print("No hay kernel o imagen cargada correctamente, clique los iconos para cargar una imagen con dtb o un kernel")
    else:
        print("No existe el path indicado,debes introducir un correcto para poder iniciar o reiniciar, se mantendrá el anterior")


def guardar_path_qemu(qemu_path):
    with open(absolute_path + "/path.cof", "w") as file: #se crea un fichero guardando el path en caso de existir
        file.write(qemu_path)
    print(f"Se ha guardado el path a QEMU en path.cof: {qemu_path}")

def recargar_qemu(Cargar_imagen):
    global vgpio, command_thread, stop, archivo, qemu_path,archivo_kernel,archivo_img,archivo_img, proceso_qemu
    with mutex:

        stop = 1
        command_thread.join()

        subprocess.Popen("pkill qemu-system", shell=True)
        
        vgpio = VGPIOManager()
        stop = 0
        command_thread = threading.Thread(target=command_loop, args=(vgpio,))
        command_thread.start()
        time.sleep(0.05) # esperamos 50ms para que de tiempo abrir el socket de nuevo

        if(Cargar_imagen):
            terminal_command = f'gnome-terminal -x {qemu_path} -M raspi3b  -kernel {archivo_kernel} -sd {archivo_img} -serial stdio -append "rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1" -dtb  {archivo_dbt}'
        else:
            terminal_command = f"gnome-terminal -- bash -c '{qemu_path} -M raspi3b -kernel {archivo} -nographic -qtest unix:/tmp/tmp-gpio.sock; exec bash'"

        proceso_qemu = subprocess.Popen(terminal_command, shell=True) #/home/jose/Escritorio/qemu/build/qemu-system-aarch64  -M raspi3b  -kernel /home/jose/Escritorio/Imagen/kernel8.img -sd /home/jose/Escritorio/Imagen_SO/2022-04-04-raspios-bullseye-armhf-resized.img -serial stdio  -append "rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1" -dtb Imagen/bcm2710-rpi-3-b-plus.dtb
        print (terminal_command)

def cambiar_delay(event = None):

    global pop_delay

    if('pop'in globals()):
        pop.destroy()
        
    pop_delay = Toplevel(root)
    pop_delay.title("Ajustar delay")
    pop_delay.config(bg = "#191818")

    frame = tk.Frame(pop_delay,bg = "#191818")
    frame.pack(pady=10)

     # Create a label
    label = tk.Label(frame, text="Introduce el tiempo de espera entre consultas. Por ejemplo: 0.5",bg = "#191818",fg = "White")
    label.grid(row=0, column=0)
    
    # Create a text box
    global entry_delay
    entry_delay = tk.Entry(frame)
    entry_delay.grid(row=1, column=0)
    
    # Create a label below the text box
    below_label = tk.Label(frame, text="Aceptar",bg = "#191818",fg = "White")
    below_label.grid(row=2, column=0)
    below_label.bind("<Button-1>",lambda event: clic_aceptar_delay())



def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    

def clic_aceptar_delay():
    global entry_delay,delay
    valor = entry_delay.get()
    if(is_float(valor)):
        with mutex_sleep:
            delay = float(valor)
            pop_delay.destroy()


def command_loop(vgpio): # METER MUTEX
    global stop
    while not stop:
        if(len(conexiones) > 0): # Si no hay ninguna conexion no reviso
            with mutex:
                copia_GPIO_usado = GPIO_usado.copy()
                copia_conexiones = conexiones.copy()
                copia_tag_a_tipo = tag_a_tipo.copy()
                copia_estado_leds = estado_leds.copy()
            obtenido = None
            with mutex_gpio:

                if proceso_qemu is not None and proceso_qemu.poll() != None:
                    obtenido = int(vgpio.read_all_gpio().split()[1], 0)
            if obtenido is not None:
                for i in copia_GPIO_usado: # Recorro solo pines con conexion IGUAL SOBRA
                    valor_GPIO = vgpio.get_GPIO_Val(int(i),obtenido) #para un GPIO da su valor

                    for tag in copia_conexiones: # Recorro todas las conexiones
                        if(copia_conexiones[tag] == str(i)): # Comprobando si se conecta al GPIO que he leido
                            if(copia_tag_a_tipo[tag] == "led"):  # Separo comportamiento segun dispositivo
                                if(valor_GPIO != copia_estado_leds[tag]): 
                                    with mutex:
                                        estado_leds[tag] = valor_GPIO
                                    actualiza_led(valor_GPIO,tag)
            with mutex_sleep:
                time.sleep(delay)
        else:
            time.sleep(0.2)


def close():
    subprocess.Popen("pkill qemu-system", shell=True)	
    subprocess.Popen("pkill gnome-terminal", shell=True)
    global stop
    stop = 1
    command_thread.join()
    root.destroy()

def ocultar_mostrar_lineas(event = None):
    with mutex:
        global mostrando_lineas
        if mostrando_lineas:
            mostrando_lineas = False
            aux = lineas.copy()
            for tag in aux:
                canvas.delete(lineas[tag])
                del lineas[tag]
        else:
            mostrando_lineas = True
            for tag in conexiones:
                coords = canvas.coords(identificadores[int(tag)])
                pin = coordenadas_gpio(conexiones[tag])
                lineas[tag] = canvas.create_line(coords[0], coords[1]+15, pin[0], pin[1], fill="red", width=2)
def show_tooltip(event,widget):
    global tooltip
    tooltip = tk.Toplevel(root)
    tooltip.wm_overrideredirect(True)  # Remove window decorations
    tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")  # Position the tooltip near the mouse cursor
    label = tk.Label(tooltip, text=tooltips_text[widget])
    label.pack()

# ---MAIN---
root = tk.Tk()
root.configure(background="#191818")

# Configura el tamaño de la ventana
window_width = 800
window_height = 800
root.geometry(f"{window_width}x{window_height}")

root.grid_columnconfigure(0,weight = 1)
root.grid_columnconfigure(1,minsize=40)
root.grid_rowconfigure(0, weight = 1)

canvas = tk.Canvas(root, bg = "#3A3939",highlightthickness=0)
canvas.grid(row = 0, column = 0, sticky = "nesw")


items = tk.Frame(root, bg="#191818")
items.grid(row=0, column=1, sticky="nsw")

# Coloca raspi
rasp = ImageTk.PhotoImage(file = full_path_Raspi)
raspi_tag = canvas.create_image(250,280,image=rasp,tag="raspi")
canvas.tag_bind(raspi_tag,'<Button-3>', popup_GPIO)
canvas.tag_bind(raspi_tag,'<Enter>', lambda e:show_tooltip(e,"rasp"))
canvas.tag_bind(raspi_tag,"<Leave>", lambda e: tooltip.destroy())

# Coloca led
ledF = ImageTk.PhotoImage(file = full_path_LedOFF)
label = Label(items, image=ledF,background="#191818")
label.bind('<Button-1>', on_clic_led)
label.pack(padx=10, pady=10)
label.bind('<Enter>', lambda e:show_tooltip(e,"led"))
label.bind("<Leave>", lambda e: tooltip.destroy())

# Coloca boton
boton = ImageTk.PhotoImage(file = full_path_Boton)
label_boton = Label(items, image=boton,background="#191818")
label_boton.bind('<Button-1>', on_clic_boton)
label_boton.pack(padx=10, pady=10)
label_boton.bind('<Enter>', lambda e:show_tooltip(e,"boton"))
label_boton.bind("<Leave>", lambda e: tooltip.destroy())
# Coloca Guardado
guardado = ImageTk.PhotoImage(file = full_path_Guarda)
label_guarda = Label(items, image=guardado,background="#191818")
label_guarda.bind('<Button-1>', guardar_estado)
label_guarda.pack(padx=10, pady=10)
label_guarda.bind('<Enter>', lambda e:show_tooltip(e,"guarda"))
label_guarda.bind("<Leave>", lambda e: tooltip.destroy())
# Limpiar
limpia = ImageTk.PhotoImage(file = full_path_limpiar)
label_limpia = Label(items, image=limpia,background="#191818")
label_limpia.pack(padx=10, pady=10)
label_limpia.bind('<Button-1>', delete)
label_limpia.bind('<Enter>', lambda e:show_tooltip(e,"limpia"))
label_limpia.bind("<Leave>", lambda e: tooltip.destroy())
# Reinciar QEMU
reinicio = ImageTk.PhotoImage(file = full_path_recarga)
label_reinicio = Label(items, image=reinicio,background="#191818")
label_reinicio.bind('<Button-1>', reboot)
label_reinicio.pack(padx=10, pady=10)
label_reinicio.bind('<Enter>', lambda e:show_tooltip(e,"qemu"))
label_reinicio.bind("<Leave>", lambda e: tooltip.destroy())

# Cargar lienzo
cargar = ImageTk.PhotoImage(file = full_path_Carga)
boton_cargar = Label(items, image=cargar,background="#191818")
boton_cargar.bind('<Button-1>', cargar_estado)
boton_cargar.pack(padx=10, pady=10)
boton_cargar.bind('<Enter>', lambda e:show_tooltip(e,"carga"))
boton_cargar.bind("<Leave>", lambda e: tooltip.destroy())
# Cargar archivo elf
kernel  = ImageTk.PhotoImage(file = full_path_kernel)
boton_kernel = Label(items, image=kernel,background="#191818")
boton_kernel.bind('<Button-1>', cargar_baremetal)
boton_kernel.pack(padx=10, pady=10)
boton_kernel.bind('<Enter>', lambda e:show_tooltip(e,"elf"))
boton_kernel.bind("<Leave>", lambda e: tooltip.destroy())
# Modificar velocidad consultas
velolcidad  = ImageTk.PhotoImage(file = full_path_velocidad)
boton_velolcidad = Label(items, image=velolcidad,background="#191818")
boton_velolcidad.bind('<Button-1>', cambiar_delay)
boton_velolcidad.pack(padx=10, pady=10)
boton_velolcidad.bind('<Enter>', lambda e:show_tooltip(e,"velocidad"))
boton_velolcidad.bind("<Leave>", lambda e: tooltip.destroy())
# Cambiar path QEMU
qemu  = ImageTk.PhotoImage(file = full_path_qemu)
boton_qemu = Label(items, image=qemu,background="#191818")
boton_qemu.bind('<Button-1>', cambiar_path)
boton_qemu.pack(padx=10, pady=10)
boton_qemu.bind('<Enter>', lambda e:show_tooltip(e,"path"))
boton_qemu.bind("<Leave>", lambda e: tooltip.destroy())
# Cargar imagen

imagen =  ImageTk.PhotoImage(file = full_path_imagen)
boton_imagen = Label(items, image=imagen,background="#191818")
boton_imagen.bind('<Button-1>', cargar_imagen)
boton_imagen.pack(padx=10, pady=10)
boton_imagen.bind('<Enter>', lambda e:show_tooltip(e,"imagen"))
boton_imagen.bind("<Leave>", lambda e: tooltip.destroy())
# Ocultar/mostrar lineas
lineas2 =  ImageTk.PhotoImage(file = full_path_ojo)
boton_lineas = Label(items, image=lineas2,background="#191818")
boton_lineas.bind('<Button-1>', ocultar_mostrar_lineas)
boton_lineas.pack(padx=10, pady=10)
boton_lineas.bind('<Enter>', lambda e:show_tooltip(e,"lineas"))
boton_lineas.bind("<Leave>", lambda e: tooltip.destroy())


if __name__ == "__main__":
    try:
        global vgpio, command_thread

        print('[ ] Virtual GPIO manager')
        print('[ ] Listening for connections')
        vgpio = VGPIOManager()

        command_thread = threading.Thread(target=command_loop, args=(vgpio,))
        command_thread.start()

        if os.path.exists(absolute_path + "/path.cof"):     # Si el archivo path.cof existe, cargar el qemu_path desde allí
            with open(absolute_path + "/path.cof", "r") as file:
                qemu_path = file.read().strip()
            print(f"Cargando qemu_path desde path.cof: {qemu_path}")
        else:
            cambiar_path()

        root.protocol("WM_DELETE_WINDOW", close)

        root.mainloop()
    except:
        print(f"Se ha producido una excepción")
        close()