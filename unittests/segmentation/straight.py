x = int(input())
y = int(input())
z = int(input())
# RESULT: r→⫱, x→⟂, y→⚫, z→⚫, list1→[{【[0,0]】} ⟂ ?{【[1,1]】} ⫱ {【[2,2]】} ⫱ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
list1 = [x, y, z]
r = list1[1] + list1[2]

print(r)
