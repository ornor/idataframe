from IPython.display import display, HTML

import numpy as np
import pandas as pd
import plotnine as pn
import idataframe as idf


# df_sd = idf.DataFrame(pd.read_csv("test-data/sastdes.csv").drop(columns=[]))


df_planets = idf.DataFrame(pd.read_csv("test-data/planets.csv"))

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

#TODO  deal with np.nan values in dataframe -> Amount   put 'nan|' in regexp