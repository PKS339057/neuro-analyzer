import numpy as np


def _detect_delimiter(filepath):
    """
    Читает первую строку файла и определяет разделитель.
    Возвращает ';', '\t' или None (None = пробельные символы).
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            first_line = f.readline().strip()
    except OSError:
        return None

    for delim in [';', '\t']:
        if delim in first_line:
            return delim
    return None  # любой пробельный символ (np.loadtxt по умолчанию)


def load_csv(filepath):
    """
    Загружает ЭЭГ-данные из текстового файла.

    Автоматически определяет разделитель: ';', Tab или пробел/несколько пробелов.
    Поддерживает файлы без заголовка и с заголовком (первая строка пропускается).

    Возвращает: time (сек), signal (мкВ), fs (Гц)
    """
    delim = _detect_delimiter(filepath)

    # Перебираем варианты: текущий разделитель + пропуск 0 или 1 строки
    # При неудаче пробуем следующий разделитель
    candidates = []
    if delim is not None:
        candidates += [(delim, 0), (delim, 1)]
    # Всегда также пробуем whitespace-режим (delim=None)
    if delim != ';':
        candidates += [(None, 0), (None, 1)]
    if delim != '\t':
        candidates += [(None, 0), (None, 1)]
    # Дополнительно — прямой перебор всех вариантов на случай ошибки автодетекта
    for alt in [';', '\t', None]:
        for skip in (0, 1):
            candidates.append((alt, skip))

    # Убираем дубликаты, сохраняя порядок
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)

    last_error = None
    for delimiter, skiprows in unique_candidates:
        try:
            kwargs = {'skiprows': skiprows}
            if delimiter is not None:
                kwargs['delimiter'] = delimiter
            data = np.loadtxt(filepath, **kwargs)

            if data.ndim != 2 or data.shape[1] < 2:
                continue
            if data.shape[0] < 3:
                continue

            time = data[:, 0]
            signal = data[:, 1]

            diffs = np.diff(time)
            if np.any(diffs <= 0):
                continue  # некорректная временная ось

            fs = 1.0 / np.mean(diffs)
            return time, signal, fs

        except Exception as e:
            last_error = e
            continue

    raise ValueError(
        "Не удалось автоматически определить формат файла.\n"
        "Поддерживаются файлы с разделителями: ';', Tab или пробел.\n"
        f"Последняя ошибка: {last_error}"
    )
