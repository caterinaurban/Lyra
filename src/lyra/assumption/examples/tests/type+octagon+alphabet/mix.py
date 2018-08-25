
# 3:(Integer, ⊤, T, (∅, Σ)), 3.1 * [6:(Float, >0, OCT(6.1 - 11.0 >= 0), (∅, Σ)), 7:(String, ⊤, T, (∅, {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}))]
T:int = int(input())
# STATE:  T * [6:(Float, [11, inf], (∅, Σ)), 7:(String, [-inf, inf], ({'a', 'b', 'd'}, {'a', 'b', 'd'}))]
for i in range(T):
    x: float = float(input())
    y: str = input()
    if x > 10 and y.isalpha():
        pass
    else:
        raise ValueError
# FINAL: ε

# TOTAL ASSUMPTIONS:
# SOUND ASSUMPTIONS:
# IMPRECISIONS:
# LINE        DOMAIN      COMMENT