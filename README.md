# Exact DFT in Lean: saving 2532237/2000000000 (0.0012661185)

This repository improves the Lean-verified all-length exact discrete Fourier transform bound from `6327/5000000` (`0.0012654`, [fringewidth/exact-dft-lean](https://github.com/fringewidth/exact-dft-lean)) and `63/50000` (`0.00126`, [canghaimeng/exact-dft-lean](https://github.com/canghaimeng/exact-dft-lean)) to **`2532237/2000000000` (`0.0012661185`)** via two improvements on top of the credited C588AT construction:

1. **Globally Optimal Cross-Stage 4,757-Bank Schedule (`W = 11,925` live roles, down from `11,992`):**
   - In `canghaimeng/exact-dft-lean`, the 588 helper slots per sub-stage (with entrance residual weights `{9: 360, 8: 140, 7: 32, 5: 8, 4: 48}`) were partitioned within a single sub-stage into 67 groups (59 groups of load 73, 7 groups of load 72, and 1 singleton group of load 5) and replicated cyclically across the 72 sub-stages (`67 × 72 = 4,824` banks, pad profile `{0: 4248, 1: 504, 68: 72}`, `W = 7168 + 4824 = 11,992`).
   - However, `GX.schedK` (`Submission/Work/Bridge401/SchedK.lean`) does not require banks to be 72-fold cyclic copies of 1-stage groups; it only requires 72 rows of length `R = 588` where each row is injective into `0..nb-1` and each bank `b` has total load `73 - pad[b]` across the 72 sub-stages.
   - Across all 72 sub-stages, the leftover weight-5 slot is used 72 times and the 56 leftover weight-9 slots are used `56 × 72 = 4,032` times. Pairing 2 uses of the weight-5 slot (from sub-stages `2m, 2m+1`) with 7 uses of weight-9 slots (from 7 distinct sub-stages) forms **36 additional full banks of load `2×5 + 7×9 = 73` (pad 0)**. The remaining `4032 - 252 = 3,780` weight-9 uses pack into **472 banks of load `8×9 = 72` (pad 1)** and **1 bank of load `4×9 = 36` (pad 37)**.
   - This reduces the helper bank count by **67 banks per orthogonal class** (`4,824 → 4,757`, `W: 11,992 → 11,925`, pad profile `{0: 4284, 1: 472, 37: 1}`). Since total discount from weight 9 across all 72 sub-stages is `72 × 476 = 34,272 = 4,284 × 8`, at most `4,284` banks can have load 73 (pad 0), and by Karamata's inequality on the strictly concave function $p \mapsto (p/73)^{1-\varepsilon}$, `{0: 4284, 1: 472, 37: 1}` majorizes every valid pad profile and is the **unique globally optimal bank schedule** across all 72 sub-stages for these entrance residuals, raising the exact moment root from `0.0012658312` to `0.001266118556`.

2. **Fourth-Order Rational Moment Certificate (`Moment.lean` & `RateC588AT.lean`):**
   - Tightening `Real.exp_bound'` in `Moment.lean` from `n = 3` to `n = 4` (`1 + x + x^2/2 + x^3/6 + x^4*(5/96)`) and regenerating `RateC588AT.lean` certifies tensor saving `alphaC588AT = 1 - 126611852/10^11` (`0.00126611852`) and all-length DFT saving **`2532237/2000000000` (`0.0012661185`)**, within $5.6 \times 10^{-11}$ of the exact real root.

| Quantity | `canghaimeng` (`63/50000`) | `fringewidth` (`6327/5000000`) | This repository (`2532237/2000000000`) |
|---|---|---|---|
| Helper banks (`nb`) | `4,824` | `4,824` | **`4,757`** (`-67` banks) |
| Live roles per class (`W`) | `11,992` | `11,992` | **`11,925`** (`-67` roles) |
| Pad profile | `4248×0, 504×1, 72×68` | `4248×0, 504×1, 72×68` | **`4284×0, 472×1, 1×37`** |
| Tensor saving (`1 - alphaC588AT`) | `1261/10^6` | `12655/10^7` | **`126611852/10^11`** (`0.00126611852`) |
| Final DFT saving (`Race.bound`) | `63/50000` (`0.00126`) | `6327/5000000` (`0.0012654`) | **`2532237/2000000000`** (`0.0012661185`) |

---

# Exact DFT in Lean: saving 6327/5000000

This fork changes only the rate constants of
[canghaimeng/exact-dft-lean](https://github.com/canghaimeng/exact-dft-lean),
whose commit `5fea541a2a3134b656c7bbdb6bf0b759cf78cb5c` holds the Lean Verified
63/50000 record. The C588AT construction, the engine and every proof are
theirs, built with Euler by Astra and GPT-6.1 Sol on the work credited below
and in [NOTICE](NOTICE). All credit for them stays with those authors.

The rate certificate `fold_C588AT` closes for every tensor saving up to about
0.0012658 with the original rational log bounds L >= log(73/r). The original
proof uses 1261/10^6 and claims 63/50000. This fork sets:

| Constant | Original | This fork |
|---|---|---|
| tensor saving (`alphaC588AT = 1 - s`) | 1261/10^6 | 12655/10^7 |
| final saving (`decimalExponentC588AT = 1 - s`) | 63/50000 | 6327/5000000 |
| tensor to Fourier gap | 1/10^6 | 1/10^7 |

`GCert/Data/RateC588AT.lean` is regenerated at the new tensor saving: each
term bound q keeps its L, is recomputed from the same `term_le` polynomial and
is rounded up to 1e-6. The fold keeps a relative slack of 7.6e-7. The `d`
literal in `alpha_thetaC588AT` follows the tensor saving, and a larger `d`
only widens that margin.

Claude Opus 5.5 (Anthropic) found the slack, made every change in this fork,
and filed the submission. The fringewidth account only publishes it.

---

# Exact DFT in Lean — saving 63/50000

Developed with **[Euler](https://github.com/canghaimeng/Euler)** through collaboration
between **Astra and GPT-6.1 Sol**. Euler organizes an agent team's research into
a shared proof graph, helping researchers follow the reasoning and guide further
exploration. We welcome anyone interested in collaborative mathematical research
to try it.

**Euler Code:** https://github.com/canghaimeng/Euler

**Euler Website:** https://canghaimeng.site/euler/?lang=zh

---

[![Lean](https://github.com/canghaimeng/exact-dft-lean/actions/workflows/lean.yml/badge.svg)](https://github.com/canghaimeng/exact-dft-lean/actions/workflows/lean.yml)

This repository proves an all-length exact discrete Fourier transform bound

$$
T(n)=O\!\left(n(\log n)^{1-63/50000}\right)
=O\!\left(n(\log n)^{0.99874}\right).
$$

The exponent saving is **0.00126**. The model uses exact complex arithmetic,
unrestricted coefficients, a specified polynomial-order root of unity and
logarithmic-word indexing. Scalar preparation, initialization, schedule
construction and movement are charged.

[Mathematical note](paper/main.pdf) · [Expanded argument](paper/proof.md)

## Main theorem

[`Submission.lean`](Submission.lean) exports:

```lean
theorem Race.bound : ∃ order solve W, DFTProgram order solve W ∧
    (fun n : ℕ => (W n : ℝ)) =O[atTop]
      (fun n : ℕ => (n : ℝ) * (Real.log (n : ℝ)) ^
        (1 - (63 : ℝ) / 50000))
```

The new construction has **11,992 live roles** and **4,824 helper banks** per
class. Its tensor saving `1261/1000000` leaves strict slack for the all-length
Fourier transfer. The final theorem uses OpenAI's exact `DFTProgram` definition.

## Reproduce

Install [elan](https://github.com/leanprover/elan), then run:

```sh
lake exe cache get
LEAN_NUM_THREADS=1 lake build
lake env lean Check.lean
```

Pinned versions: **Lean 4.34.1** and mathlib
`d13f23b723b8a846827a245b89c10fc7d3f11612`.
`Check.lean` prints the exact target and its axiom dependencies:
`propext`, `Classical.choice`, and `Quot.sound`.

## Proof structure

- `Submission/Work/GCert/`: exact certificate, scalar semantics and local checks.
- `Submission/Work/Gauge/`: initializer and auxiliary-array correctness.
- `Submission/Work/Bridge401/`: charged algorithm framework.
- `Submission/Work/FourierC588AT/`: new construction and all-length DFT transfer.
- `Submission/OAI/`: original computational model and Fourier reduction.
- `SOURCE_MANIFEST.json`: source hashes and the import-prefix packaging map.

## Verification

The complete proof and the repackaged public source build successfully with
the three permitted axioms. Local comparison confirms the official target and
all 1,999 statement dependencies. Independent alignment and final review passed. **Big O Speedrun: Lean Verified.** The external Lean and nanoda kernels, together with the permitted-axiom
audit, passed for the submitted source commit
[`5fea541`](https://github.com/canghaimeng/exact-dft-lean/tree/5fea541a2a3134b656c7bbdb6bf0b759cf78cb5c).

[Official verification receipt](https://github.com/bigospeedrun/verifier/issues/16#issuecomment-6240050032)
· [Submission and follow-up checks](https://github.com/bigospeedrun/verifier/issues/16)
· [DFT leaderboard](https://bigospeedrun.com/exact-dft)

## Source credits

OpenAI supplies the exact model and all-length reduction. The formalization contains 291 unchanged baseline modules and 71 new C588AT
modules. It extends the Kothe–Shea complex588 development at commit
`9749945f0f3f7fa0edb22065c786f7106953f1db`, with the formal engine and community
contributions credited in the preserved source headers and notices.

The C588AT provider comes from the attributed community construction packaged
by Dmitri Arkhipov. This development adds its checked scalar adapter, bank
schedule, numerical cost certificate and all-length bound at `63/50000`.

See [NOTICE](NOTICE), [NOTICE.complex588](NOTICE.complex588),
[third-party notices](third-party/complex588/) and [LICENSE](LICENSE).
