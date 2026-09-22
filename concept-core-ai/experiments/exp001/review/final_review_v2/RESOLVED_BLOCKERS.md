# RESOLVED_BLOCKERS

| 旧項目 | 判定 | 理由 |
| --- | --- | --- |
| NB-01 | NOT_RESOLVED | 5個のmaster seed、用途別導出、同一commit、runとaggregateの分離は定義された。しかし`EXPERIMENTAL_FAILURE`を含む5 runについて、`INCONCLUSIVE`と「有効runが5件未満なら`NOT_EVALUATED`」が競合する。probe全候補非収束やbootstrap失敗時のrun statusも未定。 |
| B-01 | NOT_RESOLVED | `probe_delta_A`、`distance_contrast_A`、`distance_delta_A`と数値閾値は機械判定できる。通常完了した5 runでは三値分類も一意。一方、評価不能なrunを含む場合は`INCONCLUSIVE`と`NOT_EVALUATED`の適用境界が一意でない。 |
| B-02 | RESOLVED | 色と幾何、座標、16 subpixelのinside判定と算術平均まで確定した。平均結果が小数でも「最終pixel RGBは算術平均」という正規条件が優先するため、整数への追加丸めは許されない。保存形式はこの値を保持できるものを実装側で選べる。 |
| B-03 | RESOLVED | 9組み合わせ×1,000、組み合わせ別800/100/100、`split_seed`、排他性、全件網羅、split用途が定義された。 |
| B-04 | RESOLVED | 層、bias、latent、Kaiming/Xavierの対象と設定、bias初期値、`model_seed`、FP32、AMP/FP16/BF16/TF32無効が確定した。 |
| B-05 | RESOLVED | 再構成のみ、MSE mean、Adam、50 epoch、batch 128、shuffle、無効化する機構、update前initialと50 epoch後final、Validationの限定用途が確定した。 |
| B-06 | NOT_RESOLVED | 前処理・分類器・C選択・Test隔離は確定した。全C非収束時はprobeがFAILEDになるが、runの`INVALID`/`EXPERIMENTAL_FAILURE`/その他の扱いとaggregate判定への影響が未定である。 |
| B-07 | NOT_RESOLVED | 全pair、4カテゴリ、Train統計、ddof=0、aggregate再計算、sample単位bootstrapのinstance規則は確定した。なお1000回復元抽出の乱数生成規約と2.5/97.5百分位の算出規約がなく、同じ入力・`analysis_seed`から複数の妥当な95% CIが得られる。`bootstrap_status: FAILED`のrun判定への作用も未定。 |
| B-08 | RESOLVED | 2種類のPixel特徴、foreground、ddof=0、Train標準化、classifier、C grid、収束処理、split用途、指標がlatent probeと整合する。Pixel baselineは成功条件に使われない。 |

旧レビュー内の古い記述は監査履歴として扱い、この判定の根拠にはしない。
