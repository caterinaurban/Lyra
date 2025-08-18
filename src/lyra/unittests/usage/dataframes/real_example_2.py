import pandas as pd

# INITIAL: df -> {_ -> W}
df: pd.DataFrame = pd.read_csv('train.csv')

# STATE: df -> {Age -> U, FoodCourt -> U, Name -> U, PassengerId -> U, ShoppingMall -> U, Spa -> U, Transported -> U, VRDeck -> U, _ -> U}
df.head()

# STATE: df -> {Age -> U, FoodCourt -> U, Name -> U, PassengerId -> U, ShoppingMall -> U, Spa -> U, Transported -> U, VRDeck -> U, _ -> U}
df.describe()

# STATE: df -> {Age -> U, FoodCourt -> U, Name -> U, PassengerId -> U, ShoppingMall -> U, Spa -> U, Transported -> U, VRDeck -> U, _ -> U}
df.info()

# STATE: df -> {Age -> U, FoodCourt -> U, Name -> N, PassengerId -> N, ShoppingMall -> U, Spa -> U, Transported -> U, VRDeck -> U, _ -> U}
df["Transported"].hist()

# STATE: df -> {Age -> U, FoodCourt -> U, Name -> N, PassengerId -> N, ShoppingMall -> U, Spa -> U, VRDeck -> U, _ -> U}
df['Age'].hist(bins=50)

# STATE: df -> {FoodCourt -> U, Name -> N, PassengerId -> N, ShoppingMall -> U, Spa -> U, VRDeck -> U, _ -> U}
df['FoodCourt'].hist(bins=50)

# STATE: df -> {Name -> N, PassengerId -> N, ShoppingMall -> U, Spa -> U, VRDeck -> U, _ -> U}
df['ShoppingMall'].hist(bins=50)

# STATE: df -> {Name -> N, PassengerId -> N, Spa -> U, VRDeck -> U, _ -> U}
df['Spa'].hist(bins=50)

# STATE: df -> {Name -> N, PassengerId -> N, VRDeck -> U, _ -> U}
df['VRDeck'].hist(bins=50)

# STATE: df -> {Name -> N, PassengerId -> N, _ -> U}
df.drop(['PassengerId', 'Name'], axis=1, inplace=True)

# STATE: df -> {_ -> U}
df.head()

# FINAL: df -> {_ -> N}
