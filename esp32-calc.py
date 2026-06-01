import urequests as requests
import network
import time

def AP(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=ssid, password=password, authmode=3)

    print('IP del ESP32 (Puerta de enlace):', ap.ifconfig()[0])
    
def wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    wlan.connect("Totalplay-2.4G-0930", "cMPdP3sTdYzEXxux")
    
    print("conectando")
    while not wlan.isconnected():
        print(".")

    print("Wifi conectado")

wifi()

url = "http://192.168.100.117:3030/solve"

def sym(ecuation):
    data = {
        "mode":"sym",
        "ecuation":ecuation
    }
    request = requests.post(url, json=data)
    return request.json()["result"].replace(" ", "")

def derivate(ecuation):
    data = {
        "mode":"derivate",
        "ecuation":ecuation
    }
    request = requests.post(url, json=data)
    return request.json()["result"].replace(" ", "")

def integrate_indef(ecuation):
    data = {
        "mode":"integrate_indef",
        "ecuation":ecuation
    }
    request = requests.post(url, json=data)
    return request.json()["result"]

def integrate_def(ecuation, range):
    data = {
        "mode":"integrate_def",
        "ecuation":ecuation,
        "range":range
    }
    request = requests.post(url, json=data)
    return request.json()["result"].replace(" ", "")

def integrate_doble(ecuation, rangex, rangey):
    data = {
        "mode":"integrate_doble",
        "ecuation":ecuation,
        "rangex":rangex,
        "rangey":rangey
    }
    request = requests.post(url, json=data)
    return request.json()["result"].replace(" ", "")

def grafic(ecuation, rangex, multiplier):
    data = {
        "mode":"grafic",
        "ecuation":ecuation,
        "range":rangex,
        "multiplier":multiplier
    }
    request = requests.post(url, json=data)
    return request.json()["result"]

print(grafic("x^2", [-20, 20], 30))