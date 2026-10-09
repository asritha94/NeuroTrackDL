import pandas as pd
import matplotlib.pyplot as plt

# Load CSV log
df = pd.read_csv("fatigue_log.csv")

# Convert time to index
df["time_index"] = range(len(df))

# Convert fatigue labels to numeric
df["fatigue_level"] = df["fatigue"].map({"Normal": 0, "High": 1})

# -------- Plot --------
plt.figure(figsize=(12, 6))

plt.plot(df["time_index"], df["blink_count"], label="Blink Count", color="blue")
plt.plot(df["time_index"], df["ear"], label="EAR", color="green")
plt.plot(df["time_index"], df["pitch"], label="Head Pitch", color="orange")
plt.plot(df["time_index"], df["fatigue_level"] * 10, label="Fatigue (High)", color="red")

plt.xlabel("Time")
plt.ylabel("Value")
plt.title("NeuroTrackDL – Fatigue Timeline")
plt.legend()
plt.grid(True)

plt.show()
