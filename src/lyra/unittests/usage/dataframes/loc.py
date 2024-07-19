import pandas as pd

df : pd.DataFrame = pd.read_csv("...")
x : pd.DataFrame = pd.read_csv("...")
# l : List[int] = []

# x: List[int] = l[1]
# y: List[int] = l[1:4]

# df2 : pd.DataFrame = df.loc[df["a"] > 2, "A"]
# df2 : pd.DataFrame = df.loc[1, "A":"F"] # TODO slices

# STATE: df -> {A -> U, B -> U, _ -> N}; df2 -> {_ -> W}; x -> {A -> U, B -> U, _ -> N}; x2 -> {_ -> W}
df2 : pd.DataFrame = df.loc[1, ["A", "B"]]
x2 : pd.DataFrame = x[["A", "B"]]

# STATE: df -> {_ -> N}; df2 -> {B -> U, C -> W, Y -> W, Z -> U, _ -> U}; x -> {_ -> N}; x2 -> {B -> U, C -> W, _ -> U}
df2.loc[3, "B"].head()
x2["B"].head()

# df3 = df2.loc[df2["Z"] > 4, "C"]
# df3 = df2["Z"] + df2["C"]

# STATE: df -> {_ -> N}; df2 -> {C -> W, Y -> W, Z -> U, _ -> U}; x -> {_ -> N}; x2 -> {C -> W, _ -> U}
df2.loc[df2["Z"] > 4, "Y"] = 1
# equivalent?

# STATE: df -> {_ -> N}; df2 -> {C -> W, _ -> U}; x -> {_ -> N}; x2 -> {C -> W, _ -> U}
df2.loc[3, "C"] = 1
x2["C"] = 1

# STATE: df -> {_ -> N}; df2 -> {_ -> U}; x -> {_ -> N}; x2 -> {_ -> U}
df2.loc[3].head()
x2.head()

# FINAL: df -> {_ -> N}; df2 -> {_ -> N}; x -> {_ -> N}; x2 -> {_ -> N}
