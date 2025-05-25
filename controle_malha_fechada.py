class ControladorPID:
    def __init__(self, kp=0.1, ki=0.05, kd=0.02):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.erro_anterior = 0
        self.integral = 0
        
    def calcular(self, erro, dt):
        self.integral += erro * dt
        self.integral = max(-1.0, min(1.0, self.integral))
        
        derivada = (erro - self.erro_anterior) / dt
        self.erro_anterior = erro
        
        saida = (erro * self.kp + 
                 self.integral * self.ki + 
                 derivada * self.kd)
        
        return max(-1.0, min(1.0, saida))

class ControleMarcha:
    def __init__(self):
        self.pid = ControladorPID(kp=0.2, ki=0.1, kd=0.05)
        self.rpm_alvo = 800
        
    def calcular_correcao(self, rpm_atual, dt):
        erro = (self.rpm_alvo - rpm_atual) / 1000  # Normaliza erro
        correcao = self.pid.calcular(erro, dt)
        return 1.0 + correcao  # Fator de correção 0.0 a 2.0

class ControleLambda:
    def __init__(self):
        self.pid = ControladorPID(kp=0.1, ki=0.05, kd=0.01)
        self.correcao_atual = 1.0
        
    def calcular_correcao(self, lambda_atual, lambda_alvo, dt):
        erro = (lambda_alvo - lambda_atual)
        correcao = self.pid.calcular(erro, dt)
        self.correcao_atual = max(0.8, min(1.2, 1.0 + correcao))
        return self.correcao_atual

class ControleKnock:
    def __init__(self):
        self.reducao_maxima = 10  # Graus
        self.knock_threshold = 5.0
        self.recuperacao_rate = 0.5  # Graus por segundo
        self.reducao_atual = 0
        
    def calcular_correcao(self, knock_sensor, dt):
        if knock_sensor > self.knock_threshold:
            self.reducao_atual = min(self.reducao_maxima, 
                                   self.reducao_atual + 2)
        else:
            self.reducao_atual = max(0, 
                                   self.reducao_atual - self.recuperacao_rate * dt)
        return -self.reducao_atual

class GerenciadorControle:
    def __init__(self):
        self.controle_marcha = ControleMarcha()
        self.controle_lambda = ControleLambda()
        self.controle_knock = ControleKnock()
        self.ultimo_timestamp = None
        
    def atualizar(self, dados_motor):
        timestamp_atual = dados_motor['timestamp']
        if self.ultimo_timestamp is None:
            self.ultimo_timestamp = timestamp_atual
            return {}
            
        dt = timestamp_atual - self.ultimo_timestamp
        self.ultimo_timestamp = timestamp_atual
        
        return {
            'corr_marcha': self.controle_marcha.calcular_correcao(
                dados_motor['rpm'], dt),
            'corr_lambda': self.controle_lambda.calcular_correcao(
                dados_motor['lambda'], dados_motor['lambda_alvo'], dt),
            'corr_knock': self.controle_knock.calcular_correcao(
                dados_motor.get('knock', 0), dt)
        }
