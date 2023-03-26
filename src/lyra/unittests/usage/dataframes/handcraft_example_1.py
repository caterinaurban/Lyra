import pandas as pd

# INITIAL: df -> {_: W}
df: pd.DataFrame = pd.read_csv("...")

# STATE: df -> {"id": N, "t": U, _: N}
df.drop(['id'], axis=1, inplace=True)

# STATE: df -> {"t": U, _: N}
df["t"].head()

# FINAL: df -> {_: N}
