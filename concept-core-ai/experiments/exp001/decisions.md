# DEC-NB-v3-01 — Bootstrap RNG API Convention

Status: APPROVED

Experiment 001のbootstrap resamplingについて、同一`analysis_seed`から同一index列を一意に生成するため、乱数生成APIを固定する。

---

## RNG implementation

Bootstrap用RNGは、Python環境におけるNumPyの以下の構成を正式baselineとする。

```text
bit_generator:
  numpy.random.PCG64

generator:
  numpy.random.Generator
```

初期化は概念的に以下と同一でなければならない。

```python
rng = numpy.random.Generator(
    numpy.random.PCG64(analysis_seed)
)
```

`analysis_seed` はDEC-NB01で定義された32-bit unsigned integerをそのまま `PCG64` constructorへ渡す。

独自のseed展開処理を追加してはならない。

---

## Bootstrap index generation

各bootstrap iterationについて、index列は概念的に以下と同一の方法で生成する。

```python
indices = rng.integers(
    low=0,
    high=900,
    size=900,
    endpoint=False,
    dtype=numpy.int64,
)
```

したがって生成される各indexは、

```text
0 <= index < 900
```

を満たす。

---

## RNG stream

`rng` は1000 bootstrap iterationの開始前に一度だけ生成する。

1000 iteration全体で同一Generator instanceを連続使用する。

iterationごとに、

- 再seed
- Generator再生成
- PCG64再生成

を行ってはならない。

---

## Sampling order

iteration 0から999まで順番に処理する。

各iterationで900 indexを一度だけ生成する。

概念的には、

```python
for iteration in range(1000):
    indices = rng.integers(
        low=0,
        high=900,
        size=900,
        endpoint=False,
        dtype=numpy.int64,
    )
```

と同一のindex列を生成すること。

---

## Test sample mapping

index `0...899` は、保存済みTest sampleの決定的順序へ対応する。

この順序はbootstrap開始前に固定し、iteration間で変更してはならない。

---

## Reproducibility

以下が同一である場合、

```text
NumPy version
analysis_seed
Test sample order
Test latent
metadata
Train standardization statistics
```

bootstrap index列および最終CIが同一であることを要求する。

実行時にはNumPy versionをrun metadataへ記録する。

正式baselineの5 runは同一NumPy versionを使用する。

---

## Constraints

- `numpy.random.default_rng()` の将来的なdefault変更へ依存しない。
- `RandomState` を使用しない。
- Python標準`random`を使用しない。
- `numpy.random.randint`等のlegacy global RNGを使用しない。
- 独自のPCG64出力→整数変換を実装しない。
- frameworkごとの別RNGへ置換しない。
