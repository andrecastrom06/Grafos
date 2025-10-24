import pandas as pd
import sys

input_file = "../../data/flight.csv"
output_file = "../../data/flight_filtrado.csv"

required_cols = ['from_country', 'dest_country', 'flight_number', 'departure_time', 'arrival_time']
final_cols = ['from_country', 'dest_country', 'flight_number', 'duration_minutes']

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

    print(f"Filtrando pelas colunas necessárias para o processo: {required_cols}")
    df_filtrado = df[required_cols].copy() 
    linhas_antes_null = len(df_filtrado)
    print(f"Removendo linhas com valores nulos... (Total atual: {linhas_antes_null} linhas)")
    df_filtrado = df_filtrado.dropna()
    linhas_removidas_null = linhas_antes_null - len(df_filtrado)
    print(f"{linhas_removidas_null} linhas com valores nulos foram removidas.")

    if not df_filtrado.empty:
        print("Convertendo 'departure_time' e 'arrival_time' para formato de data...")
        
        df_filtrado['departure_time'] = pd.to_datetime(df_filtrado['departure_time'], errors='coerce')
        df_filtrado['arrival_time'] = pd.to_datetime(df_filtrado['arrival_time'], errors='coerce')

        linhas_antes_nat = len(df_filtrado)
        df_filtrado = df_filtrado.dropna(subset=['departure_time', 'arrival_time'])
        linhas_removidas_nat = linhas_antes_nat - len(df_filtrado)
        if linhas_removidas_nat > 0:
            print(f"{linhas_removidas_nat} linhas removidas por terem datas inválidas ('NaT').")

        print("Calculando a duração do voo em minutos...")
        duracao_timedelta = df_filtrado['arrival_time'] - df_filtrado['departure_time']
        df_filtrado['duration_minutes'] = (duracao_timedelta.dt.total_seconds() / 60).astype(int)
        print(f"Nova coluna 'duration_minutes' criada.")

        print(f"Removendo voos duplicados (com base em 'flight_number')... (Total atual: {len(df_filtrado)} linhas)")
        linhas_antes_duplicatas = len(df_filtrado)
        df_filtrado = df_filtrado.drop_duplicates(subset=['flight_number'], keep='first')
        linhas_removidas_duplicatas = linhas_antes_duplicatas - len(df_filtrado)
        print(f"{linhas_removidas_duplicatas} linhas duplicadas (flight_number) foram removidas.")

    else:
        print("DataFrame vazio após remoção de nulos. Pulando filtros de data.")

    print(f"Selecionando colunas finais para o output: {final_cols}")
    df_filtrado = df_filtrado[final_cols]
    
    df_filtrado.to_csv(output_file, index=False)
    
    print("\n--- SUCESSO ---")
    print(f"O arquivo '{output_file}' foi gerado com sucesso.")
    print(f"Total de linhas processadas: {len(df_filtrado)}")

except FileNotFoundError:
    print(f"\n--- ERRO ---")
    print(f"O arquivo '{input_file}' não foi encontrado.")
    print(f"Por favor, verifique o caminho e o nome do arquivo '{input_file}'.")

except pd.errors.EmptyDataError:
    print(f"\n--- ERRO ---")
    print(f"O arquivo '{input_file}' está vazio.")

except Exception as e:
    print(f"\n--- ERRO INESPERADO ---")
    print(f"Ocorreu um erro: {e}")