import pandas as pd

# INITIAL: df -> {_: W}; sub -> {_: W}
df: pd.DataFrame = pd.read_csv("...")

# STATE: df -> {"A": U, "B": U, "C": U, _: N}; sub -> {_: W}
sub: pd.DataFrame = df[["A", "B", "C"]]

# STATE: df -> {_: N}; sub -> {_: U}
sub.head()

# FINAL: df -> {_: N}; sub -> {_: N}
