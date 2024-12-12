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









email1 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)#(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"
email2 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)@(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"
email3 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)!(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"



a = ( idft.Value(['j@ravv.nl', 42, 43])
      | idft.parse_str
      | idft.match(email1) | idft.form('{username}###{domain}')
      | idft.match(email2) | idft.form('{username}@@@{domain}')
      | idft.match(email3) | idft.form('{username}!!!{domain}')
    )

print(repr(a))
