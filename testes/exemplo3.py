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
