from IPython.display import display, HTML

import numpy as np
import pandas as pd
import plotnine as pn
import idataframe as idf

custdf = pd.read_csv("test-data/customers-10000.csv").drop(columns=['Index'])
# display(custdf)

sastdf = pd.read_csv("test-data/sastdes.csv")
# display(' / '.join(('{}: {}'.format(k,v) for k, v in sastdf.iloc[0].to_dict().items())))
# display((pn.ggplot(sastdf.iloc[1000:9000], pn.aes(x="UID.longitude", y="UID.latitude")) + pn.geom_point(alpha=0.1)))
# display(sastdf)

salesmanhdf = pd.read_csv("test-data/rollingsales-manhattan.csv")
# display(salesmanhdf)

titanic_df = pd.read_csv("test-data/titanic.csv").drop(columns=['PassengerId'])
# display(titanic_df)

planets_df = pd.read_csv("test-data/planets.csv").drop(columns=[])
# display(planets_df)

diamonds_df = pd.read_csv("test-data/diamonds.csv").drop(columns=[])
# display(diamonds_df)

iris_df = pd.read_csv("test-data/iris.csv").drop(columns=[])
# display(iris_df)

car_crashes_df = pd.read_csv("test-data/car_crashes.csv").drop(columns=[])
# display(car_crashes_df)

flights_df = pd.read_csv("test-data/flights.csv").drop(columns=[])
# display(flights_df)

healthexp_df = pd.read_csv("test-data/healthexp.csv").drop(columns=[])
# display(healthexp_df)