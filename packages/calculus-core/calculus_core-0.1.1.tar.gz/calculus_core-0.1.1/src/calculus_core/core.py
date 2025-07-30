from .aoki_velloso import AokiVelloso
from .decourt_quaresma import DecourtQuaresma
from .models import Estaca, PerfilSPT
from .teixeira import Teixeira


def calcular_capacidade_estaca(
    metodo_calculo: AokiVelloso | Teixeira | DecourtQuaresma,
    perfil_spt: PerfilSPT,
    tipo_estaca: str,
    processo_construcao: str,
    formato: str,
    secao_transversal: float,
):
    """
    Calcula a capacidade de carga de uma estaca metro a metro
    usando o método especificado.

    Args:
        metodo_calculo (AokiVelloso | Teixeira | DecourtQuaresma):
            Método de cálculo a ser utilizado.
        perfil_spt: Perfil SPT da estaca.
        tipo_estaca: Tipo de estaca (cravada, franki, pré_moldada, metálica,
            ômega, escavada, escavada_bentonita, hélice_contínua, raiz,
            injetada).
        processo_construcao: escavada, deslocamento.
        formato: Formato da estaca (circular, quadrada).
        secao_transversal: Seção transversal da estaca em metros.

    Returns:
        dict: Resistências de ponta, lateral e total em kN.
    """

    resultado: list[dict] = []
    cota_parada = metodo_calculo.cota_parada(perfil_spt)
    for i in range(1, cota_parada + 1):
        estaca = Estaca(
            tipo=tipo_estaca,
            processo_construcao=processo_construcao,
            formato=formato,
            secao_transversal=secao_transversal,
            cota_assentamento=i,
        )

        resultado_estaca = metodo_calculo.calcular(perfil_spt, estaca)
        resultado.append(
            {
                'cota': i,
                'resistencia_ponta': resultado_estaca['resistencia_ponta'],
                'resistencia_lateral': resultado_estaca['resistencia_lateral'],
                'capacidade_carga': resultado_estaca['capacidade_carga'],
                'capacidade_carga_adm': resultado_estaca[
                    'capacidade_carga_adm'
                ],
            }
        )
    return resultado
