import time
import pandas as pd
from config_motor import CONFIG_MOTOR
from ecu_core import ECU
from controle_malha_fechada import GerenciadorControle
from obd_reader import OBDReader

def simular_ecu(duracao_segundos=60, intervalo=0.5, usar_obd=False):
    ecu = ECU(CONFIG_MOTOR)
    controle = GerenciadorControle()
    registros = []
    t_inicio = time.time()
    
    # Inicializa OBD se necessário
    obd_reader = None
    if usar_obd:
        try:
            # Tenta conexão Bluetooth primeiro
            obd_reader = OBDReader(bluetooth=True)
            try:
                obd_reader.connect()
            except ConnectionError:
                print("Tentando conexão USB...")
                obd_reader = OBDReader(bluetooth=False)
                obd_reader.connect()
            
            # Adiciona PIDs customizados se suportados
            supported = obd_reader.get_supported_commands()
            print(f"Comandos suportados: {supported}")
            
            # Inicia leitura contínua dos comandos principais
            main_commands = [obd_reader.commands[x] for x in ['rpm', 'speed', 'throttle']]
            obd_reader.start_continuous(main_commands)
            
        except Exception as e:
            print(f"Erro ao conectar OBD: {e}")
            return
    
    while (time.time() - t_inicio) < duracao_segundos:
        # Verifica pause
        try:
            with open("controle_simulacao.txt", "r") as f:
                if f.read().strip() == "PAUSE":
                    time.sleep(0.1)
                    continue
        except FileNotFoundError:
            pass
            
        t_corrente = time.time() - t_inicio
        
        # Lê dados reais ou simulados
        if usar_obd and obd_reader:
            dados_ecu = obd_reader.read_all_advanced()
        else:
            dados_ecu = ecu.cycle(t_corrente)
        
        # Aplica controles em malha fechada
        correcoes = controle.atualizar(dados_ecu)
        dados_ecu.update(correcoes)
        
        registros.append(dados_ecu)
        
        # Salva log
        df = pd.DataFrame(registros)
        df.to_csv("log_ecu_simulada.csv", index=False)
        
        time.sleep(intervalo)

if __name__ == "__main__":
    print("Iniciando ECU...")
    try:
        simular_ecu(duracao_segundos=600, intervalo=0.5, usar_obd=True)
        print("Simulação finalizada com sucesso.")
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário.")
    except Exception as e:
        print(f"Erro durante a simulação: {e}")
