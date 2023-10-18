import pandas as pd

# INITIAL: df -> {_: W}
df: pd.DataFrame = pd.read_csv("train.csv")

# STATE: df -> {"f": U, "id": U, _: U}
df.head()

# STATE: df -> {"f": U, "id": N, "norm_f": W, _: N}
df.drop(['id'], axis=1, inplace=True)

# STATE: df -> {"f": U, "norm_f": W, _: N}
df["norm_f"] = (df["f"] - df["f"].min()) / (df["f"].min() - df["f"].max())

# STATE: df -> {"norm_f": U, _: N}
df["norm_f"].head()

# FINAL: df -> {_: N}
