

 

import ctypes

from ctypes import wintypes

from ctypes import Array, byref, c_char, memset, sizeof,windll

from ctypes import c_int, c_void_p, POINTER

from ctypes import (c_int, windll, byref, create_unicode_buffer,

                   Structure, POINTER, WINFUNCTYPE, sizeof, wintypes, Array, c_char, memset, c_void_p)

from ctypes.wintypes import *

from enum import Enum

import sys

from PIL import Image, ImageTk

import tkinter as tk

from tkinter import ttk, Menu

import time

import json

import os

import subprocess

 

from tkinterdnd2 import TkinterDnD, DND_FILES

 

# For icons from .llnk files:

import win32com.client

import win32con

 

 

# Constants and structures

BI_RGB = 0

DIB_RGB_COLORS = 0

 

CUSTOM_OFFSET = 100

 

class ICONINFO(ctypes.Structure):

    _fields_ = [

        ("fIcon", BOOL),

        ("xHotspot", DWORD),

        ("yHotspot", DWORD),

        ("hbmMask", HBITMAP),

        ("hbmColor", HBITMAP)

    ]

 

class RGBQUAD(ctypes.Structure):

    _fields_ = [

        ("rgbBlue", BYTE),

        ("rgbGreen", BYTE),

        ("rgbRed", BYTE),

        ("rgbReserved", BYTE),

    ]

 

class BITMAPINFOHEADER(ctypes.Structure):

    _fields_ = [

        ("biSize", DWORD),

        ("biWidth", LONG),

        ("biHeight", LONG),

       ("biPlanes", WORD),

        ("biBitCount", WORD),

        ("biCompression", DWORD),

        ("biSizeImage", DWORD),

        ("biXPelsPerMeter", LONG),

        ("biYPelsPerMeter", LONG),

        ("biClrUsed", DWORD),

        ("biClrImportant", DWORD)

    ]

 

class BITMAPINFO(ctypes.Structure):

    _fields_ = [

        ("bmiHeader", BITMAPINFOHEADER),

        ("bmiColors", RGBQUAD * 1),

    ]

 

 

 

class RECT(ctypes.Structure):

    _fields_ = [

        ('left', ctypes.c_long),

        ('top', ctypes.c_long),

        ('right', ctypes.c_long),

        ('bottom', ctypes.c_long)

    ]

 

 

wintypes.RECT = RECT

 

class POINT(ctypes.Structure):

    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

 

class MONITORINFO(ctypes.Structure):

    _fields_ = [

        ('cbSize', ctypes.c_ulong),

        ('rcMonitor', RECT),

        ('rcWork', RECT),

        ('dwFlags', ctypes.c_ulong)

    ]

 

# DLL imports

shell32 = ctypes.WinDLL("shell32", use_last_error=True)

user32 = ctypes.WinDLL("user32", use_last_error=True)

gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

 

# Function prototypes

gdi32.CreateCompatibleDC.argtypes = [HDC]

gdi32.CreateCompatibleDC.restype = HDC

gdi32.GetDIBits.argtypes = [

    HDC, HBITMAP, UINT, UINT, LPVOID, c_void_p, UINT

]

gdi32.GetDIBits.restype = c_int

gdi32.DeleteObject.argtypes = [HGDIOBJ]

gdi32.DeleteObject.restype = BOOL

shell32.ExtractIconExW.argtypes = [

    LPCWSTR, c_int, POINTER(HICON), POINTER(HICON), UINT

]

shell32.ExtractIconExW.restype = UINT

user32.GetIconInfo.argtypes = [HICON, POINTER(ICONINFO)]

user32.GetIconInfo.restype = BOOL

user32.DestroyIcon.argtypes = [HICON]

user32.DestroyIcon.restype = BOOL

 

# Additional functions for window enumeration

EnumWindows = ctypes.windll.user32.EnumWindows

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))

GetWindowText = ctypes.windll.user32.GetWindowTextW

GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW

IsWindowVisible = ctypes.windll.user32.IsWindowVisible

GetWindowLong = ctypes.windll.user32.GetWindowLongW

GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

GetModuleFileNameEx = ctypes.windll.psapi.GetModuleFileNameExW

OpenProcess = ctypes.windll.kernel32.OpenProcess

CloseHandle = ctypes.windll.kernel32.CloseHandle

 

PROCESS_QUERY_INFORMATION = 0x0400

PROCESS_VM_READ = 0x0010

 

MAXCOLS = 10

 

class IconSize(Enum):

    SMALL = 1

    LARGE = 2

 

    @staticmethod

    def to_wh(size: "IconSize") -> tuple[int, int]:

        size_table = {

            IconSize.SMALL: (16, 16),

            IconSize.LARGE: (32, 32)

        }

        return size_table[size]

 

 

 

 

 

 

 

def extract_icon(filename: str, size: IconSize) -> Array[c_char]:

    #print(f"extract_icon from {filename}")

    dc: HDC = gdi32.CreateCompatibleDC(0)

    if dc == 0:

        raise ctypes.WinError()

 

    hicon: HICON = HICON()

    extracted_icons: UINT = shell32.ExtractIconExW(

        filename,

        0,

        byref(hicon) if size == IconSize.LARGE else None,

        byref(hicon) if size == IconSize.SMALL else None,

        1

    )

    if extracted_icons != 1:

        #print(f"ERROR: no icons found in {filename}. {extracted_icons}")

        raise ctypes.WinError()

 

    def cleanup() -> None:

        if icon_info.hbmColor != 0:

            gdi32.DeleteObject(icon_info.hbmColor)

        if icon_info.hbmMask != 0:

            gdi32.DeleteObject(icon_info.hbmMask)

        user32.DestroyIcon(hicon)

 

    icon_info: ICONINFO = ICONINFO(0, 0, 0, 0, 0)

    if not user32.GetIconInfo(hicon, byref(icon_info)):

        cleanup()

        raise ctypes.WinError()

 

    w, h = IconSize.to_wh(size)

    bmi: BITMAPINFO = BITMAPINFO()

    memset(byref(bmi), 0, sizeof(bmi))

    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)

    bmi.bmiHeader.biWidth = w

    bmi.bmiHeader.biHeight = -h

    bmi.bmiHeader.biPlanes = 1

    bmi.bmiHeader.biBitCount = 32

    bmi.bmiHeader.biCompression = BI_RGB

    bmi.bmiHeader.biSizeImage = w * h * 4

    bits = ctypes.create_string_buffer(bmi.bmiHeader.biSizeImage)

    copied_lines = gdi32.GetDIBits(

        dc, icon_info.hbmColor, 0, h, bits, byref(bmi), DIB_RGB_COLORS

    )

    if copied_lines == 0:

        cleanup()

        raise ctypes.WinError()

 

    cleanup()

    return bits

 

def win32_icon_to_image(icon_bits: Array[c_char], size: IconSize) -> Image:

    w, h = IconSize.to_wh(size)

    img = Image.frombytes("RGBA", (w, h), icon_bits, "raw", "BGRA")

    return img

 

def get_window_title(hwnd):

    length = GetWindowTextLength(hwnd)

    buff = ctypes.create_unicode_buffer(length + 1)

    GetWindowText(hwnd, buff, length + 1)

    return buff.value

 

def get_process_path(hwnd):

    process_id = ctypes.c_uint()

    GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

    process_handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, process_id.value)

    if process_handle:

        try:

            buff = ctypes.create_unicode_buffer(wintypes.MAX_PATH)

            if GetModuleFileNameEx(process_handle, None, buff, wintypes.MAX_PATH):

                return buff.value

        finally:

            CloseHandle(process_handle)

    return None

 

class ApplicationIconViewer:

    def __init__(self, root):

        self.root = root

        self.root.title("My appbar")

 

        self.last_screen_check = 0

        self.screen_check_delay = 200  # ms

 

        self.current_screen = 1

        self.screen_info = {}  # Dizionario per memorizzare le info degli schermi

 

        self.is_dragging = False

        self.drag_start_pos = (0, 0)

 

        # Imposta la finestra sempre in primo piano

        self.root.attributes('-topmost', True)

 

        # Crea la barra di stato

        self.create_status_bar()

 

        # Inizializza gli stili

        self.init_styles()

 

 

        # Main container with fixed size

        self.main_frame = tk.Frame(root)

        self.main_frame.pack(fill=tk.BOTH, expand=True)

 

        # Divide the main frame into two panels

        self.left_panel = tk.Frame(self.main_frame, relief='sunken', bg='lightgray')

        self.right_panel = tk.Frame(self.main_frame, relief='sunken', bg='lightgray')

 

        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

 

        # Configure grid weights

        self.main_frame.grid_columnconfigure(0, weight=1)

        self.main_frame.grid_columnconfigure(1, weight=1)

 

 

        # Bind drag and drop events using tkinterdnd2

        self.left_panel.drop_target_register(DND_FILES)

        self.right_panel.drop_target_register(DND_FILES)

 

        self.left_panel.dnd_bind('<<Drop>>', self.on_drop("sinistra"))

        #self.right_panel.dnd_bind('<<Drop>>', self.on_drop("destra"))

 

        # Bind events for visual feedback

        self.left_panel.bind("<Enter>", lambda e: self.on_mouse_enter("sinistra"))

        self.right_panel.bind("<Enter>", lambda e: self.on_mouse_enter("destra"))

 

        self.left_panel.bind("<Leave>", lambda e: self.on_mouse_leave("sinistra"))

        self.right_panel.bind("<Leave>", lambda e: self.on_mouse_leave("destra"))

 

 

####################

       # Inizializza la lista dei pulsanti QuickLaunch

        self.quicklaunch_buttons = []

 

        # Setup drag and drop

        self.setup_drag_drop()

 

 

        self.setup_quicklaunch_frame()

 

        # Carica la configurazione all'avvio

        self.load_quicklaunch_data()

 

        # Variable to store the dragged item

        self.dragged_item = None

 

 

####################

 

 

        # Inizializza il contatore per la posizione nella griglia

        self.grid_position = 0

        # Inizializza la lista dei widget

        self.app_widgets = []

        # Inizializza il dizionario dei frame

        self.app_frames = {}

 

        # Canvas with scrollbar in the right panel

        self.canvas = tk.Canvas(self.right_panel)

        self.scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

 

        self.scrollable_frame.bind(

            "<Configure>",

            lambda e: self.canvas.configure(

                scrollregion=self.canvas.bbox("all")

            )

        )

 

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

 

        # Dizionario per memorizzare gli HWND delle finestre

        self.window_handles = {}

        # Dizionario per memorizzare le associazioni titolo-hwnd

        self.title_to_hwnd = {}

 

        # Layout

        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar.pack(side="right", fill="y")

 

        # Initialize screen info

        self.screen_info = self.get_screen_info()

 

        # Create the menu bar

        self.create_menu_bar()

 

 

 

        # Bind window resize event

        self.root.bind("<Configure>", self.on_window_resize)

        self.root.bind("<Configure>", self.on_screen_change)

 

        # Bind degli eventi di trascinamento

        #self.root.bind("<ButtonPress-1>", self.start_drag)

        #self.root.bind("<B1-Motion>", self.on_drag)

        #self.root.bind("<ButtonRelease-1>", self.stop_drag)

 

        self.prev_active_hwnd_int = 0

 

        # Track application widgets

        self.app_widgets = []

        self.current_columns = 0

 

        # Initial refresh

        self.auto_refresh()

 

        # Forza l'aggiornamento dell'interfaccia

        root.update_idletasks()

 

        # Ora calcola il layout corretto

        self.update_layout()

 

        # Ridimensiona la finestra dopo che tutto e pronto

        root.after(100, self.finalize_window)

 

        self.update_status_info()

 

        self.load_window_position()

 

######################

 

    def setup_drag_drop(self):

        """Configura il drag and drop per i pannelli"""

        self.left_panel.drop_target_register(DND_FILES)

        self.left_panel.dnd_bind('<<Drop>>', self.on_drop("sinistra"))

 

    def setup_quicklaunch_frame(self):

        container_frame = tk.Frame(self.left_panel, bg='lightgray')

        container_frame.pack(fill='both', expand=True, padx=5, pady=5)

 

        self.ql_canvas = tk.Canvas(container_frame, bg='white', highlightthickness=0, height=200)

        self.ql_scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=self.ql_canvas.yview)

        self.ql_scrollable_frame = tk.Frame(self.ql_canvas, bg='white')

 

        self.ql_scrollable_frame.bind(

            "<Configure>",

            lambda e: self.ql_canvas.configure(scrollregion=self.ql_canvas.bbox("all"))

        )

 

        self.ql_canvas.create_window((0, 0), window=self.ql_scrollable_frame, anchor="nw")

        self.ql_canvas.configure(yscrollcommand=self.ql_scrollbar.set)

 

        self.ql_canvas.pack(side="left", fill="both", expand=True)

        self.ql_scrollbar.pack(side="right", fill="y")

 

        self.ql_canvas.bind("<MouseWheel>", self._on_mousewheel)

 

    def _on_mousewheel(self, event):

        self.ql_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

 

    def is_executable(self, file_path):

        """Controlla se il file è eseguibile"""

        try:

            if not os.path.isfile(file_path):

                return False

 

            # Controlla estensioni eseguibili Windows

            executable_extensions = {'.exe', '.bat', '.cmd', '.com', '.msi', '.lnk'}

            _, ext = os.path.splitext(file_path.lower())

            return ext in executable_extensions

        except:

            return False

 

 

 

 

 

    def add_quicklaunch_button(self, button_name, file_path, arg_path, icon_path):

 

        def get_default_icon():

            """Restituisce un'icona predefinita"""

            # Crea un'immagine vuota come icona predefinita

            img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

            return img

 

        def is_directory(path):

            return os.path.isdir(path)

 

        def get_folder_icon():

            # Funzione per ottenere un'icona predefinita per le cartelle

            # Qui puoi implementare la logica per ottenere un'icona di sistema per le cartelle

            # Per ora, restituisce un'immagine vuota

            img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))

            return img

 

        def launch_folder(path):

            # Funzione per aprire una cartella con l'esploratore di file

            subprocess.Popen(['explorer', path])

 

        try:

            # Risolvi il percorso se è un collegamento

            if file_path.endswith('.lnk'):

                file_path = self.get_shortcut_target(file_path)

                file_path = file_path.replace('\\', '/')

 

            if button_name == "":

              app_name = os.path.splitext(os.path.basename(file_path))[0]

            else:

              app_name = button_name

 

 

            if is_directory(file_path):

                img = get_folder_icon()

                command = lambda: launch_folder(file_path)

            else:

                try:

                  icon = extract_icon(file_path, IconSize.SMALL)

                  img = win32_icon_to_image(icon, IconSize.SMALL)

                except:

                  img = get_default_icon()

 

                arg_path2 = arg_path.replace('/', '\\') if 'explorer.exe' in file_path else arg_path

                command = lambda: self.launch_executable(

                    file_path,

                    arg_path2

                )

            img = img.resize((16, 16), Image.LANCZOS)

            photo = ImageTk.PhotoImage(img)

 

            # Crea il pulsante

            button = tk.Button(

                self.ql_scrollable_frame,

                text=app_name,

                image=photo,

                compound=tk.LEFT,

                command=command,

                relief='raised',

                bd=2,

                font=('Arial', 8),

                wraplength=80

            )

            button.image = photo  # Mantieni un riferimento all'immagine

 

            # Calcola la posizione nella griglia (MAXCOLS colonne)

            row = self.grid_position // MAXCOLS

            col = self.grid_position % MAXCOLS

            button.grid(row=row, column=col, padx=5, pady=5)

            self.grid_position += 1

 

 

            # Aggiungi context menu

            self.add_context_menu(button, file_path, arg_path)

 

            # Salva i dati del pulsante (senza l'oggetto Button)

            button_data = {

                'name': app_name,

                'path': file_path,

                'arg_path': arg_path,

                'icon_path' : icon_path,

                'row': row,

                'col': col

            }

            self.quicklaunch_buttons.append(button_data)  # Salva solo i dati, non il pulsante

            self.rearrange_buttons()

            self.save_quicklaunch_data()

 

 

            return button  # Restituisci il pulsante creato se necessario

 

        except Exception as e:

            print(f"Errore nell'aggiungere il pulsante: {e}")

            return None

 

 

    def add_context_menu(self, button, file_path, arg_path):

        """Aggiunge un menu contestuale al pulsante per la rimozione"""

        def show_context_menu(event):

            context_menu = Menu(self.root, tearoff=0)

            # Passa il dizionario dei dati del pulsante, non l'oggetto Button

            button_data = {

                'name': button.cget('text'),

                'path': file_path,

                'arg_path': arg_path,

                'row': self.grid_position // MAXCOLS,

                'col': self.grid_position % MAXCOLS

            }

            context_menu.add_command(label="Rimuovi", command=lambda: self.remove_quicklaunch_button(button_data))

            context_menu.post(event.x_root, event.y_root)

 

        button.bind("<Button-3>", show_context_menu)

 

    def remove_quicklaunch_button(self, button_data):

        """Rimuove un pulsante dalla QuickLaunch"""

        try:

            # Trova e rimuovi il pulsante corrispondente ai dati

            for idx, data in enumerate(self.quicklaunch_buttons):

                if data['name'] == button_data['name'] and data['path'] == button_data['path']:

                    # Rimuovi il pulsante dalla griglia

                    for button in self.ql_scrollable_frame.winfo_children():

                        if isinstance(button, tk.Button) and button.winfo_exists():

                            if button.cget('text') == button_data['name']:

                                button.destroy()

                                break

 

                    # Rimuovi i dati del pulsante dalla lista

                    self.quicklaunch_buttons.pop(idx)

                    #self.grid_position -= 1

                    self.rearrange_buttons()

                    self.save_quicklaunch_data()

                    break

        except Exception as e:

            print(f"Errore nella rimozione del pulsante: {e}")

 

    def rearrange_buttons(self):

        """Riordina i pulsanti nella griglia dopo la rimozione di un pulsante"""

        # Ottieni tutti i pulsanti dal frame scrollabile

        buttons = [widget for widget in self.ql_scrollable_frame.winfo_children() if isinstance(widget, tk.Button)]

 

        # Riordina i pulsanti

        for index, button in enumerate(buttons):

            row = index // MAXCOLS

            col = index % MAXCOLS

            button.grid(row=row, column=col, padx=5, pady=5)

 

 

    def launch_executable(self, executable_path, arg_path=None):

        try:

            # Se è stato fornito un arg_path, lo passiamo come argomento all'eseguibile

            if arg_path:

                print(f"lancio {executable_path} con arg {arg_path}")

                subprocess.Popen([executable_path, arg_path])

            else:

                print(f"lancio  solo {executable_path} ")

                subprocess.Popen(executable_path)

        except Exception as e:

            print(f"Errore nel lancio dell'eseguibile: {e}")

 

 

    def get_shortcut_target(self, lnk_path):

        try:

            import win32com.client

            shell = win32com.client.Dispatch("WScript.Shell")

            shortcut = shell.CreateShortCut(lnk_path)

            return shortcut.Targetpath

        except Exception as e:

            print(f"Errore nel risolvere il collegamento: {e}")

            return lnk_path

 

 

 

    def save_quicklaunch_data(self):

        """Salva la configurazione della QuickLaunch in JSON"""

        try:

            # Salva in file JSON

            config_file = "quicklaunch_config.json"

            with open(config_file, 'w', encoding='utf-8') as f:

                json.dump(self.quicklaunch_buttons, f, indent=2, ensure_ascii=False)

            #print(f"Configurazione QuickLaunch salvata ({len(self.quicklaunch_buttons)} applicazioni)")

        except Exception as e:

            print(f"Errore nel salvataggio della configurazione QuickLaunch: {e}")

 

 

 

 

    def load_quicklaunch_data(self):

        """Carica la configurazione della QuickLaunch dal JSON e ricrea i pulsanti con le icone"""

        try:

            config_file = "quicklaunch_config.json"

 

            # Controlla se il file esiste

            if not os.path.exists(config_file):

                print("File di configurazione QuickLaunch non trovato")

                return

 

            # Pulisci lo stato corrente

            self.quicklaunch_buttons = []

            self.grid_position = 0

 

            # Carica i dati dal file

            with open(config_file, 'r', encoding='utf-8') as f:

                quicklaunch_data = json.load(f)

                #print(f"quicklaunch_data={quicklaunch_data}")

 

            # Ricrea i pulsanti con le icone

            loaded_count = 0

            for data in quicklaunch_data:

                try:

                    button_name = data['name']

                    file_path = data['path']

                    arg_path = "empty"

                    arg_path = data.get('arg_path')  # Usa get per evitare errori se 'arg_path' non esiste

                    icon_path = ""

                    icon_path = data.get('icon_path')  # Usa get per evitare errori se 'arg_path' non esiste

                    #print(f"{file_path}, {arg_path}")

 

                    # Verifica che il file esista ancora

                    if not os.path.exists(file_path):

                        print(f"File non trovato, saltato: {file_path}")

                        #continue   #debug

 

                    # Ricrea il pulsante usando la funzione esistente

                    button = self.add_quicklaunch_button(button_name, file_path, arg_path, icon_path)

                    if button:

                        loaded_count += 1

 

                except Exception as e:

                    print(f"Errore nel caricare il pulsante {data}: {e}")

 

            #print(f"Configurazione QuickLaunch caricata ({loaded_count} applicazioni)")

 

        except Exception as e:

            print(f"Errore nel caricamento della configurazione QuickLaunch: {e}")

 

#############################

 

    def get_screen_info(self):

        """Get information about all available screens"""

        screens = []

 

        try:

            # Define the necessary structures

            class RECT(ctypes.Structure):

                _fields_ = [('left', ctypes.c_long),

                            ('top', ctypes.c_long),

                            ('right', ctypes.c_long),

                            ('bottom', ctypes.c_long)]

 

            # Define the callback function

            def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):

                rect = lprcMonitor.contents

                screens.append({

                    'left': rect.left,

                    'top': rect.top,

                    'right': rect.right,

                    'bottom': rect.bottom,

                    'width': rect.right - rect.left,

                    'height': rect.bottom - rect.top

                })

                return True

 

            # Define the function prototype for the callback

            MONITORENUMPROC = ctypes.WINFUNCTYPE(

                ctypes.c_int,  # Return type

                ctypes.c_void_p,  # HMONITOR hMonitor

                ctypes.c_void_p,  # HDC hdcMonitor

                ctypes.POINTER(RECT),  # LPRECT lprcMonitor

                ctypes.c_double  # LPARAM dwData

            )

 

            # Convert the callback function to the correct type

            callback_func = MONITORENUMPROC(callback)

 

            # Call EnumDisplayMonitors with the correct arguments

            ctypes.windll.user32.EnumDisplayMonitors(None, None, callback_func, 0)

 

        except Exception as e:

            print(f"Error getting screen info: {e}")

 

        return screens

 

 

 

    def position_window_on_screen(self, screen_index):

        """Position the window on the selected screen, setting only x, y, and width, leaving height unchanged"""

        try:

            screens = self.get_screen_info()

            #print(f"screens={screens}")

            #print(f"requested screen={screen_index}")

 

            if screen_index < len(screens):

                screen = screens[screen_index]

                #print(f"screen={screen}")

 

                screen_width = screen['width']

                screen_left = screen['left']

                screen_top = screen['top']

 

                # Get the current height of the window

                current_height = self.root.winfo_height()

 

                #print(f"dim={screen_width},{current_height},{screen_left},{screen_top}")

 

                # Set the window width and position, keeping the current height

                self.root.geometry(f"{screen_width}x{current_height}+{screen_left}+{screen_top + screen['height'] - current_height - 100}")

 

        except Exception as e:

            print(f"Error positioning window: {e}")

 

 

 

    def open_file_with_window(self, file_path, hwnd):

        process_id = wintypes.DWORD()

        windll.user32.GetWindowThreadProcessId(hwnd, byref(process_id))

        h_process = windll.kernel32.OpenProcess(0x0410, False, process_id)

        if h_process:

            try:

                buff = create_unicode_buffer(260)

                if windll.psapi.GetModuleFileNameExW(h_process, None, buff, 260):

                    exe_path = buff.value

                    print(f"Executable path: {exe_path}")

                    print(f"File path: {file_path}")

 

                    # Assicurati che i percorsi siano corretti e non contengano virgolette extra

                    subprocess.Popen([exe_path, file_path], shell=False)

                    return

            finally:

                windll.kernel32.CloseHandle(h_process)

        else:

            print("Failed to open process to get executable path.")

 

 

    def on_mouse_enter(self, side):

        """Gestisce l'evento di quando il mouse entra in un pannello"""

        pass

        #print(f"Mouse entrato nel pannello {side}")

 

    def on_mouse_leave(self, side):

        """Gestisce l'evento di quando il mouse esce da un pannello"""

        pass

        #print(f"Mouse uscito dal pannello {side}")

 

 

#     def on_drop(self, side):

#         """Factory method to handle drop event"""

#         def handle_drop(event):

#             # Ottieni i file rilasciati

#             files = event.data

#             print(f"File rilasciati sul pannello {side}: {files}")

#         return handle_drop

 

    def _on_mousewheel(self, event):

        """Gestisce lo scroll con la rotellina del mouse"""

        self.ql_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

 

 

    def on_drop(self, side):

        """Factory method to handle drop event"""

        def handle_drop(event):

            # Ottieni i file rilasciati

            print(f"FILES:{event.data}")

            dummy = event.data.replace("} {", "MyOwnSeparator890012")  # tkinterdnd2 restituisce una stringa

            dummy = dummy.replace('{', '')

            dummy = dummy.replace('}', '')

            files = dummy.split("MyOwnSeparator890012")  # tkinterdnd2 restituisce una stringa

            print(f"   File rilasciati sul pannello {side}: {files}")

 

            # Se è il pannello sinistro, aggiungi alla QuickLaunch

            if side == "sinistra":

                for file_path in files:

                    print(f"Raw: {file_path}")

                    # Rimuovi le graffe se presenti (tkinterdnd2 può aggiungere {})

                    file_path = file_path.strip('{}').strip('"')

                    #if self.is_executable(file_path):

                    arg_path = "debug"

                    file_name = os.path.basename(file_path)

                    self.add_quicklaunch_button(file_name, file_path, arg_path, file_path) #debug

 

 

        return handle_drop

 

 

 

 

    def on_screen_change(self, event):

        """Rileva quando la finestra viene spostata tra schermi"""

        if event.widget == self.root and not self.is_dragging:

            # Aggiorna solo se non stiamo trascinando

            #self.update_screen_info()   DEBUG

            #print ("(schermo cambiato)")

            pass

 

 

 

    def get_mouse_position(self):

        """Restituisce le coordinate (x,y) del mouse relative allo schermo"""

        try:

            # Struttura per memorizzare la posizione del mouse

            class POINT(ctypes.Structure):

                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

 

            pt = POINT()

            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))

            return pt.x, pt.y

 

        except Exception as e:

            #print(f"Errore rilevamento posizione mouse: {e}")

            # Fallback: restituisci la posizione della finestra

            return self.root.winfo_pointerx(), self.root.winfo_pointery()

 

 

    def create_status_bar(self):

        """Crea la barra di stato in fondo alla finestra"""

        self.status_bar = ttk.Frame(self.root, relief='sunken')

        self.status_bar.pack(side='bottom', fill='x')

 

        # Etichette per le informazioni

        self.status_position = ttk.Label(self.status_bar, text="Pos: (0, 0)", width=15)

        self.status_position.pack(side='left', padx=5)

 

        self.status_size = ttk.Label(self.status_bar, text="Size: 0x0", width=15)

        self.status_size.pack(side='left', padx=5)

 

        self.status_screen = ttk.Label(self.status_bar, text="Screen: 1 (1920x1080)", width=25)

        self.status_screen.pack(side='left', padx=5)

 

        # Pulsante per toggle always on top

        self.toggle_topmost_btn = ttk.Button(

            self.status_bar,

            text="Always on Top: ON",

            command=self.toggle_always_on_top

        )

        self.toggle_topmost_btn.pack(side='right', padx=5)

 

 

 

    def toggle_always_on_top(self):

        """Attiva/disattiva il sempre in primo piano"""

        current_state = self.root.attributes('-topmost')

        new_state = not current_state

        self.root.attributes('-topmost', new_state)

        self.toggle_topmost_btn.config(

            text=f"Always on Top: {'ON' if new_state else 'OFF'}"

        )

 

    def update_screen_info_based_on_window(self):

        """Aggiorna le info basate sulla posizione della finestra"""

        #print("****update_screen_info_based_on_window****\n")

        try:

            x, y = self.root.winfo_x(), self.root.winfo_y()

            screen_num, screen_width, screen_height = self.get_current_screen(x, y)

            #print (f"Schermo {screen_num}: TOP/LEFT ={x}, {y}, screen_width, screen_height ={screen_width}, {screen_height}\n")

 

            # Aggiorna la barra di stato

            self.status_position.config(text=f"Pos: ({x}, {y})")

            self.status_screen.config(text=f"Screen: {screen_width}x{screen_height}")

 

            # Ridimensiona solo se necessario

            if self.root.winfo_width() != screen_width:

                #print ("aggiorno")

                current_height = self.root.winfo_height()

                #self.root.geometry(f"{screen_width}x{current_height}")

 

        except Exception as e:

            print(f"Errore aggiornamento schermo: {e}")

 

 

 

    def update_status_info(self):

        """Aggiorna le informazioni della barra di stato"""

        #print("-")

        try:

            # Posizione della finestra:

            x, y = self.root.winfo_x(), self.root.winfo_y()

            # Dimensioni finestra:

            width, height = self.root.winfo_width(), self.root.winfo_height()

            # Schermo dove si trova la finestra

            screen_num, screen_width, screen_height = self.get_current_screen(x, y)

            #print (f"----------------------------Schermo {screen_num}: WINDOW TOP/LEFT ={x}, {y}, screen_width, screen_height ={screen_width}, {screen_height}--------------------------------\n\n")

 

            # Se stiamo trascinando, usa la logica speciale

            if self.is_dragging:

                print ("DRAGGING")

                self.update_screen_info_based_on_window()

            else:

                #print ("normal")

                # Altrimenti aggiorna solo le info di base

                screen_num, screen_width, screen_height = self.get_current_screen(x, y)

                self.status_position.config(text=f"Pos: ({x}, {y})")

                self.status_size.config(text=f"Size: {width}x{height}")

                self.status_screen.config(text=f"Screen {screen_num}: {screen_width}x{screen_height}")

 

        except Exception as e:

            print(f"Error updating status: {e}")

 

        # Richiama questa funzione ogni 500ms

        self.root.after(500, self.update_status_info)

 

 

 

 

    def get_current_screen(self, x, y):

        """Determina lo schermo corrente basato su coordinate (x,y)"""

        try:

            # Strutture necessarie

            class POINT(ctypes.Structure):

                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

 

            class MONITORINFO(ctypes.Structure):

                _fields_ = [

                    ('cbSize', ctypes.c_ulong),

                    ('rcMonitor', RECT),

                    ('rcWork', RECT),

                    ('dwFlags', ctypes.c_ulong)

                ]

 

            pt = POINT(x, y)

            monitor = ctypes.windll.user32.MonitorFromPoint(pt, 2)  # MONITOR_DEFAULTTONEAREST=2

 

            # Ottieni informazioni sul monitor

            monitor_info = MONITORINFO()

            monitor_info.cbSize = ctypes.sizeof(MONITORINFO)

            ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info))

 

            screen_width = monitor_info.rcMonitor.right - monitor_info.rcMonitor.left

            screen_height = monitor_info.rcMonitor.bottom - monitor_info.rcMonitor.top

 

 

            return monitor, screen_width, screen_height

 

        except Exception as e:

            print(f"Errore rilevamento schermo: {e}")

            return 1, self.root.winfo_screenwidth(), self.root.winfo_screenheight()

 

 

    def create_menu_bar(self):

        """Create the main menu bar"""

        menubar = tk.Menu(self.root)

 

        # Menu File

        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(label="Refresh", command=self.refresh, accelerator="F5")

        file_menu.add_separator()

        file_menu.add_command(label="Save Window Position", command=self.save_window_position, accelerator="Ctrl+S")

        file_menu.add_separator()

        file_menu.add_command(label="Exit", command=self.root.quit)

        menubar.add_cascade(label="File", menu=file_menu)

 

        # Menu View

        view_menu = tk.Menu(menubar, tearoff=0)

        view_menu.add_command(label="Large Icons", command=lambda: self.change_icon_size(IconSize.LARGE))

        view_menu.add_command(label="Small Icons", command=lambda: self.change_icon_size(IconSize.SMALL))

        menubar.add_cascade(label="View", menu=view_menu)

 

        # Menu Position

        position_menu = tk.Menu(menubar, tearoff=0)

        screens = self.get_screen_info()

        for i, screen in enumerate(screens):

            position_menu.add_command(label=f"Screen {i+1}", command=lambda i=i: self.position_window_on_screen(i))

        menubar.add_cascade(label="Position", menu=position_menu)

 

        # Menu Help

        help_menu = tk.Menu(menubar, tearoff=0)

        help_menu.add_command(label="About", command=self.show_about)

        menubar.add_cascade(label="Help", menu=help_menu)

 

        self.root.config(menu=menubar)

 

        # Bind shortcut keys

        self.root.bind("<F5>", lambda e: self.refresh(0))  # DEBUG

        self.root.bind("<Control-s>", lambda e: self.save_window_position())

 

 

 

 

    def save_window_position(self):

        """Salva la posizione e dimensione corrente della finestra"""

        try:

            # Ottieni posizione e dimensioni correnti

            x = self.root.winfo_x()

            y = self.root.winfo_y()

            width = self.root.winfo_width()

            height = self.root.winfo_height()

 

            # Crea dizionario con i dati

            window_data = {

                "x": x,

                "y": y,

                "width": width,

                "height": height

            }

 

            print(f"Salvo: {x},{y},{width},{height}")

            # Salva in file JSON

            config_file = "window_position.json"

            with open(config_file, 'w') as f:

                json.dump(window_data, f, indent=2)

 

            print(f"   Posizione finestra salvata: {x}x{y}, dimensioni: {width}x{height}")

 

 

        except Exception as e:

            print(f"Errore nel salvataggio della posizione: {e}")

 

    def load_window_position(self):

        """Carica e applica la posizione e dimensione salvate"""

        try:

            config_file = "window_position.json"

 

            # Controlla se il file esiste

            if not os.path.exists(config_file):

                print("File di configurazione non trovato, usando posizione predefinita")

                return

 

            # Carica i dati dal file

            with open(config_file, 'r') as f:

                window_data = json.load(f)

 

            # Estrai i valori

            x = window_data.get("x", 100)

            y = window_data.get("y", 100)

            width = window_data.get("width", 800)

            height = window_data.get("height", 600)

            #print(f"Caricato: {x},{y},{width},{height}")

 

            # Applica la geometria

            self.root.geometry(f"{width}x{height}+{x}+{y}")

 

            #print(f"Posizione finestra ripristinata: {x}x{y}, dimensioni: {width}x{height}")

            return height

 

        except Exception as e:

            print(f"Errore nel caricamento della posizione: {e}")

 

    def change_icon_size(self, size):

        """Change icon size (example additional functionality)"""

        self.icon_size = size

        self.refresh(0) # debug

 

    def show_about(self):

        """Show about dialog (example)"""

        tk.messagebox.showinfo("About", "Windows Open Applications Viewer\nVersion 1.0")

 

 

    def auto_refresh(self):

        """Auto-refresh"""

        #print("**AUTOREFRESH**\n\n")

        self.refresh(0)

        self.root.after(100, self.auto_refresh)

 

 

 

    def get_current_screen_index(self, x, y):

        """Determina l'indice dello schermo corrente basato su coordinate (x, y)"""

        try:

            screens = self.get_screen_info()

            for index, screen in enumerate(screens):

                #print(f"  == Schermo {index} ({screen['left']},{screen['top']}) / ({screen['right']},{screen['bottom']}); finestra: {x},{y}")

                if (screen['left'] <= x < screen['right']) and (screen['top'] <= y < screen['bottom']):

                    return index

            return 0  # Default to the first screen if not found

        except Exception as e:

            print(f"Errore nel determinare lo schermo corrente: {e}")

            return 0

 

 

 

 

    def refresh(self, active_hwnd):

        """Refresh the list of open applications only if windows have changed"""

 

        def resizeWindows():

          # Ottieni la posizione della finestra dell'app

          app_x = self.root.winfo_x()

          app_y = self.root.winfo_y()

 

          # Determina l'indice dello schermo su cui si trova la finestra dell'app

          app_screen_index = self.get_current_screen_index(app_x, app_y)

          app_screen = self.get_screen_info()[app_screen_index]

 

          # Lista delle finestre da escludere dal ridimensionamento automatico

          excluded_windows = ["elevenclock", "my appbar", "program manager"]

 

          for title, path, hwnd in current_windows:

              #print(f"{title}")

              try:

                  # Controlla se il titolo della finestra Ã¨ nella lista di esclusione

                  if any(title.lower().startswith(excluded_title.lower()) for excluded_title in excluded_windows):

                      #print(f"Excluding window: {title}")  # Debug print

                      continue

 

                  # Ottieni la posizione attuale della finestra

                  rect = ctypes.wintypes.RECT()

                  ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))

 

                  # Estrai le coordinate della finestra

                  window_x = rect.left

                  window_y = rect.top

                  window_width = rect.right - rect.left

                  window_height = rect.bottom - rect.top

 

                  #Estrae dati schermo

                  screen_y = app_screen["top"]

                  screen_height = app_screen['height']

 

                  # Determina l'indice dello schermo su cui si trova la finestra

                  window_screen_index = self.get_current_screen_index(window_x+8, window_y+8) # Finestre a tutto schermo sono -7,-7 rispetto a coordinate top-left schermo, perche'??

                  #print(f"Finestra {title}:\n    x,y= {window_x},{window_y} --> schermo n. {window_screen_index}\n    Appbar: x,y =  {app_x},{app_y} --> schermo n. {app_screen_index}")

 

                  # Controlla se la finestra si trova sullo stesso schermo dell'app

                  if window_screen_index == app_screen_index:

                      #print(f"      Finestra {title} si trova in schermo dell'app, controllo dimensioni...")

                      # Ottieni l'altezza della finestra dell'app

                      #self.root.update_idletasks()

                      app_height = self.root.winfo_height()

                      if app_height == 1:

                        #print ("RETURN, app window not ready")

                        return # app window not ready

 

                      # Calcola la posizione verticale limite per evitare sovrapposizioni

                      max_allowed_winY = screen_y + screen_height - (app_height + CUSTOM_OFFSET)

                      #print(f"        La barra e' alta {app_height}")

                      #print(f"        Lo schermo e' alto {screen_height} e va da {screen_y} a {screen_y + screen_height}")

                      #print(f"        App alta {window_height} e va da y = {window_y} a {window_y + window_height} rispetto a soglia {max_allowed_winY}")

                      #print(f"        max_allowed_winY = {max_allowed_winY}")

                      # Controlla se la finestra si sovrappone alla finestra dell'app

                      if window_y + window_height > max_allowed_winY:

                          #print(f"         ================       SOVRAPPOSTA! ====================\n\n")

                          # Calcola la nuova altezza della finestra per evitare sovrapposizioni

                          new_window_height = max_allowed_winY - window_y

                          #print(f"      Nuova altezza necessaria: {new_window_height}")

 

 

                          # Define the WINDOWPLACEMENT structure

                          class WINDOWPLACEMENT(ctypes.Structure):

                              _fields_ = [

                                  ("length", wintypes.UINT),

                                  ("flags", wintypes.UINT),

                                  ("showCmd", wintypes.UINT),

                                  ("ptMinPosition", wintypes.POINT),

                                  ("ptMaxPosition", wintypes.POINT),

                                  ("rcNormalPosition", wintypes.RECT)

                              ]

 

                          def is_zoomed(hwnd):

                              """Check if the window is zoomed (maximized)"""

                              placement = WINDOWPLACEMENT()

                              placement.length = ctypes.sizeof(WINDOWPLACEMENT)

                              ctypes.windll.user32.GetWindowPlacement(hwnd, ctypes.byref(placement))

                              return placement.showCmd == ctypes.windll.user32.SW_MAXIMIZE

 

 

                          if new_window_height > 0:

                              # Check if the window is maximized

                              if True: #is_zoomed(hwnd):

                                  #print(f"Finestra {title} e' a tutto schermo, ripristino prima del ridimensionamento.")

                                  # Store the current width

                                  stored_width = window_width

                                  # Restore the window to normal state

                                  ctypes.windll.user32.ShowWindow(hwnd, 9) # RESTORE before resizing

                                  # Wait a bit to ensure the window is restored

                                  self.root.update_idletasks()

 

                                  # Now resize the window

                                  # MoveWindow(handle, x, y, width, height, repaint(bool))

                                  success = ctypes.windll.user32.MoveWindow(

                                      hwnd,

                                      window_x,

                                      window_y,

                                      stored_width,

                                      new_window_height,

                                      True

                                  )

                              else:

                                  #print(f"Ridimensionando finestra: {title} per evitare sovrapposizioni: {window_x},{window_y},{window_width},{new_window_height}")

                                  success = ctypes.windll.user32.MoveWindow(

                                      hwnd,

                                      window_x,

                                      window_y,

                                      window_width,

                                      new_window_height,

                                      True

                                  )

                          else:

                              pass

                              print(f"La finestra {title} non puo' essere ridimensionata senza sovrapporsi completamente.")

                      else:

                        pass

                        #print(f"   OK, {title} non si sovrappone")

              except Exception as e:

                  pass

                  #print(f"Errore nel ridimensionamento della finestra {title}: {e}")

 

 

 

        # Lista per memorizzare le finestre correnti

        current_windows = []

        current_handles = set()

 

        def is_main_window(hwnd):

            #print(f"Finestra: {get_window_title(hwnd)}")

 

            # Controlla se la finestra e' una finestra principale

            if not IsWindowVisible(hwnd):

                #print("   invisible")

                return False

 

            # Controlla se la finestra ha un titolo

            if GetWindowTextLength(hwnd) == 0:

                #print("   no title")

                return False

 

            # Controlla se la finestra e' una finestra di dialogo o una finestra di messaggio

            if ctypes.windll.user32.GetWindow(hwnd, 4) != 0:  # GW_OWNER

               return False

 

            # Controlla se la finestra e' una finestra figlia

            if GetWindowLong(hwnd, -16) & 0x40000000:  # GWL_STYLE e WS_CHILD

                return False

 

            # Controlla lo stile della finestra per assicurarsi che sia una finestra principale

            style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE

            if style & 0x40000000:  # WS_CHILD

                return False

 

            return True

 

 

 

        def enum_windows_proc(hwnd, lParam):

            if IsWindowVisible(hwnd):

                if is_main_window(hwnd):

                    title = get_window_title(hwnd)

                    path = get_process_path(hwnd)

                    current_windows.append((title, path, hwnd))

                    handle_int = ctypes.cast(hwnd, ctypes.c_void_p).value

                    current_handles.add(handle_int)

                    #print(f"Fin '{title}',  handle={hwnd}, act={active_hwnd}, handle_int={handle_int}")

                    #if handle_int == active_hwnd: print ("    ATTIVA")

            return True

 

 

 

 

        current_windows = []

        current_handles = set()

 

        EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

 

        resizeWindows()

 

       # Ottieni l'handle della finestra attiva

        active_hwnd = ctypes.windll.user32.GetForegroundWindow()

        active_hwnd_int = ctypes.cast(active_hwnd, ctypes.c_void_p).value

 

        try:

            # Controlla se e la prima esecuzione

            #print(f"Inizio: current_windows={current_windows}")

            if not hasattr(self, '_last_windows_handles'):

                #print("First refresh, initializing...")

                self._last_windows_handles = set()

                self.app_frames = {}  # Dizionario per tenere traccia dei frame esistenti

 

                # Ora procedi con il refresh vero e proprio

                # Conserva le immagini per prevenire la garbage collection

                self.saved_images = [getattr(widget, 'photo', None) for widget in self.app_widgets]

 

                # Pulisci i widget esistenti

                #print ("### DISTRUGGO ###")

                #for widget in self.app_widgets:

                #    widget.destroy()

                #self.app_widgets = []

                #self.window_handles = {}

                #self.title_to_hwnd = {}

 

                # Create new frames usando la lista current_windows gia ottenuta

                #print("Creo finestre...")

                if  hasattr(self, 'current_windows'):

                  for title, path, hwnd in current_windows:

                      #print(f"   CREO  {title}")

                      try:

                          handle_int = ctypes.cast(hwnd, ctypes.c_void_p).value

                          if handle_int == active_hwnd_int:

                              frame_style = 'Active.TFrame'

                          else:

                              frame_style = 'App.TFrame'

                              # Controlla se il titolo della finestra Ã¨ nella lista di esclusione

                              if any(title.lower().startswith(excluded_title.lower()) for excluded_title in excluded_windows):

                                  #print(f"Excluding window: {title}")  # Debug print

                                  continue

                          self.add_app_frame(title, path, hwnd, frame_style)

                      except Exception as e:

                          pass

                          #print(f"Error creating frame for {title}: {e}")

            else:

              #print("Second exec")

              pass

 

 

 

 

 

            # Controlla se gli handle delle finestre sono gli stessi della volta precedente

            #print("Controllo finestre aperte/chiuse:")

            #print(f"   self._last_windows_handles PRIMA 1 =  {self._last_windows_handles}")

            #print(f"   current_handles                    =  {current_handles}")

 

            closed_handles = set()

            new_handles = set()

 

 

            if hasattr(self, '_last_windows_handles'):

              #print(f"      _last_windows_handles esiste, entro in controllo")

              if self._last_windows_handles == current_handles:

                  #print("          Nessun cambiamento rilevato nelle finestre, vediamo se e' cambiata la finestra attiva:")

                  # Controlla se l'handle della finestra attiva e' cambiato

                  if hasattr(self, 'prev_active_hwnd_int') and self.prev_active_hwnd_int != active_hwnd_int:

                      self.prev_active_hwnd_int = active_hwnd_int

                  # Aggiorna lo stile di tutti i frame

                  for handle_int, frame in self.app_frames.items():

                      if handle_int == active_hwnd_int:

                          frame.configure(style='Active.TFrame')

                      else:

                          frame.configure(style='App.TFrame')

 

                  #if hasattr(self, 'prev_active_hwnd_int') and self.prev_active_hwnd_int != active_hwnd_int:

                  #    self.prev_active_hwnd_int = active_hwnd_int

                  #    print("          SI'")

                  else:

                      self.prev_active_hwnd_int = active_hwnd_int

                      #return

              else:

                  #print("        === Rilevato cambiamento finestre ===")

                  # Se ci sono cambiamenti, aggiorna la lista delle finestre

                  # Gestione delle finestre nuove/chiuse

                  #print(f"    self._last_windows_handles DOPO  =   {self._last_windows_handles}")

                  #print(f"    current_handles PRIMA 2          =   {current_handles}")

                  #print(f"    closed_handles PRIMA 2           =   {closed_handles}")

                  #print(f"    new_handles PRIMA 2              =   {new_handles}")

                  closed_handles = self._last_windows_handles - current_handles

                  new_handles = current_handles - self._last_windows_handles

                  #print(f"    current_handles DOPO             =   {current_handles}")

                  #print(f"    closed_handles DOPO              =   {closed_handles}")

                  #print(f"    new_handles DOPO                 =   {new_handles}")

                  self._last_windows_handles = current_handles.copy()

                  if hasattr(self, 'prev_active_hwnd_int') and self.prev_active_hwnd_int != active_hwnd_int:

                      self.prev_active_hwnd_int = active_hwnd_int

                      #print(f"PULSANTI:{self.app_frames.items}")

                      # Aggiorna lo stile di tutti i frame

                      for handle_int, frame in self.app_frames.items():

                          if handle_int == active_hwnd_int:

                              frame.configure(style='Active.TFrame')

                          else:

                              frame.configure(style='App.TFrame')

            else:

              pass

              #print(f"        _last_windows_handles non ancora disponibile, non faccio controlli")

 

            #print(f"    Controllo terminato.")

 

 

 

 

            # Salva gli handle attuali per il prossimo confronto

            self._last_windows_handles = current_handles.copy()

 

            # Lista delle finestre da escludere dal ridimensionamento automatico

            excluded_windows = ["elevenclock", "my appbar", "program manager"]  # Debug DUPLICATO, farla globale

 

            # Aggiorna i titoli dei frame esistenti

            for title, path, hwnd in current_windows:

                handle_int = ctypes.cast(hwnd, ctypes.c_void_p).value

                if handle_int in self.app_frames:

                    frame = self.app_frames[handle_int]

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label) and hasattr(child, 'is_name_label'):

                            child.configure(text=title[:15])

 

 

 

            # Aggiungi nuovi frame per le nuove finestre

            for title, path, hwnd in current_windows:

                handle_int = ctypes.cast(hwnd, ctypes.c_void_p).value

                if handle_int not in self.app_frames:

                    # Controlla se il titolo della finestra Ã¨ nella lista di esclusione

                    if any(title.lower().startswith(excluded_title.lower()) for excluded_title in excluded_windows):

                        #print(f"Excluding window: {title}")  # Debug print

                        continue

                    frame_style = 'Active.TFrame' if handle_int == active_hwnd_int else 'App.TFrame'

                    self.add_app_frame(title, path, hwnd, frame_style)

 

            # Rimuovi i frame per le finestre chiuse e compatta la griglia

            handles_to_remove = set(self.app_frames.keys()) - current_handles

            for handle_int in handles_to_remove:

                frame = self.app_frames.pop(handle_int)

                frame.destroy()

                self.app_widgets.remove(frame)

 

 

            # Forza l'aggiornamento dell'interfaccia

            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            self.root.update_idletasks()

            self.update_layout()

 

        except Exception as e:

            print(f"Error during refresh: {e}")

        finally:

            # Pulisci le immagini salvate dopo che i nuovi widget sono stati creati

            self.saved_images = None

 

 

 

    def finalize_window(self):

        """Operazioni finali dopo il caricamento completo"""

        # Calcola la larghezza necessaria

        if self.app_widgets:

            widget_width = self.app_widgets[0].winfo_reqwidth()

            cols = max(1, self.root.winfo_screenwidth() // widget_width)

            required_width = cols * widget_width

 

            # Imposta la geometria finale

            self.load_window_position()

            #self.root.geometry(f"{min(required_width, self.root.winfo_screenwidth())}x80+0+0")

 

 

        # Disabilita il ridimensionamento verticale

        #self.root.resizable(True, True)

 

 

 

 

    def _get_current_windows(self):

        """Get the current state of windows for comparison (kept for compatibility)"""

        current_windows = set()

 

        # Enumera tutte le finestre visibili

        def enum_windows_proc(hwnd, lParam):

            if IsWindowVisible(hwnd):

                title = get_window_title(hwnd)

                if title:

                    path = get_process_path(hwnd)

                    if path:

                        current_windows.add((title, path))

            return True

 

        try:

            EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

        except Exception as e:

            print(f"Error enumerating windows: {e}")

 

        return current_windows

 

 

    def _get_current_windows(self):

        """Get the current state of windows for comparison (kept for compatibility)"""

        current_windows = set()

 

        # Enumera tutte le finestre visibili

        def enum_windows_proc(hwnd, lParam):

            if IsWindowVisible(hwnd):

                title = get_window_title(hwnd)

                if title:

                    path = get_process_path(hwnd)

                    if path:

                        current_windows.add((title, path))

            return True

 

        try:

            EnumWindows(EnumWindowsProc(enum_windows_proc), 0)

        except Exception as e:

            print(f"Error enumerating windows: {e}")

 

        return current_windows

 

 

    def on_icon_click(self, event):

        """Handle click on application icon"""

        # Trova quale widget e stato cliccato

        print ("click")

        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        clicked_widget = None

 

        for widget in self.app_widgets:

            if widget.winfo_containing(x, y):

                clicked_widget = widget

                break

        print (f"Cliccato su {clicked_widget}")

        if clicked_widget:

            # Ottieni il titolo dalla label

            for child in clicked_widget.winfo_children():

                if isinstance(child, ttk.Label) and child['image'] == '':

                    title = child['text']

                    print (f"   Nome:{title}")

                    break

 

            if title in self.window_handles:

                hwnd = self.window_handles[title]

                print (f"   Handle:{hwnd}")

 

                # Ripristina la finestra se minimizzata

                #if user32.IsIconic(hwnd):

                user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9

 

                # Porta in primo piano

                user32.SetForegroundWindow(hwnd)

 

 

 

    def init_styles(self):

        """Initialize all custom styles"""

        self.style = ttk.Style()

 

        # Stile base

        self.style.configure('App.TFrame',

                          background='#f0f0f0',

                          borderwidth=1,

                          relief='raised')

 

        # Stile hover

        self.style.configure('Hover.TFrame',

                          background='#e0e0ff',

                          borderwidth=1,

                          relief='raised')

 

        # Stile Mouse

        self.style.configure('Mouse.TFrame',

                          background='#e0e0ff',

                          borderwidth=1,

                          relief='raised')

 

        # Stile pressed

        self.style.configure('Pressed.TFrame',

                          background='#d0d0ff',

                          borderwidth=1,

                          relief='sunken')

 

        # Stile active window

        self.style.configure('Active.TFrame',

                          background='#ffe0e0',

                          borderwidth=3,

                          relief='sunken')

 

        # Stile base per le etichette

        self.style.configure('App.TLabel', background='#f0f0f0')

        self.style.configure('Mouse.TLabel', background='#e0e0ff')

        self.style.configure('Pressed.TLabel', background='#d0d0ff')

        self.style.configure('Active.TLabel', background='#ffe0e0')

 

        # Mappa degli stati (alternativa per hover)

        self.style.map('App.TFrame',

                     background=[('active', '#e0e0ff')],

                     relief=[('pressed', 'sunken')])

 

 

 

 

    def add_app_frame(self, title, path, hwnd, frame_style):

        """Create or update a clickable application frame"""

        #print(f"Aggiungo finestra '{title}'")

        try:

            handle_int = ctypes.cast(hwnd, ctypes.c_void_p).value

 

            # Se il frame esiste gia, aggiornalo invece di crearne uno nuovo

            if hasattr(self, 'app_frames') and handle_int in self.app_frames:

                frame = self.app_frames[handle_int]

 

                # Aggiorna lo stile del frame

                frame.configure(style=frame_style)

 

                # Aggiorna i widget interni

                for child in frame.winfo_children():

                    if isinstance(child, ttk.Label):

                        if hasattr(child, 'is_name_label'):  # e' la label del testo

                            child.configure(text=title[:15])

                        child_style = 'Active.TLabel' if frame_style == 'Active.TFrame' else 'App.TLabel'

                        child.configure(style=child_style)

 

                # Aggiorna l'icona se necessario (potresti aggiungere un controllo per vedere se e cambiata)

                if hasattr(frame, 'photo'):

                    icon = extract_icon(path, IconSize.SMALL)

                    img = win32_icon_to_image(icon, IconSize.SMALL)

                    img = img.resize((16, 16), Image.LANCZOS)

                    frame.photo = ImageTk.PhotoImage(img)

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label) and not hasattr(child, 'is_name_label'):

                            child.configure(image=frame.photo)

 

                return frame

 

 

            # Estrai l'icona solo per i nuovi frame

            icon = extract_icon(path, IconSize.SMALL)

            img = win32_icon_to_image(icon, IconSize.SMALL)

            img = img.resize((16, 16), Image.LANCZOS)

            photo = ImageTk.PhotoImage(img)

 

            # Crea il frame

            frame = ttk.Frame(self.scrollable_frame, style=frame_style, height=30)

            frame.photo = photo

            frame.hwnd = hwnd

 

            # Registra il frame nel dizionario

            if not hasattr(self, 'app_frames'):

                self.app_frames = {}

            self.app_frames[handle_int] = frame

 

            # Configura il drop target

            frame.drop_target_register(DND_FILES)

            frame.dnd_bind('<<Drop>>', lambda e, f=frame: self.on_frame_drop(e, f))

            frame.dnd_bind('<<DragEnter>>', lambda e: frame.configure(style='Hover.TFrame'))

            frame.dnd_bind('<<DragLeave>>', lambda e: frame.configure(style=frame_style))

 

            # Configura il layout del frame

            frame.grid_columnconfigure(0, weight=1)

            frame.grid_columnconfigure(1, weight=1)

 

            # Crea le label per icona e testo

            label_style = 'Active.TLabel' if frame_style == 'Active.TFrame' else 'App.TLabel'

            icon_label = ttk.Label(frame, image=photo, style=label_style)

            icon_label.grid(row=0, column=0, padx=2, pady=2)

 

            name_label = ttk.Label(frame, text=title[:15], width=15, style=label_style)

            name_label.is_name_label = True  # Marcatore per identificare la label del testo

            name_label.grid(row=0, column=1, padx=2, pady=2)

 

 

            def on_enter(event, frame):

                # Memorizza l'handle della finestra attiva al momento dell'entrata del mouse

                frame.active_window_at_enter = user32.GetForegroundWindow()

                #print(f"Memorizzo finestra attiva: {frame.active_window_at_enter}")

 

                # Cambia lo stile del frame e delle etichette quando il mouse entra

                if frame.cget("style") == 'Pressed.TFrame':

                    # Se il pulsante Ã¨ giÃ  premuto, applichiamo uno stile diverso per indicare l'hover

                    frame.configure(style='PressedMouse.TFrame')

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label):

                            child.configure(style='PressedMouse.TLabel')

                else:

                    # Se il pulsante non Ã¨ premuto, applichiamo lo stile normale di hover

                    frame.configure(style='Mouse.TFrame')

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label):

                            child.configure(style='Mouse.TLabel')

 

            def on_leave(event, frame):

                # Ripristina lo stile originale quando il mouse esce

                if frame.cget("style") == 'PressedMouse.TFrame':

                    # Se il pulsante Ã¨ nello stato premuto con hover, lo riportiamo a premuto

                    frame.configure(style='Pressed.TFrame')

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label):

                            child.configure(style='Pressed.TLabel')

                else:

                    # Se il pulsante non Ã¨ premuto, lo riportiamo allo stile originale

                    frame.configure(style=frame.prev_style)

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label):

                            child.configure(style='TLabel')

 

            def on_click(event, frame):

                # Cambia lo stato del pulsante e chiama on_frame_click

                #print(f"Prima la finestra attiva era {frame.active_window_at_enter}")

                if frame.cget("style") == 'Pressed.TFrame' or frame.cget("style") == 'PressedMouse.TFrame':

                    # Se il pulsante Ã¨ premuto, lo riportiamo allo stato non premuto

                    frame.configure(style=frame.prev_style)

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label):

                            child.configure(style='TLabel')

                else:

                    # Se il pulsante non Ã¨ premuto, lo impostiamo come premuto

                    frame.configure(style='Pressed.TFrame')

                    for child in frame.winfo_children():

                        if isinstance(child, ttk.Label):

                            child.configure(style='Pressed.TLabel')

 

                # Chiama la funzione on_frame_click

                self.on_frame_click(frame)

                frame.active_window_at_enter = user32.GetForegroundWindow()

                #print(f"Adesso e': {user32.GetForegroundWindow()}")

 

            # Associa gli eventi al frame

            frame.prev_style = frame.cget("style")  # Memorizza lo stile iniziale del frame

            frame.bind('<Enter>', lambda e, f=frame: on_enter(e, f))

            frame.bind('<Leave>', lambda e, f=frame: on_leave(e, f))

            frame.bind('<Button-1>', lambda e, f=frame: on_click(e, f))

 

            # Associa gli eventi alle etichette

            for child in [icon_label, name_label]:

                child.bind('<Enter>', lambda e, f=frame: on_enter(e, f))

                child.bind('<Button-1>', lambda e, f=frame: on_click(e, f))

 

 

 

 

 

            # Aggiungi il frame all'interfaccia nella posizione corretta

            row = self.grid_position // 3

            column = self.grid_position % 3

            #print(f"agiungo in row,col = {row},{column}")

            frame.grid(row=row, column=column, padx=5, pady=5)

            self.app_widgets.append(frame)

 

            # Incrementa la posizione nella griglia

            self.grid_position += 1

 

       except Exception as e:

            #print(f"Error creating/updating frame for {title}: {e}")

            return None

 

 

    def on_frame_click(self, frame):

        """Handle click on application frame"""

        #print(f"Clicked on frame with hwnd: {ctypes.cast(frame.hwnd, ctypes.c_void_p).value}")

        try:

            # Ottieni l'handle della finestra attiva al momento dell'entrata del mouse

            active_window_at_enter = getattr(frame, 'active_window_at_enter', None)

 

            # Controlla se la finestra e'  iconizzata (minimizzata)

            if user32.IsIconic(frame.hwnd):

                #print("La finestra e'  iconizzata, ripristino")

                user32.ShowWindow(frame.hwnd, 9)  # SW_RESTORE

                user32.SetForegroundWindow(frame.hwnd)

                return "activated"

 

            # Controlla se la finestra e'  visibile ma non attiva

            #print(f" Controlla se la finestra e'  visibile ma non attiva: {active_window_at_enter} vs {ctypes.cast(frame.hwnd, ctypes.c_void_p).value}")

            if user32.IsWindowVisible(frame.hwnd):

                if active_window_at_enter != ctypes.cast(frame.hwnd, ctypes.c_void_p).value:

                    #print("La finestra e'  visibile ma non attiva, attivo")

                    user32.SetForegroundWindow(frame.hwnd)

                    return "activated"

                else:

                    #print("La finestra e'  attiva, minimizzo")

                    user32.ShowWindow(frame.hwnd, 6)  # SW_MINIMIZE

                    return "iconized"

            else:

                #print("La finestra non e'  visibile, attivo")

                user32.SetForegroundWindow(frame.hwnd)

                return "activated"

 

        except Exception as e:

            print(f"Error toggling window: {e}")

            return "error"

 

    def on_frame_drop(self, event, frame):

        """Handle drop event on a specific frame"""

        files = event.data.strip('{}')

        #print(f"RAW FILES: {files}")

        self.open_file_with_window(files, frame.hwnd)

        #print(f"File dropped on frame with hwnd {frame.hwnd}: {files}")

 

 

 

    def bring_window_to_front(self, hwnd):

        """Toggle window visibility"""

        #print (f"TEST: {user32.IsWindowVisible(hwnd), user32.IsIconic(hwnd)}")

        try:

            user32.SetForegroundWindow(hwnd)

            user32.ShowWindow(hwnd, 1)

 

        except Exception as e:

            print(f"Error toggling window: {e}")

 

 

 

    def update_layout(self):

        """Improved layout distribution"""

        #print("Update layout")

        if not hasattr(self, 'app_widgets') or not self.app_widgets:

            #print(">>>>>>>>>>>>>>>>Non aggiorno proprio niente, non ci sono widget...")

            return

 

        canvas_width = self.canvas.winfo_width()

        if not canvas_width:

            return

 

        # Assicurati che ci siano widget validi

        valid_widgets = [widget for widget in self.app_widgets if widget.winfo_exists()]

        if not valid_widgets:

            return

 

        widget_width = valid_widgets[0].winfo_reqwidth()

        columns = max(1, canvas_width // (widget_width + 4))  # +4 for padding

 

        for i, widget in enumerate(valid_widgets):

            if widget.winfo_exists():

                row, col = divmod(i, columns)

                widget.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

 

        # Configure uniform column weights

        for col in range(columns):

            self.scrollable_frame.grid_columnconfigure(col, weight=1, uniform="apps")

 

 

 

    def on_window_resize(self, event):

        """Handle window resize events"""

        print("Resize")

        if event.widget == self.root:

            self.update_layout()

 

 

    def start_drag(self, event):

        """Inizia il trascinamento della finestra"""

        print ("STARTdrag")

        if event.widget == self.root:  # Solo se clicchi sulla finestra principale

            self.is_dragging = True

            self.drag_start_pos = (event.x_root, event.y_root)

 

    def on_drag(self, event):

        """Gestisce il trascinamento della finestra"""

        print ("ondrag")

        if self.is_dragging:

            x, y = event.x_root, event.y_root

            # Calcola lo spostamento (opzionale, per logica aggiuntiva)

            dx = x - self.drag_start_pos[0]

            dy = y - self.drag_start_pos[1]

            self.drag_start_pos = (x, y)

 

            # Aggiorna le info dello schermo durante il trascinamento

            self.update_screen_info_based_on_window()

 

    def stop_drag(self, event):

        """Termina il trascinamento"""

        print ("STOPdrag")

        self.is_dragging = False

 

 

 

if __name__ == "__main__":

    root = TkinterDnD.Tk()

 

 

    def on_closing():

        """Funzione da eseguire prima della chiusura dell'applicazione."""

        print("Esecuzione di operazioni prima della chiusura...")

        app.save_window_position()

        root.destroy()

 

    # Associa la funzione on_closing all'evento di chiusura della finestra

    root.protocol("WM_DELETE_WINDOW", on_closing)

 

    app = ApplicationIconViewer(root)

    root.mainloop()
