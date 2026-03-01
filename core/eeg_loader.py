import numpy as np


def load_csv(filepath):
    """
    Загружает ЭЭГ-данные из CSV файла с разделителем ';'.

    Поддерживает файлы без заголовка и с заголовком.
    Возвращает: time (сек), signal (мкВ), fs (Гц)
    """
    try:
        data = np.loadtxt(filepath, delimiter=';')
    except ValueError:
        # Если первая строка — заголовок, пропускаем её
        data = np.loadtxt(filepath, delimiter=';', skiprows=1)

    time = data[:, 0]
    signal = data[:, 1]
    fs = 1.0 / np.mean(np.diff(time))

    return time, signal, fs
