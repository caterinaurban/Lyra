for x in range(10):
    if x > 7:
        x += 2
    else:
        x = x + 1
        print("Still in the loop.")
        if x == 8:
            break
print ("Outside of the loop.")

x = 3
while x < 10:
    if x > 7:
        x += 2
    else:
        x = x + 1
        print("Still in the loop.")
        if x == 8:
            break
print ("Outside of the loop.")