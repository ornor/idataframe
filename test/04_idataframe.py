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




email1 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)#(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"
email2 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)@(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"
email3 = "^(?P<username>[a-zA-Z][a-zA-Z0-9._%+\-]*)!(?P<domain>[a-zA-Z][a-zA-Z.\-]+\.[a-zA-Z]{2,})$"

print('\n')
(it.Value('j@ravv.nl') | it.debug()
    | it.parse_str()
    | it.if_str_match(email1)
        | it.format_str_by_groups('{username}###{domain}')
    | it.elif_str_match(email2)
        | it.format_str_by_groups('{username}@@@{domain}')
    | it.elif_str_match(email3)
        | it.format_str_by_groups('{username}!!!{domain}')
    | it.else_()
    | it.end_if()
)

print('\n')
(it.Value(1) | it.debug()
    | it.if_value_greater_than(10)
        | it.map_fn(lambda x: 1*x)
    | it.elif_value_greater_than(0)
        | it.map_fn(lambda x: 2*x)
    | it.else_()
        | it.map_fn(lambda x: 10*x)
    | it.end_if()
)

print('\n')
(it.Value('asdf') | it.debug()
    | it.if_value_equal_to('asdfa')
        | it.change('___')
    | it.elif_value_equal_to('asdf')
        | it.change('yes')
    | it.else_()
        | it.change('no')
    | it.end_if()
)

# c = it.Value([None, 34, None], {'foo': 42}, 'msg1') | it.parse_int
# d = c | it.parse_str
# e = d | it.parse_float

# it.Value([12, 23, 34, 45], None, 'asdf') | it.stack_product | debug

# it.Value(['asdf', ';lkj'], None, 'asdf') | it.stack_reverse | it.stack_concat | debug

# it.Value(['asdf', ';lkj'], None, 'asdf') | it.map_fn(lambda x:2*x) | debug

# c | it.replace_na('yes') | debug
