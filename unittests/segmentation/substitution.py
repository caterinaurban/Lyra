x = int(input())
y = int(input())
z = int(input())
list1 = [x, y, z]
q = 2
# RESULT: q→⚫, r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[1,1]】} ⚫ {【+q】,【[2,2]】} ⚫ {【+q + [1,1]】} ⟂ ?{【+list1__len】}], list1__len→⟂
r = list1[1] + list1[q]

print(r)
