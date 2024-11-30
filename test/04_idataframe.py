from IPython.display import display, HTML

import numpy as np
import pandas as pd
import plotnine as pn
import idataframe as idf


# df_sd = idf.DataFrame(pd.read_csv("data/sastdes.csv").drop(columns=[]))


df_planets = idf.DataFrame(pd.read_csv("data/planets.csv"))

df_planets.register({
    'method': idf.Label,
    'number': idf.Count,
    'orbital_period': idf.Amount,
    'mass': idf.Amount,
    'distance': idf.Amount,
    'year': idf.Count,
})

df_planets.parse_all()

df = df_planets.df

print(df)
print(df_planets._df_original)


a = idf.tools.Value(25, ['msg 1', 'msg 2', 'msg 3'])
b = idf.tools.Value(a, 'msg 4')
c = idf.tools.Value(None, 'only msg')

#TODO  deal with np.nan values in dataframe -> Amount   put 'nan|' in regexp