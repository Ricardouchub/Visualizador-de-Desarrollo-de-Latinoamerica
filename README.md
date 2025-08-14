# Visualizador de Desarrollo de Latinoamérica

##  Descripción

Este proyecto es un dashboard interactivo construido con **Dash y Plotly** que permite visualizar y comparar indicadores clave de desarrollo económico y social para los países de Latinoamérica. Los datos son obtenidos en tiempo real desde la API pública del **Banco Mundial**, garantizando que la información esté siempre actualizada.

La aplicación ofrece una interfaz de usuario moderna y oscura, diseñada para ser intuitiva y permitir a los usuarios explorar tendencias, comparar el rendimiento entre países y analizar métricas específicas a través de una variedad de gráficos dinámicos.

##  Características

* **Datos en Tiempo Real:** Conexión directa a la API del Banco Mundial para obtener los datos más recientes.
* **Dashboard Interactivo:** Filtros dinámicos por indicador, múltiples países y rango de años.
* **Visualizaciones Múltiples:**
    * **Gráfico de Líneas:** Para analizar la evolución de un indicador a lo largo del tiempo.
    * **Gráfico de Barras:** Para comparar el último valor disponible entre los países seleccionados.
    * **Mapa Coroplético:** Para una vista geográfica del indicador en la región.
* **KPIs Detallados:** Tarjetas con métricas clave como el último valor, la variación anual, la tasa de crecimiento anual compuesta (CAGR) y el ranking regional para un país específico.
* **Diseño Moderno y Responsivo:** Interfaz oscura y profesional construida con Dash Bootstrap Components.
* **Descarga de Datos:** Funcionalidad para descargar los datos del indicador seleccionado en formato CSV.

## Despliegue 

Este proyecto está configurado para un despliegue sencillo en **Render**.

1.  **Sube tu proyecto a GitHub:** Asegúrate de que tu repositorio contenga los archivos `app.py`, `requirements.txt` y la carpeta `assets`.
2.  **Crea una cuenta en Render:** Ve a [render.com](https://render.com) y regístrate.
3.  **Nuevo Servicio Web:** En tu dashboard de Render, crea un **"New Web Service"** y conéctalo a tu repositorio de GitHub.
4.  **Configuración:**
    * **Environment:** `Python 3`
    * **Build Command:** `pip install -r requirements.txt`
    * **Start Command:** `gunicorn app:server`
5.  **¡Desplegar!** Haz clic en "Create Web Service". Render se encargará de instalar las dependencias y poner tu aplicación en línea.

## Herramientas

* **Backend y Visualización:**
    * [Dash](https://dash.plotly.com/): Framework principal para construir la aplicación web.
    * [Plotly Express](https://plotly.com/python/plotly-express/): Para la creación de gráficos interactivos.
    * [Pandas](https://pandas.pydata.org/): Para la manipulación y procesamiento de datos.
    * [Requests](https://requests.readthedocs.io/en/latest/): Para realizar las peticiones a la API del Banco Mundial.
* **Frontend y Diseño:**
    * [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/): Para un diseño responsivo y componentes modernos.
    * [Bootstrap Icons](https://icons.getbootstrap.com/): Para los íconos utilizados en la interfaz.

## Autor

Este proyecto fue desarrollado por **Ricardo Urdaneta**.
