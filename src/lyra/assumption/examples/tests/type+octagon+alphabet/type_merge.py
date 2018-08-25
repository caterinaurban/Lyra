# 2:(Integer, ⊤, T, (∅, Σ)), 4:(String, ⊤, T, (∅, Σ))
y: int = int(input())
if y > 0:
    a: str = input()
    if a == 'abc':
        pass
    else:
        raise ValueError
else:
    x: int = int(input())
    if x > 10:
        pass
    else:
        raise ValueError

# TOTAL ASSUMPTIONS:
# SOUND ASSUMPTIONS:
# IMPRECISIONS:
# LINE        DOMAIN      COMMENT