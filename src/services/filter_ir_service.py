import numpy as np
import librosa
import matplotlib.pyplot as plt
import soundfile as sf
from scipy.fft import fft, ifft
from scipy.signal import lfilter
from scipy.signal.windows import tukey
from scipy.ndimage import (
    gaussian_filter1d,
)

# === Hilfsfunktionen ===


def calculate_transfer_function(in_t, out_t, fs, sr):
    # Berechnet die Übertragungsfunktion aus einem Ein- und Ausgangssignal.
    min_len = min(len(in_t), len(out_t))  # Angleichen der Länge
    # Zeitversetzt da die verwendete Testaufnahme nicht mit dem sweep beginnt
    start_sample = int(75 * sr)
    in_t = in_t[start_sample : start_sample + min_len]
    # Bei einer anderen direktionalen Testaufnahme
    # in_t = in_t[:min_len]
    out_t = out_t[:min_len]

    # Anwenden eines Tukey-Fensters zum Glätten der Signalkanten
    window = tukey(len(in_t), alpha=0.1)
    in_t_win = in_t * window
    out_t_win = out_t * window

    # FFT zur Transformation in den Frequenzbereich
    in_f = fft(in_t_win)
    out_f = fft(out_t_win)

    # Übertragungsfunktion: Quotient von Ausgang zu Eingang
    tf = out_f / in_f
    return tf


def extract_impulse_response_alt(tf, fs):
    # Extrahiert eine Impulsantwort aus einer Übertragungsfunktion.
    ir = np.real(ifft(tf))  # Rücktransformation in den Zeitbereich
    threshold = 1e-7 * np.max(np.abs(ir))  # Schwellenwert zur Begrenzung der Länge

    # Ende der relevanten Impulsantwort finden
    for i in range(len(ir) - 1, 0, -1):
        if np.abs(ir[i]) > threshold:
            end_idx = i
            break
    else:
        return ir[np.argmax(np.abs(ir)) :]  # Falls nichts gefunden wird

    # Anfang finden, nachdem die Energie wieder unter den Schwellenwert fällt
    found_low = False
    for i in range(end_idx - 1, 0, -1):
        if np.abs(ir[i]) <= threshold:
            found_low = True
        elif found_low and np.abs(ir[i]) > threshold:
            start_idx = i
            break
    else:
        start_idx = 0

    return np.roll(ir, -start_idx)  # Beginn der IR an den Anfang schieben


def trim_ir(ir, max_length=2048):
    # Beschneidet eine Impulsantwort um das Maximum herum auf eine definierte Länge da selbst berechnete antwort länger.
    peak = np.argmax(np.abs(ir))
    start = max(0, peak - max_length // 2)
    end = start + max_length
    return ir[start:end]


def visualize_impulse_response(ir_data, fs, title="Impulse Response Analysis"):
    # Visualisiert die Impulsantwort im Zeit-, Energie- und Frequenzbereich.
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    time_axis = np.arange(len(ir_data)) / fs

    # Zeitbereich
    axes[0].plot(time_axis, ir_data)
    axes[0].set_title("Time Domain")

    # Energiedekay (schrittweise Energieabnahme über die Zeit)
    axes[1].plot(
        time_axis,
        10
        * np.log10(
            np.cumsum(ir_data[::-1] ** 2)[::-1] / np.max(np.cumsum(ir_data[::-1] ** 2))
            + 1e-10
        ),
    )
    axes[1].set_title("Energy Decay")

    # Frequenzbereich (Frequenzgang)
    freqs = np.fft.rfftfreq(len(ir_data), 1 / fs)
    axes[2].semilogx(freqs, 20 * np.log10(np.abs(np.fft.rfft(ir_data)) + 1e-10))
    axes[2].set_title("Frequency Response")

    for ax in axes:
        ax.grid(True)
    fig.suptitle(title)
    plt.tight_layout()
    return fig


# === Hauptprogramm ===
def main():
    sr = 48000  # Samplingrate

    # === 1. Lade Ein- und Ausgangssignal des Sweep-Experiments ===
    in_t, sr = librosa.load("../../ressources/uncut_direktional_1.wav", sr=None)
    out_t, sr = librosa.load("../../ressources/sweep_ausgangs_datei.wav", sr=sr)

    # === 2. Berechne Übertragungsfunktion und extrahiere Impulsantwort ===
    tf = calculate_transfer_function(in_t, out_t, sr, sr)
    ir = extract_impulse_response_alt(tf, sr)

    # === 3. Analysiere Impulsantwort visuell erster Plot ===
    visualize_impulse_response(ir, sr, "Impulse Response (direktional)")
    plt.show()

    # === 4. Lade omnidirektionale IR, beschneide beide IRs auf gleiche Länge ===
    h_omni, _ = librosa.load(
        "../../ressources/impulsresponse_omnidirektional.wav", sr=sr
    )
    h_dir = trim_ir(ir)
    h_omni = trim_ir(h_omni)

    # === 5. Normalisiere Energie + angleichen der Länge ===
    h_dir /= np.sqrt(np.mean(h_dir**2))  # RMS-Normalisierung
    h_omni /= np.sqrt(np.mean(h_omni**2))
    min_len = min(len(h_dir), len(h_omni))
    h_dir = h_dir[:min_len]
    h_omni = h_omni[:min_len]

    # === 6. Korrekturfilter im Frequenzbereich berechnen ===
    # Fourier-Transformation der Impulsantworten
    # Um vom Zeitbereich (Impulsantwort) in den Frequenzbereich (Frequenzgang) zu gelangen
    H_dir = np.fft.rfft(h_dir)
    H_omni = np.fft.rfft(h_omni)
    # Korrekturkurve berechnen
    epsilon = 1e-6  # Verhindert Division durch 0
    H_corr = H_omni / (H_dir + epsilon)
    # Impulsantwort des Korrekturfilters (FIR-Koeffizienten)
    h_corr = np.fft.irfft(H_corr)

    # === 7. Lade Testsignal (ungerichtetes Mikrofonsignal) und filtere es ===
    y_test, _ = librosa.load("../../ressources/uncut_direktional_1.wav", sr=sr)
    filtered = lfilter(h_corr, [1.0], y_test)  # Faltung im Zeitbereich

    # === 8. Vergleiche Frequenzgänge vor und nach Filterung ===
    S_test = np.abs(np.fft.rfft(y_test))
    S_filtered = np.abs(np.fft.rfft(filtered))
    S_test /= np.max(S_test)  # Normalisieren für besseren Vergleich
    S_filtered /= np.max(S_filtered)
    freqs_test = np.fft.rfftfreq(len(y_test), 1 / sr)

    # Leider keine vergleichs Omnidatei zum Anzeigen und überprüfen
    plt.figure(figsize=(8, 6))
    plt.semilogx(freqs_test, 20 * np.log10(S_test), label="Original (direktional)")
    plt.semilogx(freqs_test, 20 * np.log10(S_filtered), label="Gefiltert (aus IR)")
    plt.xlabel("Frequenz [Hz]")
    plt.ylabel("Pegel [dB]")
    plt.grid(True, which="both", linestyle=":")
    plt.legend()
    plt.title("Frequenzgangvergleich: IR-basierte Filterung")
    plt.tight_layout()
    plt.show()


# === Ausführung starten ===
main()

# Das hier ist nur das Grundgerüst für den Filter. Korrekturkurve glätten und weitere anpassungen,
# die aufgrund des Vergleichs eines direktional-omni Paares entstehen fehlen noch, da wir so ein paar nicht haben
# Für diese Anpassungen kann man sich an filter_service.py orientieren dort gibt es einige Anpassungen schon
