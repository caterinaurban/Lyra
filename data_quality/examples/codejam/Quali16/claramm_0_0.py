# code jam

# MAD: input has to exist as integer
n = int(input())

# MAD: no output if n <= 0
for i in range(n):
    new = 0
    nums = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 0: 0}
    num = input()
    num2 = str(num)
    t = 1

    if num == '0':
        print("Case #%d: INSOMNIA" % (i + 1))

    else:
        while new < 10:
            for k in num2:
                # MAD: k is elements of [str(int(num)*t)] and num = input()
                # MAD: k has to be in dictionary (need information if dictionary or array)
                # MAD: k has to be a integer
                if nums[int(k)] == 0:
                    new += 1
                    nums[int(k)] += 1

                # MAD: no output if new += 1 (above) not reached 10 times
                # MAD: not reached if num2 never containes all of the 10 elements in dictionary at some point
                # MAD: => input cannot be '000' for example
                if new == 10:
                    print("Case #%d: %s" % (i + 1, num2))
                    break

                else:
                    nums[int(k)] += 1
            t += 1
            # MAD: num has to exist as integer (num = input())
            num2 = str(int(num) * t)
