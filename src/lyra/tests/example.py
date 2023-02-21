import pandas as pd

df: pd.DataFrame = pd.read_csv("data.csv")

sub: pd.DataFrame = df[["First", "Second"]]
sub.head()
df.head()