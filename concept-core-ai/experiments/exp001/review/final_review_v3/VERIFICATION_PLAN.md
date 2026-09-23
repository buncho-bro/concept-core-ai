# VERIFICATION_PLAN

IMPLEMENT後、以下を自動検証する。NB-v3-01の決定後にbootstrapのgolden index列を固定する。

1. **正式seedと履歴**: `1001`〜`1005`のみを同一git commitで束ね、SHA-256からgeneration/split/model/loader/probe/analysisを処理順序に依存せず導出する。run単位で三値科学判定しない。
2. **失敗状態の境界**: 5 VALID＋完全指標は通常三値判定、4 VALID＋1 INVALIDは`NOT_EVALUATED`、4 VALID＋1 EXPERIMENTAL_FAILUREは`INCONCLUSIVE`、1 PROBE_FAILEDおよび1 DISTANCE_FAILEDは`INCONCLUSIVE`。BOOTSTRAP_CI_FAILEDのみなら`DISTANCE_CI_INCOMPLETE`を、PIXEL_BASELINE_FAILEDのみなら`CONTROL_INCOMPLETE`を報告して三値判定を継続する。複数flagと欠損優先順位も検証する。
3. **bootstrap抽出**: 承認後のPCG64初期化・整数化のgolden index列、1本の連続stream、iterationごとの再seed禁止、900回×1000反復、保存したTest順を検証する。同一original sample_id間pair除外、他sample間multiplicity、unordered instance pair、pair直接bootstrap禁止を確認する。
4. **bootstrap数値**: fixed Test latentとTrain scaler、iterationごとの再fitなし、有効反復の昇順、`h=(n-1)q`による線形補間、`Q(0.025)`/`Q(0.975)`、950/949反復境界、同一入力・seedでCI一致を確認する。
5. **datasetとsplit**: 色、変動、位置、外接円半径、角度端点、頂点、16 subpixel平均、境界と非clippingをfixtureで確認する。9組み合わせ各1000、各split 800/100/100、排他・全件網羅・全組み合わせを検証する。
6. **モデルと学習**: 層・bias・初期化対象・biasゼロ・FP32/AMP等無効、MSE mean・Adam・50 epoch、update前initialと50 epoch後final、Validation/Test更新禁止を確認する。評価ラベルとmetadataがAutoencoder入力・損失・更新に入らない。
7. **probe**: initial/final×Train/Validation/Testのlatent完全性、状態別Train scaler、ddof=0、near-zero除外、同一classifier条件、C候補の収束扱い、Validation最大・同率最小C、Test隔離、Encoderへの勾配禁止、class順・必須指標を検証する。
8. **距離とcontrol**: Testのunique unordered pair 404,550、4カテゴリ44,550/90,000/90,000/180,000、集合結合後のaggregate、状態別Train標準化とraw補助距離を確認する。2種のPixel baselineはTrain標準化、同じclassifier/C規則、Test最終評価のみとしAutoencoder学習へ影響させない。
9. **成功判定と成果物**: `probe_delta_A`、`distance_contrast_A`、`distance_delta_A`、4/5、中央値の等号境界、color/shape OR、指標欠損の判定順序をtable-driven testで確認する。run-levelとaggregate-levelの保存情報から結果を再計算し、INVALID・EXPERIMENTAL_FAILUREを削除・上書きしない。
