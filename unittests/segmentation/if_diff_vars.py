x = int(input())
y = int(input())
z = int(input())

a = 1
b = int(input())

list1 = [x, y, z]

r = 0

# RESULT: a→⚫, b→⫱, q→⫱, r→⫱, x→⚫, y→⟂, z→⟂, list1→[{【[0,0]】} ⫰ ?{【+a】} ⚫ {【+a + [1,1]】,【[2,2]】} ⚫ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
b = a + 1 # via the substitution, bounds get equal and have to be merged!
if x > 0:
    # RESULT: ... | a→⚫, b→⟂, q→⫱, r→⟂, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【+a】} ⚫ {【+a + [1,1]】,【[2,2]】} ⫱ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
    q = list1[a]
    list1[2] = 3
else:
    q = list1[b]

r = list1[2]
print(r + q)
