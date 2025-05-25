def decode_wideband(messages):
    """Decodifica sensor wideband O2"""
    d = messages[0].data
    return (d[0] * 256 + d[1]) / 32768

def decode_boost(messages):
    """Decodifica pressão do boost"""
    d = messages[0].data
    return (d[0] - 128) * 0.01

def decode_percent(messages):
    """Decodifica valores percentuais"""
    return messages[0].data[0] * 100.0 / 255.0
