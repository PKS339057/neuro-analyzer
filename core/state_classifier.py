INTERPRETATIONS = {
    'Delta': 'Глубокий сон или сильное расслабление',
    'Theta': 'Медитативное состояние или лёгкая дремота',
    'Alpha': 'Состояние спокойного бодрствования',
    'Beta':  'Активное мышление и концентрация',
    'Gamma': 'Высокая когнитивная активность',
}


def compute_state_indices(band_powers):
    """
    Вычисляет индексы состояния на основе относительной мощности ритмов.

    Возврат: {'relaxation': X, 'concentration': Y, 'drowsiness': Z}
    """
    delta = band_powers['Delta']
    theta = band_powers['Theta']
    alpha = band_powers['Alpha']
    beta  = band_powers['Beta']

    relaxation    = alpha / (beta + theta + 0.01) * 100
    concentration = beta  / (alpha + theta + 0.01) * 100
    drowsiness    = (delta + theta) / (alpha + beta + 0.01) * 100

    return {
        'relaxation':    min(relaxation,    100.0),
        'concentration': min(concentration, 100.0),
        'drowsiness':    min(drowsiness,    100.0),
    }


def generate_conclusion(band_powers, state_indices, duration):
    """
    Генерирует текстовое заключение по результатам анализа ЭЭГ.

    Возврат: строка с заключением.
    """
    dominant = max(band_powers, key=band_powers.get)
    dominant_pct = band_powers[dominant]

    lines = [
        "ЗАКЛЮЧЕНИЕ:",
        "",
        f"На основе анализа ЭЭГ-сигнала длительностью {duration:.1f} секунд:",
        "",
        f"✓ Доминируют {dominant}-волны ({dominant_pct:.0f}%)",
        f"  → {INTERPRETATIONS[dominant]}",
        "",
        f"✓ Индекс расслабления:  {state_indices['relaxation']:.0f}%",
        f"✓ Индекс концентрации: {state_indices['concentration']:.0f}%",
        f"✓ Индекс сонливости:   {state_indices['drowsiness']:.0f}%",
        "",
        "ИТОГ: " + _make_summary(state_indices),
    ]

    return "\n".join(lines)


def _make_summary(state_indices):
    r = state_indices['relaxation']
    c = state_indices['concentration']
    d = state_indices['drowsiness']

    if d > 60:
        return "Признаки сонливости. Рекомендуется отдых."
    if r > 60:
        return "Расслабленное состояние. Подходит для отдыха, медитации."
    if c > 60:
        return "Высокая концентрация. Подходит для сложных задач."
    return "Сбалансированное состояние."
