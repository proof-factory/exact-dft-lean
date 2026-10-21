# Publication relocation: only certificate/report paths and command text changed.
# Mathematical checking logic is unchanged from the accepted proof artifact.
"""Standalone exact checker for the finite packing and moment lemma.

No imported source code, third-party package, floating point, or network.
This checks no complex circuit or infinite DFT theorem.
"""

from collections import Counter, deque
from fractions import Fraction as Q


WEIGHTS = (9, 8, 7, 5, 4)
COUNTS = (360, 140, 32, 8, 48)
PATTERNS = (
    (30, (6, 1, 1, 0, 1)),
    (18, (5, 3, 0, 0, 1)),
    (3, (7, 0, 0, 2, 0)),
    (1, (6, 0, 2, 1, 0)),
    (7, (1, 8, 0, 0, 0)),
)
# rank, number of calls, rational upper log numerator (denominator 5*10^11).
RATE = (
    (1, 185368, 2145229720575), (2, 35424, 1798656130295),
    (3, 20160, 1595923576241), (4, 16704, 1452082540015),
    (5, 4032, 1340510764358), (6, 4032, 1249349985961),
    (8, 12000, 1105508949735), (16, 3584, 758935359455),
    (32, 3584, 412361769175), (37, 1, 339770764255),
    (48, 3584, 209629215121),
)


def log2_interval(t):
    """Atanh-series enclosure for log(t), 1 <= t <= 2."""
    assert 1 <= t <= 2
    z = (t-1)/(t+1)
    lower = 2 * sum((z**(2*j+1)/Q(2*j+1) for j in range(40)), Q(0))
    upper = lower + 2*z**81/(Q(81)*(1-z*z))
    return lower, upper


def main():
    residuals = [w for w, count in zip(WEIGHTS, COUNTS) for _ in range(count)]
    assert len(residuals) == 588 and sum(residuals) == 4816
    available = {w: deque(i for i, r in enumerate(residuals) if r == w) for w in WEIGHTS}
    groups = []
    for mult, pattern in PATTERNS:
        for _ in range(mult):
            group = []
            for w, count in zip(WEIGHTS, pattern):
                group.extend(available[w].popleft() for _ in range(count))
            groups.append(group)
    assert len(groups) == 59
    q5 = available[5].popleft()
    q9s = list(available[9])
    assert len(q9s) == 56 and all(not v for w, v in available.items() if w != 9)
    assert all(1 <= len(g) <= 9 for g in groups)
    group_loads = [sum(residuals[q] for q in g) for g in groups]
    assert Counter(group_loads) == {73: 59}
    pads = [0]*4284 + [1]*472 + [37]
    assert len(pads) == 4757 and Counter(pads) == {0: 4284, 1: 472, 37: 1}
    rows = [[-1]*588 for _ in range(72)]
    for stage in range(72):
        for g, slots in enumerate(groups):
            for j, q in enumerate(slots):
                rows[stage][q] = 72*g + (stage+j) % 72
        rows[stage][q5] = 4248 + (stage // 2)
    stage_q9_banks = [[] for _ in range(72)]
    for m in range(36):
        b = 4248 + m
        for j in range(7):
            stage_q9_banks[(2*m + 2 + j) % 72].append(b)
    pool_strided = []
    for pass_idx in range(8):
        pool_strided.extend(range(4284, 4756))
        if pass_idx < 4:
            pool_strided.append(4756)
    idx = 0
    for stage in range(72):
        need = 56 - len(stage_q9_banks[stage])
        extra = pool_strided[idx:idx+need]
        idx += need
        for q, b in zip(q9s, stage_q9_banks[stage] + extra):
            rows[stage][q] = b
    loads = [0]*4757
    for stage in range(72):
        row = rows[stage]
        assert len(set(row)) == 588 and min(row) >= 0 and max(row) < 4757
        for q, bank in enumerate(row):
            loads[bank] += residuals[q]
    assert all(load+pad == 73 and 0 <= pad < 73 for load, pad in zip(loads, pads))

    _, log_two_upper = log2_interval(Q(2))
    a, total = Q(12661185597, 10**13), Q(0)
    for r, n, u in RATE:
        t, exponent = Q(73, r), 0
        while t >= 2:
            t /= 2
            exponent += 1
        _, upper = log2_interval(t)
        assert exponent*log_two_upper+upper <= Q(u, 5 * 10**11)
        x = a*Q(u, 5 * 10**11)
        assert 0 <= x <= 1
        exp_upper = 1+x+x**2/2+x**3/6+x**4*Q(5, 96)
        total += Q(r*n, 73*11925)*exp_upper
    assert sum(r*n for r, n, _ in RATE) == 73*11925-2560
    assert total < 1
    assert Q(2532237, 2000000000) < Q(3165296399, 2500000000000) < a
    print("PASS: 72 injective stages, 4757 bank loads, rational log/exp bounds and strict comparisons")
    print("Exact rational upper bound:", float(total))


if __name__ == "__main__":
    main()
