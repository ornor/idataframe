from IPython.display import display, HTML
import numpy as np
import pandas as pd
import plotnine as pn
from scipy import stats

import idataframe as idf


# custdf = pd.read_csv("data/customers-10000.csv")
# email = idf.Email(custdf['Email'])
email = idf.Email.from_test_data()
email.parse()
email_df = email.df

label = idf.Label.from_test_data()
label.parse()
label_df = label.df

# salesmanhdf = pd.read_csv("data/rollingsales-manhattan.csv")
# addr = idf.StreetAddressUS(salesmanhdf['ADDRESS'])
addr = idf.StreetAddressUS.from_test_data()
addr.parse()
addr_df = addr.df

text = idf.Text.from_test_data()
text.parse()
text_df = text.df

grade = idf.Grade.from_test_data()
grade.parse()
grade_df = grade.df

rank = idf.Rank.from_test_data()
rank.parse()
rank_df = rank.df

# custdf = pd.read_csv("data/customers-10000.csv")
# count = idf.Count(custdf['Index'])
count = idf.Count.from_test_data()
count.parse()
count_df = count.df

amount = idf.Amount.from_test_data()
amount.parse()
amount_df = amount.df

balance = idf.Balance.from_test_data()
balance.parse()
balance_df = balance.df