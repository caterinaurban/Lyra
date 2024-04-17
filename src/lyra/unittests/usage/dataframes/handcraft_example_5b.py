import pandas as pd

# INITIAL: df -> {_: W}; sub -> {_: W}
df: pd.DataFrame = pd.read_csv("...")

# STATE: df -> {"A": U, "B": N, "X": U, "Y": U _: N}; sub -> {_: W}
sub: pd.DataFrame = df[["A", "B", "Y"]]

# STATE: df -> {"X": U, "Y": U, _: N}; sub -> {"B": W, _: U}
sub["B"] = df["X"] + df["Y"]

# STATE: df -> {_: N}; sub -> {_: U}
sub.head()

# FINAL: df -> {_: N}; sub -> {_: N}
