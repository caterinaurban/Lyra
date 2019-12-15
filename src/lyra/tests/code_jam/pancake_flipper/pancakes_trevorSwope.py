def flips(sequence: str, k: int) -> int:
    count: int = 0
    reached: Set[str] = set()
    if done(sequence):
        return 0
    else:
        count: int = (count + 1)
        iterations: Set[str] = generate_flips(sequence, k, reached)
        while (len(iterations) > 0):
            new_iterations: Set[str] = set()
            for item in iterations:
                if done(item):
                    return count
                else:
                    reached.add(item)
                    new_iterations.update(generate_flips(item, k, reached))
            iterations: Set[str] = new_iterations
            count: int = (count + 1)
        return (- 1)

def done(sequence: str) -> bool:
    for ele in sequence:
        if (ele == '-'):
            return False
    return True

def generate_flips(sequence: str, k: int, reached: Set[str]) -> Set[str]:
    new_iterations: Set[str] = set()
    for i in range(0, ((len(sequence) + 1) - k)):
        new_string: str = ((sequence[:i] + flip(sequence[i:(i + k)])) + sequence[(i + k):])
        if (new_string not in reached):
            new_iterations.add(new_string)
            reached.add(new_string)
    return new_iterations

def flip(string: str) -> str:
    new_string: str = ''
    for i in string:
        if (i == '+'):
            new_string: str = (new_string + '-')
        else:
            new_string: str = (new_string + '+')
    return new_string

def run() -> None:
    f: IO = open('A-small-attempt1.in', 'r')
    data: str = f.read()
    f.close()
    inputs: List[str] = data.splitlines()[1:]
    answer: str = ''
    count: int = 1
    for line in inputs:
        sequence: str = line.split(' ')[0]
        k: str = line.split(' ')[1]
        line_answer: int = flips(sequence, int(k))
        if (line_answer == (- 1)):
            answer: str = (((answer + 'Case #') + str(count)) + ': IMPOSSIBLE\n')
        else:
            answer: str = (((((answer + 'Case #') + str(count)) + ': ') + str(line_answer)) + '\n')
        count: int = (count + 1)
    f: IO = open('Output', 'w')
    f.write(answer)
    f.close()
