import time
import requests
from bs4 import BeautifulSoup

import pandas as pd
import matplotlib.pyplot as plt

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image


def get_data():

    url = 'https://www.uol.com.br/esporte/futebol/campeonatos/brasileirao/'
    response = requests.get(url)
    content = BeautifulSoup(response.content, 'html.parser')

    time.sleep(1)
    table = content.findAll('table', attrs={'class': ['data-table', 'name']})
    tbody01 = table[0].find('tbody')
    tbody02 = table[1].find('tbody')

    tr01 = tbody01.findAll('tr')
    tr02 = tbody02.findAll('tr')

    name_team = []
    data_team = []

    for tr in tr01:
        td = tr.find('td')
        span = td.find('span', attrs={'class': 'name'})
        name = span.find('div', attrs={'class': ['visible-sm', 'visible-lg']})
        name_team.append(name.text)

    td_list = [tr.findAll('td') for tr in tr02]

    n = 0

    for td in td_list:
        dict_data = {
            'Nome': name_team[n],
            'PG': td[0].text,
            'J': td[1].text,
            'V': td[2].text,
            'E': td[3].text,
            'D': td[4].text,
            'GC': td[5].text,
            'GP': td[6].text,
            'SG': td[7].text,
            '%': td[8].text,
        }
        data_team.append(dict_data)
        n += 1

    df = pd.DataFrame(data_team)

    cols_to_convert = ['J', 'V', 'E', 'D', 'SG', 'GC', 'GP', 'PG', '%']
    df[cols_to_convert] = df[cols_to_convert].astype(int)

    df['Porcentagem_V'] = df['V'] / df['J'] * 100
    df['Porcentagem_D'] = df['D'] / df['J'] * 100
    df['Porcentagem_E'] = df['E'] / df['J'] * 100

    df_info = df[['Nome', 'J', 'Porcentagem_V', 'Porcentagem_D', 'Porcentagem_E']]

    with pd.ExcelWriter('brasileirao.xlsx', engine='openpyxl') as writer:
        # Salvar DataFrame como planilha de dados
        df.to_excel(writer, sheet_name='Dados', index=False)

        workbook = writer.book
        worksheet = workbook.create_sheet('Gráfico')

        # Criar um gráfico de barras
        bar_width = 0.5

        fig, ax_partidas = plt.subplots(figsize=(12, 8))  # Ajuste o tamanho da figura conforme necessário
        df.sort_values(by='SG', ascending=False).plot(kind='bar', ax=ax_partidas, x='Nome', y='SG')
        plt.title('Percentual (%) de gols por Time')
        plt.xlabel('Time')
        plt.ylabel('Percentual (%)')
        ax_partidas.set_xticklabels(ax_partidas.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig('grafico_temp1.png')
        img1 = Image('grafico_temp1.png')
        worksheet.add_image(img1, 'A1')

        fig, ax = plt.subplots(figsize=(12, 8))
        df_info.set_index('Nome').plot(kind='bar', stacked=True, ax=ax, legend=None, width=bar_width)
        plt.title('Informações sobre Jogos e Porcentagens')
        plt.xlabel('Time')
        plt.ylabel('Valores')

        plt.tight_layout()

        for p in ax.patches:
            width, height = p.get_width(), p.get_height()
            x, y = p.get_xy()
            ax.annotate(f'{height:.2f}%', (x + width / 2, y + height / 2), ha='center', va='center')

        plt.savefig('grafico_temp2.png')
        img2 = Image('grafico_temp2.png')

        worksheet.add_image(img2, 'R1')

        if 'Sheet' in workbook.sheetnames:
            workbook.remove(workbook['Sheet'])

    import os
    os.remove('grafico_temp1.png')
    os.remove('grafico_temp2.png')

    print('Arquivo gerado com sucesso!')
