def f1(x):
    return x


def f2(x, y):
    return x + y


def f3(x, y):
    return x * y


def f4(x, y):
    return x * y + 3


def f5(x, y):
    a = x["string"] + y
    b = y + 3
    return a | b


def f6(a, b, i):
    x = a * 3
    y = b["string"]
    z = a[i]
    return (x[0] + z) * (y + 3)


def f7(x):
    return x["string"]


a = f1(2.0)
b = f2(1, 3)
c = f2("st1", "st2")
d = f3(3, [1, 2, 3])
e = f3(2.0, 7)
f = f3("st", 3)
g = f4(2, 3)
h = f5({"st": 2}, 3)
i = f6([[3]], {"string": 1}, 2)
j = f7({"string": 1})
