
# INITIAL: N -> Any, .IN -> Float
if True:
    # STATE: N -> Any, .IN -> Int
    N:int = input()
else:
    # STATE: N -> Any, .IN -> Float
    N:float = input()
# STATE: N -> Float, .IN -> Any
N: float = N + 1
# FINAL: N -> Any, .IN -> ⊥
