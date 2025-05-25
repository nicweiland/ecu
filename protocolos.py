from dataclasses import dataclass

@dataclass
class ProtocoloConfig:
    nome: str
    baudrate: int
    id_ecu: str
    timeout: float
    
PROTOCOLOS = {
    # Protocolos comuns
    "AUTO": None,  # Detecção automática
    
    # CAN 11-bit (ISO 15765-4)
    "CAN_11_500": ProtocoloConfig(
        nome="CAN_11_500",
        baudrate=500000,
        id_ecu="7E0",
        timeout=0.1
    ),
    
    # Protocolo ISO 9141-2 (Veículos mais antigos)
    "ISO9141": ProtocoloConfig(
        nome="ISO9141",
        baudrate=10400,
        id_ecu="33",
        timeout=0.2
    ),
    
    # Protocolo KWP2000 (Veículos europeus)
    "KWP2000": ProtocoloConfig(
        nome="KWP2000",
        baudrate=10400,
        id_ecu="33",
        timeout=0.2
    )
}
