import pandas as pd
from business_intelligence import elasticity


df = './dataset/dataset_food.csv'
df = pd.read_csv(df, low_memory=False)

test1 = elasticity.config_table(
    data=df, 
    date_col= 'fecha',
    articule_cod_col='cod_art',
    quantity_col= 'kilos',
    sales_col='_ventas')

print(test1.calculate_elasticity(cod_art='5972discarvi'))
