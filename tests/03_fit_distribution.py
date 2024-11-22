import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import plotnine as pn

import idataframe as idf

def fit(series, *args, **kwargs):
    balance = idf.Balance(series)  #  make all series of type Balance
    distribution = balance.fitDistribution()
    return distribution

# sastdes_df = pd.read_csv("data/sastdes.csv")
# distr = fit(sastdes_df['CO2_int_(ton/capita 2018)'])
# distr = fit(sastdes_df['G14Lb_size_terrestial_km2'])  # log
# distr = fit(sastdes_df['UID.latitude'])
# distr = fit(sastdes_df['Shape_Length_UID'])           # log
# distr = fit(sastdes_df['N26_perc_forest_2000'])
# distr = fit(sastdes_df['UID_2020_Population'])


# titanic_df = pd.read_csv("data/titanic.csv").drop(columns=['PassengerId'])
# distr = fit(titanic_df['Fare'])
# distr = fit(titanic_df['Age'], interval=1.0, distributions='ALL')
# distr = fit(titanic_df['Pclass'])     # 1, 2 or 3  -> use idf.analyse_data_nominal_ordinal


# flights_df = pd.read_csv("data/flights.csv").drop(columns=[])
# distr = fit(flights_df['passengers'])                 # cube


# diamonds_df = pd.read_csv("data/diamonds.csv").drop(columns=[])
# distr = fit(diamonds_df['depth'])                     # normal
# distr = fit(diamonds_df['table'], interval=1.0)       # log
# distr = fit(diamonds_df['price'])

planets_df = pd.read_csv("data/planets.csv").drop(columns=[])
# distr = fit(planets_df['orbital_period'])             # log
# distr = fit(planets_df['mass'])                       # cube
# distr = fit(planets_df['distance'])                   # log
distr = fit(planets_df['year'], interval=1.0)         # normal

# distr = fit(pd.Series(np.random.normal(loc=30.0, scale=10.0, size=1000)))


print("\n",

    distr.type,
    distr.cdf(60) - distr.cdf(20),
    distr.cdf_inv(0.50),
    distr.median,
    distr.random(100),
    distr.data,
    distr.data[distr.is_dirty],

sep="\n\n"+80*"="+"\n\n")
