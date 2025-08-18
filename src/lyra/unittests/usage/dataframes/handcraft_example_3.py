import pandas as pd

# INITIAL: df -> {_ -> W}
df: pd.DataFrame = pd.read_csv("data.csv")

# STATE: df -> {Column -> N, First -> U, Second -> U, Some -> N, Third -> U, _ -> N}
df[["Second", "Third"]].info()

# STATE: df -> {Column -> N, First -> U, Some -> N, _ -> N}
df["First"].info()

# STATE: df -> {Column -> N, First -> N, Some -> N, _ -> N}
df.drop("First", axis=1)

# STATE: df -> {Column -> N, Some -> N, _ -> N}
df.drop(["Some", "Column"], axis=1)

# FINAL: df -> {_ -> N}
