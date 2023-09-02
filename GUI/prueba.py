#!/usr/bin/env python3
import tkinter as tk

from tkinter import *
from tkinter import filedialog
from tkinter import Button
from PIL import Image, ImageTk
import psutil
import signal
import webbrowser

import re
import os
import os.path
import sys
import pexpect
import time
import threading
import subprocess
import json
import base64

Pin_1 =  [116, 188]
tooltips_text = {
    'lineas': 'Mostrar/ocultar lineas',
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
    'rasp': 'Clic derecho para más información',
    'debug': 'Activa/Desactiva Debug',
    'terminal': 'Abrir terminal de comandos',
    'Play' : 'Play',
    'Stop' : 'Stop'
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



# ---RUTAS FICHEROS---
absolute_path = os.path.dirname(__file__)
relative_path_UI = "IMG/"
aarch64_path = "/build/qemu-system-aarch64"
# ---IMAGENES---
full_path_LedON = os.path.join(absolute_path, relative_path_UI+ "ledON.png") #https://github.com/fritzing/fritzing-parts/blob/develop/svg/core/breadboard/DUO_LED_RG_breadboard.svg
full_path_LedOFF = os.path.join(absolute_path, relative_path_UI + "ledOFF.png")
full_path_Boton = os.path.join(absolute_path, relative_path_UI + "boton.png")
full_path_Raspi = os.path.join(absolute_path, relative_path_UI + "raspi.png") #https://github.com/fritzing/fritzing-parts/blob/develop/svg/core/breadboard/raspberry_pi_3_rev-1.2.svg
full_path_Guarda = os.path.join(absolute_path, relative_path_UI + "guarda.png")
full_path_Carga = os.path.join(absolute_path, relative_path_UI + "import.png")
full_path_kernel = os.path.join(absolute_path, relative_path_UI + "kernel.png")
full_path_limpiar = os.path.join(absolute_path, relative_path_UI + "limpiar.png")
full_path_ojo = os.path.join(absolute_path, relative_path_UI + "ojo.png")
full_path_imagen= os.path.join(absolute_path, relative_path_UI + "OS.png")
full_path_recarga = os.path.join(absolute_path, relative_path_UI + "recarga.png")
full_path_velocidad = os.path.join(absolute_path, relative_path_UI + "velocidad.png")
full_path_qemu = os.path.join(absolute_path, relative_path_UI + "qemu.png")
full_path_debug = os.path.join(absolute_path, relative_path_UI + "debug.png")
full_path_terminal = os.path.join(absolute_path, relative_path_UI + "terminal.png")
full_path_play = os.path.join(absolute_path, relative_path_UI + "play.png")
full_path_stop = os.path.join(absolute_path, relative_path_UI + "stop.png")
# ---DIRECCIONES RASPBERRY PI 3B---
SOCK_PATH="/tmp/tmp-gpio.sock"
GPIO_RANGE=[0x3f200000, 0x3f200fff]
IC_RANGE  =[0x3f00b200, 0x3f00b3ff]

GPIO_SET_OFFSET=0x1c
GPIO_RESET_OFFSET=0x28
GPIO_READ_OFFSET=0x34




#Funciones controlador
def raspi_clic(event):
    global app,gui
    if app.proceso_qemu is not None:
        config_GPIO = app.vgpio.carga_estado_GPIO()
        if config_GPIO == -1:
        	gui.popup_error("No se pudo cargar el estado de los GPIO")
        else:
        	gui.popup_GPIO(config_GPIO,event.x_root ,event.y_root,app.proceso_qemu)
    else:
        gui.popup_error("No hay emulaciones activas")
    

def led_clic(event):
    global app,gui
    id = gui.add_item( full_path_LedOFF,"led")
    app.add_item(id,"led")
    return id


def button_clic(event):
    global app,gui
    id = gui.add_item(full_path_Boton, "boton", button_pressedC, button_releaseC)
    app.add_item(id,"boton")
    return id
def button_pressedC(id):
    global app
    app.button_pressed(id)
def button_releaseC(id):
    global app
    app.button_release(id)
def on_motion(event, id):
    global gui,app
    x = event.x
    y = event.y
    gui.move_item(x,y,id,app.dame_conexiones())
def abrirNavegador(event): 
    webbrowser.open("https://pinout.xyz/pinout/pin27_gpio0#")
def clean_clic(event= None):
    global gui,app
    items = gui.canvas.find_all()
    for id in items:
        if id != 1:
            gui.delete_item(id)
            app.delete_item(id)


def  reboot_clic(event):
    global app
    app.reboot()


def save_clic(event = None):
    global gui,app
    data = {
    "conexiones": app.dame_conexiones(),
    "posiciones": gui.AUX_pos,
    "tag": gui.AUX_tag,
    }
    coord = []
    gui.AUX_tag.clear()
    gui.AUX_pos.clear()
    items = gui.canvas.find_all()
    for id in items:
        coords = gui.canvas.coords(id)
        gui.AUX_pos[id] = coords
        gui.AUX_tag[id] = gui.canvas.itemcget(id, "tags")
    with open(absolute_path + "datos.json", "w") as json_file:
        json.dump(data, json_file)

    print(json.dumps(data, indent=4))

def load_clic(event = None):
    clean_clic()
    try:
        with open(absolute_path + "datos.json", "r") as json_file:
            data = json.load(json_file)

        print(json.dumps(data, indent=4))

        AUX_tag = data.get('tag', {})
        conexiones_aux = data.get('conexiones', {})
        coords_aux = data.get('posiciones', {})

        for id in AUX_tag:
            conexionesAUX = app.dame_conexiones()
            if(AUX_tag[id] == "led"):
                idNuevo = led_clic(None)
                gui.move_item(coords_aux[id][0],coords_aux[id][1],idNuevo,conexionesAUX)
                if(id in conexiones_aux):
                    if app.conect_gpio(conexiones_aux[id],idNuevo):
                        gui.conect_item(idNuevo,conexiones_aux[id])
            elif(AUX_tag[id] == "boton"):
                idNuevo = button_clic(None)
                gui.move_item(coords_aux[id][0],coords_aux[id][1],idNuevo,conexionesAUX)
                if(id in conexiones_aux):
                    if app.conect_gpio(conexiones_aux[id],idNuevo):
                        gui.conect_item(idNuevo,conexiones_aux[id])
    except:
        gui.popup_error("No se encontró un JSON para cargar")
def get_delay():
    global app
    return app.dame_delay()
def get_conexiones():
    global app
    return app.dame_conexiones()
def get_estado_leds():
    global app
    return app.dame_estadoLeds()
def emulacion_activa():
    global app
    return app.emulacion_activa()

def load_baremetal_clic(event):
    global gui,app
    archivo_aux = gui.choose_file("Archivos ELF e IMG","*.elf *.img","Selecciona un kernel (.elf o .img)") 
    if app.load_baremetal_file(archivo_aux) is not True:
    	gui.popup_error("No existe el path indicado")
        
def delay_clic(event):
    global gui,app
    gui.popup_delay()
def clic_aceptar_delay(event):
    global gui,app
    if app.set_delay(gui.entry_delay.get()):
        gui.cierra_popup_delay()
    else:
        gui.popup_error("Intorduce un dígito")
def path_clic(event):
    global gui,app
    ruta = gui.choose_directory()
    if app.set_QEMU_path(ruta) is not True:
    	gui.popup_error("Ruta no válida")
    
def close():
    global app
    app.close()
    gui.close()
def img_clic(event):
    global gui,app
    archivo_kernel_aux = gui.choose_file("Archivos ELF e IMG","*.elf *.img","Selecciona un kernel (.elf o .img)") 
    archivo_img_aux = gui.choose_file("Archivos IMG","*.img","Selecciona una imagen (.img)") 
    archivo_dbt_aux = gui.choose_file("Archivos DTB","*.dtb","Selecciona un archivo DTB (.dtb)") 
    if app.load_img(archivo_kernel_aux,archivo_img_aux,archivo_dbt_aux) is not True:
    	gui.popup_error("No existe el path indicado")

def lines_clic(event):
    global gui,app
    gui.ocultar_mostrar_lineas(app.dame_conexiones())
def debug_clic(event):
    global app
    if not app.debugear():
        gui.popup_error("No hay emulaciones activas")
def terminal_clic(event):
    global gui
    gui.popup_terminal()

def clic_aceptar_terminal(event):
    global gui,app
    if app.emulacion_activa():
        command = gui.entry_terminal.get()   
        gui.entry_terminal.delete(0, tk.END)
        gui.text_box.configure(state='normal')
        gui.text_box.delete("1.0", tk.END)
        gui.text_box.insert('end', app.vgpio.parse(command))
        gui.text_box.configure(state='disabled')
    else: 
        gui.text_box.configure(state='normal')
        gui.text_box.delete("1.0", tk.END)
        gui.text_box.insert('end', "No se pudo conectar con QEMU")
        gui.text_box.configure(state='disabled')
def play_clic():
    global app
    result = app.Play()
    if result == 1:
        gui.popup_error("Ficheros sin cargar para la emulación")
    elif result == 0:
        gui.popup_error("Ruta a QEMU sin cargar")

def stop_clic():
    global app
    app.Stop()

def clic_aceptar(event,id):
    global gui,app
    if app.conect_gpio(gui.entry.get(),id):
        gui.conect_item(id)
        gui.cierra_popup_conexion()
    else:
        gui.popup_error("Introduce un dígito entre 0 y 27")
    
def show_popup(event,id):
    global gui
    gui.popup_conexion(event.x_root,event.y_root,id)
def delete_clic(event,id):
    global gui,app
    gui.delete_item(id)
    app.delete_item(id)
class VGPIOManager(object):
    fd = None
    
    def __init__(self, spath=SOCK_PATH):
        self.load(spath)

    def load(self, spath=SOCK_PATH):
        if os.path.exists(SOCK_PATH):
            os.unlink(SOCK_PATH)

        self.fd = pexpect.spawn("socat - UNIX-LISTEN:{}".format(SOCK_PATH))

    def validate_address(self, address): #PUEDE SER UTIL
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
        aux = self.fd.sendline(s)
        return aux

    def _read(self):
      
      
        self.fd.readline()
        aux = self.fd.readline()

        return aux
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

    def get_gpio_location(self, num):
        if num > 54 or num < 0:
            return 0
        return GPIO_RANGE[0] + int(num / 32)

    def read_ic_area(self):
            v = self.read(IC_RANGE[0], 0x200)
            return v

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

            valor= int(self.readl(GPIO_RANGE[0]).split()[1],0)
            valor2 = int(self.readl(GPIO_RANGE[0] + 0x4).split()[1],0)
            valor3 = int(self.readl(GPIO_RANGE[0] + 0x8).split()[1],0)
            config_GPIO = {}
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
            return config_GPIO

        except:
            return -1

    def toggle(self, gpionum):
        v = self.get(gpionum)
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
        return "Comando no válido, use 'help' para ver los comandos disponibles"

class GUI():
    imagenes_mostradas = {} # Dado el tag te da la imagen
    config_GPIO = {}        # Dado un pin de GPIO dice si es "input" o "output" 
    etiquetas = {}		    # Dado un tag da el ID de canvas de la etiqueta
    AUX_tag = {}		    # Dado un tag da el ID de canvas de la etiqueta
    AUX_pos = {}            # Guarda posiciones antes de realizar un borrado, util para cargar mejor
    lineas = {}
    pop_delay = None
    pop_GPIO = None
    pop_terminal = None
    pop = None
    pop_error = None
    def __init__(self):
        self.numItems = 0
        self.root = tk.Tk()
        self.mostrando_lineas = True
        self.root.configure(background="#191818")
        self.root.bind("<<LedUpdated>>", self.actualiza_led)
        # Configura el tamaño de la ventana
        window_width = 1060
        window_height = 800
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(window_width, window_height)
        self.root.maxsize(window_width, window_height)

        self.root.grid_columnconfigure(0,weight = 1)
        self.root.grid_rowconfigure(0,minsize=40)
        self.root.grid_rowconfigure(1, weight = 1)

        self.canvas = tk.Canvas(self.root, bg = "#3A3939",highlightthickness=0)
        self.canvas.grid(row = 1, column = 0, sticky = "nesw")


        self.items = tk.Frame(self.root, bg="#191818")
        self.items.grid(row=0, column=0, sticky="nsw")

        # Coloca raspi
        self.rasp = ImageTk.PhotoImage(file = full_path_Raspi)
        self.raspi_tag = self.canvas.create_image(250,280,image=self.rasp,tag="raspi")
        self.canvas.tag_bind(self.raspi_tag,'<Button-3>', raspi_clic)
        self.canvas.tag_bind(self.raspi_tag,'<Enter>', lambda e:self.show_tooltip(e,"rasp"))
        self.canvas.tag_bind(self.raspi_tag,"<Leave>", lambda e: self.tooltip_delete())

        # Coloca led
        self.ledF = ImageTk.PhotoImage(file = full_path_LedOFF)
        self.label = Label(self.items, image=self.ledF,background="#191818")
        self.label.bind('<Button-1>', led_clic)
        self.label.grid(row=0, column=0 ,padx=10, pady=10)
        self.label.bind('<Enter>', lambda e:self.show_tooltip(e,"led"))
        self.label.bind("<Leave>", lambda e: self.tooltip_delete())

        # Coloca boton
        self.boton = ImageTk.PhotoImage(file = full_path_Boton)
        self.label_boton = Label(self.items, image=self.boton,background="#191818")
        self.label_boton.bind('<Button-1>', button_clic)
        self.label_boton.grid(row=0, column=1 ,padx=10, pady=10)
        self.label_boton.bind('<Enter>', lambda e:self.show_tooltip(e,"boton"))
        self.label_boton.bind("<Leave>", lambda e: self.tooltip_delete())
        # Coloca Guardado
        self.guardado = ImageTk.PhotoImage(file = full_path_Guarda)
        self.label_guarda = Label(self.items, image=self.guardado,background="#191818")
        self.label_guarda.bind('<Button-1>', save_clic)
        self.label_guarda.grid(row=0, column=2 ,padx=10, pady=10)
        self.label_guarda.bind('<Enter>', lambda e:self.show_tooltip(e,"guarda"))
        self.label_guarda.bind("<Leave>", lambda e: self.tooltip_delete())
        # Limpiar
        self.limpia = ImageTk.PhotoImage(file = full_path_limpiar)
        self.label_limpia = Label(self.items, image=self.limpia,background="#191818")
        self.label_limpia.grid(row=0, column=3 ,padx=10, pady=10)
        self.label_limpia.bind('<Button-1>', clean_clic)
        self.label_limpia.bind('<Enter>', lambda e:self.show_tooltip(e,"limpia"))
        self.label_limpia.bind("<Leave>", lambda e: self.tooltip_delete())
        # Reinciar QEMU
        self.reinicio = ImageTk.PhotoImage(file = full_path_recarga)
        self.label_reinicio = Label(self.items, image=self.reinicio,background="#191818")
        self.label_reinicio.bind('<Button-1>', reboot_clic)
        self.label_reinicio.grid(row=0, column=4 ,padx=10, pady=10)
        self.label_reinicio.bind('<Enter>', lambda e:self.show_tooltip(e,"qemu"))
        self.label_reinicio.bind("<Leave>", lambda e: self.tooltip_delete())

        # Cargar lienzo
        self.cargar = ImageTk.PhotoImage(file = full_path_Carga)
        self.boton_cargar = Label(self.items, image=self.cargar,background="#191818")
        self.boton_cargar.bind('<Button-1>', load_clic)
        self.boton_cargar.grid(row=0, column=5 ,padx=10, pady=10)
        self.boton_cargar.bind('<Enter>', lambda e:self.show_tooltip(e,"carga"))
        self.boton_cargar.bind("<Leave>", lambda e: self.tooltip_delete())
        # Cargar archivo elf
        self.kernel  = ImageTk.PhotoImage(file = full_path_kernel)
        self.boton_kernel = Label(self.items, image=self.kernel,background="#191818")
        self.boton_kernel.bind('<Button-1>', load_baremetal_clic)
        self.boton_kernel.grid(row=0, column=6 ,padx=10, pady=10)
        self.boton_kernel.bind('<Enter>', lambda e:self.show_tooltip(e,"elf"))
        self.boton_kernel.bind("<Leave>", lambda e: self.tooltip_delete())
        # Modificar velocidad consultas
        self.velolcidad  = ImageTk.PhotoImage(file = full_path_velocidad)
        self.boton_velolcidad = Label(self.items, image=self.velolcidad,background="#191818")
        self.boton_velolcidad.bind('<Button-1>', delay_clic)
        self.boton_velolcidad.grid(row=0, column=7 ,padx=10, pady=10)
        self.boton_velolcidad.bind('<Enter>', lambda e:self.show_tooltip(e,"velocidad"))
        self.boton_velolcidad.bind("<Leave>", lambda e: self.tooltip_delete())
        # Cambiar path QEMU
        self.qemu  = ImageTk.PhotoImage(file = full_path_qemu)
        self.boton_qemu = Label(self.items, image=self.qemu,background="#191818")
        self.boton_qemu.bind('<Button-1>', path_clic)
        self.boton_qemu.grid(row=0, column=8 ,padx=10, pady=10)
        self.boton_qemu.bind('<Enter>', lambda e:self.show_tooltip(e,"path"))
        self.boton_qemu.bind("<Leave>", lambda e: self.tooltip_delete())
        # Cargar imagen

        self.imagen =  ImageTk.PhotoImage(file = full_path_imagen)
        self.boton_imagen = Label(self.items, image=self.imagen,background="#191818")
        self.boton_imagen.bind('<Button-1>', img_clic)
        self.boton_imagen.grid(row=0, column=9 ,padx=10, pady=10)
        self.boton_imagen.bind('<Enter>', lambda e:self.show_tooltip(e,"imagen"))
        self.boton_imagen.bind("<Leave>", lambda e: self.tooltip_delete())
        # Ocultar/mostrar lineas
        self.lineas2 =  ImageTk.PhotoImage(file = full_path_ojo)
        self.boton_lineas = Label(self.items, image=self.lineas2,background="#191818")
        self.boton_lineas.bind('<Button-1>', lines_clic)
        self.boton_lineas.grid(row=0, column=10 ,padx=10, pady=10)
        self.boton_lineas.bind('<Enter>', lambda e:self.show_tooltip(e,"lineas"))
        self.boton_lineas.bind("<Leave>", lambda e: self.tooltip_delete())

        # Toogle debug
        self.debug_ico =  ImageTk.PhotoImage(file = full_path_debug)
        self.boton_debug = Label(self.items, image=self.debug_ico,background="#191818")
        self.boton_debug.bind('<Button-1>', debug_clic)
        self.boton_debug.grid(row=0, column=11 ,padx=10, pady=10)
        self.boton_debug.bind('<Enter>', lambda e:self.show_tooltip(e,"debug"))
        self.boton_debug.bind("<Leave>", lambda e: self.tooltip_delete())

        # Terminal
        self.terminal_ico =  ImageTk.PhotoImage(file = full_path_terminal)
        self.boton_terminal = Label(self.items, image=self.terminal_ico,background="#191818")
        self.boton_terminal.bind('<Button-1>', terminal_clic)
        self.boton_terminal.grid(row=0, column=12 ,padx=10, pady=10)
        self.boton_terminal.bind('<Enter>', lambda e:self.show_tooltip(e,"terminal"))
        self.boton_terminal.bind("<Leave>", lambda e: self.tooltip_delete())

        # Toogle play
        self.debug_Play =  ImageTk.PhotoImage(file = full_path_play)
        self.boton_play = Label(self.items, image=self.debug_Play,background="#191818")
        self.boton_play.bind('<Button-1>',lambda event:  play_clic())
        self.boton_play.grid(row=0, column=13 ,padx=10, pady=10)
        self.boton_play.bind('<Enter>', lambda e:self.show_tooltip(e,"Play"))
        self.boton_play.bind("<Leave>", lambda e: self.tooltip_delete())

        # Toogle stop
        self.debug_stop =  ImageTk.PhotoImage(file = full_path_stop)
        self.boton_stop = Label(self.items, image=self.debug_stop,background="#191818")
        self.boton_stop.bind('<Button-1>',lambda event: stop_clic())
        self.boton_stop.grid(row=0, column=14 ,padx=10, pady=10)
        self.boton_stop.bind('<Enter>', lambda e:self.show_tooltip(e,"Stop"))
        self.boton_stop.bind("<Leave>", lambda e:self.tooltip_delete())
        
        self.root.protocol("WM_DELETE_WINDOW", close)
        self.periodical_led_update()
    def close(self):
        self.root.destroy()
    def periodical_led_update(self):
        conexiones = get_conexiones()
        estado_leds = get_estado_leds()
        if len(conexiones) > 0 & emulacion_activa(): 
            items = self.canvas.find_all()
            for id in items:
                tags = self.canvas.itemcget(id, "tags")
                if len(estado_leds) > 0 and id in estado_leds:
                    
                    if tags == "led":
                        
                        if estado_leds[id] == "True":
                            self.actualiza_led(full_path_LedON,id)
                        else:
                            self.actualiza_led(full_path_LedOFF,id)
        delay = get_delay()
        if delay < 0.1: delayAux = 0.1
        else: delayAux = delay
        self.root.after(int(delayAux * 1000), self.periodical_led_update)
    def delete_item(self,id):
      
        self.canvas.delete(id)
        if(id in self.etiquetas):
            self.canvas.delete(self.etiquetas[id])
            del self.etiquetas[id]
        if(id in self.lineas):
            self.canvas.delete(self.lineas[id])
            del self.lineas[id] 

    def add_item(self,imagen,tipo, on_hold_func=None, on_release_func=None):
        x = 50 #+ (elementos % 5) * 100  # 5 es el número máximo de elementos por fila
        y = 50 #+(elementos // 5) * 50 

       
        identificador = self.canvas.create_image(x, y , tags = tipo)
        self.imagenes_mostradas[identificador]  = ImageTk.PhotoImage(file=imagen)
        self.canvas.itemconfig(identificador,image= self.imagenes_mostradas[identificador] )

        self.canvas.tag_bind(identificador, "<B1-Motion>", lambda event: on_motion(event, identificador))
        self.canvas.tag_bind(identificador, "<Button-3>", lambda event: show_popup(event, identificador))
        self.canvas.tag_bind(identificador, "<Button-2>", lambda event: delete_clic(event, identificador))
        if on_hold_func:
           self.canvas.tag_bind(identificador, "<ButtonPress-1>", lambda event: on_hold_func(identificador))
        if on_release_func:
            self.canvas.tag_bind(identificador, "<ButtonRelease-1>", lambda event: on_release_func(identificador))
        self.numItems += 1
        return identificador

    def coordenadas_gpio(self,gpio):
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

    def move_item(self,x,y, id,conexiones):
     
            self.canvas.coords(id,x,y)
            # Actualizar la posición de la etiqueta
            etiqueta = self.etiquetas.get(id)
            if etiqueta is not None:
                etiqueta = self.etiquetas[id]
                self.canvas.coords(etiqueta, x, y + 30)
            linea = self.lineas.get(id)
            if linea is not None:
                linea = self.lineas[id]
                pin = self.coordenadas_gpio(conexiones[id])
                self.canvas.coords(linea, x, y + 15, pin[0], pin[1])

    def conect_item(self, id, gpio = None):
            if gpio==None: text = self.entry.get()
            else : text = gpio
            coords = self.canvas.coords(id)
            if coords:
                if id in self.etiquetas: self.canvas.delete(self.etiquetas[id])
                self.etiquetas[id] = self.canvas.create_text(coords[0], coords[1] + 30, text="", fill="white", font=("Arial", 10), anchor="n", tags=("etiqueta",))
                self.canvas.itemconfig(self.etiquetas[id], text="GPIO " + text)
                if id in self.lineas: self.canvas.delete(self.lineas[id])
            
                if self.mostrando_lineas:
                    pin = self.coordenadas_gpio(text)
                    self.lineas[id] = self.canvas.create_line(coords[0], coords[1]+15,  pin[0], pin[1], fill="red", width=2)
           
    def cierra_popup_error(self):
        if self.pop_error is not None:
            self.pop_error.destroy()
            self.pop_error= None
    def cierra_popup_conexion(self):
        if self.pop is not None:
            self.pop.destroy()
            self.pop= None
    def cierra_popup_terminal(self):
        if self.pop_terminal is not None:
            self.pop_terminal.destroy()
            self.pop_terminal = None
    def cierra_popup_delay(self):
        if self.pop_delay is not None:
            self.pop_delay.destroy()
            self.pop_delay = None
    def cierra_popup_GPIO(self):
        if self.pop_GPIO is not None:
            self.pop_GPIO.destroy()
            self.pop_GPIO = None
    def popup_conexion(self,x,y,id):
        self.cierra_popup_conexion()
        self.pop = Toplevel(self.root)
        self.pop.maxsize(300, 110)
        self.pop.minsize(300, 90)
        self.pop.title("Conexión")
        self.pop.config(bg = "#191818")

        frame = tk.Frame(self.pop,bg = "#191818")
        frame.pack(pady=10)

        # Create a label
        label = tk.Label(frame, text="Conectar al GPIO número:",bg = "#191818",fg="white")
        label.grid(row=0, column=0)
        
        # Create a text box
  
        self.entry = tk.Entry(frame)
        self.entry.grid(row=1, column=0)
        
        # Create a label below the text box
        below_label = tk.Button(frame, text="Aceptar",command=lambda: clic_aceptar(None,id))
        below_label.grid(row=2, column=0,pady=10)


        self.pop.geometry(f"+{x}+{y}")
    def popup_error(self, texto):
        popup_width = 300
        popup_height = 80
        self.cierra_popup_error()
        self.pop_error = Toplevel(self.root)
        self.set_in_middle(self.pop_error,popup_width,popup_height)
        self.pop_error.title("Error")
        self.pop_error.config(bg = "#191818")


        frame = tk.Frame(self.pop_error,bg = "#191818")
        frame.pack(pady=10)

        # Create a label
        label = tk.Label(frame, text=texto,bg = "#191818",fg="white")
        label.grid(row=0, column=0)
        
        # Create a label below the text box
        
        below_label = tk.Button(frame, text="Aceptar",command = self.cierra_popup_error)
        below_label.grid(row=2, column=0)


    def popup_GPIO(self,config_GPIO,x,y,proceso_qemu): #Codigo duplicado!!!!!!!!!!!!!!
            self.cierra_popup_GPIO()

            if proceso_qemu is not None:
                
                self.pop_GPIO = Toplevel(self.root)
                self.pop_GPIO.title("Resumen GPIO")
                self.pop_GPIO.config(bg = "#191818")

                frame = tk.Frame(self.pop_GPIO,bg = "#191818")
                frame.pack(pady=10)
                
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
                                
                        valor = tk.Label(frame, text=str(texto), borderwidth=1, relief="solid", bg = "#191818",fg="white",font=("Helvetica",9))
                        valor.grid(row=0, column=columna, padx=5, pady=5)

                for columna in range(1, 41):
                    if columna % 2 == 0:
                        valor = tk.Label(frame, text=str(columna), borderwidth=1, relief="solid", bg = "#191818",fg="white",font=("Helvetica", 9))
                        valor.grid(row=1, column=columna, padx=5, pady=5)

                for columna in range(1, 41):
                    if columna % 2 != 0:
                        valor = tk.Label(frame, text=str(columna), borderwidth=1, relief="solid", bg = "#191818",fg="white",font=("Helvetica", 9))
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

                        valor = tk.Label(frame, text=str(texto), borderwidth=1, relief="solid", bg = "#191818",fg="white",font=("Helvetica", 9))
                        valor.grid(row=3, column=columna+ 1, padx=5, pady=5)

                valor = tk.Label(frame, text="Para más detalle clicar aquí", borderwidth=1, relief="solid", bg="#191818", fg="blue")
                valor.grid(row=4, column=20, padx=5, pady=5)
                valor.bind("<Button-1>",  abrirNavegador )
                
  
    def actualiza_led(self,imagen,id):  
        self.imagenes_mostradas[id]  = ImageTk.PhotoImage(file=imagen)
        self.canvas.itemconfig(id ,image=self.imagenes_mostradas[id])
   
    def popup_delay(self):

        self.cierra_popup_delay()

        self.pop_delay = Toplevel(self.root)
        self.set_in_middle(self.pop_delay,500,110)
        self.pop_delay.title("Ajustar delay")
        self.pop_delay.config(bg = "#191818")
    
        frame = tk.Frame(self.pop_delay,bg = "#191818")
        frame.pack(pady=10)

        # Create a label
        label = tk.Label(frame, text="Introduce el tiempo de espera entre consultas. Por ejemplo: 0.5",bg = "#191818",fg = "White")
        label.grid(row=0, column=0)
        
        # Create a text box
     
        self.entry_delay = tk.Entry(frame)
        self.entry_delay.grid(row=1, column=0)
        
        # Create a label below the text box
        below_label = tk.Button(frame, text="Aceptar",command=lambda: clic_aceptar_delay(None))
        below_label.grid(row=2, column=0,pady=10)


    def ocultar_mostrar_lineas(self,conexiones):
            
            if self.mostrando_lineas:
                self.mostrando_lineas = False
                aux = self.lineas.copy()
                for id in aux:
                    self.canvas.delete(self.lineas[id])
                    del self.lineas[id]
            else:
                self.mostrando_lineas = True
                for id in conexiones:
                    coords = self.canvas.coords(id)
                    pin = self.coordenadas_gpio(conexiones[id])
                    self.lineas[id] = self.canvas.create_line(coords[0], coords[1]+15, pin[0], pin[1], fill="red", width=2)
    
    def show_tooltip(self,event,widget):
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)  
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=tooltips_text[widget])
        label.pack()
    def set_in_middle(self,popAux,w,h):
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        x = root_x + (root_width - w) // 2
        y = root_y + (root_height - h) // 2
        popAux.geometry('%dx%d+%d+%d' % (w, h, x, y))
        popAux.maxsize(w, h)
        popAux.minsize(w, h)
    def popup_terminal(self):
        self.cierra_popup_terminal()
        self.pop_terminal = tk.Toplevel(self.root)
        self.set_in_middle(self.pop_terminal,700,270)

        self.pop_terminal.title("Terminal")
        self.pop_terminal.config(bg="#191818")

        frame = tk.Frame(self.pop_terminal, bg="#191818")
        frame.pack(pady=10)

        # Crear una etiqueta
        label = tk.Label(frame, text="Introduce comandos para modificar el estado del sistema (usa 'help' para ayuda)", bg="#191818", fg="White")
        label.grid(row=0, column=0, columnspan=2, pady=(0, 10))  # Agregar pady para separación

        # Crear un cuadro de texto fijo
        self.text_box = tk.Text(frame, wrap=tk.WORD, height=10, width=70, bg="#D3D3D3")
        self.text_box.grid(row=1, column=0)
        self.text_box.insert( tk.END ,self.help())
        self.text_box.configure(state='disabled')

        # Crear un widget de entrada para la entrada
        self.entry_terminal = tk.Entry(frame)
        self.entry_terminal.grid(row=2, column=0, pady=20)  # Agregar padx para separación
        self.entry_terminal.bind("<Return>", clic_aceptar_terminal)

       

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
        
    def choose_file(self,text, file_types,title):
        return filedialog.askopenfilename(filetypes=[(text, file_types)],title=title)
    

    def print_terminal(self,texto):
        self.label_comando.config(text = texto)

    def choose_directory(self):
        return filedialog.askdirectory( title="Busca tu carpeta de QEMU")
    def tooltip_delete(self):
        self.tooltip.destroy()
class Aplicacion(): #AL ESCRIBIR EN GPIO POR BOTON COMPROBAR SI ESTA A 1 Y EN ESE CASO NO HACER NADA E INDICAR AL SOLTAR Q ESTABA A 1
    
    def __init__(self):
        self.mutex_sleep = threading.Lock() 
        self.mutex = threading.Lock() 
        self.mutex_gpio = threading.Lock() 
        self.conexiones = {} 	    # Dado el tag dice a que GPIO esta conectado
        self.GPIO_usado = {} 	    # Dice si un GPIO esta asignado TODO:MEJORAR
        self.estado_leds = {} 
        self.proceso_qemu = None
        self.qemu_path = ""
        self.archivo = ""
        self.archivo_kernel = ""
        self.archivo_img = ""
        self.archivo_dbt = ""
        self.debug = False
        self.stop = 0                
        self.delay = 0.1           
        if __name__ == "__main__": 
            try:
                
                self.command_thread = 0
                print('[ ] Virtual GPIO manager')
                print('[ ] Listening for connections')

                if os.path.exists(absolute_path + "/path.cof"):     # Si el archivo path.cof existe, cargar el qemu_path desde allí
                    with open(absolute_path + "/path.cof", "r") as file:
                        self.qemu_path = file.read().strip()
                    print(f"Cargando qemu_path desde path.cof: {self.qemu_path}")
                
            except Exception  as e: 
                print(f"Se ha producido una excepción: " + e) 
                self.close()
    def add_item(self,id,tipo):
        with self.mutex:
            if tipo == 'led': 
                self.estado_leds[id] = "False"

    def dame_delay(self):
        with self.mutex_sleep:
            result = self.delay
        return result
    def emulacion_activa(self):
        with self.mutex:
            result = self.proceso_qemu != None
        return result
    def dame_conexiones(self):
        with self.mutex:
            result = self.conexiones.copy()
        return result
    def dame_estadoLeds(self):
        with self.mutex:
            result = self.estado_leds.copy()
        return result
    def dame_stop(self):
        with self.mutex:
            result = self.stop
        return result
    def delete_item(self,id):
        with self.mutex:
            if(id in self.conexiones and self.conexiones[id]in self.GPIO_usado and self.GPIO_usado[self.conexiones[id]]  == 1):
                del self.GPIO_usado[self.conexiones[id]]
            elif(id in self.conexiones and self.conexiones[id]in self.GPIO_usado):
                self.GPIO_usado[self.conexiones[id]]-=1
            if(id in self.conexiones):	
                del self.conexiones[id]	
            if(id in self.estado_leds):
                del self.estado_leds[id]

    def button_pressed(self,id):
        conexiones= self.dame_conexiones()
        if self.emulacion_activa():
            if(id in conexiones):
                gpio =  conexiones[id]
                with self.mutex_gpio:
                    self.vgpio.set(int(gpio), 1)
                  
    def button_release(self,id):
        conexiones= self.dame_conexiones()
        if self.emulacion_activa():
            if(id in conexiones):
                gpio =  conexiones[id]
                with self.mutex_gpio:
                    self.vgpio.set(int(gpio), 0)
               


    def conect_gpio(self,gpio, id): #Ordenar
        with self.mutex:
             
            if gpio.isdigit() and  int(gpio) < 28:
                if (id in self.conexiones):
                    if (self.GPIO_usado[self.conexiones[id]] == 1):
                        del self.GPIO_usado[self.conexiones[id]]
                    else:
                        self.GPIO_usado[self.conexiones[id]] -= 1
                    del self.conexiones[id]
                    
                self.conexiones[id] = gpio
                if (gpio in self.GPIO_usado):
                    self.GPIO_usado[gpio] += 1
                else:
                    self.GPIO_usado[gpio] = 1
                return True
            else:
                return False
    def reboot(self):
        if self.emulacion_activa():
                self.Play()
    
    def load_baremetal_file(self,archivo_aux):
        if  len(archivo_aux) == 0:
            archivo_aux = "" 
        if  len(self.qemu_path) == 0:
            self.qemu_path = "" 

        if len(archivo_aux) > 0 and os.path.exists(archivo_aux):
            if(len(self.qemu_path)>0 and os.path.exists(self.qemu_path)):
                self.archivo = archivo_aux

                self.archivo_kernel = ""
                self.archivo_img = ""
                self.archivo_dbt = ""
                
            return True
       
            
        return False
        
    def load_img(self,archivo_kernel_aux,archivo_img_aux,archivo_dbt_aux):

        if  len(archivo_kernel_aux) == 0:
            archivo_kernel_aux = "" 
        if  len(self.qemu_path) == 0:
            self.qemu_path = "" 

        if len(archivo_kernel_aux) > 0 and os.path.exists(archivo_kernel_aux):
            if  len(archivo_img_aux) == 0:
                archivo_img_aux = "" 

            if len(archivo_img_aux) > 0 and os.path.exists(archivo_img_aux):
                if  len(archivo_dbt_aux) == 0:
                    archivo_dbt_aux = "" 

                if len(archivo_dbt_aux) > 0 and os.path.exists(archivo_dbt_aux):
                    if(len(self.qemu_path)>0 and os.path.exists(self.qemu_path)):
                        self.archivo_kernel = archivo_kernel_aux
                        self.archivo_img = archivo_img_aux
                        self.archivo_dbt = archivo_dbt_aux
                        self.archivo = ""
               

                    return True

              
        return False

    def set_QEMU_path(self,qemu_path_aux):
        if  len(self.archivo) == 0:
            self.archivo = "" 
        if  len(qemu_path_aux) == 0:
            qemu_path_aux = "" 
        else:
            qemu_path_aux += aarch64_path

        if(len(qemu_path_aux)>0 and os.path.exists(qemu_path_aux)):
            self.qemu_path = qemu_path_aux
            self.guardar_path_qemu(self.qemu_path)
            return True
     
       
        return False

    def guardar_path_qemu(self,qemu_path):
        with open(absolute_path + "/path.cof", "w") as file: #se crea un fichero guardando el path en caso de existir
            file.write(qemu_path)
      	   

    def Play(self):
        if emulacion_activa():
                self.Stop()

        self.terminal_command = None
        if( len(self.qemu_path)>0 and os.path.exists(self.qemu_path)):
            if  len(self.archivo) > 0  and os.path.exists(self.archivo):
                self.terminal_command = f"gnome-terminal -- {self.qemu_path} -M raspi3b  -s -kernel {self.archivo} -nographic -qtest unix:/tmp/tmp-gpio.sock " #-qtest-log /dev/null" descativa log
            elif   len(self.archivo_kernel) > 0 and os.path.exists(self.archivo_kernel) and len(self.archivo_img) > 0 and os.path.exists(self.archivo_img) and len(self.archivo_dbt) > 0 and os.path.exists(self.archivo_dbt):
                self.terminal_command = f'gnome-terminal -- {self.qemu_path} -s -M raspi3b  -kernel {self.archivo_kernel} -sd {self.archivo_img} -serial stdio -append "rw earlyprintk loglevel=8 console=ttyAMA0,115200 dwc_otg.lpm_enable=0 root=/dev/mmcblk0p2 rootdelay=1" -dtb  {self.archivo_dbt} -qtest unix:/tmp/tmp-gpio.sock '
        else:
            return 0
        if(self.terminal_command is not None):
            with self.mutex_gpio:
                self.vgpio = VGPIOManager()

            with self.mutex:
                self.stop = 0
            self.command_thread = threading.Thread(target=self.command_loop)
            self.command_thread.start()

            time.sleep(0.05) # esperamos 50ms para que de tiempo abrir el socket de nuevo
            with self.mutex:
                self.stop = 0
                self.proceso_qemu = subprocess.Popen(self.terminal_command, shell=True) 
            
            print (self.terminal_command)
            return 2
        return 1

    def Stop(self):
        with self.mutex:
            self.stop = 1
   
        if(self.command_thread != 0):
        
            self.command_thread.join()
            self.command_thread = 0
    
        if self.emulacion_activa():
            with self.mutex_gpio:
                self.vgpio.close()
            subprocess.Popen("pkill qemu-system", shell=True)
            with self.mutex:
                self.proceso_qemu = None
        if self.debug:
            self.debugear()
 
    def is_float(self,string):
        try:
            float(string)
            return True
        except ValueError:
            return False
    

    def set_delay(self,valor):
        if(self.is_float(valor)):
            with self.mutex_sleep:
                self.delay = float(valor)
            return True
        return False

        
    def command_loop(self): # METER MUTEX

        while not self.dame_stop():
     
            if(len(self.dame_conexiones()) > 0 and emulacion_activa()): # Si no hay ninguna conexion no reviso
                parse = ""
                obtenido = None
           
                if emulacion_activa():
                    with self.mutex_gpio:
                        parse = self.vgpio.read_all_gpio().split()
                if len(parse) == 2:
                    obtenido = int(parse[1], 0)
                elif emulacion_activa():
                    with self.mutex:
                        self.proceso_qemu.terminate()
                        self.proceso_qemu = None
                if obtenido is not None:
                    with self.mutex:
                        for id in self.conexiones: # Recorro todas las conexiones
                            if(id in self.estado_leds):  # Separo comportamiento segun dispositivo

                                with self.mutex_gpio:
                                    valor_GPIO = self.vgpio.get_GPIO_Val(int(self.conexiones[id]),obtenido) #para un GPIO da su valor
                                self.estado_leds[id] = valor_GPIO
                              
                        
                delayAux = self.dame_delay()
                time.sleep(delayAux)
            else:
                time.sleep(0.2)
              
    
    def close(self):
        if self.emulacion_activa():
            with self.mutex:
                self.stop = 1
            self.command_thread.join()
            subprocess.Popen("pkill qemu-system", shell=True)
            
        if self.debug:
            subprocess.Popen("pkill gnome-terminal", shell=True)
           
        

    def debugear(self):
     
        if(self.debug):
            subprocess.Popen("pkill gdb-multiarch", shell=True)
            self.debug = False	
            return True
        else:
            if self.emulacion_activa():
                if(self.archivo is not None):
                    subprocess.Popen(f' gnome-terminal --   gdb-multiarch {self.archivo}  -ex "target remote localhost:1234"', shell=True)
                    self.debug = True
                elif  self.archivo_kernel is not None:
                    subprocess.Popen(f' gnome-terminal --   gdb-multiarch {self.archivo_kernel}  -ex "target remote localhost:1234"', shell=True)
                    self.debug = True
                return True
            else:
                return False
        
    def clic_aceptar_terminal(self,command):
        with self.mutex_gpio:
            return self.vgpio.parse(command)









global app
app = Aplicacion()

global gui
gui = GUI()

gui.root.mainloop()
