# Source: GUC Introduction to Computer Science
A = eval(input())
size = len(A)
check = "sorted"
i = 0
while i < size - 1 and check != "unsorted":
    # we can't handle this -> must be assumption on whole list
    if A[i] > A[i + 1]:
        check = "unsorted"
    i += 1
