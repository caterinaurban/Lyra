T: int = int(input())
for i in range(T):
    x: int = int(input())
    y: str = input()
    z: float = float(input())
    if x <= 10 and not y.isalpha():
        pass
    else:
        raise ValueError
    if x > z:
        pass
    else:
        raise ValueError

# 1:(Integer, ⊤, ⊤, (∅, Σ)), 1.1 * [3:(Integer, ⊤, OCT(10.0 >= 3.1), (∅, Σ)), 4:(String, ⊤, OCT(10.0 >= 3.1), (∅, {'	', '
# ', '', '', '
# ', ' ', '!', '"', '#', '$', '%', '&', ''', '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\', ']', '^', '_', '`', '{', '|', '}', '~'})), 5:(Float, ⊤, OCT(9.0 >= 5.1,3.1 - 1.0 >= 5.1,19.0 >= 5.1 + 3.1,10.0 >= 3.1), (∅, Σ))]