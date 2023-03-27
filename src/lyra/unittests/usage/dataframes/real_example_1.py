import pandas as pd

# STATE: orig -> {_: W}; train -> {_: W}
train: pd.DataFrame = pd.read_csv('train.csv')

# STATE: orig -> {_: W}; train -> {"gen": W, "id": N, "lat": U, "lon": U, _: W}
train.drop('id', axis=1, inplace=True)

# STATE: orig -> {_: W}; train -> {"gen": W, "lat": U, "lon": U, _: W}
orig: pd.DataFrame = pd.read_csv("original.csv")

# STATE: orig -> {"gen": W, _: N}; train -> {"gen": W, "lat": U, "lon": U, _: W}
train['gen'] = 1

# STATE: orig -> {"gen": W, _: N}; train -> {"lat": U, "lon": U, _: W}
orig['gen'] = 0

# STATE: orig -> {_: N}; train -> {"lat": U, "lon": U, _: W}
train = pd.concat([train, orig])

# STATE: orig -> {_: N}; train -> {"lat": U, "lon": U, _: U}
train.head()

# STATE: orig -> {_: N}; train -> {"lat": U, "lon": U, "r": W, _: U}
train['r'] = train['lat'] + train['lon']

# STATE: orig -> {_: N}; train -> {_: U}
train.head()

# FINAL: orig -> {_: N}; train -> {_: N}
