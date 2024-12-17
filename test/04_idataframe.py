# from IPython.display import display, HTML

import numpy as np
import pandas as pd
import plotnine as pn
import idataframe as idf

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

vpl = (idf.tools.ValuePipeLine().debug()
    .parse_str()
    .if_str_match(email1)
        .format_str_by_groups('{username}###{domain}')
    .elif_str_match(email2)
        .format_str_by_groups('{username}@@@{domain}')
    .elif_str_match(email3)
        .format_str_by_groups('{username}!!!{domain}')
    .else_()
    .end_if()
)
vpl('j@ravv.nl')
vpl(42)

vpl = (idf.tools.ValuePipeLine().debug()
    .if_value_greater_than(10)
        .map_fn(lambda x: 1*x)
    .elif_value_greater_than(0)
        .map_fn(lambda x: 2*x)
    .else_()
        .map_fn(lambda x: 10*x)
    .end_if()
)
vpl(1)
vpl(42)

vpl = (idf.tools.ValuePipeLine().debug()
    .if_value_equal_to('asdfa')
        .change('___')
    .elif_value_equal_to('asdf')
        .change('yes')
    .else_()
        .change('no')
    .end_if()
)
vpl('asdf')
