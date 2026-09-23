# RESOLVED_BLOCKERS

| 項目 | 判定 | 理由 |
| --- | --- | --- |
| NB-01 | RESOLVED | 正式master seedは1001〜1005。SHA-256からgeneration/split/model/loader/probe/analysisを導出し、同一commitの5 runをmanifestで固定する。run-levelとExperiment-levelの成果物・判定も分離されている。 |
| NB-v2-01 | RESOLVED | `VALID`/`INVALID`/`EXPERIMENTAL_FAILURE`と評価flagが分離され、§19の優先順が`NOT_EVALUATED`、主要指標欠損の`INCONCLUSIVE`、通常の三値判定を一意に定める。CI/controlだけの失敗は三値判定を止めない。 |
| NB-v2-02 | RESOLVED | sample単位・instance単位のpair処理、連続RNG stream、1000反復、有効反復950件、`h=(n-1)q`による線形補間が確定した。 |
| NB-v3-01 | RESOLVED | `Generator(PCG64(analysis_seed))`と`rng.integers(low=0, high=900, size=900, endpoint=False, dtype=numpy.int64)`が明示され、各反復で同じGeneratorを継続使用する。Test順序を保存し、正式5 runのNumPy版を揃えて記録する。独自seed展開や整数写像は禁じられている。 |
| B-01 | RESOLVED | color/shape別のprobe delta、distance contrast/delta、4/5条件、中央値閾値、positive trend、主要指標欠損時の優先判定が機械的に定義されている。 |
| B-02 | RESOLVED | 基準RGB、channel変動、位置・外接円半径・角度、図形幾何、pixel/subpixel座標、境界、16点平均、非clipping、追加量子化禁止が維持されている。 |
| B-03 | RESOLVED | 9組み合わせ各1000、組み合わせ別800/100/100、独立したsplit seed、排他・網羅、全splitの9組み合わせ、Train/Validation/Test用途が維持されている。 |
| B-04 | RESOLVED | Encoder/Decoder層、bias=true、latent_dim=32、Kaiming/Xavierの対象、bias=0、model seed、FP32およびAMP/FP16/BF16/TF32無効、BatchNorm/Dropoutなしが維持されている。 |
| B-05 | RESOLVED | 再構成のみ、MSE mean、Adamの全指定値、50 epoch、batch 128、loader seed、無効な機構、update前initialと50 epoch後final、Validationの監視用途が維持されている。 |
| B-06 | RESOLVED | 凍結initial/final Encoder、Train-onlyの別scaler、ddof=0、near-zero除外、指定logistic regression/C grid/solver、Validation選択、Test最終評価、非収束時flagが維持されている。 |
| B-07 | RESOLVED | Test全404,550 unique pair、4カテゴリ、Train統計でのstandardized Euclidean主解析、raw補助解析、aggregate再計算、sample単位bootstrap、固定NumPy APIとCI規約が維持されている。 |
| B-08 | RESOLVED | 7画像統計特徴と12288 raw pixel特徴、ddof=0、foreground定義、Train標準化、probeと同じclassifier・C選択・Test用途、control失敗flagが維持されている。 |

v3 reviewの古い指摘は監査履歴であり、現行の正規仕様を上書きしない。
