import pandas as pd

df: pd.DataFrame = pd.read_csv("...")
a: int = input()


df.index = a
print(df.index)
df.index = 1
df.head()
df.index = 1
df["A"] = 1

