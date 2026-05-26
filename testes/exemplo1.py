def ligar(namedevice):
    print(namedevice + " ligado!")

def desligar(namedevice):
    print(namedevice + " desligado!")

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
