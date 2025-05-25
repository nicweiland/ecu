import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import time
import serial.tools.list_ports
from mapas_base import criar_mapa_lambda_base, criar_mapa_ve_base, criar_mapa_ignicao_base
from config_motor import CONFIG_MOTOR
from obd_reader import OBDReader  # Novo import para OBDReader
from ecu_mapper import ECUMapper

st.set_page_config(page_title="Painel ECU Simulada", layout="wide")

st.title("🧠 ECU Simulada - Painel Interativo com Plotly")

# Inicializa estado
if "rodando" not in st.session_state:
    st.session_state.rodando = True

# Botões Play/Pause
col_play, col_intervalo = st.sidebar.columns([1, 2])
if col_play.button("⏯️ Play/Pause"):
    st.session_state.rodando = not st.session_state.rodando
    # Atualiza arquivo de controle
    with open("controle_simulacao.txt", "w") as f:
        f.write("PAUSE" if not st.session_state.rodando else "RUN")

intervalo = col_intervalo.slider("⏱️ Atualizar a cada (s)", 0.5, 5.0, 1.0)

# --- Configurações de malha
rpm_bins = [1000, 2000, 3000, 4000, 5000, 6000, 7000]
tps_bins = [0, 10, 25, 50, 75, 100]  # Em %

def criar_mapa_vazio():
    return pd.DataFrame(
        0.0,
        index=[f"{rpm} RPM" for rpm in rpm_bins],
        columns=[f"{tps}%" for tps in tps_bins]
    )

df = None
log_path = "log_ecu_simulada.csv"
if os.path.exists(log_path):
    try:
        df = pd.read_csv(log_path)
    except Exception as e:
        st.error(f"Erro ao ler dados: {e}")
        df = pd.DataFrame()  # DataFrame vazio como fallback


# ================================
# MAPAS VE e IGNIÇÃO INTERATIVOS
# ================================

st.markdown("---")
st.header("🗺️ Mapas Interativos - VE e Ignição")

aba = st.tabs(["🟢 Mapa VE", "🔥 Mapa Ignição", "🎯 Mapa Lambda", "🔍 Diagnóstico", "📝 Remapeamento"])

# --- Mapa VE ---
with aba[0]:
    st.subheader("Mapa VE")
    if os.path.exists("mapa_ve.csv"):
        mapa_ve = pd.read_csv("mapa_ve.csv", index_col=0)
    else:
        mapa_ve = criar_mapa_ve_base()  # Usa mapa base ao invés de vazio
    mapa_ve_editado = st.data_editor(mapa_ve, num_rows="dynamic", key="mapa_ve_editor")
    if st.button("Salvar Mapa VE", key="btn_salvar_ve"):
        mapa_ve_editado.to_csv("mapa_ve.csv")
        st.success("Mapa VE salvo!")

# --- Mapa Ignição ---
with aba[1]:
    st.subheader("Mapa Ignição")
    if os.path.exists("mapa_ign.csv"):
        mapa_ign = pd.read_csv("mapa_ign.csv", index_col=0)
    else:
        mapa_ign = criar_mapa_ignicao_base()  # Usa mapa base ao invés de vazio
    mapa_ign_editado = st.data_editor(mapa_ign, num_rows="dynamic", key="mapa_ign_editor")
    if st.button("Salvar Mapa Ignição", key="btn_salvar_ign"):
        mapa_ign_editado.to_csv("mapa_ign.csv")
        st.success("Mapa Ignição salvo!")

# --- Mapa Lambda ---
with aba[2]:
    st.subheader("Mapa Lambda")
    if os.path.exists("mapa_lambda.csv"):
        mapa_lambda = pd.read_csv("mapa_lambda.csv", index_col=0)
    else:
        mapa_lambda = criar_mapa_lambda_base()  # Usa mapa base ao invés de vazio
        mapa_lambda.values[:] = 1.0  # Valor padrão lambda = 1.0
    mapa_lambda_editado = st.data_editor(mapa_lambda, num_rows="dynamic", key="mapa_lambda_editor")
    if st.button("Salvar Mapa Lambda", key="btn_salvar_lambda"):
        mapa_lambda_editado.to_csv("mapa_lambda.csv")
        st.success("Mapa Lambda salvo!")

# --- Aba Diagnóstico ---
with aba[3]:
    st.subheader("🔍 Diagnóstico OBD")
    
    # Status da conexão
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if 'protocol' in df.columns:
            st.info(f"Protocolo: {df['protocol'].iloc[-1]}")
    with status_col2:
        if 'voltage' in df.columns:
            st.info(f"Tensão: {df['voltage'].iloc[-1]}V")
    
    # Dados do motor em tempo real
    st.subheader("📊 Dados do Motor")
    metricas1, metricas2, metricas3 = st.columns(3)
    
    with metricas1:
        if 'rpm' in df.columns:
            st.metric("RPM", f"{df['rpm'].iloc[-1]:.0f}")
        if 'speed' in df.columns:
            st.metric("Velocidade", f"{df['speed'].iloc[-1]} km/h")
        if 'throttle' in df.columns:
            st.metric("TPS", f"{df['throttle'].iloc[-1]:.1f}%")
            
    with metricas2:
        if 'coolant_temp' in df.columns:
            st.metric("Temp. Motor", f"{df['coolant_temp'].iloc[-1]}°C")
        if 'intake_temp' in df.columns:
            st.metric("Temp. Ar", f"{df['intake_temp'].iloc[-1]}°C")
        if 'map' in df.columns:
            st.metric("MAP", f"{df['map'].iloc[-1]} kPa")
            
    with metricas3:
        if 'maf' in df.columns:
            st.metric("MAF", f"{df['maf'].iloc[-1]:.1f} g/s")
        if 'timing' in df.columns:
            st.metric("Avanço", f"{df['timing'].iloc[-1]}°")
        if 'o2_voltage' in df.columns:
            st.metric("O2", f"{df['o2_voltage'].iloc[-1]:.2f}V")
    
    # Códigos de erro
    st.subheader("⚠️ Diagnóstico")
    if 'dtc' in df.columns and df['dtc'].iloc[-1]:
        st.error(f"Códigos de Erro: {df['dtc'].iloc[-1]}")
    else:
        st.success("Nenhum código de erro")
        
    # Status MIL
    if 'mil_on' in df.columns:
        if df['mil_on'].iloc[-1]:
            st.warning("⚠️ Check Engine LIGADA")
        else:
            st.success("✅ Check Engine DESLIGADA")

    # Todos os PIDs disponíveis
    if st.checkbox("Mostrar todos os PIDs disponíveis"):
        st.json({col: df[col].iloc[-1] for col in df.columns 
                if col not in ['timestamp', 'tempo']})

# --- Aba Remapeamento ---
with aba[4]:
    st.subheader("📝 Remapeamento ECU")
    
    if "obd_reader" not in st.session_state:
        st.warning("⚠️ Conecte o OBD primeiro!")
    else:
        mapper = ECUMapper(st.session_state.obd_reader.connection)
        
        # Seleção do tipo de mapa
        map_type = st.selectbox(
            "Selecione o mapa",
            ["Combustível", "Ignição", "Boost"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Ler Mapa Atual"):
                try:
                    current_map = mapper.read_current_map(map_type.lower())
                    st.session_state.current_map = current_map
                    st.success("✅ Mapa lido com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro lendo mapa: {e}")
                    
        with col2:
            if st.button("💾 Fazer Backup"):
                try:
                    backup_file = mapper.backup_map(map_type.lower())
                    st.success(f"✅ Backup salvo em: {backup_file}")
                except Exception as e:
                    st.error(f"❌ Erro no backup: {e}")
        
        # Editor de mapa
        if "current_map" in st.session_state:
            mapa_editado = st.data_editor(
                st.session_state.current_map,
                num_rows="dynamic",
                key=f"mapa_editor_{map_type}"
            )
            
            # Botões de ação
            col3, col4 = st.columns(2)
            with col3:
                if st.button("✍️ Gravar na ECU"):
                    try:
                        mapper.write_map(map_type.lower(), mapa_editado)
                        st.success("✅ Mapa gravado com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro gravando mapa: {e}")
                        
            with col4:
                # Lista backups disponíveis
                backups = os.listdir(mapper.backup_dir)
                backup_select = st.selectbox(
                    "Restaurar backup",
                    backups,
                    key="backup_select"
                )
                
                if st.button("🔄 Restaurar"):
                    try:
                        # Implementar restauração
                        st.success("✅ Mapa restaurado!")
                    except Exception as e:
                        st.error(f"❌ Erro restaurando: {e}")

# Adicionar configurações do motor na sidebar
with st.sidebar:
    st.subheader("⚙️ Configurações do Motor")
    st.json(CONFIG_MOTOR)

# Adicionar seleção de porta OBD na sidebar
with st.sidebar:
    st.subheader("🔌 Conexão OBD")
    usar_obd = st.checkbox("Usar OBD", value=False)
    if usar_obd:
        # Auto-detectar portas
        portas_disponiveis = [p.device for p in serial.tools.list_ports.comports()]
        porta_com = st.selectbox(
            "Selecione a porta",
            options=portas_disponiveis,
            help="Selecione a porta COM do seu adaptador OBD"
        )
        st.session_state.porta_obd = porta_com
        
        if st.button("Conectar OBD"):
            try:
                obd_reader = OBDReader(porta_com)
                info = obd_reader.get_vehicle_info()
                st.session_state.info_veiculo = info
                st.success("✅ Conectado com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro na conexão: {e}")

# Informações do Veículo após conexão
if "info_veiculo" in st.session_state:
    with st.expander("ℹ️ Informações do Veículo", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**VIN:**", st.session_state.info_veiculo.get('vin', 'N/A'))
            st.write("**ECU:**", st.session_state.info_veiculo.get('ecu_name', 'N/A'))
            st.write("**Protocolo:**", st.session_state.info_veiculo.get('protocol', 'N/A'))
        with col2:
            st.write("**Combustível:**", st.session_state.info_veiculo.get('fuel_type', 'N/A'))
            st.write("**Calibração:**", st.session_state.info_veiculo.get('cal_id', 'N/A'))
            st.write("**Tensão:**", f"{st.session_state.info_veiculo.get('voltage', 'N/A')}V")

# Real-time monitoring section
log_path = "log_ecu_simulada.csv"

# Espera o log aparecer
if not os.path.exists(log_path):
    st.warning("Aguardando log_ecu_simulada.csv...")
    st.stop()

placeholder = st.empty()

while True:
    if not st.session_state.rodando:
        time.sleep(0.5)
        continue

    try:
        df = pd.read_csv(log_path)
        
        # Gera timestamp único para os gráficos
        chart_timestamp = int(time.time() * 1000)
        
        last_row = df.iloc[-1]
        
        # Formata as correções com cores
        if 'corr_marcha' in df.columns:
            valor = last_row['corr_marcha']
            st.sidebar.markdown(f"Marcha Lenta: **:{'red' if valor < 1 else 'green'}[{valor:.3f}]**")
            
        if 'corr_lambda' in df.columns:
            valor = last_row['corr_lambda']
            st.sidebar.markdown(f"Lambda: **:{'red' if valor < 1 else 'green'}[{valor:.3f}]**")
            
        if 'corr_knock' in df.columns:
            valor = last_row['corr_knock']
            st.sidebar.markdown(f"Knock: **:{'red' if valor < 0 else 'green'}[{valor:.1f}°]**")

        if df.empty or "timestamp" not in df:
            st.warning("Aguardando dados válidos...")
            time.sleep(intervalo)
            continue

        df["tempo"] = df["timestamp"] - df["timestamp"].iloc[0]

        with placeholder.container():
            st.subheader("📊 Gráficos em tempo real")
            
            # Mostra tamanho do DataFrame
            st.text(f"Quantidade de amostras: {len(df)}")

            # Define todas as colunas no início
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            col5, col6 = st.columns(2)  # col6 para manter simetria, mesmo que não use

            # --- Gráfico 1: RPM / TPS ---
            fig1 = go.Figure()
            if 'rpm' in df.columns:
                fig1.add_trace(go.Scatter(x=df["tempo"], y=df["rpm"], 
                    mode='lines', name='RPM', line=dict(color='blue')))
            if 'tps' in df.columns:
                fig1.add_trace(go.Scatter(x=df["tempo"], y=df["tps"], 
                    mode='lines', name='TPS (%)', line=dict(color='green')))
            fig1.update_layout(title="RPM e TPS", height=300)
            col1.plotly_chart(fig1, use_container_width=True, key=f"chart_rpm_tps_{chart_timestamp}")

            # --- Gráfico 2: Temperatura Motor ---
            fig2 = go.Figure()
            if 'temp_motor' in df.columns:
                fig2.add_trace(go.Scatter(x=df["tempo"], y=df["temp_motor"], 
                    mode='lines', name='Temp. Motor (°C)', line=dict(color='red')))
            fig2.update_layout(title="Temperatura Motor", height=300)
            col2.plotly_chart(fig2, use_container_width=True, key=f"chart_temp_{chart_timestamp}")

            # --- Gráfico 3: Knock e Correção de Avanço ---
            if 'knock' in df.columns:
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=df["tempo"], y=df["knock"], 
                    mode='lines', name='Knock', line=dict(color='red')))
                if 'corr_knock' in df.columns:
                    fig3.add_trace(go.Scatter(x=df["tempo"], y=df["corr_knock"], 
                        mode='lines', name='Correção Knock (°)', line=dict(color='orange')))
                fig3.update_layout(title="Knock e Correção", xaxis_title="Tempo (s)", height=300)
                col3.plotly_chart(fig3, use_container_width=True, key=f"chart_knock_{chart_timestamp}")

            # --- Gráfico 4: Lambda e Correção ---
            if 'lambda' in df.columns:
                fig4 = go.Figure()
                fig4.add_trace(go.Scatter(x=df["tempo"], y=df["lambda"], 
                    mode='lines', name='Lambda Real', line=dict(color='blue')))
                if 'lambda_alvo' in df.columns:
                    fig4.add_trace(go.Scatter(x=df["tempo"], y=df["lambda_alvo"], 
                        mode='lines', name='Lambda Alvo', line=dict(color='green')))
                if 'corr_lambda' in df.columns:
                    fig4.add_trace(go.Scatter(x=df["tempo"], y=df["corr_lambda"], 
                        mode='lines', name='Correção Lambda', line=dict(color='purple')))
                fig4.update_layout(title="Lambda e Correção", xaxis_title="Tempo (s)", height=300)
                col4.plotly_chart(fig4, use_container_width=True, key=f"chart_lambda_{chart_timestamp}")

            # --- Gráfico 5: Correções Marcha Lenta ---
            if 'corr_marcha' in df.columns:
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(x=df["tempo"], y=df["corr_marcha"], 
                    mode='lines', name='Correção Marcha', line=dict(color='cyan')))
                fig5.update_layout(title="Correção Marcha Lenta", xaxis_title="Tempo (s)", height=300)
                col5.plotly_chart(fig5, use_container_width=True, key=f"chart_marcha_{chart_timestamp}")

            # --- Gráfico 6: Sensores Adicionais ---
            row3_col1, row3_col2 = st.columns(2)
            
            # Gráfico MAF e MAP
            if any(x in df.columns for x in ['maf', 'map', 'boost']):
                fig6 = go.Figure()
                if 'maf' in df.columns:
                    fig6.add_trace(go.Scatter(x=df["tempo"], y=df["maf"],
                        mode='lines', name='MAF (g/s)', line=dict(color='blue')))
                if 'map' in df.columns:
                    fig6.add_trace(go.Scatter(x=df["tempo"], y=df["map"],
                        mode='lines', name='MAP (kPa)', line=dict(color='red')))
                if 'boost' in df.columns:
                    fig6.add_trace(go.Scatter(x=df["tempo"], y=df["boost"],
                        mode='lines', name='Boost (PSI)', line=dict(color='green')))
                fig6.update_layout(title="Fluxo e Pressão", height=300)
                row3_col1.plotly_chart(fig6, use_container_width=True, key=f"chart_air_{chart_timestamp}")
            
            # Gráfico Temperaturas
            if any(x in df.columns for x in ['iat', 'ect', 'cat_temp']):
                fig7 = go.Figure()
                for sensor, cor in [('iat', 'blue'), ('ect', 'red'), ('cat_temp', 'orange')]:
                    if sensor in df.columns:
                        fig7.add_trace(go.Scatter(x=df["tempo"], y=df[sensor],
                            mode='lines', name=f'Temp. {sensor.upper()}', line=dict(color=cor)))
                fig7.update_layout(title="Temperaturas", height=300)
                row3_col2.plotly_chart(fig7, use_container_width=True, key=f"chart_temps_{chart_timestamp}")

            # Adiciona área para códigos de erro se existirem
            if 'dtc_count' in df.columns and df['dtc_count'].iloc[-1] > 0:
                st.error(f"⚠️ {df['dtc_count'].iloc[-1]} códigos de erro detectados!")

        time.sleep(intervalo)

    except Exception as e:
        st.error(f"Erro: {e}")
        time.sleep(1)