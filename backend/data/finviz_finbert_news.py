import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, List, Dict

try:
    from fake_useragent import UserAgent
except ImportError:
    # Fallback si no está instalado
    class UserAgent:
        @property
        def chrome(self):
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

logger = logging.getLogger("finviz_finbert_scraper")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

class FinvizFinbertScraper:
    """
    Combina el raspado de Finviz (para extraer titulares recientes)
    con el modelo de lenguaje FinBERT de HuggingFace para evaluar el sentimiento.
    """

    def __init__(self, model_name: str = "ProsusAI/finbert", device: Optional[int] = None):
        """
        Inicializa el analizador. 
        device: 0 para usar GPU, -1 o None para CPU.
        """
        self.model_name = model_name
        self.nlp = None

        if pipeline is not None:
            try:
                logger.info(f"Cargando modelo FinBERT: {model_name}...")
                kwargs = {"model": model_name, "tokenizer": model_name, "top_k": None}
                if device is not None:
                    kwargs["device"] = device
                self.nlp = pipeline("sentiment-analysis", **kwargs)
                logger.info("Modelo FinBERT cargado exitosamente.")
            except Exception as e:
                logger.error(f"Error cargando pipeline FinBERT: {e}")
        else:
            logger.warning("Librería 'transformers' no encontrada. Se requerirá instalarla para evaluar sentimientos reales.")

    def scrape_finviz_news(self, ticker: str) -> List[Dict]:
        """
        Descarga y parsea la tabla de noticias de Finviz para un activo dado.
        Retorna una lista de diccionarios con Fecha, Hora y Titular.
        """
        url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
        ua = UserAgent()
        headers = {"User-Agent": str(ua.chrome)}
        
        logger.info(f"Descargando noticias de {ticker} desde Finviz...")
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error conectando a Finviz: {e}")
            return []

        soup = BeautifulSoup(r.content, "html5lib")
        tabla_noticias = soup.find(id="news-table")
        
        if not tabla_noticias:
            logger.warning(f"No se encontró la tabla de noticias para {ticker}.")
            return []
            
        noticias = tabla_noticias.find_all("tr")
        data = []
        last_fecha = datetime.now().strftime("%b-%d-%y")
        
        for noticia in noticias:
            a_tag = noticia.find("a", attrs={"class": "tab-link-news"})
            if not a_tag:
                continue
                
            titular = a_tag.text.strip()
            td_tag = noticia.find("td")
            if not td_tag:
                continue
                
            fecha_publicacion = td_tag.text.replace("\n", "").strip().split()
            
            # Formato devuelto por web puede ser: "Oct-15-23 08:30AM" o solamente "08:30AM"
            if len(fecha_publicacion) == 2:
                fecha = fecha_publicacion[0]
                hora = fecha_publicacion[1]
                if fecha.lower() == "today":
                    fecha = datetime.now().strftime("%b-%d-%y")
                last_fecha = fecha
            elif len(fecha_publicacion) == 1:
                hora = fecha_publicacion[0]
                fecha = last_fecha
            else:
                continue
                
            data.append({
                "Ticker": ticker,
                "Fecha": fecha,
                "Hora": hora,
                "Titular": titular
            })
            
        return data

    def evaluate_sentiment_batch(self, titles: List[str], batch_size: int = 8) -> List[Dict]:
        """
        Toma una lista de titulares y los somete al motor NLP en lotes para mayor eficiencia.
        """
        if not self.nlp:
            logger.warning("El pipeline FinBERT no está activo. Los sentimientos retornarán 0.")
            return [{"positive": 0.0, "neutral": 0.0, "negative": 0.0} for _ in titles]

        results = []
        for i in range(0, len(titles), batch_size):
            batch = titles[i:i + batch_size]
            try:
                preds = self.nlp(batch)
                
                for p in preds:
                    mapping = {}
                    # Manejo robusto dependiendo de la estructura retornada por el pipeline
                    if isinstance(p, dict):
                        lbl = str(p.get("label", "")).lower()
                        score = float(p.get("score", 0.0))
                        mapping[lbl] = score
                    elif isinstance(p, list):
                        for d in p:
                            if isinstance(d, dict):
                                lbl = str(d.get("label", "")).lower()
                                score = float(d.get("score", 0.0))
                                mapping[lbl] = score
                    
                    results.append({
                        "positive": mapping.get("positive", mapping.get("pos", 0.0)),
                        "neutral": mapping.get("neutral", mapping.get("neu", 0.0)),
                        "negative": mapping.get("negative", mapping.get("neg", 0.0))
                    })
            except Exception as e:
                logger.error(f"Error procesando batch en FinBERT: {e}")
                # Fallback neutro por fallo de bloque
                results.extend([{"positive": 0.0, "neutral": 1.0, "negative": 0.0}] * len(batch))
                
        return results

    def get_news_sentiment(self, ticker: str, max_news: int = 20) -> pd.DataFrame:
        """
        Orquesta el scraping y la evaluación.
        Retorna las columnas: Ticker, Fecha, Hora, Titular, pos_%, neu_%, neg_%, Gap
        """
        # 1. Obtener la data cruda desde Finviz
        raw_news = self.scrape_finviz_news(ticker)
        if not raw_news:
            return pd.DataFrame()
            
        # Limitar resultados
        raw_news = raw_news[:max_news]
        
        # 2. Extraer titulares para evaluación
        titles = [item["Titular"] for item in raw_news]
        
        # 3. Procesamiento NLP (FinBERT)
        logger.info(f"Evaluando sentimiento de {len(titles)} titulares...")
        sentiments = self.evaluate_sentiment_batch(titles)
        
        # 4. Formatear la tabla final
        rows = []
        for news_meta, sent in zip(raw_news, sentiments):
            pos_pct = round(sent["positive"] * 100.0, 2)
            neu_pct = round(sent["neutral"] * 100.0, 2)
            neg_pct = round(sent["negative"] * 100.0, 2)
            
            # Balance de pesimismo vs optimismo (excluyendo neutralidad base)
            gap = round(pos_pct - neg_pct, 2)
            
            rows.append({
                "Ticker": news_meta["Ticker"],
                "Fecha": news_meta["Fecha"],
                "Hora": news_meta["Hora"],
                "Titular": news_meta["Titular"],
                "pos_%": pos_pct,
                "neu_%": neu_pct,
                "neg_%": neg_pct,
                "Gap": gap
            })
            
        df = pd.DataFrame(rows)
        return df


if __name__ == "__main__":
    # Test opcional
    # Requiere: pip install fake_useragent bs4 html5lib transformers torch
    scraper = FinvizFinbertScraper()
    
    ticker = "DECK"
    df_news = scraper.get_news_sentiment(ticker, max_news=10)
    
    if not df_news.empty:
        print(df_news)
    else:
        print(f"No se pudieron extraer noticias para {ticker}.")
