import math
from abc import ABC, abstractmethod


class Estaca:
    def __init__(
        self,
        tipo: str,
        processo_construcao: str,
        formato: str,
        secao_transversal: float,
        cota_assentamento: int,
    ):
        if formato not in ['circular', 'quadrada']:
            raise ValueError(
                'Formato de estaca deve ser "circular" ou "quadrada".'
            )
        self.tipo = tipo
        self.processo_construcao = processo_construcao
        self.formato = formato
        self.secao_transversal = secao_transversal
        self.cota_assentamento = int(cota_assentamento)

    def area_ponta(self):
        if self.formato == 'circular':
            raio = self.secao_transversal / 2
            return math.pi * (raio**2)
        elif self.formato == 'quadrada':
            largura = self.secao_transversal
            return largura**2

    def perimetro(self):
        if self.formato == 'circular':
            raio = self.secao_transversal / 2
            return 2 * math.pi * raio
        elif self.formato == 'quadrada':
            largura = self.secao_transversal
            return 4 * largura


class MedidaSPT:
    """
    Representa uma única medida do ensaio SPT, agora com suporte
    para registrar condições de impenetrável.
    """

    def __init__(self, profundidade, N_SPT, tipo_solo):
        """
        Args:
            profundidade (float): Profundidade da medida em metros.
            N_SPT (int): Número de golpes (soma dos 2 últimos segmentos de
                15cm).
            tipo_solo (str): Tipo de solo. Pode ser "impenetravel".
        """
        self.profundidade = profundidade
        self.N_SPT = N_SPT
        self.tipo_solo = tipo_solo

    def __repr__(self):
        return (
            f'MedidaSPT(profundidade={self.profundidade}, '
            f'N_SPT={self.N_SPT}, tipo_solo={self.tipo_solo})'
        )


class PerfilSPT:
    def __init__(self, nome_sondagem: str = 'SP-01', confiavel: bool = True):
        self.nome_sondagem = nome_sondagem
        self.confiavel = confiavel
        self.medidas: list[MedidaSPT] = []

    def adicionar_medida(self, profundidade, N_SPT, tipo_solo):
        medida = MedidaSPT(profundidade, N_SPT, tipo_solo)
        self.medidas.append(medida)
        self.medidas.sort(key=lambda x: x.profundidade)

    def adicionar_medidas(self, dados: list[tuple]):
        """
        Adiciona múltiplas medidas ao perfil SPT.

        Args:
            dados (list[tuple]): Lista de tuplas contendo profundidade, N_SPT e
                tipo_solo.
        """
        for profundidade, N_SPT, tipo_solo in dados:
            self.adicionar_medida(profundidade, N_SPT, tipo_solo)
            self.medidas.sort(key=lambda x: x.profundidade)

    def __repr__(self):
        return f'PerfilSPT(nome_sondagem={self.nome_sondagem}, medidas={self.medidas})'  # noqa: E501

    def __len__(self):
        return len(self.medidas)

    def __getitem__(self, index):
        return self.medidas[index]

    def __iter__(self):
        return iter(self.medidas)

    def __contains__(self, profundidade):
        """
        Verifica se uma profundidade específica está registrada no perfil SPT.

        Args:
            profundidade (int): Profundidade a ser verificada.

        Returns:
            bool: True se a profundidade estiver registrada,
                False caso contrário.
        """
        return any(
            medida.profundidade == profundidade for medida in self.medidas
        )

    def obter_medida(self, profundidade: int, aprox: bool = False):
        if not self.medidas:
            raise ValueError('Nenhuma medida registrada no perfil SPT.')

        if profundidade - self.medidas[-1].profundidade == 1 and aprox:
            return MedidaSPT(profundidade, 50, 'impenetravel')
        if profundidade > self.medidas[-1].profundidade and not aprox:
            raise ValueError(
                (
                    f'Profundidade {profundidade}m está abaixo da profundidade'
                    ' máxima registrada.'
                )
            )
        if profundidade < self.medidas[0].profundidade and not aprox:
            raise ValueError(
                (
                    f'Profundidade {profundidade}m está acima da profundidade'
                    ' mínima registrada.'
                )
            )
        for medida in self.medidas:
            if medida.profundidade == profundidade:
                return medida
        if aprox:
            return min(
                self.medidas, key=lambda x: abs(x.profundidade - profundidade)
            )

        raise ValueError(
            f'Medida não encontrada para a profundidade {profundidade}m.'
        )


class MetodoCalculo(ABC):
    """
    Classe abstrata para métodos de cálculo de fundações.
    """

    @abstractmethod
    def calcular(self, perfil_spt: PerfilSPT, estaca: Estaca) -> dict:
        """
        Método abstrato que deve ser implementado por subclasses.
        Realiza o cálculo específico do método de fundação.

        Returns:
            dict: Dicionário com os resultados do cálculo, com chaves:
            {
                'resistencia_ponta',
                'resistencia_lateral',
                'capacidade_carga',
                'capacidade_carga_adm',
            }
        """
        pass
