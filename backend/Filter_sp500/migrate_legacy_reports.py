import os
import pandas as pd
from pathlib import Path
import os
import sys

# Agregar el root al sys.path para poder importar módulos locales
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MODULO_FUNDAMENTALES.database import get_engine, setup_postgres_schema, save_scan_to_db

def migrate_legacy_reports():
    print("=" * 60)
    print("  MIGRANDO REPORTES LOCALES A POSTGRESQL")
    print("=" * 60)
    
    engine = get_engine()
    setup_postgres_schema(engine)
    
    reports_dir = Path(__file__).parent / 'reports'
    
    if not reports_dir.exists():
        print(f"El directorio {reports_dir} no existe.")
        return
        
    csv_files = list(reports_dir.glob("fundamentals_scan_*.csv"))
    
    if not csv_files:
        print("No se encontraron reportes .csv para migrar.")
        return
        
    print(f"Se encontraron {len(csv_files)} reportes para migrar.")
    
    migrated_count = 0
    
    for file_path in csv_files:
        filename = file_path.name
        # Extraer el ID de la ejecución (asumiendo formato fundamentals_scan_YYYYMMDD_HHMMSS.csv)
        try:
            timestamp_str = filename.replace("fundamentals_scan_", "").replace(".csv", "")
            # Convertir string tipo '20260219_193229' a datetime
            execution_date = pd.to_datetime(timestamp_str, format="%Y%m%d_%H%M%S")
        except ValueError:
            print(f"Skipping {filename}: No se pudo parsear la fecha.")
            continue
            
        try:
            df = pd.read_csv(file_path)
            
            # Subir a la tabla histórica (todos los locales suelen ser masivos por defecto en el sistema anterior)
            save_scan_to_db(df, execution_id=timestamp_str, execution_date=execution_date, is_custom=False)
            print(f"✓ Migrado exitosamente: {filename}")
            migrated_count += 1
        except Exception as e:
            print(f"× Error migrando {filename}: {e}")
            
    print("=" * 60)
    print(f"  MIGRACIÓN COMPLETADA: {migrated_count} REPORTES MIGRADOS")
    print("=" * 60)

if __name__ == "__main__":
    migrate_legacy_reports()
