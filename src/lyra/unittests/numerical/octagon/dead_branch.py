x = int(input())
a = 0

a = a - 1

if a > 0:
    a = x
    # STATE: ⊥
else:
    x = a

a = 2

print(a - x)
