# INITIAL: a -> ⊤, b -> ⊤, c -> ⊤
a: bool = True
# STATE: a -> >0, b -> ⊤, c -> ⊤
b: bool = False
# STATE: a -> >0, b -> =0, c -> ⊤
c: bool = a and b
# STATE: a -> >0, b -> =0, c -> =0
c: bool = a or b
# STATE: a -> >0, b -> =0, c -> >0
if a:
    # STATE: a -> >0, b -> =0, c -> >0
    c: bool = False
    # STATE: a -> >0, b -> =0, c -> =0
# STATE: a -> >0, b -> =0, c -> =0
if not a:
    # STATE: a -> ⊥, b -> =0, c -> =0
    c: bool = True
    # STATE: a -> ⊥, b -> =0, c -> >0
# FINAL: a -> >0, b -> =0, c -> =0
