n = int(input())
x = int(input())
i = 0
# RESULT: i→⟂, n→⟂, x→⫱
while i < n:
    x = i / 2  # BUG: should be x = x / 2
    i = i + 1
else:
    x = -1
print(x)
