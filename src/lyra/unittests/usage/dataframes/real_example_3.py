import pandas as pd

# STATE: df -> {_: W}
df: pd.DataFrame = pd.read_csv('train.csv')

# STATE: df -> {"Age": U, "Cabin": U, "Embarked": U, "Fare": U, "Name": U, "Parch": U, "PassengerId": U, "SibSp": U, "Ticket": U, "Title": U, _: U}
df.info()

# STATE: df -> {"Age": U, "Cabin": N, "Embarked": U, "Fare": U, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Age'] = df['Age'].fillna(df['Age'].median())

# STATE: df -> {"Cabin": N, "Embarked": U, "Fare": U, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])

# STATE: df -> {"Cabin": N, "Fare": U, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Fare'] = df['Fare'].fillna(df['Fare'].median())

# STATE: df -> {"Cabin": N, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Title'] = df['Title'].replace(['Lady', 'Countess','Capt', 'Col','Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')

# STATE: df -> {"Cabin": N, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Title'] = df['Title'].replace('Mlle', 'Miss')

# STATE: df -> {"Cabin": N, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Title'] = df['Title'].replace('Ms', 'Miss')

# STATE: df -> {"Cabin": N, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, "Title": U, _: U}
df['Title'] = df['Title'].replace('Mme', 'Mrs')

# STATE: df -> {"Cabin": N, "Name": N, "Parch": U, "PassengerId": N, "PassengersInGroup": W, "SibSp": U, "Ticket": N, _: U}
df['PassengersInGroup'] = df['SibSp'] + df['Parch'] + 1

# STATE: df -> {"Cabin": N, "Name": N, "Parch": N, "PassengerId": N, "SibSp": N, "Ticket": N, _: U}
df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin', 'SibSp', 'Parch'], axis=1, inplace=True)

# STATE: df -> {_: U}
df.head()

# FINAL: df -> {_: N}

