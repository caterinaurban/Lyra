x: str = input()
y: str = input()

if not x.islower():
    pass
else:
    raise ValueError

if not x.isalpha() or not y.isalnum():
    raise ValueError

# 1:(String, ⊤, ⊤, (∅, {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
# 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'})), 2:(String, ⊤, ⊤, (∅, {'0', '1',
#  '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
# 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c',
#  'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
# 'v', 'w', 'x', 'y', 'z'}))
