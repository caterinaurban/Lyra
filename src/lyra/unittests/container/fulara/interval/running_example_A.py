# INITIAL: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [-inf, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}
scores: Dict[int, int] = input()     #dictinput()   # id -> score
# STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [-inf, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}

score_occurrences: Dict[int, int] = {}        # defaultdict(int)    # initialized to 0
# STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}
for a, b in scores.items():
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    a = a
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    if a < 100:     # 'early adopter'
        # STATE: a -> [-inf, 99], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
        weight: int = 3
        # STATE: a -> [-inf, 99], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [3, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    else:
        # STATE: a -> [100, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
        weight: int = 1
        # STATE: a -> [100, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 1], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    a = a
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    if a not in score_occurrences.keys():        # fix for defaultdict
        # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
        score_occurrences[a] = 0
        # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
    score_occurrences[a] += weight   # BUG A: should be indexed by b
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [1, 3], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(scores, a, b)}
# STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [-inf, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}
scores_gt_10: int = 0
# STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, 0], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}
for k in score_occurrences.keys():
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(score_occurrences, k, None)}
    a = a
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(score_occurrences, k, None)}
    if k > 10:
        # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [11, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(score_occurrences, k, None)}
        scores_gt_10 += score_occurrences[k]
        # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [11, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(score_occurrences, k, None)}
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(score_occurrences, k, None)}
    a = a
    # STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {(score_occurrences, k, None)}
# STATE: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}
print(scores_gt_10)
# FINAL: a -> [-inf, inf], b -> [-inf, inf], k -> [-inf, inf], scores_gt_10 -> [0, inf], weight -> [-inf, inf], score_occurrences -> {([-inf, inf], [0, inf])}, scores -> {([-inf, inf], [-inf, inf])}, score_occurrences -> {([-inf, inf], True)}, scores -> {([-inf, inf], True)}, {}