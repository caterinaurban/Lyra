import pandas as pd

# STATE: df -> {_ -> W}
df: pd.DataFrame = pd.read_csv("...")

# STATE: df -> {Latitude -> U, Longitude -> U, rot_15_x -> W, rot_30_x -> W, rot_45_x -> W, _ -> U}
df['rot_15_x'] = 0.96 * df['Longitude'] + 0.25 * df['Latitude']

# STATE: df -> {Latitude -> U, Longitude -> U, rot_30_x -> W, rot_45_x -> W, _ -> U}
df['rot_30_x'] = 0.86 * df['Longitude'] + 0.49 * df['Latitude']

# STATE: df -> {Latitude -> U, Longitude -> U, rot_45_x -> W, _ -> U}
df['rot_45_x'] = 0.71 * df['Longitude'] + 0.71 * df['Latitude']

# STATE: df -> {_ -> U}
df.head()

# FINAL: df -> {_ -> N}
