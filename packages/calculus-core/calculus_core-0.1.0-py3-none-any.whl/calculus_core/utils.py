def normalizar_tipo_solo(  # noqa
    tipo_solo: str, metodo: str, tabela: str | None = None
) -> str:
    """
    Normaliza o tipo de solo para um formato padrão.

    Args:
        tipo_solo: Tipo de solo como string.

    Returns:
        str: Tipo de solo normalizado.
    """
    tipo_solo = tipo_solo.lower().replace(' ', '_').replace('-', '_')
    if metodo == 'décourt_quaresma' and tabela == 'alfa' or tabela == 'beta':
        if tipo_solo in [
            'argila',
            'argila_arenosa',
            'argila_areno_siltosa',
            'argila_siltosa',
            'argila_silto_arenosa',
        ]:
            return 'argila'
        elif tipo_solo in [
            'silte',
            'silte_arenoso',
            'silte_areno_argiloso',
            'silte_argiloso',
            'silte_argilo_arenoso',
        ]:
            return 'silte'
        elif tipo_solo in [
            'areia',
            'areia_com_pedregulhos',
            'areia_siltosa',
            'areia_silto_argilosa',
            'areia_argilosa',
            'areia_argilo_siltosa',
        ]:
            return 'areia'
    if metodo == 'décourt_quaresma' and tabela == 'K':
        if tipo_solo in [
            'argila',
            'argila_arenosa',
            'argila_areno_siltosa',
            'argila_siltosa',
            'argila_silto_arenosa',
        ]:
            return 'argila'
        elif tipo_solo in [
            'silte',
            'silte_arenoso',
            'silte_areno_argiloso',
        ]:
            return 'silte_arenoso'
        elif tipo_solo in [
            'silte_argiloso',
            'silte_argilo_arenoso',
        ]:
            return 'silte_argiloso'
        elif tipo_solo in [
            'areia',
            'areia_com_pedregulhos',
            'areia_siltosa',
            'areia_silto_argilosa',
            'areia_argilosa',
            'areia_argilo_siltosa',
        ]:
            return 'areia'

    if metodo == 'teixeira':
        if tipo_solo in ['argila_siltosa', 'argila_silto_arenosa']:
            return 'argila_siltosa'
        elif tipo_solo in ['silte_argiloso', 'silte_argilo_arenoso']:
            return 'silte_argiloso'
        elif tipo_solo in ['argila_arenosa', 'argila_areno_siltosa']:
            return 'argila_arenosa'
        elif tipo_solo in ['silte_arenoso', 'silte_areno_argiloso']:
            return 'silte_arenoso'
        elif tipo_solo in ['areia_argilosa', 'areia_argilo_siltosa']:
            return 'areia_argilosa'
        elif tipo_solo in ['areia_siltosa', 'areia_silto_argilosa']:
            return 'areia_siltosa'
        elif tipo_solo == 'areia':
            return 'areia'
        elif tipo_solo == 'areia_com_pedregulhos':
            return 'areia_com_pedregulhos'

    if metodo == 'aoki_velloso':
        if tipo_solo == 'areia_com_pedregulhos':
            return 'areia'

    return tipo_solo


def normalizar_tipo_estaca(tipo_estaca: str, metodo: str) -> str:
    """
    Normaliza o tipo de estaca para um formato padrão.

    Args:
        tipo_estaca: Tipo de estaca como string.

    Returns:
        str: Tipo de estaca normalizado.
    """
    tipo_estaca = tipo_estaca.lower().replace(' ', '_').replace('-', '_')
    if metodo == 'décourt_quaresma':
        if tipo_estaca in [
            'cravada',
            'franki',
            'pré_moldada',
            'metálica',
            'ômega',
        ]:
            return 'cravada'
        elif tipo_estaca in [
            'escavada',
            'escavada_bentonita',
            'hélice_contínua',
            'raiz',
            'injetada',
        ]:
            return tipo_estaca
    return tipo_estaca
