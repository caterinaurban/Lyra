
# INITIAL:
x: float = float(input())
# STATE:
y: float = float(input())
# STATE:
if x < 1 or x > 3 or y < 0 or y > 2:
    raise ValueError
    # STATE: ⊥
while y <= 3:   # LOOP: -1·y + 4 >= 0 ∧ 1·y + 0 >= 0 ∧ 1·x - 1 >= 0 ∧ 2·x - 1·y + 0 >= 0 ∧ 4·x - 3·y + 3 >= 0
    # STATE: -1·y + 3 >= 0 ∧ 1·y + 0 >= 0 ∧ 1·x - 1 >= 0 ∧ 2·x - 1·y + 0 >= 0
    x = 1.5 * x
    # STATE: -1·y + 3 >= 0 ∧ 1·y + 0 >= 0 ∧ 2·x - 3 >= 0 ∧ 4·x - 3·y + 0 >= 0
    y = y + 1
    # STATE: -1·y + 4 >= 0 ∧ 1·y - 1 >= 0 ∧ 2·x - 3 >= 0 ∧ 4·x - 3·y + 3 >= 0
# FINAL: -1·y + 4 >= 0 ∧ 1·y - 3 > 0 ∧ 4·x - 3·y + 3 >= 0
