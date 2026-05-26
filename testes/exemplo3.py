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
    movimento = 0
    umidade = 0
    potencia = 0
    potencia = 100
    if umidade < 40:
        alerta('Monitor', 'Ar seco detectado')
    if movimento == True:
        ligar('lampada')
    else:
        desligar('lampada')

if __name__ == "__main__":
    main()
