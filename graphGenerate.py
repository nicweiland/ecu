import pandas as pd
import matplotlib.pyplot as plt

# Carregar o log
df = pd.read_csv("log_ecu_simulada.csv")

# Converter timestamp para tempo relativo
df["tempo"] = df["timestamp"] - df["timestamp"].iloc[0]

# Plotar gráfico principal
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# RPM
axs[0].plot(df["tempo"], df["rpm"], label="RPM", color="blue")
axs[0].set_ylabel("RPM")
axs[0].legend()
axs[0].grid(True)

# VE e MAP
axs[1].plot(df["tempo"], df["ve"], label="VE (%)", color="green")
axs[1].plot(df["tempo"], df["map_kpa"], label="MAP (kPa)", color="orange", linestyle="dashed")
axs[1].set_ylabel("VE / MAP")
axs[1].legend()
axs[1].grid(True)

# Tempo de injeção e avanço
axs[2].plot(df["tempo"], df["inj_ms"], label="Inj (ms)", color="red")
axs[2].plot(df["tempo"], df["avanco_deg"], label="Avanço (°)", color="purple")
axs[2].set_ylabel("Injeção / Avanço")
axs[2].set_xlabel("Tempo (s)")
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()
plt.show()
