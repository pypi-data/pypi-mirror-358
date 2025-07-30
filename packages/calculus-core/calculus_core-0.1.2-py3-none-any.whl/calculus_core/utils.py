mapeamento_decourt_quaresma = {
    'argila': [
        'argila',
        'argila_arenosa',
        'argila_areno_siltosa',
        'argila_siltosa',
        'argila_silto_arenosa',
    ],
    'silte': [
        'silte',
        'silte_arenoso',
        'silte_areno_argiloso',
        'silte_argiloso',
        'silte_argilo_arenoso',
    ],
    'areia': [
        'areia',
        'areia_com_pedregulhos',
        'areia_siltosa',
        'areia_silto_argilosa',
        'areia_argilosa',
        'areia_argilo_siltosa',
    ],
}

mapeamento_teixeira = {
    'argila_siltosa': ['argila_siltosa', 'argila_silto_arenosa'],
    'silte_argiloso': ['silte_argiloso', 'silte_argilo_arenoso'],
    'argila_arenosa': ['argila_arenosa', 'argila_areno_siltosa'],
    'silte_arenoso': ['silte_arenoso', 'silte_areno_argiloso'],
    'areia_argilosa': ['areia_argilosa', 'areia_argilo_siltosa'],
    'areia_siltosa': ['areia_siltosa', 'areia_silto_argilosa'],
}

mapeamento_aoki_velloso = {'areia': ['areia', 'areia_com_pedregulhos']}

mapeamento_metodos = {
    'décourt_quaresma': mapeamento_decourt_quaresma,
    'teixeira': mapeamento_teixeira,
    'aoki_velloso': mapeamento_aoki_velloso,
}


def normalizar_tipo_solo(
    tipo_solo: str, metodo: str, tabela: str | None = None
) -> str:
    """
    Normaliza o tipo de solo para um formato padrão.

    Args:
        tipo_solo: Tipo de solo como string.

    Returns:
        str: Tipo de solo normalizado.
    """
    tipo_solo_norm = tipo_solo.lower().replace(' ', '_').replace('-', '_')

    mapeamento_solo = mapeamento_metodos.get(metodo, {})

    if metodo == 'décourt_quaresma' and tabela == 'K':
        if tipo_solo_norm == 'silte':
            return 'silte_arenoso'

    if mapeamento_solo:
        for grupo, solos in mapeamento_solo.items():
            if tipo_solo_norm in solos:
                return grupo

    return tipo_solo_norm


def normalizar_tipo_estaca(tipo_estaca: str, metodo: str) -> str:
    """
    Normaliza o tipo de estaca para um formato padrão.

    Args:
        tipo_estaca: Tipo de estaca como string.

    Returns:
        str: Tipo de estaca normalizado.
    """
    tipo_estaca_norm = tipo_estaca.lower().replace(' ', '_').replace('-', '_')
    if metodo == 'décourt_quaresma':
        if tipo_estaca_norm in [
            'cravada',
            'franki',
            'pré_moldada',
            'metálica',
            'ômega',
        ]:
            return 'cravada'
        elif tipo_estaca_norm in [
            'escavada',
            'escavada_bentonita',
            'hélice_contínua',
            'raiz',
            'injetada',
        ]:
            return tipo_estaca_norm
    return tipo_estaca_norm
