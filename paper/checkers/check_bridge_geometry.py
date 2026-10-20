# Publication relocation: only certificate/report paths and command text changed.
# Mathematical checking logic is unchanged from the accepted proof artifact.
"""Exact finite checks for the lead's 73-coordinate, 72-invocation bridge.

This checks the global geometry independently of the local scalar checker.
It does not execute Lean or assert Euler admission. The complex semantics
and the universal orthogonal-class argument are proved in the companion text.
"""

from collections import Counter, deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform


ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "code/c588at-provider.json"
CERT_HASH = "b52b8e31dd731c7bdc1fa3e556224ffa51c76dc66ca36849ecec8c85733f9624"
D = 73
H = set(range(9))
HP = H - {0}


def dot(x, y):
    return (x & y).bit_count() & 1


def image(columns, x):
    y = 0
    while x:
        bit = x & -x
        y ^= columns[bit.bit_length() - 1]
        x ^= bit
    return y


def transpose(columns):
    return [sum(((columns[j] >> i) & 1) << j for j in range(D))
            for i in range(D)]


def row(c):
    return set(range(9 + 8*c, 17 + 8*c))


def post(stage, side):
    s = H | set(range(9, 9 + 8*stage))
    return s if side == 0 else s - {0}


def check_classes(data):
    """Check all port-dependent right multipliers at the identity class.

    Left multiplication by arbitrary orthogonal g preserves these exact
    identities, as proved in the companion text; Q is never enumerated here.
    """
    checks = 0
    assert len(data["orthobases"]) == len(data["ports"]) == 112
    for port, base in zip(data["ports"], data["orthobases"]):
        assert len(base) == 9 and base[0] == port
        assert all(dot(x, y) == int(i == j)
                   for i, x in enumerate(base) for j, y in enumerate(base))
        b = base + [1 << j for j in range(9, D)]
        bt = transpose(b)
        assert all(image(bt, b[j]) == 1 << j for j in range(D))
        for stage in range(9):
            pi = list(range(D))
            if stage:
                c = stage - 1
                for j in range(1, 9):
                    z = 9 + 8*c + j - 1
                    pi[j], pi[z] = z, j
            permutation = [1 << j for j in pi]
            # R = B Pi B^T; class g is served by invocation d=g R.
            r = [image(b, image(permutation, bt[j])) for j in range(D)]
            assert all(image(r, r[j]) == 1 << j for j in range(D))
            assert all(dot(r[i], r[j]) == int(i == j)
                       for i in range(D) for j in range(D))
            # In the class basis, the invocation basis is B^T R.
            coord = lambda x: image(bt, image(r, x))
            background = set(range(9, 9 + 8*stage))
            a = {coord(1 << j) for j in background}
            x_in = a | {coord(port)}
            y_in = a
            x_out = a | {coord(u) for u in base}
            y_out = a | {coord(u) for u in base[1:]}
            before_x = {0} if stage == 0 else post(stage - 1, 0)
            before_y = set() if stage == 0 else post(stage - 1, 1)
            assert x_in == {1 << j for j in before_x}
            assert y_in == {1 << j for j in before_y}
            assert x_out == {1 << j for j in post(stage, 0)}
            assert y_out == {1 << j for j in post(stage, 1)}
            checks += 4
    return {"ports": 112, "stage_multipliers": 112*9,
            "exact_frame_set_equalities": checks}


def check_scalar_and_climbs():
    scalar = [[int(i == j) for j in range(8)] for i in range(8)]
    frames = [{0} if i % 2 == 0 else set() for i in range(8)]
    calls = []
    climbs = Counter()
    actions = []

    def add(target, source, coefficient):
        assert frames[target] == frames[source]
        scalar[target] = [x + coefficient*y
                          for x, y in zip(scalar[target], scalar[source])]
        actions.append(["add", target, source, coefficient])

    def climb(pair, stage):
        for side in (0, 1):
            r = 2*pair + side
            new = post(stage, side)
            assert frames[r] <= new
            size = len(new - frames[r])
            if size:
                climbs[size] += 1
                actions.append(["climb", r, size])
            frames[r] = new

    def invoke(stage, pair):
        x, y = 2*pair, 2*pair+1
        assert frames[x] == ({0} if stage == 0 else post(stage-1, 0))
        assert frames[y] == (set() if stage == 0 else post(stage-1, 1))
        if stage % 2 == 0:
            scalar[y] = [v+u for u, v in zip(scalar[x], scalar[y])]
            orientation = "forward"
        else:
            scalar[x] = [u-v for u, v in zip(scalar[x], scalar[y])]
            orientation = "inverse_transpose"
        frames[x], frames[y] = post(stage, 0), post(stage, 1)
        calls.append([stage, pair, orientation])
        actions.append(["invoke", stage, pair, orientation])

    invoke(0, 0)
    invoke(1, 0)
    for pair in range(1, 4):
        old = pair - 1
        climb(pair, 2*pair-1)
        add(2*old, 2*pair, 1)
        add(2*pair+1, 2*old+1, -1)
        invoke(2*pair, old)
        climb(pair, 2*pair)
        add(2*pair+1, 2*old+1, 1)
        add(2*old, 2*pair, -1)
        invoke(2*pair+1, pair)
    invoke(8, 3)
    for pair in range(4):
        climb(pair, 8)
    for pair in (3, 2, 1):
        add(2*(pair-1)+1, 2*pair+1, -1)
        add(2*pair, 2*(pair-1), 1)
    expected = [[0]*8 for _ in range(8)]
    for pair in range(4):
        expected[2*pair][2*pair+1] = -1
        expected[2*pair+1][2*pair] = 1
    assert scalar == expected
    assert [s for s, _, _ in calls] == list(range(9))
    assert climbs == Counter({8: 6, 16: 4, 32: 4, 48: 4})
    return {"scalar_matrix": scalar, "invocations": calls,
            "climbs_per_port_per_run": dict(sorted(climbs.items())),
            "actions": actions}, climbs


def check_banks(data):
    residuals = [9-len(data["frames"][f]) for f in data["start"][224:]]
    assert Counter(residuals) == Counter({9: 360, 8: 140, 7: 32, 5: 8, 4: 48})
    patterns = [(30, (6, 1, 1, 0, 1)), (18, (5, 3, 0, 0, 1)),
                (3, (7, 0, 0, 2, 0)), (1, (6, 0, 2, 1, 0)),
                (7, (1, 8, 0, 0, 0))]
    weights = (9, 8, 7, 5, 4)
    waiting = {r: deque(q for q, z in enumerate(residuals) if z == r)
               for r in weights}
    groups = []
    for mult, counts in patterns:
        for _ in range(mult):
            groups.append([waiting[r].popleft()
                           for r, n in zip(weights, counts) for _ in range(n)])
    assert len(groups) == 59
    q5 = waiting[5].popleft()
    q9s = list(waiting[9])
    assert len(q9s) == 56 and all(not v for r, v in waiting.items() if r != 9)
    rows = [[-1]*588 for _ in range(72)]
    for k in range(72):
        for g, group in enumerate(groups):
            for position, q in enumerate(group):
                rows[k][q] = 72*g + (k+position) % 72
    stage_q9_banks = [[] for _ in range(72)]
    for k in range(72):
        rows[k][q5] = 4248 + (k // 2)
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
    for k in range(72):
        need = 56 - len(stage_q9_banks[k])
        extra = pool_strided[idx:idx+need]
        idx += need
        for q, b in zip(q9s, stage_q9_banks[k] + extra):
            rows[k][q] = b
    loads = [0]*4757
    checked = 0
    for k in range(72):
        used = set()
        stage = k % 9
        for q, bank in enumerate(rows[k]):
            assert bank not in used and 0 <= bank < 4757
            used.add(bank)
            u = set(range(loads[bank]))
            t = set(range(loads[bank], loads[bank]+residuals[q]))
            assert u.isdisjoint(t) and max(t) < D
            label = data["frames"][data["start"][224+q]]
            pivots = {x.bit_length()-1 for x in label}
            r = {8*stage+j for j in range(9) if j not in pivots}
            assert len(t) == len(r) == residuals[q]
            # Explicit permutation sigma(T)=R, extended on complements.
            sigma = dict(zip(sorted(t), sorted(r)))
            sigma.update(zip(sorted(set(range(D))-t), sorted(set(range(D))-r)))
            assert len(set(sigma.values())) == D
            assert {sigma[j] for j in t} == r
            loads[bank] += residuals[q]
            checked += 1
        assert len(used) == 588
    pads = Counter(D-load for load in loads)
    assert pads == Counter({0: 4284, 1: 472, 37: 1})
    assert min(loads) > 0 and max(loads) == 73
    return {"bank_count": 4757, "uses_checked": checked,
            "padding_histogram": dict(sorted(pads.items())),
            "groups": groups}, pads


def main():
    (ROOT / ".build").mkdir(exist_ok=True)
    raw = CERT.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CERT_HASH
    data = json.loads(raw)
    assert (data["h"], data["v"], data["slots"]) == (9, 112, 588)
    classes = check_classes(data)
    scalar, climbs = check_scalar_and_climbs()
    banks, pads = check_banks(data)
    # Local invocation histogram is a separate proof premise, not reproved here.
    local = {1: 2568, 2: 492, 3: 280, 4: 232, 5: 56, 6: 56, 8: 92}
    total = Counter({r: 72*n for r, n in local.items()})
    total.update({r: 8*112*n for r, n in climbs.items()})
    total.update({r: n for r, n in pads.items() if r})
    expected = {1: 185368, 2: 35424, 3: 20160, 4: 16704, 5: 4032,
                6: 4032, 8: 12000, 16: 3584, 32: 3584, 37: 1, 48: 3584}
    assert total == Counter(expected)
    assert sum(r*n for r, n in total.items()) == 73*11925-2560
    report = {"status": "PASS: exact finite geometry checks, not Euler admission",
              "created_at": datetime.now(timezone.utc).isoformat(),
              "run_command": "python3 checkers/check_bridge_geometry.py",
              "python": platform.python_version(), "provider_sha256": CERT_HASH,
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "classes": classes, "scalar_and_climbs": scalar, "banks": banks,
              "profile_per_orthogonal_class": dict(sorted(total.items())),
              "live_roles_per_class": 11925, "central_copy_arrays_per_class": 8,
              "proof_boundary": ["local provider semantics is a separate premise",
                                 "all-class covariance and complex adapters require the ordinary proof",
                                 "no root DFT claim is certified by this finite run"]}
    out = ROOT / ".build/bridge-geometry-check.json"
    out.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("banks", "scalar_and_climbs")}, indent=2))


if __name__ == "__main__":
    main()
