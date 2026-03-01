import numpy as np
from scipy.signal import welch


BANDS = {
    'Delta': (0.5,  4.0),
    'Theta': (4.0,  8.0),
    'Alpha': (8.0,  13.0),
    'Beta':  (13.0, 30.0),
    'Gamma': (30.0, 50.0),
}


def compute_psd(signal, fs):
    """
    Вычисляет Power Spectral Density методом Welch.

    Возврат: freqs (Гц), psd (мкВ²/Гц)
    """
    nperseg = min(len(signal), 2048)
    freqs, psd = welch(signal, fs, nperseg=nperseg)
    return freqs, psd


def compute_band_powers(freqs, psd):
    """
    Вычисляет мощность в каждом диапазоне ЭЭГ-ритмов и нормализует в проценты.

    Возврат: {'Delta': 12.5, 'Theta': 18.3, 'Alpha': 45.1, 'Beta': 18.2, 'Gamma': 5.9}
    """
    powers = {}
    for band_name, (low, high) in BANDS.items():
        mask = (freqs >= low) & (freqs <= high)
        powers[band_name] = np.trapz(psd[mask], freqs[mask])

    total = sum(powers.values())
    if total == 0:
        return {k: 0.0 for k in powers}

    return {k: (v / total) * 100.0 for k, v in powers.items()}
