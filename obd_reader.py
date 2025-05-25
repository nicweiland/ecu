import obd
import time
import serial.tools.list_ports

class OBDReader:
    def __init__(self, port=None, bluetooth=True):
        self.connection = None
        self.port = port
        self.bluetooth = bluetooth
        
        # Expandir comandos com mais sensores
        self.commands = {
            # Comandos básicos
            'rpm': obd.commands.RPM,
            'speed': obd.commands.SPEED,
            'throttle': obd.commands.THROTTLE_POS,
            
            # Sensores de temperatura
            'ect': obd.commands.COOLANT_TEMP,
            'iat': obd.commands.INTAKE_TEMP,
            'cat_temp': obd.commands.CATALYST_TEMP_B1S1,
            
            # Sensores de pressão/fluxo
            'map': obd.commands.INTAKE_PRESSURE,
            'maf': obd.commands.MAF,
            'fuel_pressure': obd.commands.FUEL_PRESSURE,
            
            # Sensores de combustível
            'o2_b1s1': obd.commands.O2_B1S1,
            'o2_b1s2': obd.commands.O2_B1S2,
            'fuel_level': obd.commands.FUEL_LEVEL,
            'fuel_rate': obd.commands.FUEL_RATE,
            
            # Sensores de ignição
            'timing': obd.commands.TIMING_ADVANCE,
            'spark_advance': obd.commands.SPARK_ADVANCE_B1,
            
            # Sensores de diagnóstico
            'voltage': obd.commands.ELM_VOLTAGE,
            'dtc_status': obd.commands.STATUS
        }
        
        # Adiciona PIDs customizados
        self.custom_commands = {
            'wideband': obd.OBDCommand('WIDEBAND', 'Wideband O2', b'01 24', 2, decode_wideband),
            'egr': obd.OBDCommand('EGR_PCT', 'EGR Percentage', b'01 2C', 1, decode_percent),
            'boost': obd.OBDCommand('BOOST', 'Boost Pressure', b'01 0B', 1, decode_boost)
        }
        
    def find_obd_port(self):
        """Procura por adaptador OBD em portas COM"""
        print("Procurando adaptador OBD...")
        
        for port in serial.tools.list_ports.comports():
            # Procura por adaptadores comuns (ELM327, STN, etc)
            if any(id in port.description.lower() for id in ["elm", "obd", "serial"]):
                print(f"Encontrado possível adaptador OBD: {port.device} - {port.description}")
                return port.device
                
        return None
        
    def connect(self):
        print("Conectando ao OBD-II...")
        
        if not self.port:
            self.port = self.find_obd_port()
            if not self.port:
                raise ConnectionError("Nenhum adaptador OBD encontrado")
        
        try:
            self.connection = obd.OBD(self.port)
            if not self.connection.is_connected():
                raise ConnectionError("Não foi possível conectar ao OBD-II")
            
            print(f"Conectado na porta: {self.port}")
            print(f"Protocolo: {self.connection.protocol_name()}")
            
        except Exception as e:
            print(f"Erro de conexão: {e}")
            raise
            
    def get_supported_commands(self):
        """Retorna lista de comandos suportados pelo veículo"""
        if not self.connection:
            self.connect()
        return [cmd for cmd, command in self.commands.items() 
                if self.connection.supports(command)]
    
    def read_dtc(self):
        """Lê códigos de erro (DTC)"""
        if not self.connection:
            self.connect()
        response = self.connection.query(obd.commands.GET_DTC)
        return response.value if not response.is_null() else []
    
    def read_sensor(self, command_name):
        if command_name in self.commands:
            response = self.connection.query(self.commands[command_name])
            if response.is_null():
                return None
            return response.value
        return None
        
    def read_all(self):
        if not self.connection:
            self.connect()
            
        data = {
            'timestamp': time.time(),
        }
        
        for name in self.commands:
            value = self.read_sensor(name)
            if value is not None:
                data[name] = value
                
        return data
    
    def add_custom_pid(self, name, command_str, bytes_returned, decoder):
        """Adiciona PID customizado"""
        cmd = obd.OBDCommand(name, name, command_str, bytes_returned, decoder)
        self.custom_commands[name] = cmd
        if self.connection:
            self.connection.supported_commands.add(cmd)

    def read_all_advanced(self, include_custom=True):
        """Leitura avançada com mais informações"""
        data = self.read_all()
        
        # Adiciona status de diagnóstico
        status = self.connection.query(obd.commands.STATUS)
        if not status.is_null():
            data['mil_on'] = status.value.MIL
            data['dtc_count'] = status.value.DTC_count
        
        # Lê PIDs customizados
        if include_custom:
            for name, cmd in self.custom_commands.items():
                response = self.connection.query(cmd)
                if not response.is_null():
                    data[name] = response.value
                    
        return data

    def start_continuous(self, commands):
        """Inicia leitura contínua de comandos específicos"""
        if not self.connection:
            self.connect()
        self.connection.start_async(commands)

    def stop_continuous(self):
        """Para leitura contínua"""
        if self.connection:
            self.connection.stop_async()
            
    def get_vehicle_info(self):
        """Obtém informações do veículo"""
        info = {}
        
        # VIN
        response = self.connection.query(obd.commands.VIN)
        if not response.is_null():
            info['vin'] = response.value
            
        # Nome ECU
        response = self.connection.query(obd.commands.ECU_NAME)
        if not response.is_null():
            info['ecu_name'] = response.value
            
        # Protocolo
        info['protocol'] = self.connection.protocol_name()
        
        # Tipo combustível
        response = self.connection.query(obd.commands.FUEL_TYPE)
        if not response.is_null():
            info['fuel_type'] = response.value
            
        # Tensão
        response = self.connection.query(obd.commands.ELM_VOLTAGE)
        if not response.is_null():
            info['voltage'] = response.value
            
        # Calibração
        response = self.connection.query(obd.commands.CAL_ID)
        if not response.is_null():
            info['cal_id'] = response.value
            
        return info
        
    def get_dtc_info(self):
        """Obtém e decodifica DTCs"""
        dtcs = []
        response = self.connection.query(obd.commands.GET_DTC)
        if not response.is_null():
            for code in response.value:
                dtc_info = {
                    'code': code.code,
                    'description': code.description,
                    'severity': 'Grave' if code.severity > 1 else 'Leve'
                }
                dtcs.append(dtc_info)
        return dtcs
