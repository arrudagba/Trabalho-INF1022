def ligar(namedevice):
    print(namedevice + " ligado!")
    return 1

def desligar(namedevice):
    print(namedevice + " desligado!")
    return 0

def verificar(namedevice):
    # placeholder: real implementation depends on device state tracking
    print(namedevice + " esta desligado.")
    return 0

def alerta(namedevice, msg, var=None):
    print(namedevice + " recebeu o alerta:")
    if var is None:
        print(msg)
    else:
        print(msg + " " + str(var))

def main():
    temperatura = 0
    potencia = 0
    temperatura = 40
    potencia = 90
    if temperatura > 30:
        ligar('ventilador')

if __name__ == "__main__":
    main()
