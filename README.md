# 応用情報技術者試験 Webテキスト

IPAの試験要綱 Ver.5.6 と応用情報技術者試験シラバス Ver.7.2 に沿って作成した、応用情報技術者試験（AP）の学習用Webテキストです。2026年度からのCBT方式（科目A・科目B）に対応しています。

公開URL： https://kazuomiya.github.io/ap-exam-webtext/

## 収録内容

- 全19章の解説と補講（テクノロジ系、マネジメント系、ストラテジ系）、図解
- 四肢択一の演習問題 587問（基本・標準・上級の3段階）
- 模擬科目A（80問・150分。本番の分野比率で毎回ランダムに出題。画面内のメモと電卓付き）
- 科目B 記述式演習 22題（全11分野。うち本番級の長文問題14題。解答例と採点のポイント付き）
- 学習の記録（ブラウザの localStorage に保存）

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
