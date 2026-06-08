from machine import Pin, SPI
import ili9341
from xglcd_font import XglcdFont
import time
import api
import gc

bot_left = Pin(14, Pin.IN, Pin.PULL_UP)
bot_right = Pin(13, Pin.IN, Pin.PULL_UP)
bot_up = Pin(16, Pin.IN, Pin.PULL_UP)
bot_down = Pin(17, Pin.IN, Pin.PULL_UP)
bot_exe = Pin(25, Pin.IN, Pin.PULL_UP)
bot_back = Pin(4, Pin.IN, Pin.PULL_UP)

spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23))

display = ili9341.Display(
    spi,
    cs=Pin(5),
    dc=Pin(27),
    rst=Pin(26),
    width=240, height=320, rotation=0
)

lightgreen = ili9341.color565(73, 255, 112)
aqua = ili9341.color565(0, 255, 255)
greenyellow = ili9341.color565(173, 255, 47)
aquamarine = ili9341.color565(127, 255, 212)
backblue = ili9341.color565(9, 10, 70)
backgreen = ili9341.color565(14, 58, 8)
withe = ili9341.color565(255, 255, 255)
black = ili9341.color565(0, 0, 0)
red = ili9341.color565(255, 0, 0)
gray = ili9341.color565(64, 64, 64)
yellow = ili9341.color565(255, 255, 0)
green = ili9341.color565(0, 255, 0)
orange = ili9341.color565(255, 165, 0)

font_xl = XglcdFont('lib/EspressoDolce18x24.c', 18, 24)
font_xs = XglcdFont("lib/NeatoReduced5x7.c", 5, 7)

columns_pines = [
    Pin(2, Pin.OUT), Pin(13, Pin.OUT), Pin(32, Pin.OUT), Pin(33, Pin.OUT)
]
colums = [33, 32, 13, 2]

rows_pines = [
    Pin(19, Pin.IN, Pin.PULL_DOWN), Pin(14, Pin.IN, Pin.PULL_DOWN), Pin(21, Pin.IN, Pin.PULL_DOWN),
    Pin(22, Pin.IN, Pin.PULL_DOWN), Pin(25, Pin.IN, Pin.PULL_DOWN)
]
rows = [19, 14, 21, 22, 25]

buttons = [
    ["S", "r", "^", "v"],
    ["1", "2", "3", "+"],
    ["4", "5", "r", "6"],
    ["7", "8", "9", "*"],
    ["0", "r", "x", "E"]
]

buttons_s = {
    "1":"sin(", "2":"cos(", "3":"tan(", "+":"!", "5":"log(", "6":"/", "7":"pi", "8":"y",
    "9":"z", "*":"^", "0":"(", "x":")"
}

buttons_a = {
    "1":"sec(", "2":"csc(", "3":"cot(", "6":"root(", "*":"-", "0":".", "x":","    
}
values = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "-", "*", "x")

class Entry:
    def __init__(self, level):
        self.type = "active"
        self.text = ""
        self.idx = len(self.text)
        self.selected = False
        self.level = level
        
    def show(self):
        display.fill_rectangle(11, self.level*26 + 13, 218, 24, backgreen)
        display.draw_rectangle(10, self.level*26 + 12, 220, 26, aqua)
        if self.selected:
            if self.idx >= 17 and len(self.text) >= 17 and self.idx != len(self.text):
                display.draw_text(12,
                                  self.level*26 + 13,
                                  "<" + self.text[self.idx-16:self.idx] + "|" + ">",
                                  font_xl, lightgreen, backblue)
            elif self.idx > 17:
                display.draw_text(12,
                                  self.level*26 + 13,
                                  "<" + self.text[self.idx-17:self.idx] + "|" + self.text[self.idx:17],
                                  font_xl, lightgreen, backblue)
            elif self.idx <= 17 and len(self.text) <= 17:
                display.draw_text(12,
                                  self.level*26 + 13,
                                  self.text[0:self.idx] + "|" + self.text[self.idx:],
                                  font_xl, lightgreen, backblue)
            else:
                display.draw_text(12,
                                  self.level*26 + 13,
                                  self.text[0:self.idx] + "|" + self.text[self.idx:17] + ">",
                                  font_xl, lightgreen, backblue)
        else:
            if len(self.text) > 18:
                display.draw_text(12, self.level*26 + 13, self.text[0:18] + ">", font_xl, lightgreen, backblue)
            else:
                display.draw_text(12, self.level*26 + 13, self.text[0:18], font_xl, lightgreen, backblue)
    
    def write(self, leter):
        self.text = self.text[0:self.idx] + leter + self.text[self.idx:]
        self.idx += 1
        self.show()
        
    def del_leter(self):
        if self.idx != 0:
            print(self.text)
            self.text = self.text[0:self.idx-1] + self.text[self.idx:]
            print(self.text)
            self.idx -= 1
            self.show()
        else:
            return
        
    def select(self):
        self.selected = True
        self.show()
        
    def unselect(self):
        self.selected = False
        self.show()
        
    def clear(self):
        self.text = ""
        
    def get(self):
        return self.text
    
    def set(self, text):
        self.text = text
        self.show()
        
    def scroll(self, value):
        if (self.idx == len(self.text) and value > 0) or (self.idx == 0 and value < 0):
            return
        else:
            self.idx += value
            self.show()
            
class Button:
    def __init__(self, level, text, onclick, color, width = False):
        self.type = "active"
        self.text = text
        self.onclick = onclick
        self.selected = False
        self.level = level
        self.width = width
        self.color = color
        
    def show(self):
        width = len(self.text)*15 + 4 if not self.width else self.width
        display.fill_rectangle(11, self.level*26 + 13, width-2, 24, self.color)
        if self.selected:
            display.draw_rectangle(10, self.level*26 + 12, width, 26, withe)
        else:
            display.draw_rectangle(10, self.level*26 + 12, width, 26, backblue)
        display.draw_text(12, self.level*26 + 13, self.text, font_xl, backblue, self.color)
        
    def select(self):
        self.selected = True
        self.show()
        
    def unselect(self):
        self.selected = False
        self.show()
        
    def click(self):
        self.onclick()
        
class Label:
    def __init__(self, level, text, color):
        self.level = level
        self.text = text
        self.color = color
        self.type = "inactive"
        
    def show(self):
        display.draw_text(12, self.level*26 + 13, self.text, font_xl, self.color, backblue)
        
class Grafic:
    def __init__(self, multiplier, function):
        self.multiplier = multiplier
        self.function = function
        
    def clean(self):
        self.function()
    
    def show(self):
        display.clear(backblue)
        
        Label(0, "Grafica f(x)", yellow).show()
        button = Button(1, "Limpiar Graficas", self.function, aqua, 220)
        button.show()
        button.select()
        midle_w = 110
        midle_h = 128
        
        for c in range(0, 3):
            display.draw_line(11, 64+midle_h+32*(c+1), 228, 64+midle_h+32*(c+1), gray)
            display.draw_text(midle_w+11, 64+midle_h+32*(c+1), f"-{round(32*(c+1)/self.multiplier, 1)}", font_xs, aquamarine)
        
        for c in range(0, 3):
            display.draw_line(11, 192-32*(c+1), 228, 192-32*(c+1), gray)
            display.draw_text(midle_w+11, 192-32*(c+1), f"{round(32*(c+1)/self.multiplier, 1)}", font_xs, aquamarine)
        
        for c in range(0, 2):
            display.draw_line(120-36*(c+1), 64, 120-36*(c+1), 319, gray)
            display.draw_text(120-36*(c+1)-5, midle_h+64, f"-{round(36*(c+1)/self.multiplier, 1)}", font_xs, aquamarine)
            
        for c in range(0, 2):
            display.draw_line(120+36*(c+1), 64, 120+36*(c+1), 319, gray)
            display.draw_text(120+36*(c+1)-5, midle_h+64, f"{round(36*(c+1)/self.multiplier, 1)}", font_xs, aquamarine)
        
        display.draw_rectangle(10, 63, 220, 256, aqua)
        display.draw_line(11, midle_h + 63, 228, midle_h + 63, lightgreen)
        display.draw_line(midle_w + 10, 64, midle_w + 10, 316, lightgreen)
        
    def grafic(self, x_points, y_points, color):
        midle_w = 110
        midle_h = 128
        
        grafic = []
        for c in range(0, len(x_points)):
            x_1 = (midle_w+x_points[c]) + 10
            if x_1 > 10 and x_1 < 230:
               x = x_1
            else:
                continue
            y_1 = (midle_h-y_points[c]) + 64
            if y_1 > 64 and y_1 < 316:
                y = y_1
            else:
                continue
            grafic.append([x, y])
        display.draw_lines(grafic, color)

class Window:
    def __init__(self, elements, background):
        self.background = background
        self.elements = elements
        
        self.active_elements = []
        for c in elements:
            if c.type == "active":
                self.active_elements.append(c)
                
        self.active_element = 0
        
    def add_element(self, element):
        self.elements.append(element)
        
    def get_element(self, element):
        return self.active_elements[element]
    
    def get_active(self):
        return self.active_elements[self.active_element]
    
    def show(self):
        display.clear(self.background)
        
        for c in self.elements:
            c.show()
            
        self.active_elements[self.active_element].select()
            
    def scroll(self, value):
        if not(self.active_element == 0 and value < 0) and not(self.active_element == len(self.active_elements)-1 and value > 0):
            self.active_elements[self.active_element].unselect()
            self.active_element += value
            self.active_elements[self.active_element].select()

class System:
    def __init__(self):
        self.ans = ""
        self.grafics = []
        self.rangex = [-20, 20]
        self.multiplier = "20"
        self.cualiti = "240"
        self.key_mode = "N"
        
        main_menu_items = [
            Label(0, "Calculadora Sym", green),
            Button(2, "Calculo SymPy [+-]", lambda: self.router("sym"), yellow, 220),
            Button(3, "Derivar [d/dx]", lambda: self.router("derivate"), aquamarine, 220),
            Button(4, "Integrar [_/-f(x)", lambda: self.router("integrate_indef"), orange, 220),
            Button(5, "Integrar df [_/-f(x)]", lambda: self.router("integrate_def"), greenyellow, 220),
            Button(6, "Graficar [\_/^\]", lambda: self.router("grafic"), yellow, 220),
            Button(7, "Ver Ploter", lambda: self.solve("view_plot"), aqua, 220),
            Button(8, "Siguiente ------>", lambda: self.router("second"), aqua, 220),
            
            Label(10, "-Andre-Wireframe", aqua)
        ]
        self.main_menu = Window(main_menu_items, backblue)
        self.page = self.main_menu
        
        second_menu_items = [
            Label(0, "Pag. 2", green),
            Button(2, "Solver [x=0]", lambda: self.router("solve"), yellow, 220),
            Button(3, "Factorizar [(x-1)]", lambda: self.router("fact"), aquamarine, 220),
            Button(4, "Integrar do [_/-f(x)", lambda: self.router("integrate_doble"), orange, 220),
            Button(5, "<---- Regresar", lambda: self.router("integrate_def"), greenyellow, 220),
            Button(6, "Sighiente ------->", lambda: self.router("main"), red, 220),
            
            Label(10, "-Andre-Wireframe", aqua)
        ]
        self.second_menu = Window(second_menu_items, backblue)

        sym_items = [
            Label(0, "Calculo Sym", yellow),
            Label(2, "Ecuacion", aqua),
            Entry(3),
            Label(5, "Respuesta", aqua),
            Entry(6),
            Button(8, "Resolver", lambda: self.solve("sym"), yellow, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.sym = Window(sym_items, backblue)
        
        solve_items = [
            Label(0, "Resolver", yellow),
            Label(2, "Ecuacion", aqua),
            Entry(3),
            Label(5, "Respuesta", aqua),
            Entry(6),
            Button(8, "Resolver", lambda: self.solve("solve"), yellow, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.solve_window = Window(solve_items, backblue)
        
        fact_items = [
            Label(0, "Factorizar", yellow),
            Label(2, "Ecuacion", aqua),
            Entry(3),
            Label(5, "Respuesta", aqua),
            Entry(6),
            Button(8, "Resolver", lambda: self.solve("solve"), yellow, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.fact = Window(fact_items, backblue)

        derivate_items = [
            Label(0, "Derivar funcion", yellow),
            Label(2, "Funcion f(x)", aqua),
            Entry(3),
            Label(5, "Respuesta", aqua),
            Entry(6),
            Button(8, "Resolver", lambda: self.solve("derivate"), yellow, 220),
            Button(9, "Graficar d/dx", lambda: self.router("grafic_ans"), orange, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.derivate = Window(derivate_items, backblue)

        integrate_indef_items = [
            Label(0, "Integrar Indefinida", yellow),
            Label(2, "Funcion f(x)", aqua),
            Entry(3),
            Label(5, "Respuesta", aqua),
            Entry(6),
            Button(8, "Resolver", lambda: self.solve("integrate_indef"), yellow, 220),
            Button(9, "Graficar d/dx", lambda: self.router("grafic_ans"), orange, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.integrate_indef = Window(integrate_indef_items, backblue)

        integrate_def_items = [
            Label(0, "Integrar Definida", yellow),
            Label(2, "Funcion", aqua),
            Entry(3),
            Label(4, "Rango X", aqua),
            Entry(5),
            Label(6, "Respuesta", aqua),
            Entry(7),
            Button(8, "Resolver", lambda: self.solve("integrate_def"), yellow, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.integrate_def = Window(integrate_def_items, backblue)
        
        integrate_doble_items = [
            Label(0, "Integrar Doble", yellow),
            Label(1, "Funcion", aqua),
            Entry(2),
            Label(3, "Rango X", aqua),
            Entry(4),
            Label(5, "Rango Y", aqua),
            Entry(6),
            Label(7, "Respuesta", aqua),
            Entry(8),
            Button(9, "Resolver", lambda: self.solve("integrate_doble"), yellow, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.integrate_doble = Window(integrate_doble_items, backblue)
        
        grafic_conf_items = [
            Label(0, "Configuracion", yellow),
            Label(1, "Funcion f(x)", aqua),
            Entry(2),
            Label(3, "Rango X", aqua),
            Entry(4),
            Label(5, "Zoom", aqua),
            Entry(6),
            Label(7, "Calidad", aqua),
            Entry(8),
            Button(9, "Graficar", lambda: self.solve("grafic"), yellow, 220),
            
            Label(10, "-Andre-Wireframe", green)
        ]
        self.grafic_conf = Window(grafic_conf_items, backblue)
        
        self.plotter = Grafic(1, lambda: self.solve("clean_plot"))
        
    def router(self, route):
        if route == "sym":
            self.page = self.sym
            self.sym.show()
            
        elif route == "main":
            self.page = self.main_menu
            self.page.show()
            
        elif route == "second":
            self.page = self.second_menu
            self.page.show()
            
        elif route == "solve":
            self.page = self.solve_window
            self.page.show()
            
        elif route == "fact":
            self.page = self.fact
            self.page.show()
            
        elif route == "derivate":
            self.page = self.derivate
            self.derivate.show()
            
        elif route == "integrate_indef":
            self.page = self.integrate_indef
            self.integrate_indef.show()
            
        elif route == "integrate_def":
            self.page = self.integrate_def
            self.integrate_def.show()
            
        elif route == "integrate_doble":
            self.page = self.integrate_doble
            self.integrate_doble.show()
            
        elif route == "grafic":
            self.page = self.grafic_conf
            self.grafic_conf.show()
            
    def solve(self, route):
        if route == "sym":
            entry = self.sym.get_element(0)
            result_entry = self.sym.get_element(1)
            try:
                request = api.sym(entry.get())
            except:
                request = "error"
            result_entry.set(request)
        
        elif route == "derivate":
            entry = self.derivate.get_element(0)
            result_entry = self.derivate.get_element(1)
            try:
                request = api.derivate(entry.get())
            except:
                request = "error"
            result_entry.set(request)
            
        elif route == "solve":
            entry = self.solve_window.get_element(0)
            result_entry = self.solve_window.get_element(1)
            try:
                request = api.solve_window(entry.get())
            except:
                request = "error"
            result_entry.set(request)
            
        elif route == "fact":
            entry = self.fact.get_element(0)
            result_entry = self.fact.get_element(1)
            try:
                request = api.solve(entry.get())
            except:
                request = "error"
            result_entry.set(request)
        
        elif route == "integrate_indef":
            entry = self.integrate_indef.get_element(0)
            result_entry = self.integrate_indef.get_element(1)
            try:
                request = api.integrate_indef(entry.get())
            except:
                request = "error"
            result_entry.set(request)
            
        elif route == "integrate_def":
            entry = self.integrate_def.get_element(0)
            range_entry = self.integrate_def.get_element(1)
            result_entry = self.integrate_def.get_element(2)
            
            try:
                range = [float(c) for c in range_entry.get().split("/")]
                request = api.integrate_def(entry.get(), range)
            except:
                request = "error"
            result_entry.set(request)
            
        elif route == "integrate_doble":
            entry = self.integrate_doble.get_element(0)
            rangex_entry = self.integrate_doble.get_element(1)
            rangey_entry = self.integrate_doble.get_element(2)
            result_entry = self.integrate_doble.get_element(3)
            
            try:
                rangex = [float(c) for c in rangex_entry.get().split("/")]
                rangey = [float(c) for c in rangey_entry.get().split("/")]
            
                request = api.integrate_doble(entry.get(), rangex, rangey)
            except:
                request = "error"
            result_entry.set(request)
            
        elif route == "grafic":
            entry = self.grafic_conf.get_element(0)
            rangex_entry = self.grafic_conf.get_element(1).get()
            multiplier = self.grafic_conf.get_element(2).get()
            cualiti = self.grafic_conf.get_element(3).get()
            
            try:
                rangex = [float(c) for c in rangex_entry.split("/")]
                
                self.plotter.multiplier = float(multiplier)
                
                self.grafics.append(entry.get())
                self.rangex = rangex
                self.multiplier = multiplier
                self.cualiti = cualiti
                
                self.plotter.show()
            
                points = api.grafic(entry.get(), rangex, float(multiplier), int(cualiti))
                for i,v in enumerate(self.grafics):
                    points = api.grafic(v, rangex, float(multiplier), int(cualiti))
                    if i == 0:
                        self.plotter.grafic(points["x_points"], points["y_points"], red)
                    elif i == 1:
                        self.plotter.grafic(points["x_points"], points["y_points"], yellow)
                    elif i == 2:
                        self.plotter.grafic(points["x_points"], points["y_points"], aqua)
                    elif i == 3:
                        self.plotter.grafic(points["x_points"], points["y_points"], orange)
                    elif i == 4:
                        self.plotter.grafic(points["x_points"], points["y_points"], green)
                    else:
                        self.plotter.grafic(points["x_points"], points["y_points"], red)
                        self.grafics.pop(0)
            except:
                entry.set("error")
                return
                
        elif route == "clean_plot":
            self.grafics = []
            self.plotter.show()
            
        elif route == "view_plot":
            self.page = "grafic"
            self.plotter.show()
            for i,v in enumerate(self.grafics):
                points = api.grafic(v, self.rangex, float(self.multiplier), int(self.cualiti))
                if i == 0:
                    self.plotter.grafic(points["x_points"], points["y_points"], red)
                elif i == 1:
                    self.plotter.grafic(points["x_points"], points["y_points"], yellow)
                elif i == 2:
                    self.plotter.grafic(points["x_points"], points["y_points"], aqua)
                elif i == 3:
                    self.plotter.grafic(points["x_points"], points["y_points"], orange)
                elif i == 4:
                    self.plotter.grafic(points["x_points"], points["y_points"], green)
                else:
                    self.plotter.grafic(points["x_points"], points["y_points"], red)
                    self.grafics.pop(0)
                    
    def buttons_funciton(self, button):
        if button == "S":
            if self.key_mode == "S":
                self.key_mode = "A"
            elif self.key_mode == "A":
                self.key_mode = "N"
            else:
                self.key_mode = "S"
            time.sleep(0.3)
            
        elif button == "v" and self.key_mode == "S":
            try:
                entry = self.page.get_active()
                entry.scroll(1)
                time.sleep(0.15)
            except:
                pass
            
        elif button == "v" and self.key_mode == "A":
            if self.page == self.main_menu:
                    pass
            else:
                self.page = self.main_menu
                self.page.show()
            
        elif button == "^" and self.key_mode == "S":
            try:
                entry = self.page.get_active()
                entry.scroll(-1)
                time.sleep(0.15)
            except:
                pass
            
        elif button == "v":
            try:
                self.page.scroll(1)
                time.sleep(0.15)
            except:
                pass
        
        elif button == "^":
            try:
                self.page.scroll(-1)
                time.sleep(0.15)
            except:
                pass
            
        elif button == "E" and self.key_mode == "S":
            try:
                entry = self.page.get_active()
                entry.write("=")
                time.sleep(0.3)
            except:
                pass
        
        elif button == "E" and self.key_mode == "A":
            try:
                entry = self.page.get_active()
                entry.write(self.ans)
                time.sleep(0.3)
            except:
                pass
        
        elif button == "E":
            if self.page == "grafic":
                self.plotter.clean()
                time.sleep(0.3)
            else:
                try:
                    button = self.page.get_active()
                    button.click()
                    time.sleep(0.3)
                except:
                    pass
                
        elif button == "4" and self.key_mode == "S":
            try:
                entry = self.page.get_active()
                entry.del_leter()
                time.sleep(0.3)
            except:
                pass
                
        elif button in values and self.key_mode == "S":
            try:
                entry = self.page.get_active()
                entry.write(buttons_s[button])
                time.sleep(0.3)
            except:
                pass
            
        elif button in values and self.key_mode == "A":
            try:
                entry = self.page.get_active()
                entry.write(buttons_a[button])
                time.sleep(0.3)
            except:
                pass
        
        elif button in values:
            try:
                entry = self.page.get_active()
                entry.write(button)
                time.sleep(0.3)
            except:
                pass
    
    def loop(self):
        self.main_menu.show()
        while True:
            for c in range(0, len(columns_pines)):
                columns_pines[c].value(1)
                
                for r in range(0, len(rows_pines)):
                    if rows_pines[r].value() == 1:
                        print(buttons[r][c])
                        self.buttons_funciton(buttons[r][c])
                        
                        while rows_pines[r].value == 1:
                            time.sleep_ms(10)
                        
                columns_pines[c].value(0)
                
            time.sleep_ms(20)
        
System().loop()