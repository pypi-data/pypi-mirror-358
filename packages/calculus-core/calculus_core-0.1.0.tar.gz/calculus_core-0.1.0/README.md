# CALCULUS-CORE

Este projeto tem como objetivo ser um pacote python para cálculo de capacidade de carga em fundações profundas por meio da interação solo - estaca utilizandos os métodos semiempiricos de Aoki e Velloso (1975), Aoki e Velloso módificado por Laprovitera (1988), Décourt e Quaresma (1978) e Teixeira (1996).

em src/calculus_core contém as seguintes implementações:

- aoki_velloso.py: Implementação do método de cálculo de estacas de Aoki e Velloso (1975).
- decourt_quaresma.py: Implementação do método de cálculo de estacas de Decourt e Quaresma (1978).
- teixeira.py: Implementação do método de cálculo de estacas de Teixeira (1996).
- models.py: Definição dos modelos utilizados nos cálculos.
- utils.py: Funções utilitárias para normalização de tipos de estacas e solo.
- main.py: Função de cálculo de capacidade de carga metro a metro.

## Instalação

### Pré-requisito

- Python 3.13
- Astral uv

Ao utilizar astral uv, você ganhar automaticamente um gerenciador de versões da linguaguem python.

Windows

Abra o terminal PowerShell e execute o código abaixo.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS e Linux

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Instalando o pacote

1. Inicie um projeto

```sh
uv init <nome-do-seu-projeto>
```

2. Acesse a pasta do projeto

```
cd <nome-do-seu-projeto>
```

3. Instale o pacote com uv:

```sh
uv add https://github.com/kaiosilva-dataeng/calculus-core.git
```

## Como Usar

Cálculo usando Aoki e Velloso (1975):

Crie um arquivo python e copie e cole o código de exemplo abaixo:

```python
# Faça a importação do objeto referente ao método de cálculo desejado
from calculus_core.aoki_velloso import aoki_velloso_1975
# Importe os models de Estaca e PerfilSPT
from calculus_core.models import Estaca, PerfilSPT

# Crie uma instancia do perfil SPT e adicione as camadas de solo.
perfil_spt = PerfilSPT()
perfil_spt.adicionar_medidas(
    [
        (1, 3, 'argila_arenosa'),
        (2, 3, 'argila_arenosa'),
        (3, 5, 'argila_arenosa'),
        (4, 6, 'argila_arenosa'),
        (5, 8, 'argila_arenosa'),
        (6, 13, 'areia_argilosa'),
        (7, 17, 'areia_argilosa'),
        (8, 25, 'areia_argilosa'),
        (9, 27, 'areia_silto_argilosa'),
        (10, 32, 'areia_silto_argilosa'),
        (11, 36, 'areia_silto_argilosa'),
    ]
)

# Crie uma instancia da estaca
estaca = Estaca(
    tipo='pré-moldada',
    processo_construcao='deslocamento',
    formato='quadrada',
    secao_transversal=0.3,
    cota_assentamento=10,
)

# Execute o cálculo
resultado = aoki_velloso_1975.calcular(perfil_spt, estaca)
print(resultado)
```

Veja mais exemplos em [Notebooks](notebooks).

# Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

# Créditos

Este projeto foi desenvolvido por Kaio Henrique Pires da Silva.
