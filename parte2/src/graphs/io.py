import pandas as pd
import sys

input_file = "../../data/steam.csv"
output_file = "../../data/steam_filtrado.csv"
required_cols = ['name', 'genres', 'positive_ratings', 'negative_ratings']

print(f"Iniciando o processo de filtragem...")
print(f"Arquivo de entrada: {input_file}")
print(f"Arquivo de saída: {output_file}")

try:
    print(f"Lendo '{input_file}'...")
    df = pd.read_csv(input_file)
    print("Leitura concluída.")

    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print("\n--- ERRO ---")
        print(f"O arquivo '{input_file}' não contém as seguintes colunas obrigatórias:")
        for col in missing_cols:
            print(f"- {col}")
        print("O arquivo filtrado NÃO foi gerado.")
        sys.exit() 

    print(f"Filtrando pelas colunas: {required_cols}")
    df_filtrado = df[required_cols]

    df_filtrado.to_csv(output_file, index=False)
    
    print("\n--- SUCESSO ---")
    print(f"O arquivo '{output_file}' foi gerado com sucesso.")
    print(f"Total de linhas processadas: {len(df_filtrado)}")

except FileNotFoundError:
    print(f"\n--- ERRO ---")
    print(f"O arquivo '{input_file}' não foi encontrado.")
    print("Por favor, coloque o 'steam.csv' no mesmo diretório deste script.")

except pd.errors.EmptyDataError:
    print(f"\n--- ERRO ---")
    print(f"O arquivo '{input_file}' está vazio.")

except Exception as e:
    print(f"\n--- ERRO INESPERADO ---")
    print(f"Ocorreu um erro: {e}")