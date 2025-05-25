import pandas as pd
import numpy as np

def criar_mapa_lambda_base():
    """Cria mapa lambda base com valores típicos"""
    rpm_bins = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
    tps_bins = [0, 10, 25, 50, 75, 100]
    
    # Matriz base - mais rico em carga alta, mais pobre em cruzeiro
    valores = np.ones((len(rpm_bins), len(tps_bins)))
    valores[:, -1] = 0.85  # Rico em WOT
    valores[:, 0] = 1.05   # Levemente pobre em marcha lenta
    
    return pd.DataFrame(
        valores,
        index=[f"{rpm} RPM" for rpm in rpm_bins],
        columns=[f"{tps}%" for tps in tps_bins]
    )

def criar_mapa_ve_base():
    """Cria mapa VE base com valores típicos"""
    rpm_bins = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
    tps_bins = [0, 10, 25, 50, 75, 100]
    
    # Matriz base - eficiência volumétrica aumenta com RPM e TPS
    valores = np.zeros((len(rpm_bins), len(tps_bins)))
    for i in range(len(rpm_bins)):
        for j in range(len(tps_bins)):
            valores[i,j] = 60 + (i/6)*20 + (j/5)*20
    
    return pd.DataFrame(
        valores,
        index=[f"{rpm} RPM" for rpm in rpm_bins],
        columns=[f"{tps}%" for tps in tps_bins]
    )

def criar_mapa_ignicao_base():
    """Cria mapa de ignição base com valores típicos"""
    rpm_bins = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
    tps_bins = [0, 10, 25, 50, 75, 100]
    
    # Matriz base - avanço aumenta com RPM e diminui com carga
    valores = np.zeros((len(rpm_bins), len(tps_bins)))
    for i, rpm in enumerate(rpm_bins):
        for j, tps in enumerate(tps_bins):
            # Avanço base aumenta com RPM
            avanço_base = 10 + (i/6) * 20  # 10° a 30°
            # Reduz avanço com carga (TPS)
            redução_carga = (j/5) * 10     # 0° a 10° de redução
            valores[i,j] = avanço_base - redução_carga
    
    return pd.DataFrame(
        valores,
        index=[f"{rpm} RPM" for rpm in rpm_bins],
        columns=[f"{tps}%" for tps in tps_bins]
    )

def criar_mapa_aceleracao():
    """Cria mapa de enriquecimento por aceleração"""
    delta_tps_bins = [0, 5, 10, 20, 50]  # Variação % TPS
    rpm_bins = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
    
    # Enriquecimento diminui com RPM e aumenta com delta TPS
    valores = np.zeros((len(rpm_bins), len(delta_tps_bins)))
    for i in range(len(rpm_bins)):
        for j in range(len(delta_tps_bins)):
            valores[i,j] = 1.0 + (j/4)*0.5 - (i/6)*0.2  # 1.0 a 1.5
    
    return pd.DataFrame(
        valores,
        index=[f"{rpm} RPM" for rpm in rpm_bins],
        columns=[f"{d}% TPS" for d in delta_tps_bins]
    )
