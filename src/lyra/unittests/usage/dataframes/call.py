import pandas as pd

# INITIAL: a -> {_ -> W}; b -> {_ -> W}; x -> {_ -> W}; y -> {_ -> W}

x : pd.DataFrame = pd.read_csv("...")
y : pd.DataFrame = pd.read_csv("...")
a : pd.DataFrame = pd.read_csv("...")
b : pd.DataFrame = pd.read_csv("...")

def f(x: pd.DataFrame) -> pd.DataFrame:
    return x

# STATE: a -> {A -> U, B -> U, _ -> N}; b -> {_ -> W}; x -> {X -> U, Y -> U, _ -> N}; y -> {_ -> W}
# FIXME not the same behavior with debugger?
y = g(x[["X","Y"]])

# STATE: a -> {A -> U, B -> U, _ -> N}; b -> {_ -> W}; x -> {_ -> N}; y -> {_ -> U}
b = f(a[["A","B"]])

# STATE: a -> {_ -> N}; b -> {_ -> U}; x -> {_ -> N}; y -> {_ -> U}
y.head()
# STATE: a -> {_ -> N}; b -> {_ -> U}; x -> {_ -> N}; y -> {_ -> N}
b.head()

# FINAL: a -> {_ -> N}; b -> {_ -> N}; x -> {_ -> N}; y -> {_ -> N}

