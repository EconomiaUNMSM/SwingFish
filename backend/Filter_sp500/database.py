import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, DateTime, inspect, text
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

# Cargar variables de entorno
load_dotenv(Path(__file__).parent.parent / '.env')

def get_engine():
    """Configura y retorna el engine de SQLAlchemy para PostgreSQL"""
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "decision_engine")

    # Si la contraseña tiene caracteres especiales, idealmente usar urllib.parse.quote_plus
    # urllib.parse.quote_plus(password)
    from urllib.parse import quote_plus
    encoded_pass = quote_plus(password)
    
    conn_str = f"postgresql+psycopg2://{user}:{encoded_pass}@{host}:{port}/{dbname}"
    engine = create_engine(conn_str)
    return engine

def setup_postgres_schema(engine):
    """Crea las tablas de reportes fundamentales si no existen."""
    metadata = MetaData()

    # Tabla para corridas masivas/completas
    historical_scans = Table(
        'fundamentals_historical_scans', metadata,
        Column('execution_id', String(50), primary_key=True),
        Column('ticker', String(20), primary_key=True),
        Column('execution_date', DateTime, nullable=False),
        Column('price', Float),
        Column('market_cap', Float),
        Column('sector', String(100)),
        Column('final_score', Float),
        Column('recommendation', String(50)),
        Column('piotroski', Float),
        Column('altman_z', Float),
        Column('beneish_m', Float),
        Column('magic_rank', Float),
        Column('growth_score', Float),
        Column('upside', Float),
        Column('risk_flags', String(255))
    )

    # Tabla para corridas personalizadas
    custom_scans = Table(
        'fundamentals_custom_scans', metadata,
        Column('execution_id', String(50), primary_key=True),
        Column('ticker', String(20), primary_key=True),
        Column('execution_date', DateTime, nullable=False),
        Column('price', Float),
        Column('market_cap', Float),
        Column('sector', String(100)),
        Column('final_score', Float),
        Column('recommendation', String(50)),
        Column('piotroski', Float),
        Column('altman_z', Float),
        Column('beneish_m', Float),
        Column('magic_rank', Float),
        Column('growth_score', Float),
        Column('upside', Float),
        Column('risk_flags', String(255))
    )

    metadata.create_all(engine)
    print("✓ Tablas de Fundamentales verificadas/creadas en PostgreSQL.")

def save_scan_to_db(df: pd.DataFrame, execution_id: str, execution_date: pd.Timestamp, is_custom: bool = False):
    """
    Guarda el dataframe de resultados de fundamentales en la base de datos PostgreSQL.
    Si is_custom es True, va a 'fundamentals_custom_scans', de lo contrario a 'fundamentals_historical_scans'.
    """
    if df.empty:
        return
        
    engine = get_engine()
    table_name = 'fundamentals_custom_scans' if is_custom else 'fundamentals_historical_scans'
    
    # Preparar el dataframe para DB
    db_df = df.copy()
    db_df['execution_id'] = execution_id
    db_df['execution_date'] = execution_date
    
    # Asegurarnos del orden de las columnas si existen o rellenar NaN
    expected_cols = [
        'execution_id', 'ticker', 'execution_date', 'price', 'market_cap', 'sector', 
        'final_score', 'recommendation', 'piotroski', 'altman_z', 'beneish_m', 
        'magic_rank', 'growth_score', 'upside', 'risk_flags'
    ]
    
    for col in expected_cols:
        if col not in db_df.columns:
            db_df[col] = None
            
    db_df = db_df[expected_cols]
    
    # Subir a DB optimizadamente
    try:
        # UPSERT logic manual ya que to_sql no tiene un ON CONFLICT elegante.
        # Aquí vamos registro por registro para manejar conflictos.
        with engine.begin() as conn:
            for _, row in db_df.iterrows():
                query = text(f"""
                    INSERT INTO {table_name} (
                        execution_id, ticker, execution_date, price, market_cap, sector, 
                        final_score, recommendation, piotroski, altman_z, beneish_m, 
                        magic_rank, growth_score, upside, risk_flags
                    ) VALUES (
                        :execution_id, :ticker, :execution_date, :price, :market_cap, :sector, 
                        :final_score, :recommendation, :piotroski, :altman_z, :beneish_m, 
                        :magic_rank, :growth_score, :upside, :risk_flags
                    )
                    ON CONFLICT (execution_id, ticker) DO UPDATE SET
                        execution_date = EXCLUDED.execution_date,
                        price = EXCLUDED.price,
                        market_cap = EXCLUDED.market_cap,
                        sector = EXCLUDED.sector,
                        final_score = EXCLUDED.final_score,
                        recommendation = EXCLUDED.recommendation,
                        piotroski = EXCLUDED.piotroski,
                        altman_z = EXCLUDED.altman_z,
                        beneish_m = EXCLUDED.beneish_m,
                        magic_rank = EXCLUDED.magic_rank,
                        growth_score = EXCLUDED.growth_score,
                        upside = EXCLUDED.upside,
                        risk_flags = EXCLUDED.risk_flags;
                """)
                
                # Tratar nulos correctamente para SQLAlchemy (reemplazar pd.NA / math.isnan)
                params = row.where(pd.notnull(row), None).to_dict()
                
                conn.execute(query, params)
                
    except Exception as e:
        print(f"Error al guardar a PostgreSQL: {e}")

if __name__ == "__main__":
    engine = get_engine()
    setup_postgres_schema(engine)
