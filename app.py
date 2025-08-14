# app.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from functools import lru_cache

# ============================
# 1) CONFIGURACIÓN & DATOS
# ============================

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.CYBORG, dbc.icons.BOOTSTRAP],
                title='Visualizador de Desarrollo de Latinoamérica')
server = app.server

PAISES = {
    'Argentina': 'ARG', 'Bolivia': 'BOL', 'Brasil': 'BRA', 'Chile': 'CHL',
    'Colombia': 'COL', 'Costa Rica': 'CRI', 'Cuba': 'CUB', 'Ecuador': 'ECU',
    'El Salvador': 'SLV', 'Guatemala': 'GTM', 'Honduras': 'HND', 'México': 'MEX',
    'Nicaragua': 'NIC', 'Panamá': 'PAN', 'Paraguay': 'PRY', 'Perú': 'PER',
    'República Dominicana': 'DOM', 'Uruguay': 'URY', 'Venezuela': 'VEN'
}

INDICADORES = {
    'PIB per cápita (US$)': 'NY.GDP.PCAP.CD',
    'Tasa de Inflación Anual (%)': 'FP.CPI.TOTL.ZG',
    'Tasa de Desempleo (%)': 'SL.UEM.TOTL.ZS',
    'Esperanza de Vida (años)': 'SP.DYN.LE00.IN',
    'Gasto en Salud per cápita (US$)': 'SH.XPD.CHEX.PC.CD',
    'Acceso a Electricidad (% población)': 'EG.ELC.ACCS.ZS',
    'Emisiones de CO2 (t per cápita)': 'EN.ATM.CO2E.PC',
    'Usuarios de Internet (% población)': 'IT.NET.USER.ZS'
}

DEFAULT_INDICATOR = 'PIB per cápita (US$)'
DEFAULT_COUNTRIES = ['Chile']
ANIO_INICIO, ANIO_FIN = 2000, 2024

@lru_cache(maxsize=64)
def fetch_worldbank_page(countries_iso: str, indicator: str, date_range: str, page: int = 1, per_page: int = 2000):
    url = f"https://api.worldbank.org/v2/country/{countries_iso}/indicator/{indicator}?date={date_range}&format=json&per_page={per_page}&page={page}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def obtener_datos_bm(dict_paises, dict_indicadores, anio_inicio=ANIO_INICIO, anio_fin=ANIO_FIN):
    dfs = []
    countries_iso = ";".join(dict_paises.values())
    date_range = f"{anio_inicio}:{anio_fin}"

    for nombre_ind, cod_ind in dict_indicadores.items():
        try:
            first = fetch_worldbank_page(countries_iso, cod_ind, date_range, page=1)
            if not isinstance(first, list) or len(first) < 2 or not first[1]:
                continue
            pages = int(first[0].get('pages', 1))
            all_rows = first[1]
            for p in range(2, pages + 1):
                js = fetch_worldbank_page(countries_iso, cod_ind, date_range, page=p)
                if len(js) > 1 and js[1]:
                    all_rows.extend(js[1])

            df = pd.DataFrame(all_rows)
            if df.empty:
                continue
            df_clean = df[['countryiso3code', 'country', 'date', 'value']].copy()
            df_clean.rename(columns={'countryiso3code': 'CodigoISO3', 'country': 'Pais', 'date': 'Anio', 'value': 'Valor'}, inplace=True)
            df_clean['Indicador'] = nombre_ind
            rev = {v: k for k, v in dict_paises.items()}
            df_clean['Pais'] = df_clean['CodigoISO3'].map(rev).fillna(df_clean['Pais'])
            df_clean['Anio'] = pd.to_numeric(df_clean['Anio'], errors='coerce')
            df_clean['Valor'] = pd.to_numeric(df_clean['Valor'], errors='coerce')
            df_clean.dropna(subset=['Valor', 'Anio'], inplace=True)
            dfs.append(df_clean)
        except Exception as e:
            print(f"Error con {nombre_ind}: {e}")
            continue

    if dfs:
        return pd.concat(dfs, ignore_index=True).sort_values(['Indicador', 'Pais', 'Anio'])
    return pd.DataFrame(columns=['CodigoISO3','Pais','Anio','Valor','Indicador'])

DF_ALL = obtener_datos_bm(PAISES, INDICADORES)

def formato_valor(nombre_ind, v):
    if pd.isna(v):
        return 'N/A'
    if '%' in nombre_ind:
        return f"{v:,.2f}%".replace(',', 'X').replace('.', ',').replace('X', '.')
    if 'US$' in nombre_ind:
        return f"US$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# ============================
# 2) LAYOUT
# ============================
brand = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.I(className='bi bi-bar-chart-line-fill fs-3 me-2')),
            # CAMBIO: Título y subtítulo actualizados
            dbc.Col(html.Div([
                html.H5('Visualizador de Desarrollo de Latinoamérica', className='mb-0 text-white'),
                html.Small('Datos del Banco Mundial API', className='text-muted')
            ])),
        ], align='center', className='g-2'),
        # CAMBIO: Botón de descarga eliminado de la barra de navegación
    ], fluid=True),
    color='dark', dark=True, className='shadow-sm sticky-top'
)

kpis_layout = dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('Último valor', className='kpi-title'),
        html.H3(id='kpi-valor', className='kpi-number'),
        html.Span(id='kpi-anio', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('Variación vs. año previo', className='kpi-title'),
        html.H3(id='kpi-var', className='kpi-number'),
        html.Span(id='kpi-var-abs', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('Tasa de crecimiento anual (CAGR) en rango', className='kpi-title'),
        html.H3(id='kpi-cagr', className='kpi-number'),
        html.Span(id='kpi-rango', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
    dbc.Col(dbc.Card(dbc.CardBody([
        html.P('Ranking LATAM (últ. año)', className='kpi-title'),
        html.H3(id='kpi-rank', className='kpi-number'),
        html.Span(id='kpi-top', className='kpi-sub'),
    ]), className='kpi-card'), lg=6, md=6, sm=6, xs=12, className="mb-3"),
], className='g-2')

footer_layout = html.Div([
    html.Hr(className="my-3"),
    html.P("Desarrollado por: Ricardo Urdaneta", className="text-muted small"),
    dbc.Row([
        dbc.Col(
            html.A(dbc.Button([html.I(className="bi bi-github me-2"), "GitHub"],
                              color="secondary", outline=True, className="w-100"),
                   href="https://github.com/Ricardouchub", target="_blank")
        , width=6),
        dbc.Col(
            html.A(dbc.Button([html.I(className="bi bi-linkedin me-2"), "LinkedIn"],
                              color="secondary", outline=True, className="w-100"),
                   href="https://www.linkedin.com/in/ricardourdanetacastro", target="_blank")
        , width=6)
    ])
], className="mt-auto")

sidebar = dbc.Card(
    dbc.CardBody([
        # CAMBIO: Instrucciones añadidas
        html.Div([
            html.P("Utilice los filtros para explorar los datos.", className="small"),
            html.P("Nota: Algunos países pueden no tener datos para todos los años o indicadores.", className="small text-muted")
        ], className="mb-3"),
        html.Hr(className="my-2"),
        
        html.Div([
            html.Label('Indicador', className='form-label fw-semibold'),
            dcc.Dropdown(id='dd-indicador', options=[{'label': k, 'value': k} for k in INDICADORES.keys()], value=DEFAULT_INDICATOR, clearable=False)
        ], className='mb-3'),
        html.Div([
            html.Label('Países (multi-selección)', className='form-label fw-semibold'),
            dcc.Dropdown(id='dd-paises', options=[{'label': k, 'value': k} for k in PAISES.keys()], value=DEFAULT_COUNTRIES, multi=True)
        ], className='mb-3'),
        html.Div([
            html.Label('Rango de años', className='form-label fw-semibold'),
            dcc.RangeSlider(id='rs-anios', min=int(DF_ALL['Anio'].min() if not DF_ALL.empty else ANIO_INICIO),
                            max=int(DF_ALL['Anio'].max() if not DF_ALL.empty else ANIO_FIN),
                            value=[max(ANIO_INICIO, int(DF_ALL['Anio'].min() if not DF_ALL.empty else ANIO_INICIO)),
                                   int(DF_ALL['Anio'].max() if not DF_ALL.empty else ANIO_FIN)],
                            step=1, allowCross=False, marks=None, tooltip={'placement': 'bottom', 'always_visible': True})
        ], className='mb-3'),
        html.Div([
            html.Label('Selecciona un País para ver KPIs', className='form-label fw-semibold'),
            dcc.Dropdown(id='dd-kpi-pais', options=[{'label': k, 'value': k} for k in PAISES.keys()], value='Chile', clearable=False)
        ]),
        
        html.Hr(className="my-4"),
        kpis_layout,
        footer_layout
    ], className="d-flex flex-column h-100")
, className='shadow-sm h-100')

line_chart = dbc.Card(dbc.CardBody([
    html.H5('Evolución temporal', className='card-title mb-3'),
    dcc.Loading(dcc.Graph(id='fig-lineas', config={'displaylogo': False}), type='dot')
]), className='shadow-sm')

bar_chart = dbc.Card(dbc.CardBody([
    html.H5('Último año disponible — comparación entre países', className='card-title mb-3'),
    dcc.Loading(dcc.Graph(id='fig-barras', config={'displaylogo': False}), type='dot')
]), className='shadow-sm')

map_chart = dbc.Card(dbc.CardBody([
    html.H5('Mapa coroplético — último año del rango', className='card-title mb-3'),
    dcc.Loading(dcc.Graph(id='fig-mapa', config={'displaylogo': False}), type='dot')
]), className='shadow-sm')

app.layout = dbc.Container([
    brand,
    dbc.Row([
        # CAMBIO: Ancho de la barra lateral reducido
        dbc.Col(sidebar, md=3, lg=2, className='mb-3'),
        dbc.Col([
            dbc.Row([dbc.Col(line_chart, lg=12, className='mb-3')]),
            dbc.Row([
                dbc.Col(bar_chart, lg=6, className='mb-3'),
                dbc.Col(map_chart, lg=6, className='mb-3'),
            ]),
            # CAMBIO: Botón de descarga movido al final del contenido principal
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Button("Descargar CSV", id="btn-descargar", n_clicks=0, color="secondary"),
                        dcc.Download(id='descarga-datos') # El componente Download puede estar aquí
                    ], className="d-flex justify-content-end mt-3"
                )
            ])
        ], md=9, lg=10)
    ], className='mt-3')
], fluid=True)

# ============================
# 3) CALLBACKS
# ============================

@app.callback(
    Output('descarga-datos', 'data'),
    Input('btn-descargar', 'n_clicks'),
    State('dd-indicador', 'value'),
    prevent_initial_call=True
)
def descargar(n, indicador):
    df = DF_ALL[DF_ALL['Indicador'] == indicador].copy()
    return dcc.send_data_frame(df.to_csv, f"latam_{indicador.replace(' ', '_')}.csv", index=False)

def _filtra_transforma(indicador, paises_sel, anio_ini, anio_fin):
    df = DF_ALL[(DF_ALL['Indicador'] == indicador) & (DF_ALL['Pais'].isin(paises_sel)) & (DF_ALL['Anio'].between(anio_ini, anio_fin))].copy()
    return df

@app.callback(
    [Output('kpi-valor', 'children'), Output('kpi-anio', 'children'),
     Output('kpi-var', 'children'), Output('kpi-var-abs', 'children'),
     Output('kpi-cagr', 'children'), Output('kpi-rango', 'children'),
     Output('kpi-rank', 'children'), Output('kpi-top', 'children')],
    [Input('dd-indicador', 'value'), Input('dd-kpi-pais', 'value'), Input('rs-anios', 'value')]
)
def actualizar_kpis(indicador, pais_kpi, rango):
    a0, a1 = int(rango[0]), int(rango[1])
    df_ind = DF_ALL[(DF_ALL['Indicador'] == indicador) & (DF_ALL['Pais'] == pais_kpi) & (DF_ALL['Anio'].between(a0, a1))]
    if df_ind.empty:
        return ['N/A'] * 8

    df_ind = df_ind.sort_values('Anio')
    last_row = df_ind.iloc[-1]
    last_val, last_year = last_row['Valor'], int(last_row['Anio'])
    
    if len(df_ind) >= 2:
        prev_val = df_ind.iloc[-2]['Valor']
        var_pct = ((last_val - prev_val) / prev_val) * 100 if prev_val != 0 and pd.notna(prev_val) else np.nan
        var_abs = last_val - prev_val
    else:
        var_pct, var_abs = np.nan, np.nan

    first_row = df_ind.iloc[0]
    first_val, first_year = first_row['Valor'], int(first_row['Anio'])
    n_years = max(1, last_year - first_year)
    cagr = ((last_val / first_val) ** (1 / n_years) - 1) * 100 if first_val != 0 and pd.notna(first_val) else np.nan

    df_last_year = DF_ALL[(DF_ALL['Indicador'] == indicador) & (DF_ALL['Anio'] == last_year)].dropna(subset=['Valor'])
    if df_last_year.empty:
        rank_txt, top_txt = 'N/A', ''
    else:
        df_last_year = df_last_year.sort_values('Valor', ascending=False).reset_index()
        df_last_year['rank'] = df_last_year.index + 1
        fila = df_last_year[df_last_year['Pais'] == pais_kpi]
        rank_txt = f"#{int(fila['rank'].iloc[0])} de {len(df_last_year)}" if not fila.empty else 'N/A'
        top_txt = f"Año {last_year}"

    return (
        formato_valor(indicador, last_val), f"Año {last_year}",
        (f"{var_pct:,.2f}%" if pd.notna(var_pct) else 'N/A').replace(',', 'X').replace('.', ',').replace('X', '.'),
        (f"Δ {formato_valor(indicador, var_abs)}" if pd.notna(var_abs) else 'Δ N/A'),
        (f"{cagr:,.2f}%" if pd.notna(cagr) else 'N/A').replace(',', 'X').replace('.', ',').replace('X', '.'),
        f"{a0}–{a1}", rank_txt, top_txt
    )

@app.callback(
    Output('fig-lineas', 'figure'),
    [Input('dd-indicador', 'value'), Input('dd-paises', 'value'), Input('rs-anios', 'value')]
)
def fig_lineas(indicador, paises_sel, rango):
    a0, a1 = int(rango[0]), int(rango[1])
    df = _filtra_transforma(indicador, paises_sel, a0, a1)
    if df.empty:
        return go.Figure().update_layout(title_text='No hay datos para la selección actual', template='plotly_dark')

    titulo = f"Evolución de {indicador} ({a0}–{a1})"
    ylab = indicador

    fig = px.line(df, x='Anio', y='Valor', color='Pais', markers=True, labels={'Anio': 'Año', 'Valor': ylab}, title=titulo, template='plotly_dark')
    fig.update_layout(legend_title_text='País', hovermode='x unified', transition_duration=400)
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback(
    Output('fig-barras', 'figure'),
    [Input('dd-indicador', 'value'), Input('rs-anios', 'value')]
)
def fig_barras(indicador, rango):
    a0, a1 = int(rango[0]), int(rango[1])
    df = DF_ALL[(DF_ALL['Indicador'] == indicador) & (DF_ALL['Anio'].between(a0, a1))].copy()
    if df.empty:
        return go.Figure().update_layout(title_text='No hay datos para la selección actual', template='plotly_dark')

    idx = df.sort_values('Anio').groupby('Pais')['Valor'].idxmax()
    df_last = df.loc[idx].dropna(subset=['Valor']).sort_values('Valor', ascending=False)
    
    if df_last.empty:
        return go.Figure().update_layout(title_text='No hay datos para la selección actual', template='plotly_dark')

    fig = px.bar(df_last, x='Pais', y='Valor', text='Valor', labels={'Valor': indicador, 'Pais': 'País'}, template='plotly_dark')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis_tickangle=-45, uniformtext_minsize=8, uniformtext_mode='hide', margin=dict(t=40, r=10, l=10, b=40))
    return fig

@app.callback(
    Output('fig-mapa', 'figure'),
    [Input('dd-indicador', 'value'), Input('rs-anios', 'value')]
)
def fig_mapa(indicador, rango):
    a0, a1 = int(rango[0]), int(rango[1])
    df = DF_ALL[(DF_ALL['Indicador'] == indicador) & (DF_ALL['Anio'].between(a0, a1))].copy()
    if df.empty:
        return go.Figure().update_layout(title_text='No hay datos para la selección actual', template='plotly_dark', geo=dict(visible=False))

    last_year_in_data = int(df['Anio'].max())
    df_last = df[df['Anio'] == last_year_in_data]

    fig = px.choropleth(
        df_last, locations='CodigoISO3', color='Valor', hover_name='Pais',
        color_continuous_scale='Viridis', locationmode='ISO-3', labels={'Valor': indicador},
        title=f"{indicador} — {last_year_in_data}", scope='world'
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(t=50, r=0, l=0, b=0), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', geo_bgcolor='rgba(0,0,0,0)')
    return fig

# ============================
# 4) MAIN
# ============================
if __name__ == '__main__':
    app.run(debug=True)