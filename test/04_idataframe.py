# from IPython.display import display, HTML

# import numpy as np
# import pandas as pd
# import plotnine as pn
import idataframe as idf
import idataframe.tools as idft


# df_sd = idf.DataFrame(pd.read_csv("data/sastdes.csv").drop(columns=[]))


# df_planets = idf.DataFrame(pd.read_csv("data/planets.csv"))

# df_planets.register({
#     'method': idf.Label,
#     'number': idf.Count,
#     'orbital_period': idf.Amount,
#     'mass': idf.Amount,
#     'distance': idf.Amount,
#     'year': idf.Count,
# })

# df_planets.parse_all()

# df = df_planets.df

# print(df)
# print(df_planets._df_original)


a = idft.Value(25.4, ['msg 1', 'msg 2', 'msg 3'])
b = idft.Value(a, 'msg 4')
c = idft.Value(None, 'only msg')
d = idft.Value('asdf1', 'msg 1')
dd = idft.Value('asdf2', 'msg 2')

e = a >> idft.parse_int
f = b >> idft.parse_int >> idft.double >> idft.double
g = c >> idft.parse_int >> idft.double
h = d >> idft.parse_int >> idft.double

i = d | dd
j = i >> idft.concat    # TODO stack pop  --> i value is empty (because of pop)


#TODO  deal with np.nan values in dataframe -> Amount   put 'nan|' in regexp
