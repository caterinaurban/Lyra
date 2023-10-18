import pandas as pd

# INITIAL: df -> {_: W}; norm_df -> {_: W}
df: pd.DataFrame = pd.read_csv("...")

# STATE: df -> {"norm_x1": W, "norm_x2": W, "x1": U, "x2": U, _: N}; norm_df -> {_: W}
df["norm_x1"] = (df["x1"] - df["x1"].min()) / (df["x1"].max() - df["x1"].min())

# STATE: df -> {"norm_x1": U, "norm_x2": W, "x2": U, _: N}; norm_df -> {_: W}
df["norm_x2"] = (df["x2"] - df["x2"].min()) / (df["x2"].max() - df["x2"].min())

# STATE: df -> {"norm_x1": U, "norm_x2": U, _: N}; norm_df -> {_: W}
norm_df: pd.DataFrame = df[["norm_x1", "norm_x2"]]

# STATE: df -> {_: N}; norm_df -> {_: U}
norm_df.head()

# FINAL: df -> {_: N}; norm_df -> {_: N}
