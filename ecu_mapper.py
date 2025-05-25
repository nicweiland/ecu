import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

class ECUMapper:
    def __init__(self, obd_connection):
        self.connection = obd_connection
        self.backup_dir = "mapas_backup"
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def read_current_map(self, map_type):
        """Lê mapa atual da ECU"""
        if map_type == "fuel":
            # Exemplo de leitura de mapa de combustível
            # Cada ECU tem seus próprios comandos
            values = []
            for addr in range(0x1000, 0x1FFF, 0x10):
                response = self.connection.query(f"22 {addr:04X}")
                if response.is_null():
                    continue
                values.extend(response.value)
            return self.convert_to_dataframe(values)
            
    def write_map(self, map_type, df_map):
        """Escreve mapa na ECU"""
        # Faz backup antes de escrever
        self.backup_map(map_type)
        
        values = df_map.values.flatten()
        for i, value in enumerate(values):
            addr = 0x1000 + i
            cmd = f"2E {addr:04X} {int(value):02X}"
            self.connection.query(cmd)
            
    def backup_map(self, map_type):
        """Faz backup do mapa atual"""
        current_map = self.read_current_map(map_type)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.backup_dir}/{map_type}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump({
                "type": map_type,
                "timestamp": timestamp,
                "data": current_map.to_dict()
            }, f)
        return filename
