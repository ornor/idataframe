# from IPython.display import display, HTML

import numpy as np
import pandas as pd
import plotnine as pn
import idataframe as idf
import idataframe.tools as it


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







print()
print(80*'=')
print()

email1 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)#(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"
email2 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)@(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"
email3 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)!(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"


a = it.Value(['j@ravv.nl', 42], dict(foo=True), 'start msg')
b = (a
      | it.parse_str
      | it.match(email1) | it.f_str('{username}###{domain}')
      | it.match(email2) | it.f_str('{username}@@@{domain}')
      | it.match(email3) | it.f_str('{username}!!!{domain}')
    )
print(repr(b))

c = it.Value([None, 34, None], {'foo': 42}, 'msg1') | it.parse_int
d = c | it.parse_str
e = d | it.parse_float

print(repr(it.Value([12, 23, 34, 45], None, 'asdf') | it.stack_product))
print(repr(it.Value(['asdf', ';lkj'], None, 'asdf')
           | it.stack_reverse | it.stack_concat))
print(repr(it.Value(['asdf', ';lkj'], None, 'asdf')
           | it.map_fn(lambda x:2*x)))
print(repr(c | it.replace_na('yes')))
