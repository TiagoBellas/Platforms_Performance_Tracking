# Performance Tracking Dashboard — Streamlit

Dashboard Streamlit para acompanhamento da performance por Platform, país, KPI e período, baseado no ficheiro `log_scorecardPerformanceTracking.xlsx`.

## Estrutura

```text
streamlit_performance_dashboard/
├── app.py
├── requirements.txt
├── .streamlit/config.toml
├── src/
│   ├── data_loader.py
│   └── charts.py
└── data/
    ├── log_scorecardPerformanceTracking.xlsx
    ├── *.csv
    └── workbook_summary.json
```

## Funcionalidades

- Filtros por período, Platform, país e KPI.
- KPIs principais: Actual 2026, Budget 2026, Variance, KPIs On Target.
- Gráficos Plotly: Actual vs Budget, heatmap de Achievement, dispersão por país e EBITDA Margin.
- Secção qualitativa para Business Performance & ESG e Platform Performance.
- Download dos dados filtrados.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit Cloud

1. Criar um repositório no GitHub.
2. Fazer upload de todos os ficheiros desta pasta para o repositório.
3. No Streamlit Cloud, escolher **New app**.
4. Selecionar o repositório e definir `app.py` como entrypoint.
5. Deploy.

## Modelo de dados

As folhas financeiras foram normalizadas para uma tabela principal com os campos: Platform, Country, KPI, LQ_Floor, On_Target, UQ, pesos, 2026 Budget, 2026 Actual, Period, Variance, Variance %, Achievement % e Status.

As folhas qualitativas mantêm os objetivos textuais e os respetivos pesos de Investment Platform e Servicing Platform.
