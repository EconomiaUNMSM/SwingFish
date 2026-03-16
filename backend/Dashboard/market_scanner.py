import finvizfinance.screener as screener
import pandas as pd

def get_market_screener() -> dict:
    """
    Obtiene el escáner de los instrumentos más activos y los más volátiles desde Finviz.
    Devuelve un diccionario con dos listas de diccionarios (JSON estructurado).
    """
    result = {"most_active": [], "most_volatile": []}
    
    try:
        # Most Active
        most_active = screener.overview.Overview()
        most_active.set_filter(signal="Most Active")
        df_active = most_active.screener_view(order="Change", ascend=False, limit=40)
        
        # Dependiendo del idioma/config local, Finviz puede retornar Volume o Volumen
        vol_col = "Volume" if "Volume" in df_active.columns else "Volumen"
        if vol_col in df_active.columns:
            df_active[[vol_col, "Market Cap"]] = df_active.get([vol_col, "Market Cap"], default=pd.DataFrame()).fillna(0)
        
        for col in [vol_col, "Market Cap", "Price", "Change", "P/E"]:
            if col in df_active.columns:
                df_active[col] = pd.to_numeric(df_active[col], errors='coerce').fillna(0)
                df_active[col] = df_active[col].apply(lambda x: round(x, 4 if col in ["Price", "Change", "P/E"] else 0))
                
        result["most_active"] = df_active.fillna("N/A").to_dict(orient="records")
    except Exception as e:
        result["most_active"] = [{"error": f"Error en Most Active: {str(e)}"}]
        
    try:
        # Most Volatile
        most_volatile = screener.overview.Overview()
        # En la API de finvizfinance, el orden debe ir en screener_view(), no en set_filter()
        most_volatile.set_filter(signal="Most Volatile")
        df_volatile = most_volatile.screener_view(order="Change", ascend=False, limit=40)
        
        vol_col = "Volume" if "Volume" in df_volatile.columns else "Volumen"
        if vol_col in df_volatile.columns:
            df_volatile[[vol_col, "Market Cap"]] = df_volatile.get([vol_col, "Market Cap"], default=pd.DataFrame()).fillna(0)
        
        for col in [vol_col, "Market Cap", "Price", "Change", "P/E"]:
            if col in df_volatile.columns:
                df_volatile[col] = pd.to_numeric(df_volatile[col], errors='coerce').fillna(0)
                df_volatile[col] = df_volatile[col].apply(lambda x: round(x, 4 if col in ["Price", "Change", "P/E"] else 0))
                
        result["most_volatile"] = df_volatile.fillna("N/A").to_dict(orient="records")
    except Exception as e:
        result["most_volatile"] = [{"error": f"Error en Most Volatile: {str(e)}"}]

    return result
