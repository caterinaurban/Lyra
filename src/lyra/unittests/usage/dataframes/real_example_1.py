import pandas as pd

# STATE: orig -> {_ -> W}; train -> {_ -> W}
train: pd.DataFrame = pd.read_csv('train.csv')

# wrong STATE: orig -> {_ -> W}; train -> {gen -> W, id -> N, lat -> U, lon -> U, _ -> W}
# STATE: orig -> {_ -> W}; train -> {gen -> W, id -> N, _ -> U}
train.drop('id', axis=1, inplace=True)

# wrong STATE: orig -> {_ -> W}; train -> {gen -> W, lat -> U, lon -> U, _ -> W}
# STATE: orig -> {_ -> W}; train -> {gen -> W, _ -> U}
orig: pd.DataFrame = pd.read_csv("original.csv")

# wrong STATE: orig -> {gen -> W, _ -> N}; train -> {gen -> W, lat -> U, lon -> U, _ -> W}
# STATE: orig -> {gen -> W, _ -> U}; train -> {gen -> W, _ -> U}
train['gen'] = 1

# wront STATE: orig -> {gen -> W, _ -> N}; train -> {lat -> U, lon -> U, _ -> W}
# STATE: orig -> {gen -> W, _ -> U}; train -> {_ -> U}
orig['gen'] = 0

# wrong STATE: orig -> {_ -> N}; train -> {lat -> U, lon -> U, _ -> W}
# STATE: orig -> {_ -> U}; train -> {_ -> U}
train = pd.concat([train, orig])

# STATE: orig -> {_ -> N}; train -> {lat -> U, lon -> U, _ -> U}
train.head()

# STATE: orig -> {_ -> N}; train -> {lat -> U, lon -> U, r -> W, _ -> U}
train['r'] = train['lat'] + train['lon']

# STATE: orig -> {_ -> N}; train -> {_ -> U}
train.head()

# FINAL: orig -> {_ -> N}; train -> {_ -> N}
