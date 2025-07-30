import altair as alt
import pandas as pd
import streamlit as st

from calculus_core.aoki_velloso import (
    aoki_velloso_1975,
    aoki_velloso_1975_laprovitera_1988,
)
from calculus_core.core import calcular_capacidade_estaca
from calculus_core.decourt_quaresma import decort_quaresma_1978_revisado
from calculus_core.models import PerfilSPT
from calculus_core.teixeira import teixeira_1996

st.set_page_config(
    page_title='Calculus-Core Interface',
    page_icon='🏗️',
    layout='wide',
)

st.title('🏗️ Proposta de interface para Calculus-Core')
st.write(
    (
        'Esta aplicação permite calcular a capacidade de carga de estacas '
        'utilizando os métodos de cálculo incluido pacote `calculus-core`.'
    )
)

with st.sidebar:
    st.header('Parâmetros de Entrada')

    metodos = {
        'Aoki e Velloso (1975)': aoki_velloso_1975,
        (
            'Aoki e Velloso (1975) por Laprovitera (1988)'
        ): aoki_velloso_1975_laprovitera_1988,
        'Décourt e Quaresma (1978)': decort_quaresma_1978_revisado,
        'Teixeira (1996)': teixeira_1996,
    }

    metodo_selecionado = st.selectbox(
        'Selecione o Método de Cálculo', list(metodos.keys())
    )

    st.subheader('Dados da Estaca')
    tipo_estaca = st.selectbox(
        'Tipo de Estaca',
        [
            'Pré-moldada',
            'Metálica',
            'Franki',
            'Escavada',
            'Raiz',
            'Hélice Contínua',
            'Ômega',
        ],
    )
    processo_construcao = st.selectbox(
        'Processo de Construção', ['Deslocamento', 'Escavada']
    )
    formato = st.selectbox('Formato da Estaca', ['Circular', 'Quadrada'])
    secao_transversal = st.number_input(
        'Seção Transversal (m)', min_value=0.1, value=0.3, step=0.01
    )

    st.subheader('Perfil de Sondagem (SPT)')
    st.write('Insira os dados do ensaio SPT abaixo:')

    solos_validos = {
        'Argila': 'argila',
        'Argila Arenosa': 'argila_arenosa',
        'Argila Areno Siltosa': 'argila_areno_siltosa',
        'Argila Siltosa': 'argila_siltosa',
        'Argila Silto Arenosa': 'argila_silto_arenosa',
        'Silte': 'silte',
        'Silte Arenoso': 'silte_arenoso',
        'Silte Areno Argiloso': 'silte_areno_argiloso',
        'Silte Argiloso': 'silte_argiloso',
        'Silte Argilo Arenoso': 'silte_argilo_arenoso',
        'Areia': 'areia',
        'Areia com Pedregulhos': 'areia_com_pedregulhos',
        'Areia Siltosa': 'areia_siltosa',
        'Areia Silto Argilosa': 'areia_silto_argilosa',
        'Areia Argilosa': 'areia_argilosa',
        'Areia Argilo Siltosa': 'areia_argilo_siltosa',
    }
    lista_solos_validos = list(solos_validos.keys())

    # Exemplo de dados para o perfil SPT
    exemplo_spt = [
        {'Profundidade (m)': 1, 'N_SPT': 3, 'Tipo de Solo': 'Argila Arenosa'},
        {'Profundidade (m)': 2, 'N_SPT': 3, 'Tipo de Solo': 'Argila Arenosa'},
        {'Profundidade (m)': 3, 'N_SPT': 5, 'Tipo de Solo': 'Argila Arenosa'},
        {'Profundidade (m)': 4, 'N_SPT': 6, 'Tipo de Solo': 'Argila Arenosa'},
        {'Profundidade (m)': 5, 'N_SPT': 8, 'Tipo de Solo': 'Argila Arenosa'},
        {'Profundidade (m)': 6, 'N_SPT': 13, 'Tipo de Solo': 'Areia Argilosa'},
        {'Profundidade (m)': 7, 'N_SPT': 17, 'Tipo de Solo': 'Areia Argilosa'},
        {'Profundidade (m)': 8, 'N_SPT': 25, 'Tipo de Solo': 'Areia Argilosa'},
        {
            'Profundidade (m)': 9,
            'N_SPT': 27,
            'Tipo de Solo': 'Areia Silto Argilosa',
        },
        {
            'Profundidade (m)': 10,
            'N_SPT': 32,
            'Tipo de Solo': 'Areia Silto Argilosa',
        },
        {
            'Profundidade (m)': 11,
            'N_SPT': 36,
            'Tipo de Solo': 'Areia com Pedregulhos',
        },
    ]
    dados_spt_df = pd.DataFrame(exemplo_spt)

    # 2. EDITOR DE DADOS COM CAIXA DE SELEÇÃO
    # O `st.data_editor` agora usa uma configuração de coluna específica.
    spt_editado_df = st.data_editor(
        dados_spt_df,
        column_config={
            'Tipo de Solo': st.column_config.SelectboxColumn(
                'Tipo de Solo',
                help='Selecione o tipo de solo para a camada correspondente.',
                options=lista_solos_validos,
                required=True,  # Garante que um valor seja sempre selecionado
            )
        },
        num_rows='dynamic',
        use_container_width=True,
    )


if st.button('Calcular Capacidade de Carga', type='primary'):
    with st.spinner('Calculando...'):
        try:
            perfil_spt = PerfilSPT()
            dados_spt_list = [
                (
                    row['Profundidade (m)'],
                    row['N_SPT'],
                    solos_validos[row['Tipo de Solo']],
                )
                for index, row in spt_editado_df.iterrows()
            ]
            perfil_spt.adicionar_medidas(dados_spt_list)

            metodo_calculo = metodos[metodo_selecionado]

            resultado = calcular_capacidade_estaca(
                metodo_calculo=metodo_calculo,
                perfil_spt=perfil_spt,
                tipo_estaca=tipo_estaca.lower().replace(' ', '_'),
                processo_construcao=processo_construcao.lower(),
                formato=formato.lower(),
                secao_transversal=secao_transversal,
            )

            if resultado:
                st.success('Cálculo concluído com sucesso!')
                resultado_df = pd.DataFrame(resultado)

                resultado_df.rename(
                    columns={
                        'cota': 'Cota (m)',
                        'resistencia_ponta': 'Resistência de Ponta (kN)',
                        'resistencia_lateral': 'Resistência Lateral (kN)',
                        'capacidade_carga': 'Capacidade de Carga (kN)',
                        'capacidade_carga_adm': 'Carga Admissível (kN)',
                    },
                    inplace=True,
                )

                st.subheader('Resultados do Cálculo')
                st.dataframe(
                    resultado_df, height=350, use_container_width=True
                )

                st.subheader('Gráfico da Capacidade de Carga Admissível')
                chart = (
                    alt.Chart(resultado_df)
                    .mark_line(point=True, tooltip=True)
                    .encode(
                        x=alt.X(
                            'Cota (m):Q',
                            axis=alt.Axis(title='Profundidade (m)'),
                        ),
                        y=alt.Y(
                            'Carga Admissível (kN):Q',
                            axis=alt.Axis(title='Carga Admissível (kN)'),
                        ),
                    )
                    .interactive()
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning(
                    (
                        'Nenhum resultado foi gerado. '
                        'Verifique os dados de entrada.'
                    )
                )

        except ValueError as e:
            st.error(f'Ocorreu um erro: {e}')
        except Exception as e:
            st.error(f'Um erro inesperado ocorreu: {e}')

# --- Rodapé ---
st.markdown('---')
st.markdown(
    (
        'Desenvolvido como projeto de conclusão de curso de Engenharia Civil '
        'pelo IFTO - Campus Palmas. '
        'Por [Kaio Henrique Pires da Silva](https://www.linkedin.com/in/kaiosilva-dataeng/).'
    )
)
st.markdown(
    'Para mais informações, visite o '
    '[repositório](https://github.com/kaiosilva-dataeng/calculus-core).'
)
