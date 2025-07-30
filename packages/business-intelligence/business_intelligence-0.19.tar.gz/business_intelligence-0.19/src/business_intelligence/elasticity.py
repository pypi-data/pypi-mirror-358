import pandas as pd
import numpy as np
import statsmodels.api as sm

class config_table:
    def __init__(self, date_col = None,
                 articule_cod_col=None, 
                 quantity_col=None, 
                 sales_col=None,
                 costo_col = None):
        self.date = date_col
        self.articule = articule_cod_col
        self.price_col = sales_col
        self.quantity_col = quantity_col
        self.cost_col = costo_col



    def calculate_elasticity(self,dataframe=None ,cod_art=None):
        """
        Calculate the price elasticity of demand.
        """
        if dataframe.empty:
            raise ValueError('Se requiere un DataFrame')

        # Select the columns of interest
        required_columns = [self.date,self.articule,self.price_col, self.quantity_col]
        for col in required_columns:
            if col not in dataframe.columns: 
                raise ValueError(f'La columna {col} no se encuentra en el dataframe')
        dataframe = dataframe[required_columns]

        # Filter the data by the articule
        if cod_art is not None:
            dataframe = dataframe[dataframe[self.articule] == cod_art]
            if dataframe.empty:
                raise ValueError(f'No se encontro el articulo cod {cod_art}')

        # Convertir las columnas a tipo numerico 
        dataframe[self.price_col] = pd.to_numeric(dataframe[self.price_col], errors='coerce')
        dataframe[self.quantity_col] = pd.to_numeric(dataframe[self.quantity_col], errors='coerce')

        # Eliminar filas con nan en columnas clave
        dataframe.dropna(subset=[self.price_col, self.quantity_col], inplace=True)

        # create a new column for the single price
        dataframe['range_price_avg'] = (dataframe[self.price_col] / dataframe[self.quantity_col]).round(0)

        # remove the rows with zero price or quantity
        dataframe = dataframe[(dataframe['range_price_avg'] > 0) & (dataframe[self.quantity_col] > 0)]

        # Calculate the total 
        prices_unique = dataframe['range_price_avg'].sort_values(ascending=True).unique()
        demand = []
        for price in prices_unique:
            demand.append(dataframe[dataframe['range_price_avg'] == price][self.quantity_col].sum())

        # Discritize the singel prices
        # Calculate inverval number using 'Sturges' rule
        num_bins = int(np.ceil(1 + np.log2(len(dataframe['range_price_avg']))))
        
        ranges = pd.DataFrame({'range_price_avg':prices_unique})
        ranges = pd.qcut(ranges['range_price_avg'], q=num_bins).unique()
        
        # Create a table with the demand for each price range
        table = pd.DataFrame({'range_price_avg':prices_unique, 'demand':demand})
        for range in ranges:
            for index, row in table.iterrows():
                if row['range_price_avg'] in range:
                    table.loc[index, 'range_price'] = range
        table = table.groupby('range_price').agg({'demand':'sum'}).reset_index() 

        # Calculate the elasticity of demand for each price range
        table['range_price_avg'] = table['range_price'].apply(lambda x: x.mid).round(0)
        table = table[['range_price','range_price_avg','demand']]
        table['var_range_price_avg'] = table['range_price_avg'].pct_change().abs()
        table['var_demand'] = table['demand'].pct_change().abs()
    
        # Create column log 
        table['log_price'] = np.log(table['range_price_avg'])
        table['log_demand'] = np.log(table['demand'])

        # Definir variables independiente y dependiente
        X = sm.add_constant(table['log_price']) 
        y = np.log(table['log_demand'])

        # Ajustar modelo de regresión log-log
        modelo = sm.OLS(y, X).fit()

        # Mostrar resumen del modelo
        print(modelo.summary())

        # Extraer la elasticidad precio de la demanda
        elasticidad_precio = modelo.params['log_price']
        print(f"Elasticidad Precio de la Demanda: {elasticidad_precio:.2f}")

        table = pd.DataFrame(table)

        return table

   
#df = pd.read_csv('dataset_food.csv', low_memory = False)#


#table = config_table(
#    date_col ='fecha',
#    sales_col = 'venta',
#    quantity_col = 'kilos',
#    costo_col= '_costo_venta',
#    articule_cod_col= 'cod_art'
#        )

#print(table.calculate_elasticity(dataframe=df, cod_art='5972discarvi'))