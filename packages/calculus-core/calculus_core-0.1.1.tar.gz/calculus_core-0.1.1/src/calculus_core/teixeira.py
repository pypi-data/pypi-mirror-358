import math

from .models import Estaca, MetodoCalculo, PerfilSPT
from .utils import normalizar_tipo_estaca, normalizar_tipo_solo

coeficientes_alpha_teixeira_1996 = {
    'argila_siltosa': {
        'pré_moldada': 110,
        'metálica': 110,
        'franki': 100,
        'escavada': 100,
        'raiz': 100,
    },
    'silte_argiloso': {
        'pré_moldada': 160,
        'metálica': 160,
        'franki': 120,
        'escavada': 110,
        'raiz': 110,
    },
    'argila_arenosa': {
        'pré_moldada': 210,
        'metálica': 210,
        'franki': 160,
        'escavada': 130,
        'raiz': 140,
    },
    'silte_arenoso': {
        'pré_moldada': 260,
        'metálica': 260,
        'franki': 210,
        'escavada': 160,
        'raiz': 160,
    },
    'areia_argilosa': {
        'pré_moldada': 300,
        'metálica': 300,
        'franki': 240,
        'escavada': 200,
        'raiz': 190,
    },
    'areia_siltosa': {
        'pré_moldada': 360,
        'metálica': 360,
        'franki': 300,
        'escavada': 240,
        'raiz': 220,
    },
    'areia': {
        'pré_moldada': 400,
        'metálica': 400,
        'franki': 340,
        'escavada': 270,
        'raiz': 260,
    },
    'areia_com_pedregulhos': {
        'pré_moldada': 440,
        'metálica': 440,
        'franki': 380,
        'escavada': 310,
        'raiz': 290,
    },
}

coeficientes_beta_teixeira_1996 = {
    'pré_moldada': 4,
    'metálica': 4,
    'franki': 5,
    'escavada': 4,
    'raiz': 6,
}


class Teixeira(MetodoCalculo):
    def __init__(self, coeficientes_alpha: dict, coeficientes_beta: dict):
        self._coeficientes_alpha = coeficientes_alpha
        self._coeficientes_beta = coeficientes_beta

    def coef_alpha(self, tipo_solo, tipo_estaca):
        tipo_solo = normalizar_tipo_solo(tipo_solo, 'teixeira')
        tipo_estaca = normalizar_tipo_estaca(tipo_estaca, 'teixeira')

        if tipo_solo not in self._coeficientes_alpha:
            raise ValueError(
                (
                    f'Tipo de solo não suportado '
                    f'pelo método de Teixeira: {tipo_solo}'
                )
            )
        if tipo_estaca not in self._coeficientes_alpha[tipo_solo]:
            raise ValueError(
                f'Tipo de estaca não suportado '
                f'pelo método de Teixeira: {tipo_estaca}'
            )
        return self._coeficientes_alpha[tipo_solo][tipo_estaca]

    def coef_beta(self, tipo_estaca):
        tipo_estaca = normalizar_tipo_estaca(tipo_estaca, 'teixeira')

        if tipo_estaca not in self._coeficientes_beta:
            raise ValueError(f'Tipo de estaca inválido: {tipo_estaca}')
        return self._coeficientes_beta[tipo_estaca]

    @staticmethod
    def calcular_Np(perfil_spt: PerfilSPT, cota_assentamento, diametro):
        intervalo_inicio = math.ceil(cota_assentamento - 4 * diametro)
        intervalo_fim = math.ceil(cota_assentamento + 1 * diametro)

        N_spts = [
            perfil_spt.obter_medida(i, aprox=True).N_SPT
            for i in range(intervalo_inicio, intervalo_fim + 1)
        ]

        return sum(N_spts) / len(N_spts) if len(N_spts) > 0 else 0

    @staticmethod
    def calcular_Rp(alfa, Np, area_ponta):
        return alfa * Np * area_ponta

    @staticmethod
    def calcular_Rl(beta, Nl, perimetro, espessura_camada=1):
        return beta * Nl * perimetro * espessura_camada

    @staticmethod
    def calcular_Nl(perfil_spt: PerfilSPT, cota_assentamento):
        N_spts = [
            perfil_spt.obter_medida(i).N_SPT
            for i in range(2, cota_assentamento + 1)
        ]

        return sum(N_spts) / len(N_spts) if len(N_spts) > 0 else 0

    @staticmethod
    def calcular_carga_adm(Rp, Rl):
        """
        Calcula a capacidade de carga admissível da estaca.

        Args:
            Rp: Resistência de ponta da estaca.
            Rl: Resistência lateral da estaca.

        Returns:
            float: Capacidade de carga admissível em kN.
        """
        fs = 2
        nbr_qadm = (Rp + Rl) / fs
        decort_quaresma_qadm = Rp / 4 + Rl / 1.5
        return min(nbr_qadm, decort_quaresma_qadm)

    def calcular(self, perfil_spt: PerfilSPT, estaca: Estaca) -> dict:
        camada_apoio_ponta = perfil_spt.obter_medida(
            estaca.cota_assentamento + 1
        )

        Np = self.calcular_Np(
            perfil_spt, estaca.cota_assentamento, estaca.secao_transversal
        )
        alfa = self.coef_alpha(camada_apoio_ponta.tipo_solo, estaca.tipo)
        Rp = self.calcular_Rp(alfa, Np, estaca.area_ponta())

        Nl = self.calcular_Nl(perfil_spt, estaca.cota_assentamento)
        beta = self.coef_beta(estaca.tipo)

        Rl = self.calcular_Rl(
            beta, Nl, estaca.perimetro(), estaca.cota_assentamento - 1
        )

        carga_adm = self.calcular_carga_adm(Rp, Rl)

        return {
            'resistencia_ponta': Rp,
            'resistencia_lateral': Rl,
            'capacidade_carga': Rp + Rl,
            'capacidade_carga_adm': carga_adm,
        }

    @staticmethod
    def cota_parada(perfil_spt: PerfilSPT) -> int:
        """
        Retorna a cota de parada para o cálculo da estaca.
        Para Teixeira, a cota de parada é a penúltima camada do
        perfil SPT.
        """
        return len(perfil_spt) - 1


teixeira_1996 = Teixeira(
    coeficientes_alpha_teixeira_1996, coeficientes_beta_teixeira_1996
)
