# carregar/validar e “derreter” o CSV

import pandas as pd
import unicodedata

input_filename = '../../data/bairros_recife.csv'
output_filename = '../../data/bairros_unique.csv'

try:
    df = pd.read_csv(input_filename)
    
    df_melted = df.melt(var_name='microrregiao_raw', value_name='bairro')
    
    df_melted.dropna(subset=['bairro'], inplace=True)
    df_melted = df_melted[df_melted['bairro'].str.strip() != '']

    df_melted['microrregiao'] = df_melted['microrregiao_raw'].str.split('.').str[0]

    df_final = df_melted[['bairro', 'microrregiao']].copy()

    df_final['bairro'] = df_final['bairro'].str.strip()
    df_final['bairro'] = df_final['bairro'].apply(
        lambda x: ''.join(c for c in unicodedata.normalize('NFD', x)
                          if unicodedata.category(c) != 'Mn') if isinstance(x, str) else x
    )

    df_final.drop_duplicates(subset=['bairro'], inplace=True)
    df_final.sort_values(by='bairro', inplace=True)
    df_final.reset_index(drop=True, inplace=True)

    df_final.to_csv(output_filename, index=False)

    print("Código executado com sucesso e sem avisos!")
    print(f"O arquivo '{output_filename}' foi gerado.")

except FileNotFoundError:
    print(f"Erro: O arquivo em '{input_filename}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")