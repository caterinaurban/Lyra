class TestCase():

    def __init__(self: 'TestCase', Hd: int, Ad: int, Hk: int, Ak: int, B: int, D: int) -> None:
        self.Hd: int = Hd
        self.Ad: int = Ad
        self.Hk: int = Hk
        self.Ak: int = Ak
        self.B: int = B
        self.D: int = D
        self.buffRounds: int = 0
        self.debuffRounds: int = 0

    def computeOffRounds(self: 'TestCase') -> int:
        tmp: int = (self.Hk // (self.Ad + (self.buffRounds * self.B)))
        if ((self.Hk % (self.Ad + (self.buffRounds * self.B))) != 0):
            tmp += 1
        return (tmp + self.buffRounds)

    def computeOptBuffRounds(self: 'TestCase') -> None:
        if (self.B == 0):
            self.buffRounds: int = 0
        best: int = self.computeOffRounds()
        self.buffRounds += 1
        while (self.computeOffRounds() <= best):
            best: int = self.computeOffRounds()
            self.buffRounds += 1
        self.buffRounds -= 1

    def computeDefRounds(self: 'TestCase') -> int:
        tmp: int = 0
        rounds: int = (self.totalOffRounds - 1)
        i: int = 0
        life: int = self.Hd
        damage: int = self.Ak
        lastTimeHeal: bool = False
        while (rounds != 0):
            if (life <= damage):
                if ((life > (damage - self.D)) and (i < self.debuffRounds)):
                    lastTimeHeal: bool = False
                    i += 1
                    damage -= self.D
                    if (damage < 0):
                        damage: int = 0
                    tmp += 1
                else:
                    if lastTimeHeal:
                        return 10000
                    lastTimeHeal: bool = True
                    tmp += 1
                    life: int = self.Hd
            else:
                lastTimeHeal: bool = False
                if (i < self.debuffRounds):
                    i += 1
                    damage -= self.D
                    if (damage < 0):
                        damage: int = 0
                    tmp += 1
                else:
                    rounds -= 1
            life -= damage
        return tmp

    def computeOptDebuffRounds(self: 'TestCase') -> None:
        best: int = self.computeDefRounds()
        bestrounds: int = 0
        if ((self.D == 0) or (self.Ak == 0)):
            self.debuffRounds: int = 0
            return
        self.debuffRounds: int = 0
        for i in range((((self.Ak // self.D) + 2) + 1)):
            if (self.computeDefRounds() < best):
                best: int = self.computeDefRounds()
                bestrounds: int = self.debuffRounds
            self.debuffRounds += 1
        self.debuffRounds: int = bestrounds

    def solve(self: 'TestCase') -> str:
        print('Start solving...')
        self.computeOptBuffRounds()
        self.totalOffRounds: int = self.computeOffRounds()
        print(('Off solved: ' + str(self.totalOffRounds)))
        self.computeOptDebuffRounds()
        self.totalDefRounds: int = self.computeDefRounds()
        print(('Def solved: ' + str(self.totalDefRounds)))
        print(self.debuffRounds)
        if (self.totalDefRounds >= 10000):
            return 'IMPOSSIBLE'
        return str((self.totalOffRounds + self.totalDefRounds))

def loadTestCases(path: str) -> List[TestCase]:
    out: List[TestCase] = []
    input_file: IO = open(path)
    for i in range(int(input_file.readline())):
        line: List[str] = input_file.readline().split()
        Hd: int = int(line[0])
        Ad: int = int(line[1])
        Hk: int = int(line[2])
        Ak: int = int(line[3])
        B: int = int(line[4])
        D: int = int(line[5])
        print((Hd, Ad, Hk, Ak, B, D))
        out.append(TestCase(Hd, Ad, Hk, Ak, B, D))
    input_file.close()
    return out

def solve(path: str) -> None:
    tcs: List[TestCase] = loadTestCases(path)
    output_file: IO = open((path[:(- 3)] + '.out'), 'w')
    count: int = 1
    for t in tcs:
        output_file.write((((('Case #' + str(count)) + ': ') + str(t.solve())) + '\n'))
        count += 1
    output_file.close()
solve('C-large.in')
