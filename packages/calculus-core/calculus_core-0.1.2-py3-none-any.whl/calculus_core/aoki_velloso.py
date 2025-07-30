from .models import Estaca, MetodoCalculo, PerfilSPT
from .utils import normalizar_tipo_estaca, normalizar_tipo_solo

coeficientes_aoki_velloso_1975 = {
    'areia': {'k_kpa': 1000, 'alpha_perc': 1.4},
    'areia_siltosa': {'k_kpa': 800, 'alpha_perc': 2.0},
    'areia_silto_argilosa': {'k_kpa': 700, 'alpha_perc': 2.4},
    'areia_argilosa': {'k_kpa': 600, 'alpha_perc': 3.0},
    'areia_argilo_siltosa': {'k_kpa': 500, 'alpha_perc': 2.8},
    'silte': {'k_kpa': 400, 'alpha_perc': 3.0},
    'silte_arenoso': {'k_kpa': 550, 'alpha_perc': 2.2},
    'silte_areno_argiloso': {'k_kpa': 450, 'alpha_perc': 2.8},
    'silte_argiloso': {'k_kpa': 230, 'alpha_perc': 3.4},
    'silte_argilo_arenoso': {'k_kpa': 250, 'alpha_perc': 3.0},
    'argila': {'k_kpa': 200, 'alpha_perc': 6.0},
    'argila_arenosa': {'k_kpa': 350, 'alpha_perc': 2.4},
    'argila_areno_siltosa': {'k_kpa': 300, 'alpha_perc': 2.8},
    'argila_siltosa': {'k_kpa': 220, 'alpha_perc': 4.0},
    'argila_silto_arenosa': {'k_kpa': 330, 'alpha_perc': 3.0},
}
fatores_f1_f2_aoki_velloso_1975 = {
    'franki': {'F1': 2.50, 'F2': lambda f1: 2 * f1},
    'metálica': {'F1': 1.75, 'F2': lambda f1: 2 * f1},
    'pré_moldada': {
        'F1': lambda D: 1 + (D / 0.8),
        'F2': lambda f1: 2 * f1,
    },
    'escavada': {'F1': 3.00, 'F2': lambda f1: 2 * f1},
    'raiz': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'hélice_contínua': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'ômega': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
}

coeficientes_aoki_velloso_1975_laprovitera_1988 = {
    'areia': {
        'k_kpa': 600,
        'alpha_perc': 1.4,
        'alpha_star_perc': 1.4,
    },
    'areia_siltosa': {
        'k_kpa': 530,
        'alpha_perc': 1.9,
        'alpha_star_perc': 1.9,
    },
    'areia_silto_argilosa': {
        'k_kpa': 530,
        'alpha_perc': 2.4,
        'alpha_star_perc': 2.4,
    },
    'areia_argilo_siltosa': {
        'k_kpa': 530,
        'alpha_perc': 2.8,
        'alpha_star_perc': 2.8,
    },
    'areia_argilosa': {
        'k_kpa': 530,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_arenoso': {
        'k_kpa': 480,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_areno_argiloso': {
        'k_kpa': 380,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte': {
        'k_kpa': 480,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_argilo_arenoso': {
        'k_kpa': 380,
        'alpha_perc': 3.0,
        'alpha_star_perc': 3.0,
    },
    'silte_argiloso': {
        'k_kpa': 300,
        'alpha_perc': 3.4,
        'alpha_star_perc': 3.4,
    },
    'argila_arenosa': {
        'k_kpa': 480,
        'alpha_perc': 4.0,
        'alpha_star_perc': 2.6,
    },
    'argila_areno_siltosa': {
        'k_kpa': 380,
        'alpha_perc': 4.5,
        'alpha_star_perc': 3.0,
    },
    'argila_silto_arenosa': {
        'k_kpa': 380,
        'alpha_perc': 5.0,
        'alpha_star_perc': 3.3,
    },
    'argila_siltosa': {
        'k_kpa': 250,
        'alpha_perc': 5.5,
        'alpha_star_perc': 3.6,
    },
    'argila': {
        'k_kpa': 250,
        'alpha_perc': 6.0,
        'alpha_star_perc': 4.0,
    },
}

fatores_f1_f2_aoki_velloso_1975_laprovitera_1988 = {
    'franki': {'F1': 2.50, 'F2': 3.0},
    'metálica': {'F1': 2.4, 'F2': 3.4},
    'pré_moldada': {
        'F1': 2.0,
        'F2': 3.5,
    },
    'escavada': {'F1': 4.50, 'F2': 4.50},
    'raiz': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'hélice_contínua': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
    'ômega': {'F1': 2.00, 'F2': lambda f1: 2 * f1},
}


class AokiVelloso(MetodoCalculo):
    """
    Classe para calcular a capacidade de carga de estacas
     pelo método de Aoki e Velloso (1975).
    """

    def __init__(self, coeficientes_aoki_velloso: dict, fatores_f1_f2: dict):
        self._coeficientes_aoki_velloso = coeficientes_aoki_velloso
        self._fatores_f1_f2 = fatores_f1_f2

    def obter_fatores_F1_F2(
        self,
        tipo_estaca: str,
        diametro_estaca: float | None = None,
    ):
        """
        Busca e calcula os fatores F1 e F2 para um dado tipo de estaca.
        """
        tipo_estaca = normalizar_tipo_estaca(tipo_estaca, 'aoki_velloso')

        if tipo_estaca not in self._fatores_f1_f2:
            raise ValueError(
                f'Tipo de estaca não suportado '
                f'pelo método de Aoki e Velloso: {tipo_estaca}'
            )

        dados_fator = self._fatores_f1_f2[tipo_estaca]
        valor_f1 = dados_fator['F1']
        func_f2 = dados_fator['F2']

        if callable(valor_f1):
            if diametro_estaca is None:
                raise ValueError(
                    (
                        f'Diâmetro da estaca é necessário '
                        f'para calcular F1 para estaca {tipo_estaca}.'
                    )
                )
            f1_calculado = valor_f1(diametro_estaca)
        else:
            f1_calculado = valor_f1

        if callable(func_f2):
            f2_calculado = func_f2(f1_calculado)
        else:
            f2_calculado = func_f2

        return f1_calculado, f2_calculado

    def obter_coeficiente_K(self, tipo_solo: str) -> float:
        """
        Obtém o coeficiente K para um tipo de solo específico.

        Args:
            perfil_spt: Perfil SPT contendo as medidas de N_SPT e tipo de solo.
            tipo_solo: Tipo de solo para obter o coeficiente K.

        Returns:
            float: Coeficiente K em kPa.
        """

        tipo_solo = normalizar_tipo_solo(tipo_solo, 'aoki_velloso')

        if tipo_solo not in self._coeficientes_aoki_velloso:
            raise ValueError(
                f'Tipo de solo não suportado '
                f'pelo método de Aoki e Velloso: {tipo_solo}'
            )
        return self._coeficientes_aoki_velloso[tipo_solo]['k_kpa']

    def obter_coeficiente_alfa(
        self, perfil_spt: PerfilSPT, tipo_solo: str
    ) -> float:
        """
        Obtém o coeficiente alfa para um tipo de solo específico.

        Args:
            perfil_spt: Perfil SPT contendo as medidas de N_SPT e tipo de solo.
            tipo_solo: Tipo de solo para obter o coeficiente alfa.

        Returns:
            float: Coeficiente alfa em porcentagem.
        """

        tipo_solo = normalizar_tipo_solo(tipo_solo, 'aoki_velloso')

        if tipo_solo not in self._coeficientes_aoki_velloso:
            raise ValueError(
                f'Tipo de solo não suportado '
                f'pelo método de Aoki e Velloso: {tipo_solo}'
            )
        if (
            not perfil_spt.confiavel
            and 'alpha_star_perc' in self._coeficientes_aoki_velloso[tipo_solo]
        ):
            return (
                self._coeficientes_aoki_velloso[tipo_solo]['alpha_star_perc']
                / 100
            )
        return self._coeficientes_aoki_velloso[tipo_solo]['alpha_perc'] / 100

    @staticmethod
    def calcular_Np(perfil_spt: PerfilSPT, cota_assentamento: int):
        """
            Encontra o N_SPT na camada de apoio da ponta.

        Args:
            perfil_spt: Lista de tuplas (N_SPT, tipo_solo).
            cota: Cota para calcular o N_SPT médio.

        Returns:
            float: N_SPT na cota de apoio da ponta.
        """

        if cota_assentamento not in perfil_spt:
            raise ValueError('Cota assentamento inválida para o perfil SPT.')

        cota_apoio_ponta = cota_assentamento + 1
        if cota_apoio_ponta not in perfil_spt:
            raise ValueError(
                'Cota de apoio da ponta inválida para o perfil SPT.'
            )

        camada_apoio_ponta = perfil_spt.obter_medida(cota_apoio_ponta)

        return camada_apoio_ponta.N_SPT

    @staticmethod
    def calcular_Rp(K, Np, f1, area_ponta):
        """
        Calcula a resistência de ponta da estaca.

        Args:
            K: Coeficiente K do tipo de solo.
            Np: N_SPT na cota de apoio da ponta da estaca.
            f1: Fator F1 calculado para o tipo de estaca.
            area_ponta: Área da ponta da estaca.

        Returns:
            float: Resistência de ponta em kN.
        """
        return (K * Np) / f1 * area_ponta

    @staticmethod
    def calcular_Rl_parcial(alfa, K, Nl, f2, perimetro, espessura_camada=1):
        """
        Calcula a resistência lateral parcial da estaca.

        Args:
            alfa: Coeficiente alfa do tipo de solo.
            K: Coeficiente K do tipo de solo.
            Nl: N_SPT medio na camada de solo lateral.
            f2: Fator F2 calculado para o tipo de estaca.
            perimetro: Perímetro da seção transversal da estaca.
            espessura_camada: Espessura da camada de solo em metros.

        Returns:
            float: Resistência lateral parcial em kN.
        """
        return perimetro * espessura_camada * (alfa * K * Nl) / f2

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
        return (Rp + Rl) / fs

    def calcular(self, perfil_spt: PerfilSPT, estaca: Estaca) -> dict:
        """
        Calcula a capacidade de carga de estacas
        pelo método de Aoki e Velloso (1975).

        Args:
            perfil_spt: Perfil SPT contendo as medidas de N_SPT e tipo de solo.
            estaca: Objeto Estaca contendo informações sobre a estaca.

        Returns:
            dict: Dicionário contendo as resistências de ponta,
            resistência lateral parcial,
            resistência lateral total e total da estaca.
        """

        # Cálculo da Resistência de Ponta (Rp)
        Np = self.calcular_Np(perfil_spt, estaca.cota_assentamento)

        camada_apoio_ponta = perfil_spt.obter_medida(
            estaca.cota_assentamento + 1
        )
        K = self.obter_coeficiente_K(camada_apoio_ponta.tipo_solo)
        f1, f2 = self.obter_fatores_F1_F2(
            estaca.tipo, estaca.secao_transversal
        )

        Rp = self.calcular_Rp(K, Np, f1, estaca.area_ponta())

        # Cálculo da Resistência Lateral (Rl)
        Rl = 0
        Rl_parcial = 0
        for cota in range(2, estaca.cota_assentamento + 1):
            camada_lateral = perfil_spt.obter_medida(cota)

            K = self.obter_coeficiente_K(camada_lateral.tipo_solo)
            alfa = self.obter_coeficiente_alfa(
                perfil_spt, camada_lateral.tipo_solo
            )
            Rl_parcial = self.calcular_Rl_parcial(
                alfa,
                K,
                camada_lateral.N_SPT,
                f2,
                estaca.perimetro(),
                espessura_camada=1,
            )
            Rl += Rl_parcial

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
        Para Aoki e Velloso, a cota de parada é a última camada do perfil SPT.
        """
        return len(perfil_spt) - 1


aoki_velloso_1975 = AokiVelloso(
    coeficientes_aoki_velloso=coeficientes_aoki_velloso_1975,
    fatores_f1_f2=fatores_f1_f2_aoki_velloso_1975,
)
aoki_velloso_1975_laprovitera_1988 = AokiVelloso(
    coeficientes_aoki_velloso=coeficientes_aoki_velloso_1975_laprovitera_1988,
    fatores_f1_f2=fatores_f1_f2_aoki_velloso_1975_laprovitera_1988,
)
