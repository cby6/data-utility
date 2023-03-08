import pandas as pd
import numpy as np

df = pd.read_csv('path')

df = np.where(df['column1'] == df['column2'],1,0)

df = df[['column1', 'column2']]

df = df.drop_duplicates()

df = df.iloc[:,2:4]


