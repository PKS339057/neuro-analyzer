import numpy as np
from scipy.signal import butter, filtfilt


def bandpass_filter(signal, lowcut, highcut, fs, order=4):
    """
    Полосовой фильтр Баттерворта.

    signal  — входной массив амплитуд
    lowcut  — нижняя граница (Гц)
    highcut — верхняя граница (Гц)
    fs      — частота дискретизации (Гц)
    order   — порядок фильтра
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = min(highcut / nyquist, 0.999)  # не выходим за пределы [0, 1)

    if low <= 0 or high <= 0 or low >= high:
        raise ValueError(
            f"Некорректные границы фильтра: {lowcut}-{highcut} Гц при fs={fs:.1f} Гц"
        )

    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)
