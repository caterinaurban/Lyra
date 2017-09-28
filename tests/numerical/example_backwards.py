
# mode 1,2: open file
#f = open('example_backwards_input.csv')

# mode 1: direct input reading
#a,b = [int(v) for v in f.readline().split(',')]

# mode 2: expanded input reading
#columns = f.readline().split(',')
#columns = [int(v) for v in columns]
#a = columns[0]
#b = columns[1]

# mode 1,2: close file
#f.close()
# mode 3: analysis input reading
#a = int(input())
#b = int(input())

# program
#a = a + 2
#b = b + 1
#b = 1 / (a + 1)
#assert a <= 0
#assert b > 0




a = input()
# RESULT: a -> [6,inf], b -> [-inf,inf], c -> [-inf,inf]
b = 60 - 20 + (100 / a) + 10
assert b > 0

