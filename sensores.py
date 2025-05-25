import numpy as np

class SensorManager:
    def __init__(self):
        self.sensors = {
            'rpm': 800,
            'tps': 0,
            'map_kpa': 90,
            'iat': 25.0,
            'ect': 25.0,
            'lambda': 1.0,
            'knock': 0,
            'bat': 12.0,
            've': 0
        }
    
    def read_all(self, t_corrente):
        # Simulação dos sensores
        self.sensors['tps'] = 50 + 40 * np.sin(0.7 * t_corrente)
        self.sensors['tps'] = max(0, min(100, self.sensors['tps']))
        
        # RPM baseado no TPS
        if self.sensors['tps'] < 5:
            self.sensors['rpm'] = 800 + np.random.normal(0, 50)
        else:
            rpm_delta = (self.sensors['tps'] / 100.0) * 500
            self.sensors['rpm'] = min(7000, self.sensors['rpm'] + rpm_delta)
        
        # Outros sensores
        self.sensors['ect'] = min(90, self.sensors['ect'] + 0.1)
        self.sensors['map_kpa'] = 90 + (self.sensors['tps'] * 0.5)
        self.sensors['lambda'] += np.random.normal(0, 0.02)
        self.sensors['lambda'] = max(0.7, min(1.3, self.sensors['lambda']))
        
        return self.sensors
