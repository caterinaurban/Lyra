x = int(input())
y = int(input())
z = int(input())

a = int(input())
b = int(input())

list1 = [x, y, z]


# interesting switch: do we know relation of a and b or not?
b = a + 1
# RESULT: a→⚫, b→⚫, q→⫱, x→⚫, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【+a】} ⚫ {【+a + [1,1]】,【+b】} ⚫ {【+b + [1,1]】} ⟂ ?{【+list1__len】}], list1__len→⟂
if x > 0:
    q = list1[a]
else:
    q = list1[b]

print(q)
