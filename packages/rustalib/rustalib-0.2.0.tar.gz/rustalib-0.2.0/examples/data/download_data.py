# download_data.py

import yfinance as yf
import os

# Configuración
symbol = "SPY"
start_date = "2000-01-01"
end_date = "2024-12-31"
output_dir = "examples/data"
output_file = f"{output_dir}/{symbol}_1D_2000_2024.csv"

def main():
    print(f"Descargando datos de {symbol} desde {start_date} hasta {end_date}...")

    # Descargar con yfinance
    df = yf.download(symbol, start=start_date, end=end_date, interval="1d")

    # Si hay columnas de múltiples niveles (ej. ('Close', 'SPY')), aplanarlas
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Asegurar que la columna 'Date' no esté como índice
    df.reset_index(inplace=True)

    # Crear carpeta si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Guardar CSV limpio
    df.to_csv(output_file, index=False)
    print(f"Datos guardados en {output_file}")

if __name__ == "__main__":
    import pandas as pd
    main()
