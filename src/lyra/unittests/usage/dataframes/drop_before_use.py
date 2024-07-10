import pandas as pd

x: pd.DataFrame = pd.read_csv("data.csv")
y: pd.DataFrame = pd.read_csv("data.csv")

x.drop(["A"])
y.drop(["B"])

x.head()
y["B"].head()

