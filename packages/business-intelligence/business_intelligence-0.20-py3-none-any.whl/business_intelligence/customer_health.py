# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:13:29 2024

@author: Alejandro Yegros

Corregir, sacar del constructor el select_customer, y agregarlo como parámetro en los métodos.
"""
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler

class customer_diagnostic():
    def __init__(self, data, col_date, col_customer_code, col_sku_code, ikey, col_customer_type):
        """
        Inicializa la clase customer_diagnostic.
        Se deben indicar los nombres de las columnas en las que se van a encontrar los datos.
        """
        self.path = data
        self.date = col_date
        self.customer_code = col_customer_code
        self.sku_code = col_sku_code
        self.ikey = ikey
        self.customer_type = col_customer_type
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def _get_base_dataframe(self, select_customer=None, universo=False):
        """
        Método interno para obtener el DataFrame base filtrado.
        
        Args:
            select_customer (str, optional): Código del cliente a seleccionar. Si es None y universo es False,
                                             se espera que este método sea llamado con un cliente definido.
            universo (bool): Si es True, selecciona todos los clientes excepto el `select_customer`
                             del mismo `customer_type`. Si es False, selecciona solo el `select_customer`.
        
        Returns:
            pd.DataFrame: DataFrame procesado.
        """
        df = self.path[[self.date, self.customer_code, self.sku_code, self.customer_type, self.ikey]].copy()
        
        if universo:
            if select_customer is None:
                raise ValueError("Para 'universo=True', 'select_customer' no puede ser None.")
            
            # Obtener el tipo de cliente del cliente seleccionado
            select_customer_type_df = df[df[self.customer_code] == select_customer]
            if select_customer_type_df.empty:
                raise ValueError(f"El cliente '{select_customer}' no se encontró en el dataset para determinar su tipo.")
            select_customer_type = select_customer_type_df[self.customer_type].iloc[-1]
            
            # Filtrar por tipo de cliente y excluir el cliente seleccionado
            df = df[(df[self.customer_type] == select_customer_type) & (df[self.customer_code] != select_customer)]
        else:
            if select_customer is None:
                # Si select_customer es None y universo es False, probablemente se esté llamando
                # para el caso de un solo cliente en benchmark, donde ya fue definido en indicator_outcome.
                # En un uso directo, sería un error.
                raise ValueError("Para 'universo=False', 'select_customer' debe ser proporcionado.")
            df = df[df[self.customer_code] == select_customer]
            
        df[self.date] = pd.to_datetime(df[self.date])
        df = df.groupby([self.date, self.customer_code, self.sku_code, self.customer_type]).agg({self.ikey:'sum'}).reset_index()
        df = df.sort_values(by=self.date)
        return df 

    def days_since_last_sales(self, select_customer, universo=False):
        """Calcula el tiempo transcurrido desde la última compra del cliente.
        Se considera como última fecha la fecha máxima del dataset.
        """
        df = self._get_base_dataframe(select_customer=select_customer, universo=universo) 
        
        if df.empty:
            if universo:
                # Para el universo, si el df está vacío después del filtrado, aún necesitamos calcular el rango
                # basado en el dataset completo para obtener un benchmark significativo.
                # Sin embargo, para este cálculo específico (days_since_last_sales), si no hay datos,
                # no se puede calcular. Se podría devolver un DataFrame vacío o manejar el error.
                # Optamos por devolver un DataFrame vacío en este caso para permitir el flujo.
                return pd.DataFrame(columns=['customer', 'result']) if not universo else pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

        df['last_sales'] = df.groupby(self.customer_code)[self.date].transform('max')
        
        # Necesitamos el max_date_dataset del universo completo para una comparación consistente
        full_df_for_max_date = self.path[[self.date]].copy()
        full_df_for_max_date[self.date] = pd.to_datetime(full_df_for_max_date[self.date])
        df['last_date_dataset'] = full_df_for_max_date[self.date].max()

        df['time_since_last_sales'] = (df.last_date_dataset - df['last_sales']).dt.days + 1
        df = df.groupby([self.customer_code])['time_since_last_sales'].max().reset_index()
        
        if universo:
            # Para el universo, calculamos los rangos y los índices universales
            if df.empty: # Si el universo está vacío, no se pueden calcular los rangos
                return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

            universo_rango = list(range(df.time_since_last_sales.min(), df.time_since_last_sales.max() + 1))
            universo_rango = pd.DataFrame(data=universo_rango, columns=['time_since_last_sales_rangos'])
            
            max_bins = min(100, int(df.time_since_last_sales.mean())) if not df.empty else 1 # Ajuste para evitar errores si df está vacío
            if max_bins == 0: max_bins = 1 # Asegura al menos 1 bin si el promedio es 0

            rango = pd.cut(universo_rango.time_since_last_sales_rangos, bins=max_bins, precision=0).unique()
            values = list(df.time_since_last_sales)
            resultado = []
            for r in rango:
                contador = 0
                for v in values:
                    if (v > r.left) and (v <= r.right):
                        contador += 1
                resultado.append([int(r.left), int(r.right), contador]) # Convertir a int directamente

            df_result = pd.DataFrame(resultado) 
            if not df_result.empty:
                df_result['indice_universal'] = df_result.index
                df_result['indice_universal'] = (self.scaler.fit_transform(df_result[['indice_universal']]) * 100).astype(int)
                df_result['indice_universal'] = df_result['indice_universal'].sort_index(ascending=False).reset_index(drop=True)
                df_result.columns = 'lim_low','lim_up','universo','indice_universal'
                df_result = df_result.apply(pd.to_numeric, errors='coerce')
            else:
                df_result = pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal']) # Devolver DF vacío si no hay resultados
            return df_result
        else:
            df.columns = ['customer','result']
            return df
        
    def customer_age_days(self, select_customer, universo=False):
        """Calcula la edad de los clientes en función a la fecha de su primera compra vs la última del dataset."""
        df = self._get_base_dataframe(select_customer=select_customer, universo=universo)
        
        if df.empty:
            return pd.DataFrame(columns=['customer', 'result']) if not universo else pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

        df['born'] = df.groupby(self.customer_code)[self.date].transform('min')
        
        full_df_for_max_date = self.path[[self.date]].copy()
        full_df_for_max_date[self.date] = pd.to_datetime(full_df_for_max_date[self.date])
        df['last_date_dataset'] = full_df_for_max_date[self.date].max()

        df['age_days'] = (df.last_date_dataset - df['born']).dt.days
        df = df.groupby([self.customer_code])['age_days'].max().reset_index()

        if universo:
            if df.empty:
                return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

            universo_rango = list(range(df.age_days.min(), df.age_days.max() + 1))
            universo_rango = pd.DataFrame(data=universo_rango, columns=['age_days_rango'])
            
            max_bins = min(100, int(df.age_days.mean())) if not df.empty else 1
            if max_bins == 0: max_bins = 1

            rango = pd.cut(universo_rango.age_days_rango, bins=max_bins, precision=0).unique() # Usar max_bins
            values = list(df.age_days)
            resultado = []
            for r in rango:
                contador = 0
                for v in values:
                    if (v > r.left) and (v <= r.right):
                        contador += 1
                resultado.append([int(r.left), int(r.right), contador])

            df_result = pd.DataFrame(resultado) 
            if not df_result.empty:
                df_result['indice_universal'] = df_result.index
                df_result['indice_universal'] = (self.scaler.fit_transform(df_result[['indice_universal']]) * 100).astype(int)
                df_result['indice_universal'] = df_result['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
                df_result.columns = 'lim_low','lim_up','universo','indice_universal'
                df_result = df_result.apply(pd.to_numeric, errors='coerce')
            else:
                df_result = pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])
            return df_result
        else:
            df.columns = ['customer','result']
            return df

    def recency(self, select_customer, universo=False):
        """La recency son los días que pasan desde que un cliente hace una nueva compra."""
        df = self._get_base_dataframe(select_customer=select_customer, universo=universo)
        
        if df.empty:
            return pd.DataFrame(columns=['customer', 'result']) if not universo else pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

        df = df.groupby([self.date, self.customer_code]).agg({self.ikey:'sum'}).reset_index()
        nro_customer = df[self.customer_code].unique()
        result_list = []
        for c in nro_customer:
            df_ = df[df[self.customer_code]==c].sort_values(by=self.date, ascending=True)
            df_['recency'] = df_.groupby(self.customer_code)[self.date].diff().dt.days
            df_ = df_.groupby([self.customer_code]).agg({'recency':'mean'}).fillna(0).reset_index()
            df_.recency = df_.recency.astype('int64')
            result_list.append(df_)
        
        if not result_list: # Manejar el caso donde result_list está vacío
            result = pd.DataFrame(columns=[self.customer_code, 'recency'])
        else:
            result = pd.concat(result_list, ignore_index=True)

        if universo:
            if result.empty or result['recency'].empty:
                return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

            min_recency = result.recency.min()
            max_recency = result.recency.max()
            universo_rango = list(range(min_recency, max_recency + 1))
            universo_rango = pd.DataFrame(data=universo_rango, columns=['recency'])
            
            max_bins = min(100, int(result.recency.mean())) if not result.empty else 1
            if max_bins == 0: max_bins = 1

            rango = pd.cut(universo_rango.recency, bins=max_bins, precision=0).unique() # Usar max_bins
            values = list(result.recency)
            resultado = []
            for r in rango:
                contador = 0
                for v in values:
                    if (v > r.left) and (v <= r.right):
                        contador += 1
                resultado.append([int(r.left), int(r.right), contador])

            df_result = pd.DataFrame(resultado) 
            if not df_result.empty:
                df_result['indice_universal'] = df_result.index
                df_result['indice_universal'] = (self.scaler.fit_transform(df_result[['indice_universal']]) * 100).astype(int)
                df_result['indice_universal'] = df_result['indice_universal'].sort_index(ascending=False).reset_index(drop=True)
                df_result.columns = 'lim_low','lim_up','universo','indice_universal'
                df_result = df_result.apply(pd.to_numeric, errors='coerce')
            else:
                df_result = pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])
            return df_result
        else:
            result.columns = ['customer','result']
            return result

    def nro_sku(self, select_customer, universo=False):
        """Calcula la cantidad de SKUs que compró el o los clientes."""
        df = self._get_base_dataframe(select_customer=select_customer, universo=universo)
        
        if df.empty:
            return pd.DataFrame(columns=['customer', 'result']) if not universo else pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

        df = df.groupby([self.customer_code]).agg({self.sku_code:'nunique'}).reset_index()     
        df = df[df[self.sku_code] > 0] # Asegurarse de que el número de SKUs sea positivo

        if universo:
            if df.empty or df[self.sku_code].empty:
                return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

            universo_rango = list(range(df[self.sku_code].min(), df[self.sku_code].max() + 1))
            universo_rango = pd.DataFrame(data=universo_rango, columns=['sku_code_rango'])
            
            max_bins = min(100, int(df[self.sku_code].mean())) if not df[self.sku_code].empty else 1
            if max_bins == 0: max_bins = 1

            rango = pd.cut(universo_rango.sku_code_rango, bins=max_bins, precision=0).unique() # Usar max_bins
            values = list(df[self.sku_code])
            resultado = []
            for r in rango:
                contador = 0
                for v in values:
                    if (v > r.left) and (v <= r.right):
                        contador += 1
                resultado.append([int(r.left), int(r.right), contador])

            df_result = pd.DataFrame(resultado) 
            if not df_result.empty:
                df_result['indice_universal'] = df_result.index
                df_result['indice_universal'] = (self.scaler.fit_transform(df_result[['indice_universal']]) * 100).astype(int)
                df_result['indice_universal'] = df_result['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
                df_result.columns = 'lim_low','lim_up','universo','indice_universal'
                df_result = df_result.apply(pd.to_numeric, errors='coerce')
            else:
                df_result = pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])
            return df_result
        else:
            df.columns = ['customer','result']
            return df

    def frequency(self, select_customer, universo=False):
        """Cuántas veces el cliente hizo una compra. Se tiene en cuenta una sola compra por fecha."""
        df = self._get_base_dataframe(select_customer=select_customer, universo=universo)
        
        if df.empty:
            return pd.DataFrame(columns=['customer', 'result']) if not universo else pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

        df = df[[self.customer_code, self.date]].groupby([self.customer_code]).agg({self.date:'nunique'}).reset_index()
        df = df[df[self.date] > 0] # Asegurarse de que la frecuencia sea positiva

        if universo:
            if df.empty or df[self.date].empty:
                return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

            universo_rango = list(range(df[self.date].min(), df[self.date].max() + 1))
            universo_rango = pd.DataFrame(data=universo_rango, columns=['frecuency_rango'])
            
            max_bins = min(100, int(df[self.date].mean())) if not df[self.date].empty else 1
            if max_bins == 0: max_bins = 1

            rango = pd.cut(universo_rango.frecuency_rango, bins=max_bins, precision=0).unique() # Usar max_bins
            values = list(df[self.date])
            resultado = []
            for r in rango:
                contador = 0
                for v in values:
                    if (v > r.left) and (v <= r.right):
                        contador += 1
                resultado.append([int(r.left), int(r.right), contador])

            df_result = pd.DataFrame(resultado) 
            if not df_result.empty:
                df_result['indice_universal'] = df_result.index
                df_result['indice_universal'] = (self.scaler.fit_transform(df_result[['indice_universal']]) * 100).astype(int)
                df_result['indice_universal'] = df_result['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
                df_result.columns = 'lim_low','lim_up','universo','indice_universal'
                df_result = df_result.apply(pd.to_numeric, errors='coerce')
            else:
                df_result = pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])
            return df_result
        else:
            df.columns = ['customer','result']
            return df

    def sum_ikey(self, select_customer, universo=False):
        """Total de indicator_key.""" 
        df = self._get_base_dataframe(select_customer=select_customer, universo=universo)
        
        if df.empty:
            return pd.DataFrame(columns=['customer', 'result']) if not universo else pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])

        df = df.groupby([self.customer_code]).agg({self.ikey:'sum'}).reset_index()

        if universo:
            if df.empty or df[self.ikey].empty:
                return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])
            
            # Asegurarse de que min_ikey no sea negativo para range()
            min_ikey = int(df[self.ikey].min())
            if min_ikey < 0: min_ikey = 0 
            
            universo_rango = list(range(min_ikey, int(df[self.ikey].max()) + 1))
            universo_rango = pd.DataFrame(data=universo_rango, columns=['ikey_rango'])
            
            max_bins = min(100, int(df[self.ikey].max())) if not df[self.ikey].empty else 1
            if max_bins == 0: max_bins = 1

            rango = pd.cut(universo_rango.ikey_rango, bins=max_bins, precision=0).unique() # Usar max_bins
            values = list(df[self.ikey])
            resultado = []
            for r in rango:
                contador = 0
                for v in values:
                    if (v > r.left) and (v <= r.right):
                        contador += 1
                resultado.append([int(r.left), int(r.right), contador])

            df_result = pd.DataFrame(resultado) 
            if not df_result.empty:
                df_result['indice_universal'] = df_result.index
                df_result['indice_universal'] = (self.scaler.fit_transform(df_result[['indice_universal']]) * 100).astype(int)
                df_result['indice_universal'] = df_result['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
                df_result.columns = 'lim_low','lim_up','universo','indice_universal'
                df_result = df_result.apply(pd.to_numeric, errors='coerce')
            else:
                df_result = pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal'])
            return df_result
        else:
            df.columns = ['customer','result']
            return df
    
    # ==================================================
    # Hacemos un Benchmark de cada variable
    # ==================================================
    def benchmark(self, select_customer, indicator=None):
        """
        Realiza un benchmark de un indicador específico para un cliente.

        Args:
            select_customer (str): Código del cliente a analizar.
            indicator (int): Número del indicador a evaluar.
                1: Days since last sales
                2: Customer age in days
                3: Recency
                4: Nro Sku
                5: Frequency
                6: Indicator key
        """
        funciones = {
            1: self.days_since_last_sales,
            2: self.customer_age_days,
            3: self.recency,
            4: self.nro_sku,
            5: self.frequency,
            6: self.sum_ikey
        }
        
        if indicator not in funciones:
            raise ValueError("Indicador no válido. Por favor, elija un número entre 1 y 6.")

        select_function = funciones[indicator]

        # Obtener datos del universo y del cliente específico
        df_universo = select_function(select_customer=select_customer, universo=True)
        df_customer = select_function(select_customer=select_customer, universo=False)

        if df_universo.empty or df_customer.empty:
            # Manejar el caso donde no hay datos para el benchmark
            print(f"Advertencia: No hay suficientes datos para realizar el benchmark para el indicador {indicator} y cliente {select_customer}.")
            # Se puede retornar un DataFrame vacío o con valores nulos, dependiendo del comportamiento deseado
            return pd.DataFrame(columns=['lim_low', 'lim_up', 'universo', 'indice_universal', 'result_customer', 'customer_outlier_up', 'customer_outlier_low', 'outlier_value', 'result'])


        lim_low = df_universo['lim_low']
        min_low = lim_low.min()
        lim_up = df_universo['lim_up']
        max_up = lim_up.max()
        universo_values = df_universo['universo']
        indice_universal = df_universo['indice_universal']
        customer_result = df_customer['result'].iloc[0] # El resultado del cliente es un único valor

        result_data = []
        for low, up, u, r in zip(lim_low, lim_up, universo_values, indice_universal):
            customer_in_range = None
            if low <= customer_result <= up:
                customer_in_range = customer_result
            result_data.append((low, up, u, r, customer_in_range))

        result_df = pd.DataFrame(result_data, columns=['lim_low', 'lim_up', 'universo', 'indice_universal', 'result_customer'])
        
        result_df['customer_outlier_up'] = result_df['lim_up'].apply(lambda x: customer_result if customer_result > max_up and x == max_up else 0)
        result_df['customer_outlier_low'] = result_df['lim_low'].apply(lambda x: customer_result if customer_result < min_low and x == min_low else 0)
        result_df['outlier_value'] = result_df.customer_outlier_up + result_df.customer_outlier_low
        result_df['result'] = result_df.result_customer.fillna(0) + result_df['outlier_value'] # Usar fillna(0) en lugar de apply lambda con pd.isna
        
        return result_df

    def indicator_outcome(self, customer_list):
        """
        Calcula los resultados de los indicadores para una lista de clientes.
        
        Args:
            customer_list (list): Lista de códigos de clientes a procesar.
            
        Returns:
            pd.DataFrame: Un DataFrame con los resultados de los indicadores para cada cliente.
        """
        title = {
            1: 'Days since last sales',
            2: 'Customer age in days',
            3: 'Recency',
            4: 'Nro Sku',
            5: 'Frecuency',
            6: 'Indicator key'
        }
        
        final_report = []
        for i, cliente in enumerate(customer_list): 
            resultados_clientes = [cliente] # Iniciar con el código del cliente
            
            for indicator_num in range(1, 7):  # Indicadores de 1 a 6
                try:
                    report = self.benchmark(select_customer=cliente, indicator=indicator_num)
                    
                    # Filtrar filas donde 'result' no es 0 para obtener el índice universal relevante
                    filtered_report = report.loc[report['result'] != 0]

                    if not filtered_report.empty:
                        # Si hay un resultado directo, tomar el 'indice_universal' de esa fila
                        # Si hay múltiples, tomar el promedio o un criterio específico
                        datos = filtered_report['indice_universal'].mean()
                    else:
                        # Si 'result' es 0 en todas las filas (ej. cliente fuera de todos los rangos),
                        # buscamos el índice universal que corresponde al outlier o al valor más cercano.
                        # En este caso, el valor del cliente es un outlier, y el `result` del benchmark
                        # ya contiene el valor real del cliente si es un outlier.
                        # Para el `indice_universal`, podríamos buscar la fila más cercana o asignar un valor por defecto.
                        # Por ahora, si no hay 'result' != 0, significa que el cliente no cayó en un bin específico.
                        # Una forma de manejar esto es asignar el índice universal del bin que contiene el valor del cliente
                        # si es un outlier (que ya se calcula en benchmark).
                        # O, si no hay coincidencia, asignar None o un valor por defecto para indicar que está fuera de los rangos comunes.
                        # Vamos a asignar None si no se encuentra un bin para el cliente.
                        datos = None 
                        
                        # Si el cliente es un outlier (arriba o abajo), podemos intentar asignarle el índice universal
                        # del bin de la parte superior o inferior del rango para visualización.
                        if report['customer_outlier_up'].sum() > 0:
                            # Cliente es un outlier superior, asignamos el índice del bin superior
                            datos = report.loc[report['lim_up'] == report['lim_up'].max(), 'indice_universal'].iloc[0]
                        elif report['customer_outlier_low'].sum() > 0:
                            # Cliente es un outlier inferior, asignamos el índice del bin inferior
                            datos = report.loc[report['lim_low'] == report['lim_low'].min(), 'indice_universal'].iloc[0]


                    resultados_clientes.append(datos)
                except Exception as e:
                    print(f'Error al procesar el cliente "{cliente}", indicador "{title[indicator_num]}": {e}')
                    resultados_clientes.append(None) # Añadir None si hay un error
            
            final_report.append(resultados_clientes)
            porcentaje_avance = ((i + 1) / len(customer_list)) * 100
            print(f'Porcentaje de avance: {porcentaje_avance:.1f}%, cliente: {cliente}')

        column_names = ['customer_code'] + [title[i] for i in range(1, 7)]
        informe = pd.DataFrame(final_report, columns=column_names)
        return informe


