# デバッグ用: 数式レンダリング切り分け

例8の式が崩れる原因を特定するための一時ファイルです。原因が分かり次第削除します。
それぞれの番号ごとに、GitHub上で正しく数式として表示されているか(❌ならエラー文かソースがそのまま
テキスト表示されている)を教えてください。

## 1. フルバージョン(現状壊れているもの)

$$
\min \quad -\sum_i r_i x_i + \lambda \left( \sum_i \sigma_{ii} x_i + 2\sum_{i<j} \sigma_{ij} x_i x_j \right) + P \left( \sum_i x_i - k \right)^2
$$

## 2. i<j の部分だけ

$$
\sum_{i<j} \sigma_{ij}
$$

## 3. 添字が2文字のsigma単体

$$
\sigma_{ii} x_i
$$

## 4. 数字直後にsum(スペースなし)

$$
2\sum_{i<j} \sigma_{ij} x_i x_j
$$

## 5. \left( \right) が2組ある単純な式

$$
\lambda \left( a + b \right) + P \left( c - k \right)^2
$$

## 6. \left( \right) の中にsum_iとsigma_{ii}

$$
\left( \sum_i \sigma_{ii} x_i \right)
$$

## 7. 全体から i<j だけを X に置き換えたもの

$$
\min \quad -\sum_i r_i x_i + \lambda \left( \sum_i \sigma_{ii} x_i + 2\sum_{X} \sigma_{ij} x_i x_j \right) + P \left( \sum_i x_i - k \right)^2
$$

## 8. ラムダの直後

$$
\lambda \left( \sum_i \sigma_{ii} x_i \right)
$$
