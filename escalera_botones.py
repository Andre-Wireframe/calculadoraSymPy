from machine import Pin, ADC
import time

pin_adc = ADC(Pin(34))

def read_34():
    valor = pin_adc.read()
    
    if 3900 > valor > 3800:
        print("1k")
        
    if 3400 > valor > 3300:
        print("2k")
        
    if 2600 > valor > 2500:
        print("5k")
    
    print(valor)

print("Esperando pulsaciones...")

while True:
    boton = read_34()
    time.sleep(0.2)