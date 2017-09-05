x = int(input())
y = int(input())
z = int(input())
list1 = [x, y, z]
# RESULT: r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[1,1]】} ⚫ {【[2,2]】} ⚫ {【[3,3]】} ⟂ ?{【+list2__len】}], list2→[{【[0,0]】} ⟂ ?{【[1,1]】} ⫱ {【[2,2]】} ⫱ {【[3,3]】} ⟂ ?{【+list2__len】}], list1__len→⟂, list2__len→⟂
list2 = list1
r = list2[1] + list2[2]

print(r)
