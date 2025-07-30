# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:13:29 2024

@author: Alejandro Yegros
"""
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler

class customer_diagnostic():
    def __init__(self,data,col_date,col_customer_code,col_sku_code,ikey,col_customer_type,select_customer=None):
        """ Se debe indicar los nombres de las columnas en la que se va a encontrar los datos"""
        self.path = data
        self.date = col_date
        self.customer_code = col_customer_code
        self.sku_code = col_sku_code
        self.ikey = ikey
        self.select_customer = select_customer
        self.customer_type = col_customer_type
        self.scaler = MinMaxScaler(feature_range=(0,1))

    def dataset(self, universo=False):
        """ 
        # ==================================================
        # Recibimos el df e indicamos cuales son las columnas que contienen:
        # 1. fecha
        # 2. codigo de cliente
        # 3. codigo del articulo
        # 4. ikey: "indicator_key" venta en moneda, cantidad o kilo.
        # 5. Customer_type : Atributo único de cliente 
        # Obs. universo = True - Todos los clientes exceto el seleccionado en select_custormer
        # Obs. Se espera que el dataset tenga ventas por cada artículo. Esto significa que el cliente puede tener más de una compra por cada día
        # ================================================== """
        df = self.path
        df = df[[self.date, self.customer_code,self.sku_code ,self.customer_type,self.ikey]]
        if universo == False:
            # Customer
            df = df[df[self.customer_code] == self.select_customer]
        else:
            # Universo
            select_customer_type = df[df[self.customer_code] == self.select_customer]
            select_customer_type = select_customer_type[self.customer_type].iloc[-1]
            df = df[(df[self.customer_type] == select_customer_type) & (df[self.customer_code] != self.select_customer)]            
        df[self.date] = pd.to_datetime(df[self.date])
        df = df.groupby([self.date, self.customer_code,self.sku_code ,self.customer_type,]).agg({self.ikey:'sum'}).reset_index()
        df = df.sort_values(by= self.date)
        return df          
    def days_since_last_sales(self, universo=False):
        """Calculamos el tiempo que ha trascurrido desde la última compra del cliente, se considera como última fecha a la fecha máxima del dataset """
        df = self.dataset(universo=universo) 
        df['last_sales'] = df.groupby(self.customer_code)[self.date].transform('max')
        df['last_date_dataset'] = self.dataset(universo=True)[self.date].max()
        df['time_since_last_sales'] = (df.last_date_dataset - df['last_sales']).dt.days + 1
        df = df.groupby([self.customer_code])['time_since_last_sales'].max().reset_index()
        # Creamos los rangos del universo usando los mínimos y máximos
        universo_rango = list(range(df.time_since_last_sales.min(),df.time_since_last_sales.max()+1))
        universo_rango = pd.DataFrame(data=universo_rango, columns=['time_since_last_sales_rangos'])
        # Creamos una variable para "topear" la cantidad máxima de bins
        if df.time_since_last_sales.max() > 100: max = 100
        else: max = int(df.time_since_last_sales.mean())
        if universo == True:
            rango = pd.cut(universo_rango.time_since_last_sales_rangos, bins=max, precision=0).unique()
            values = list(df.time_since_last_sales)
            resultado = []
            for r in rango:
                contador=0
                for v in values:
                    if (v > r.left) & (v <= r.right):
                        contador +=1
                resultado.append([f'{int(r.left)}',f'{int(r.right)}', contador])
            df = pd.DataFrame(resultado)          
            df['indice_universal'] = df.index
            df['indice_universal'] = (self.scaler.fit_transform(df[['indice_universal']])*100).astype(int)
            df['indice_universal'] = df['indice_universal'].sort_index(ascending=False).reset_index(drop=True)
            df.columns = 'lim_low','lim_up','universo','indice_universal'
            df = df.apply(pd.to_numeric, errors='coerce')
        else:
            df.columns = ['customer','result']
        return df
    def customer_age_days(self, universo=False):
        """Calculamos la edad que tienen los clientes en función a la self.date de su primera compra vs su última del dataset """
        df = self.dataset(universo=universo)
        df['born'] = df.groupby(self.customer_code)[self.date].transform('min')
        df['last_date_dataset'] = self.dataset(universo=True)[self.date].max()
        df['age_days'] = (df.last_date_dataset - df['born']).dt.days
        df = df.groupby([self.customer_code])['age_days'].max().reset_index()
        # Creamos los rangos del universo usando los mínimos y máximos
        universo_rango = list(range(df.age_days.min(),df.age_days.max()+1))
        universo_rango = pd.DataFrame(data=universo_rango, columns=['age_days_rango'])
        # Creamos una variable para "topear" la cantidad máxima de bins
        if df.age_days.max() > 100: max = 100 
        else: max=int(df.age_days.mean())
        if universo == True:
            rango = pd.cut(universo_rango.age_days_rango, bins=100, precision=0).unique()
            values = list(df.age_days)
            resultado = []
            for r in rango:
                contador=0
                for v in values:
                    if (v > r.left) & (v <= r.right):
                        contador +=1
                resultado.append([f'{int(r.left)}',f'{int(r.right)}', contador])
            df = pd.DataFrame(resultado)          
            df['indice_universal'] = df.index
            df['indice_universal'] = (self.scaler.fit_transform(df[['indice_universal']])*100).astype(int)
            df['indice_universal'] = df['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
            df.columns = 'lim_low','lim_up','universo','indice_universal'
            df = df.apply(pd.to_numeric, errors='coerce')
        else:
            df.columns = ['customer','result']
        return df
    def recency(self,universo=False):
        """La recency son los días que pasan desde que un cliente hace una nueva compra"""
        df = self.dataset(universo=universo)
        df = df.groupby([self.date,self.customer_code]).agg({self.ikey:'sum'}).reset_index()
        nro_customer = df[self.customer_code].unique()
        result = []
        for c in nro_customer:
            df_ = df[df[self.customer_code]==c].sort_values(by=self.date, ascending=True)
            df_['recency'] = df_.groupby(self.customer_code)[self.date].diff().dt.days
            df_ = df_.groupby([self.customer_code]).agg({'recency':'mean'}).fillna(0).reset_index()
            df_.recency = df_.recency.astype('int64')
            result.append(df_)
        result = pd.concat(result, ignore_index=True)
        # Creamos los rangos del universo usando los mínimos y máximos
        universo_rango = list(range(result.recency.min(),result.recency.max()+1))
        universo_rango = pd.DataFrame(data=universo_rango, columns=['recency'])
        # Creamos una variable para "topear" la cantidad máxima de bins
        if result.recency.max() > 100: max = 100 
        else: max=int(result.recency.mean())
        if universo == True:
            rango = pd.cut(universo_rango.recency, bins=100, precision=0).unique()
            values = list(result.recency)
            resultado = []
            for r in rango:
                contador=0
                for v in values:
                    if (v > r.left) & (v <= r.right):
                        contador +=1
                resultado.append([f'{int(r.left)}',f'{int(r.right)}', contador])
            df = pd.DataFrame(resultado)          
            df['indice_universal'] = df.index
            df['indice_universal'] = (self.scaler.fit_transform(df[['indice_universal']])*100).astype(int)
            df['indice_universal'] = df['indice_universal'].sort_index(ascending=False).reset_index(drop=True)
            df.columns = 'lim_low','lim_up','universo','indice_universal'
            df = df.apply(pd.to_numeric, errors='coerce')
        else:
            df = result
            df.columns = ['customer','result']
        return df
    def nro_sku(self,universo=False):
        """Calculamos la cantidad de sku que compró el o los clientes"""
        df = self.dataset(universo=universo)
        df = df.groupby([self.customer_code]).agg({self.sku_code:'nunique'}).reset_index()     
        df = df[df[self.sku_code]>0]
        # Creamos los rangos del universo usando los mínimos y máximos
        universo_rango = list(range(df[self.sku_code].min(),df[self.sku_code].max()+1))
        universo_rango = pd.DataFrame(data=universo_rango, columns=['sku_code_rango'])
        # Creamos una variable para "topear" la cantidad máxima de bins
        if df[self.sku_code].count() > 100: max = 100 
        else: max = int((df[self.sku_code].mean()))
        if universo == True:
            rango = pd.cut(universo_rango.sku_code_rango, bins=max, precision=0).unique()
            values = list(df[self.sku_code])
            resultado = []
            for r in rango:
                contador=0
                for v in values:
                    if (v > r.left) & (v <= r.right):
                        contador +=1
                resultado.append([f'{int(r.left)}',f'{int(r.right)}', contador])
            df = pd.DataFrame(resultado)          
            df['indice_universal'] = df.index
            df['indice_universal'] = (self.scaler.fit_transform(df[['indice_universal']])*100).astype(int)
            df['indice_universal'] = df['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
            df.columns = 'lim_low','lim_up','universo','indice_universal'
            df = df.apply(pd.to_numeric, errors='coerce')
        else:
            df.columns = ['customer','result']
        return df
    def frequency(self,universo=False):
        """Cuantas vences el cliente hizo una compra. Se tiene en cuenta una sola compra por self.date"""
        df = self.dataset(universo=universo)
        df['id_customer']= df[self.customer_code]
        df = df[[self.customer_code,self.date]].groupby([self.customer_code]).agg({self.date:'nunique'}).reset_index()
        df = df[df[self.date]>0]
        # Creamos los rangos del universo usando los mínimos y máximos
        universo_rango = list(range(df[self.date].min(),df[self.date].max()+1))
        universo_rango = pd.DataFrame(data=universo_rango, columns=['frecuency_rango'])
        # Creamos una variable para "topear" la cantidad máxima de bins
        if df[self.date].count() > 100: max = 100 
        else: max = int(df[self.date].mean())
        if universo == True:
            rango = pd.cut(universo_rango.frecuency_rango, bins=max, precision=0).unique()
            values = list(df[self.date])
            resultado = []
            for r in rango:
                contador=0
                for v in values:
                    if (v > r.left) & (v <= r.right):
                        contador +=1
                # Ajuste
                resultado.append([f'{int(r.left)}',f'{int(r.right)}', contador])
            df = pd.DataFrame(resultado)          
            df['indice_universal'] = df.index
            df['indice_universal'] = (self.scaler.fit_transform(df[['indice_universal']])*100).astype(int)
            df['indice_universal'] = df['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
            # Ajuste
            df.columns = 'lim_low','lim_up','universo','indice_universal'
            df = df.apply(pd.to_numeric, errors='coerce')
        else:
            df.columns = ['customer','result']
        return df
    def sum_ikey(self,universo=False):
        """ total de indicator_key""" 
        df = self.dataset(universo=universo)
        df = df.groupby([self.customer_code]).agg({self.ikey:'sum'}).reset_index()
        # Creamos los rangos del universo usando los mínimos y máximos
        universo_rango = list(range(df[self.ikey].min()-1,df[self.ikey].max()+1))
        universo_rango = pd.DataFrame(data=universo_rango, columns=['ikey_rango'])
        # Creamos una variable para "topear" la cantidad máxima de bins
        if df[self.ikey].max() > 100: max = 100
        else: max = int(df[self.ikey].max())
        if universo == True:
            rango = pd.cut(universo_rango.ikey_rango, bins=max, precision=0).unique()
            values = list(df[self.ikey])
            resultado = []
            for r in rango:
                contador=0
                for v in values:
                    if (v > r.left) & (v <= r.right):
                        contador +=1
                resultado.append([f'{int(r.left)}',f'{int(r.right)}', contador])
            df = pd.DataFrame(resultado)          
            df['indice_universal'] = df.index
            df['indice_universal'] = (self.scaler.fit_transform(df[['indice_universal']])*100).astype(int)
            # Configuramos la valoración
            df['indice_universal'] = df['indice_universal'].sort_index(ascending=True).reset_index(drop=True)
            df.columns = 'lim_low','lim_up','universo','indice_universal'
            df = df.apply(pd.to_numeric, errors='coerce')
        else:
            df.columns = ['customer','result']
        return df
    
    # ==================================================
    # Hacemos un Benchmark de cada variable
    # ==================================================
    def benchmark(self,indicator=None):
        """
        days_since_last_sales = 1
        customer_age_days = 2
        recency = 3
        nro_sku = 4
        frequency = 5
        sum_ikey = 6
        """
        funciones = {
            1: self.days_since_last_sales,
            2: self.customer_age_days,
            3: self.recency,
            4: self.nro_sku,
            5: self.frequency,
            6: self.sum_ikey
        }
        select_funtion = funciones[indicator]
        if indicator == indicator:
            lim_low = select_funtion(universo=True).loc[:, 'lim_low']
            min_low = min(lim_low)
            lim_up = select_funtion(universo=True).loc[:, 'lim_up']
            max_up = max(lim_up)
            universo = select_funtion(universo=True).loc[:,'universo']
            indice_universal = select_funtion(universo=True).loc[:,'indice_universal']
            customer = select_funtion(universo=False).loc[:, 'result'] 
        result = []
        for low,up,u,r in zip(lim_low,lim_up,universo,indice_universal):
            e = [] # identifique the row with the range of the customer 
            if low <= customer[0] <= up:
                e.append(customer[0])
            else:
                e.append(None)
            result.append((low, up,u,r,e[0]))
        result = pd.DataFrame(result, columns=['lim_low', 'lim_up','universo','indice_universal','result_customer'])
        result['customer_outlier_up'] = result['lim_up'].apply(lambda x: customer[0] if customer[0] > max_up and x == max_up else 0)
        result['customer_outlier_low'] = result['lim_low'].apply(lambda x: customer[0] if customer[0] < min_low and x == min_low else 0)
        result['outlier_value'] = result.customer_outlier_up + result.customer_outlier_low
        result['result'] = result.result_customer.apply(lambda x: 0 if pd.isna(x) else x)         
        result['result'] = result['outlier_value']+ result['result']
        return result
    
    def indicator_outcome(self, customer_list):
        title = {
            1: 'Days since last sales',
            2: 'Customer age in days',
            3: 'Recency',
            4: 'Nro Sku',
            5: 'Frecuency',
            6: 'Indicator key'
        }
        avance = 0
        # Iterar sobre cada cliente en la lista
        final_report = []
        for cliente in customer_list: 
            # Establecer el cliente actual en self para usarlo en otros métodos
            self.select_customer = cliente
            resultados_clientes = []
            resultados_clientes.append(cliente)
            for i in range(1, 7):  # Indicadores de 1 a 6
                try:
                    report = self.benchmark(indicator=i, print_barplot=False)
                    report = report.loc[report['result'] != 0]
                    report['customer_code'] = cliente
                    report = report[['customer_code','indice_universal']]
                    report = report.groupby(['customer_code']).agg({'indice_universal':'mean'})
                    datos = (list(report.indice_universal)[0])
                    resultados_clientes.append(datos)
                    #print(resultados_clientes)
                except Exception as e:
                    print(f'Error en el customer {cliente}, el indicador {i}: {e}')
                    pass
            #print(resultados_clientes)
            avance += 1
            porcentaje_avance = (avance / len(customer_list)) * 100
            print(f'Porcentaje de avance: {porcentaje_avance:.1f}%, customer {cliente}')
            final_report.append(resultados_clientes)
        column_names = ['customer_code'] + [title[i] for i in range(1, 7)]
        informe = pd.DataFrame(final_report, columns=column_names)
        return informe


