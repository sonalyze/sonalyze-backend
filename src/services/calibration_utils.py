import numpy as np


def calculate_latency(original: np.ndarray, 
                      recorded: np.ndarray, 
                      sample_rate: int) -> dict:
        # Normalisierung für saubere Korrelation
        original = original / np.max(np.abs(original))
        recorded = recorded / np.max(np.abs(recorded))

        # Kreuzkorrelation für Latenzschätzung
        corr = np.correlate(recorded, original, mode="full")
        lag = np.argmax(corr) - len(original) + 1
        latency_sec = lag / sample_rate

        return {
                "lag_samples": int(lag),
                "latency_seconds": round(latency_sec, 6)
        }

def calculate_latency_with_correlation(original: np.ndarray, 
                                       recorded: np.ndarray, 
                                       sample_rate: int) -> dict:
    original = original / np.max(np.abs(original))
    recorded = recorded / np.max(np.abs(recorded))

    corr = np.correlate(recorded, original, mode="full")
    lag = np.argmax(corr) - len(original) + 1
    latency_sec = lag / sample_rate

    return {
        "lag_samples": int(lag),
        "latency_seconds": round(latency_sec, 6),
        "correlation": corr.tolist()  # 👈 fürs Frontend
    }
