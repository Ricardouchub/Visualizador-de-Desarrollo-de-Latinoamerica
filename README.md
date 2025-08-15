# Visualizador Web del Desarrollo de Latinoamérica

Este proyecto es un dashboard interactivo construido con **Dash y Plotly** que permite visualizar y comparar indicadores clave de desarrollo económico y social para los países de Latinoamérica. 

Los datos son obtenidos en tiempo real desde la **API del Banco Mundial**, garantizando que la información esté siempre actualizada.

### **[Dashboard](https://visualizador-de-desarrollo-de.onrender.com/)**

<img width="2545" height="1285" alt="image" src="https://github.com/user-attachments/assets/80410f9b-5832-42b0-a1a0-9b32a1236ab7" />


---



La aplicación ofrece una interfaz de usuario moderna y oscura, diseñada para ser intuitiva y permitir a los usuarios explorar tendencias, comparar el rendimiento entre países y analizar métricas específicas a través de una variedad de gráficos dinámicos.

##  Características

* **Datos en Tiempo Real:** Conexión directa a la API del Banco Mundial para obtener los datos más recientes.
* **Dashboard Interactivo:** Filtros dinámicos por indicador, múltiples países y rango de años con visualizaciones:
    * **Gráfico de Líneas:** Para analizar la evolución de un indicador a lo largo del tiempo.
    * **Gráfico de Barras:** Para comparar el último valor disponible entre los países seleccionados.
    * **Mapa Coroplético:** Para una vista geográfica del indicador en la región.
* **KPIs:** Métricas clave como el último valor, la variación anual, la tasa de crecimiento anual y el ranking regional para un país específico.
* **Diseño Moderno y Responsivo:** Interfaz oscura y profesional construida con Dash Bootstrap Components.
* **Descarga de Datos:** Funcionalidad para descargar los datos del indicador seleccionado en formato CSV.

## Despliegue 

Esta aplicación está desplegada y disponible públicamente a través de Render, una plataforma en la nube para construir y ejecutar aplicaciones web. El despliegue se realiza automáticamente a partir del código fuente en GitHub, utilizando un servidor Gunicorn para garantizar un rendimiento robusto y escalable.

## Herramientas

* **Backend y Visualización:**
    * Dash: Framework principal para construir la aplicación web.
    * Plotly Express: Para la creación de gráficos interactivos.
    * Requests: Para realizar las peticiones a la API del Banco Mundial.
* **Frontend y Diseño:**
    * Dash Bootstrap Components: Para un diseño responsivo y componentes modernos.
    * Bootstrap Icons: Para los íconos utilizados en la interfaz.

## Autor

**Ricardo Urdaneta**

**[Linkedin](https://www.linkedin.com/in/ricardourdanetacastro)**
