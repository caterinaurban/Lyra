math = int(input())
physics = int(input())
history = int(input())

count = 0

if math >= 4:
    math += 1  # Bug A: should be 'count += 1'
if physics >= 4:
    count += 1
if physics >= 4:  # Bug B: should be 'history >= 4'
    count += 1

print(count)
