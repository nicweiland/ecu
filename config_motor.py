CONFIG_MOTOR = {
    "cilindros": 4,
    "cilindrada": 2.0,  # litros
    "cilindrada_unitaria": 0.0005,  # m³ por cilindro
    "rpm_minimo": 800,
    "rpm_maximo": 7000,
    "injetor": {
        "vazao": 280,  # cc/min
        "tempo_morto": 1.0,  # ms
        "pressao": 3.0,  # bar
        "densidade_combustivel": 0.789,  # g/cm³ (gasolina)
    },
    "lambda": {
        "min": 0.7,
        "max": 1.3,
        "alvo_padrao": 1.0,
    }
}
