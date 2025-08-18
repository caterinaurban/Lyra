import pandas as pd

x: pd.DataFrame = pd.read_csv("data.csv")
y: pd.DataFrame = pd.read_csv("data.csv")

# STATE: x -> {A -> N, _ -> U}; y -> {B -> N, _ -> N}
x.drop(["A"])
# WARNING: Warning: column B of y dropped before use!
y.drop(["B"])

# STATE: x -> {_ -> U}; y -> {B -> U, _ -> N}
x.head()
y["B"].head()

# FINAL: x -> {_ -> N}; y -> {_ -> N}
