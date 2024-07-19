import pandas as pd

df: pd.DataFrame = pd.read_csv("...")

b: bool = input()
# STATE: b -> U; df -> {x -> W, y -> U, _ -> N}; df2 -> {_ -> N}

if b:
    df["x"] = 1
else:
    df2 : pd.DataFrame = df.drop("y")

# STATE: b -> N; df -> {x -> U, y -> U, _ -> N}; df2 -> {_ -> N}
df["y"].head()
df["x"].head()
# df.head()

# FINAL: b -> N; df -> {_ -> N}; df2 -> {_ -> N}
