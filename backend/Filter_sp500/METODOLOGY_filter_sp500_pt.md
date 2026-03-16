# Metodologia de Filtragem S&P 500 | Motor de Pontuação

## 1. Visão Geral
O módulo **Filter_sp500** sintetiza a saúde corporativa em uma **Pontuação Final (0-100)** através da triangulação de 5 modelos quantitativos comprovados.

### 💡 Combate à Subjetividade
Análises de IA genéricas frequentemente resumem o "sentimento" sem olhar a qualidade do balanço. O SwingFish **combate alucinações** aplicando regras matemáticas rígidas (Altman, Piotroski, Beneish) que não podem ser contestadas por um LLM.

## 2. Sub-Modelos Ponderados
1.  **Piotroski F-Score (15%)**: Força financeira (0-9 pontos).
2.  **Altman Z-Score (10%)**: Previsão de risco de falência.
3.  **Beneish M-Score (5%)**: Detecção de manipulação contábil.
4.  **Magic Formula (20%)**: Qualidade (ROC) e Preço (EY).
5.  **Crescimento e Momentum (30%)**: Validação de tendência e receita.
6.  **Analistas (20%)**: Alvos de Wall Street.

## 3. Utilidade Prática
Para o swing trader, esta nota atua como um **Escudo de Qualidade**. Se o motor disparar um alerta de `ACCOUNTING_RISK`, o ativo é descartado, independentemente do gráfico.

---
**⚠️ Aviso**: Desenvolvido especificamente para **Ações Individuais dos EUA**.
