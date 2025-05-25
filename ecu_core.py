from sensores import SensorManager
from controle_malha_fechada import GerenciadorControle

class ECU:
    def __init__(self, config):
        self.config = config
        self.sensors = SensorManager()
        self.controle = GerenciadorControle()
        
    def cycle(self, t_corrente):
        # Lê todos os sensores
        sensor_data = self.sensors.read_all(t_corrente)
        
        # Aplica controles em malha fechada
        correcoes = self.controle.atualizar(sensor_data)
        
        # Calcula tempo de injeção
        inj_ms = self.calcular_injecao(sensor_data)
        
        return {
            **sensor_data,
            'inj_ms': inj_ms,
            **correcoes
        }
        
    def calcular_injecao(self, sensors):
        # Cálculo básico do tempo de injeção
        return 5.0  # Valor base para teste
