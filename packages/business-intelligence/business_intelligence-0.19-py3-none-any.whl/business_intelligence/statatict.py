import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from scipy.stats import norm


class config_table:
    
    def __init__(self):
        pass
    """
    Los intervalos de clase son segmentos o rangos definidos de valores 
    numéricos en los que se agrupan los datos para facilitar su análisis y visualización en estadística. 
    Son utilizados principalmente cuando se trabaja con datos numéricos continuos, 
    como edades, ingresos, temperaturas, entre otros.

    Características de los Intervalos de Clase
    Agrupación de Datos: Los intervalos de clase agrupan valores similares de datos 
    dentro de rangos específicos. Esto ayuda a resumir grandes conjuntos de datos y a 
    simplificar su interpretación.

    Mutuamente Excluyentes: Cada dato en el conjunto debe pertenecer a exactamente un 
    intervalo de clase. No puede pertenecer a más de un intervalo ni quedar fuera de todos 
    los intervalos definidos.

    Exhaustivos: Todos los datos deben estar cubiertos por los intervalos de clase definidos. 
    No debe haber datos que no estén incluidos en al menos uno de los intervalos.

    Definición de Límites: Cada intervalo de clase tiene límites inferiores y superiores bien definidos.
    Por convención, el límite inferior de un intervalo es inclusivo (se incluye en el intervalo) 
    y el límite superior es exclusivo (no se incluye en el intervalo).

    Ancho Uniforme o Variable: Los intervalos de clase pueden tener anchos uniformes, 
    donde todos los intervalos tienen el mismo tamaño, o anchos variables, donde los intervalos 
    pueden tener tamaños diferentes dependiendo de la distribución de los datos.

    Pasos para Construir Intervalos de Clase

    Determinar el Rango de los Datos
    Calcula el rango de los datos, que es la diferencia entre el valor máximo y el valor mínimo en tu conjunto de datos.
    Rango=Valormáximo−Valormínimo 

    Calcular el Número de Intervalos (k):
    Decide cuántos intervalos (k) deseas tener. La regla de Sturges es una fórmula comúnmente utilizada para determinar el número inicial de intervalos:
    k=1+log2(n) 
    Donde n es el número de observaciones en tus datos.

    Calcular el Ancho de los Intervalos (h):
    Calcula el ancho de cada intervalo (h) dividiendo el rango de los datos entre el número de intervalos (k):
    h=Rangok 
    Este paso define cuánto se extiende cada intervalo en términos de valores numéricos. A menudo, se redondea el ancho resultante para obtener números enteros manejables.

    Definir los Límites de los Intervalos:
    Utiliza el ancho de intervalo calculado para definir los límites de cada intervalo. Los límites se definen de manera que cada intervalo sea mutuamente exclusivo y exhaustivo. Por ejemplo, si el valor mínimo de tus datos es  xmin , los límites de los intervalos de clase se definen como:
    [xmin+(i−1)⋅h;xmin+i⋅h] 
    Donde i es el número de intervalo, comenzando desde 1 hasta k.
    """
    
    # Función para calcular tabla con intervalos de clase     
    def intervalos_clase(self,variable=None):
        # Calcular el número de intervalos usando Sturges' rule
        num_bins = int(np.ceil(1 + np.log2(len(variable))))

        # Calcular los bordes de los intervalos de clase
        bins = pd.cut(variable, bins=num_bins, ordered=True)

        # Calcular las frecuencias
        Freq = pd.DataFrame({'Frecuencia': bins.value_counts()})

        # Ordenar los intervalos de clase de menor a mayor
        Freq = Freq.sort_index()

        # Calcular la frecuencia acumulada y las frecuencias relativas acumuladas
        Freq['Frec_Acumulada'] = Freq['Frecuencia'].cumsum()
        Freq['Relativo'] = Freq['Frecuencia'] / Freq['Frecuencia'].sum()
        Freq['Rel_Acumulado'] = Freq['Relativo'].cumsum()

        # Mostrar la tabla resultante
        Tabla = Freq.reset_index().rename(columns={'index': 'Clases'})
        
        
        return(Tabla)
    
    # Tabla de frecuencia para variables discretas
    def tabla_frecuencia_discreta(self, dato):
        # Contar las frecuencias de cada valor único
        frecuencias = pd.Series(dato).value_counts().sort_index()

        # Crear el DataFrame para la tabla de frecuencias
        Freq = pd.DataFrame({'Frecuencia': frecuencias})

        # Calcular la frecuencia acumulada y las frecuencias relativas acumuladas
        Freq['Frec_Acumulada'] = Freq['Frecuencia'].cumsum()
        Freq['Relativo'] = Freq['Frecuencia'] / Freq['Frecuencia'].sum()
        Freq['Rel_Acumulado'] = Freq['Relativo'].cumsum()

        # Mostrar la tabla resultante
        Tabla = Freq.reset_index().rename(columns={'index': 'Valores'})
        return Tabla
    

    def estadistica_descriptiva(self,variable):
        # Calcular estadísticas descriptivas
        minimo = variable.min()
        q1 = variable.quantile(0.25)
        media = variable.mean()
        media_rec = stats.trim_mean(variable.dropna(), proportiontocut=0.025)
        mediana = variable.median()
        varianza = variable.var()
        desviacion_estandar = variable.std()
        q3 = variable.quantile(0.75)
        maximo = variable.max()
        simetria = stats.skew(variable.dropna())
        curtosis = stats.kurtosis(variable.dropna())

        # Crear una serie con las estadísticas
        desc = pd.Series([minimo, q1, media, media_rec, mediana,
                        varianza, desviacion_estandar, q3, maximo,
                        simetria, curtosis])

        # Nombres de las estadísticas
        nombres = ["Mínimo", "Q1", "Media", "Media recortada", "Mediana",
                "Varianza", "Desviación Estándar", "Q3", "Máximo", "Simetría",
                "Curtosis"]

        # Crear un DataFrame con los resultados
        descr = pd.DataFrame({'Estadística': nombres, 'Valor': desc})

        # Mostrar la tabla
        #print(descr)

        return descr 


    def graficar_histograma_con_curva(self, datos, columna):
        """
        Función para graficar un histograma de la columna especificada junto con la curva de densidad normal.

        Parámetros:
        - datos: DataFrame que contiene los datos.
        - columna: nombre de la columna del DataFrame para calcular la media y la desviación estándar.
        """
        # Cálculo de la media y desviación estándar
        mu = datos[columna].mean()
        s = datos[columna].std()

        # Crear el histograma
        plt.figure(figsize=(10, 6))
        plt.hist(datos[columna], density=True, bins=30, color="lightblue", alpha=0.7, edgecolor='black')

        # Crear la curva de densidad normal
        x = np.linspace(datos[columna].min(), datos[columna].max(), 100)
        plt.plot(x, norm.pdf(x, mu, s), color='red', linewidth=2, label='Curva de Densidad Normal')

        # Añadir líneas verticales para la media y las desviaciones estándar
        plt.axvline(mu, color='blue', linestyle='--', linewidth=2, label='Media')
        plt.axvline(mu + s, color='green', linestyle='--', linewidth=2, label='Media + 1 Desviación Estándar')
        plt.axvline(mu - s, color='green', linestyle='--', linewidth=2, label='Media - 1 Desviación Estándar')

        # Configurar los títulos y etiquetas
        plt.title('Histograma de ' + columna + ' con Curva de Densidad Normal', fontsize=16)
        plt.xlabel(columna, fontsize=14)
        plt.ylabel('Densidad', fontsize=14)
        plt.legend()
        plt.grid(False)

        # Mostrar la gráfica
        plt.tight_layout()
        plt.show()


#df = pd.read_csv('dataset_food.csv', low_memory = False)

#tr = config_table()

#tr.graficar_histograma_con_curva(df, 'venta')