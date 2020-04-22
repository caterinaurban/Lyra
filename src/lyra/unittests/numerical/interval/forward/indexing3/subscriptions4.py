
done: List[bool] = [False, False, False]
x: int = 3 if done[0] else -3
# FINAL: done -> 0@[0, 0], 1@[0, 0], 2@[0, 0], _@⊥; len(done) -> [3, 3]; x -> [-3, -3]
