x = int(input())
y = int(input())
z = int(input())
list1 = [x, y, z]

r = 0
# RESULT: r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[2,2]】} ⚫ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
if list1[1] > 0:  # list1[1] is not used since if body has no effect on output
    z = 4

r = list1[2]
print(r)
