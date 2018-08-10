# INITIAL: a -> ⊤, b -> ⊤, c -> ⊤, x -> ⊤
a: int = -2
# STATE: a -> <0, b -> ⊤, c -> ⊤, x -> ⊤
b: int = 0
# STATE: a -> <0, b -> =0, c -> ⊤, x -> ⊤
c: int = 2
# STATE: a -> <0, b -> =0, c -> >0, x -> ⊤
x: int = a + b
# STATE: a -> <0, b -> =0, c -> >0, x -> <0
x = 2 * c + 1
# FINAL: a -> <0, b -> =0, c -> >0, x -> >0
