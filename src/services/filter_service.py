import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin2, lfilter
from scipy.ndimage import gaussian_filter1d

# === 1. Lade Audiodateien ===
y_dir, sr = librosa.load(
    "../../ressources/uncut_direktional_1.wav", sr=None
)  # direktionale Mikrofonaufnahme
y_omni, _ = librosa.load(
    "../../ressources/sweep_ausgangs_datei.wav", sr=sr
)  # omnidirektionale Mikrofonaufnahme in diesem Fall als Platzhalter die Sweep Lautsprecher Datei, da keine andere vorhanden ist.
# für die Berechnung des echten Filters echte omnidirektionale Mikrofonaufnahme verwenden.

# === 2. Auf gleiche Länge kürzen ===
min_len = min(len(y_dir), len(y_omni))
# Dieser Teil existiert nur da die direktionale datei gerade uncut ist also nicht mit dem sweep anfängt
start_sample = int(75 * sr)
y_dir = y_dir[start_sample : start_sample + min_len]
# Falls cut direktionale datei(alle anderen) erstzen mit
# y_dir = y_dir[:min_len]
y_omni = y_omni[:min_len]

# === 3. Frequenzgänge berechnen vorher auf RMS-Pegel normalisieren===
y_dir /= np.sqrt(np.mean(y_dir**2))
y_omni /= np.sqrt(np.mean(y_omni**2))

S_dir = np.abs(np.fft.rfft(y_dir))
S_omni = np.abs(np.fft.rfft(y_omni))
freqs = np.fft.rfftfreq(len(y_dir), 1 / sr)

# === 4. Übertragungsfunktion (Korrekturkurve) ===
epsilon_base = 0.001 * np.median(S_dir)
freq_weights = np.interp(freqs, [20, 100, 20000], [0.1, 0.03, 0.01])
epsilon = np.maximum(1e-12, epsilon_base * freq_weights)
S_dir_min = np.maximum(S_dir, 1e-6)
correction_curve = S_omni / (S_dir_min + epsilon)

# === 5. Frequenzabhängiges Clipping ===
min_clip = np.percentile(correction_curve, 5)
max_clip = np.percentile(correction_curve, 95)
correction_curve = np.clip(correction_curve, min_clip, max_clip)

# === 6. Glättung der Korrekturkurve (sigma erhöht glättung im bassbereich) ===
correction_smoothed = gaussian_filter1d(correction_curve, sigma=50)

# === 7. FIR-Filter erstellen ===
NUMTAPS = 2049

# Korrekte Frequenzachse für firwin2
filter_freqs = np.linspace(0, sr / 2, len(correction_smoothed))

# FIR-Filter berechnen
fir_coeff = firwin2(numtaps=NUMTAPS, freq=filter_freqs, gain=correction_smoothed, fs=sr)
# das ist der Filter


# === 8. Filter anwenden ===
filtered = lfilter(fir_coeff, [1.0], y_dir)

# für andere Aufnahmen zum testen des Filters
y_test, _ = librosa.load(
    "../../ressources/direktional_2.wav", sr=sr
)  # hier eine andere nicht direktionale Datei einfügen um den Filter zu testen
y_test = y_test[:min_len]
y_test /= np.sqrt(np.mean(y_test**2))
S_test = np.abs(np.fft.rfft(y_test))
filteredt = lfilter(fir_coeff, [1.0], y_test)

# === 9. Frequenzgänge für Vergleich ===
S_dir /= np.max(S_dir)
S_omni /= np.max(S_omni)
S_filtered = np.abs(np.fft.rfft(filtered))
S_filtered /= np.max(S_filtered)
# wieder für andere Aufnahmen zum Testen
S_test /= np.max(S_test)
S_filteredt = np.abs(np.fft.rfft(filteredt))
S_filteredt /= np.max(S_filteredt)

# === 10. Plot ===
# es wird immer nur ein Plot gleichzeitig gezeigt ersten schließen,dann kommt der zweite
valid = freqs > 15
plt.figure(figsize=(8, 6))
plt.semilogx(freqs[valid], 20 * np.log10(S_dir[valid]), label="Direktional")
plt.semilogx(freqs[valid], 20 * np.log10(S_omni[valid]), label="Omni")
plt.semilogx(freqs[valid], 20 * np.log10(S_filtered[valid]), label="Gefiltert")
# plt.semilogx(freqs[valid], 20*np.log10(S_test[valid]), label='test')
# plt.semilogx(freqs[valid], 20*np.log10(S_filteredt[valid]), label='Gefilterttest')
plt.semilogx(
    freqs[valid],
    20 * np.log10(epsilon[valid]),
    "r--",
    label="Epsilon (Regularisierung)",
)
plt.xlabel("Frequenz [Hz]")
plt.ylabel("Pegel [dB]")
plt.title("Frequenzgang-Vergleich (normiert)")
plt.grid(True, which="both", linestyle=":", linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.show()

valid = freqs > 15
plt.figure(figsize=(8, 6))
plt.semilogx(freqs[valid], 20 * np.log10(S_omni[valid]), label="Omni")
plt.semilogx(freqs[valid], 20 * np.log10(S_test[valid]), label="test")
plt.semilogx(freqs[valid], 20 * np.log10(S_filteredt[valid]), label="Gefilterttest")
plt.xlabel("Frequenz [Hz]")
plt.ylabel("Pegel [dB]")
plt.title("Frequenzgang-Vergleich (normiert)")
plt.grid(True, which="both", linestyle=":", linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.show()
