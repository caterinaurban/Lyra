x = int(input())
y = int(input())
z = int(input())
list1 = [x, y, z]

q = 2  # q get used later indirectly via list1
# RESULT: q→⚫, r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[1,1]】} ⚫ {【[2,2]】} ⫱ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
list1[1] = list1[1] + 3  # this is not an overwrite
print(list1[1])  # now list1[1] is also used
# RESULT: q→⚫, r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[2,2]】} ⫱ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
list1[1] = list1[1] + list1[2]  # should not change anything to used since list1[1] and list1[2] currently unused
# RESULT: q→⚫, r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[2,2]】} ⫱ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
list1[q] = q  # this is an overwrite in list1 at index 2
# RESULT: q→⟂, r→⫱, x→⟂, y→⟂, z→⟂, list1→[{【[0,0]】} ⟂ ?{【[2,2]】} ⚫ {【[3,3]】} ⟂ ?{【+list1__len】}], list1__len→⟂
r = list1[2] + list1[2]

print(r)
