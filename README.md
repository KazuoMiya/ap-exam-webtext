# 応用情報技術者試験 Webテキスト

IPAの試験要綱 Ver.5.6 と応用情報技術者試験シラバス Ver.7.2 に沿って作成した、応用情報技術者試験（AP）の学習用Webテキストです。2026年度からのCBT方式（科目A・科目B）に対応しています。

公開URL： https://kazuomiya.github.io/ap-exam-webtext/

## 収録内容

- 全19章の解説と補講（テクノロジ系、マネジメント系、ストラテジ系）、図解
- 四肢択一の演習問題 802問（基本・標準・上級の3段階）
- 模擬科目A（80問・150分。本番の分野比率で毎回ランダムに出題。画面内のメモと電卓付き）
- 科目B 記述式演習 42題（全11分野。うち本番級の長文問題34題。解答例と採点のポイント付き）
- 学習の記録（ブラウザの localStorage に保存）

## 学習記録の考え方

- 正答率は「初めて解いたときの正答率」で数えます。解説を読んだ直後の解き直しでは上がりません。
- 「定着」は、直近の解答が正解で、かつ別々の2日以上で正解した問題です。
- 「要復習」は、一度でも間違えて、まだ定着していない問題です。
- 解き直すときは、選択肢の並びを入れ替えます（記号と選択肢の対応は変わりません）。

## 問題の品質の検証

GitHub Actions は、ビルドの前に次の検証を実行し、1件でも問題があれば公開を止めます。

```
python3 tools/validate.py      IDや選択肢の整合性、正解位置の分布、重複の疑い、科目Bの解答例の字数
python3 tools/tell.py          正解だけが目立って長い選択肢の検出（-v で該当の問題を表示）
python3 tools/verify_calc.py   計算、進数変換、SQL、トレースの187問を実際に計算して、正解と照合
python3 tools/verify_b.py      科目B 19題の数値、SQL、プログラムのトレースを計算して、解答と照合
```

手元での確認用のスクリプトです。

```
python3 tools/rebalance.py --write       正解の位置を均等にする
python3 tools/apply_choices.py 差分.txt   選択肢の差し替え（「ID|記号|新しい選択肢」の行）を適用する
python3 tools/functest.py                ブラウザでの動作テスト（Playwright と Chrome が必要）
```

verify_calc.py と verify_b.py が確かめるのは、計算で答えが決まる問題だけです。用語や法令の説明の正しさは、機械的には確かめていません。

問題はすべてオリジナルで、IPAの過去問題の転載ではありません。

## ディレクトリ構成

```
src/chapters/NN.md    章の本文（先頭にメタ情報、--- 以降がMarkdown）
src/chapters/NN-2.md  章の補講（本文の後ろに連結される）
src/questions/NN.txt  四肢択一問題（--- 区切り。NNb.txt は追加分）
src/kamokub/FF-N.md   科目B 記述式演習（FF は本番の問番号、N は連番）
src/pages/*.md        試験の概要などの固定ページ
template.html         画面とスクリプト（/*__DATA__*/ にデータを埋め込む）
build.py              ビルドスクリプト（dist/index.html を出力）
tools/rebalance.py    正解の選択肢の位置の偏りをならす補助スクリプト
```

## 問題の書き方

```
ID: 01-01
LV: 1
Q: 問題文（Markdown可、複数行可）
ア: 選択肢
イ: 選択肢
ウ: 選択肢
エ: 選択肢
正解: ウ
解説: 解説文（Markdown可）
---
```

LV は 1＝基本、2＝標準、3＝上級です。

## ローカルでのビルド

```
pip install -r requirements.txt
python build.py
```

`dist/index.html` をブラウザで開くと確認できます。

## 公開

`main` ブランチに push すると、GitHub Actions がビルドし、GitHub Pages に自動で公開します（`.github/workflows/pages.yml`）。

## 参考

- IPA 試験要綱・シラバス https://www.ipa.go.jp/shiken/syllabus/gaiyou.html
- IPA 過去問題 https://www.ipa.go.jp/shiken/mondai-kaiotu/index.html
