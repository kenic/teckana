> 公開版の補足：この文書は人手レビュー前のPoCを説明します。最新の採用129件とライセンスはルートのREADMEを参照してください。生候補の証拠ファイルと実行済みバイナリは同梱していません。

# DADS → 日本語入力辞書 PoC

NIST DADSの現行索引1,306行を全件確認し、参照URL別1,123項目に対訳案または原語維持の判断を付け、読みを推定・点検してMecabraを実測した。略称の独立入力と別読みも含めて1,191行。結果はREPORT.md、取得範囲・権利はSOURCE_POLICY.md。

**完成したのは全件を扱う対訳案・評価データであり、1,306語すべての定訳と読みを検証済みの辞書ではない。** 不確かな訳・読みは保留し、確認済み10組とAI点検までの追加168組を分けている。日本語入力のユーザー辞書には登録していない。

## 成果物

- `outputs/index_master.csv`：元の1,306見出しを欠落させず保持。別名から参照先への対応、日本語訳・読み、出典URL・取得日時・ハッシュ。
- `outputs/master.csv`：日本語表記、略称・英字出力、別読みを含む1,191評価行。読みの初期推定と補正後、対訳・読みの確認状況、保留理由、Mecabra順位。
- `outputs/mecabra_evaluation.csv`：全評価行の生候補上限1,000件での結果。API設定・OS・CLIハッシュ・測定日時・証拠ファイルを保存。
- `outputs/candidate_audit.csv`：未出現候補を上限10,000件で再測定した採否。中黒・全半角・大小文字等の表記差と、同じ表記が別読みでは出る場合を記録。
- `outputs/missing_candidates.csv`：確認済み10組＋AI点検168組。すべてを確定語とは扱わない。
- `outputs/held_candidates.csv`：訳・読み保留、未測定、記号別枠。未測定は未出現として数えない。
- `outputs/orthography_only.csv`：中黒などの差を除けば候補がある24行。綴りを整える登録には価値があり得るが、用語自体が出ないケースと区別。
- `outputs/low_rank.csv`：16位以下に出る9行。
- `outputs/latin_and_abbreviations.csv`：英字表記・略称の測定一覧。英字であることを理由に除外しない。
- `outputs/reading_corrections.csv`：初回から表記または読みを変更した127行と結果の変化。
- `outputs/macos_user_dictionary_verified.csv` / `.plist`：対訳・読みの外部根拠がある未出現10組。
- `outputs/macos_user_dictionary_review.csv` / `.plist`：上の10組とAI点検168組を合わせた178組。登録前のレビュー用。
- `outputs/summary.json` / `audit_summary.json`：機械集計・採否後の集計。件数は原則「読みと出力表記」の組数。
- `data/translations.tsv`, `data/reviews.csv`：編集可能な対訳・読み・採否の台帳。人名や専門語の表記が不確かな場合は原語を保持。
- `data/external_checks.json`：個別の外部確認の出典。`evidence/pre-review/`は補正前の記録。

## 再実行

Python 3.9以上。依存パッケージは仮想環境内だけに導入。MecabraはmacOSの非公開APIを使い、別OSでは利用できない。

```sh
cd dads-poc
python3 -m venv .venv
.venv/bin/pip install --no-cache-dir -r requirements.txt
sh src/build.sh
.venv/bin/python src/pipeline.py
.venv/bin/python src/audit.py
.venv/bin/python -m unittest discover -s src -p 'test_*.py'
```

保存済みのindex.json/concepts.jsonと対訳を使う解析にはネットワーク不要。同じOS・バイナリ・読み・上限・実行条件では生候補を再利用し、元の測定日時を保持する。測り直す場合はevidence/mecabraを別名保存してから実行する。

通常のCLIは子プロセス内でネットワーク・書込みを制限する。このCodex環境では二重制限の適用に失敗するため、既存のホスト制限下でのみ `MECABRA_ALREADY_SANDBOXED=1` を付けてpipeline.pyとaudit.pyを実行した。この変数自体は保護機能を持たない。通常のターミナルでは設定しない。

Mecabraが使えない環境での抽出・未測定出力:

```sh
.venv/bin/python src/pipeline.py --no-mecabra --output outputs-unmeasured
.venv/bin/python src/audit.py --no-mecabra --output outputs-unmeasured
```

この場合は確認済み・レビュー用plistとも空になる。CLIの不在・失敗、読み未確定もnot_measuredとして残す。

元索引の再取得は、利用条件を再確認したうえで `src/collect.py --fetch`。既存キャッシュがあればそれを使用する。配布ZIPはサイトHTMLを含まないため、索引の再抽出には取得が必要。新しい索引に更新すると参照順が変わる可能性があるため、入力ハッシュが変わればpipelineは停止する。対訳と項目IDを再照合してからtranslation_provenance.jsonを更新する。確認なしにハッシュだけ書き換えない。

## 読み・対訳・測定の意味

1. 英語見出しをAIが日本語訳。説明的な直訳、定訳不明、人名不確実は注記して保留。英語別名183行は参照先の訳に正規化する。
2. fugashi + UniDic-liteのkanaから読みを推定し、Sudachiとも照合。両辞書には共通由来の項目があり、一致だけで正解としない。木、二分、彩色、根、双対、束などの専門的な読みをAIで再点検した。
3. 一文字ずつ読む略称は推定方法を明記。FIFO/LIFO/ANSI/NIST等は慣用的な読みも別評価。英字と漢字の混在も許可する。全ての発音・表記揺れを網羅したわけではない。
4. `source_verified`はAIが個別外部資料の表記・読みを照合した意味。専門家による校閲ではない。`assistant_reviewed`はAI点検のみ。
5. Mecabraはanalysis_readingとdictionary_readingの両方が入力全体と一致する候補を採用。NFC表記一致、重複を除くAPI列挙順の上位15件を評価する。GUIの順位ではない。
6. 未出現候補は上限10,000件で再測定。列挙終了と上限打切りを区別。not_observed_exhaustedは今回の条件で列挙終了まで未出現を意味し、Apple辞書への未収録を断定しない。
7. 表記差の診断はNFKC・英字大小文字・中黒・空白・ハイフンを正規化した一致。プラス記号など意味のある記号は削除しない。厳密一致の元結果は変更しない。
8. 別の読みで同じ表記が出る場合はother_readings_with_hitsに記録する。たとえばNISTは「にすと」で未出現でも英字一字読みでは出る。
9. 分割すれば変換できることは除外理由にしていない。今回の目的は用語を自然な単位で一括変換できるようにすること。
10. plistはphrase/shortcut構造、読み32文字・表記64文字を検査。構文検査のみでGUIインポートは未試験。既存辞書・学習・入力設定は変更していない。

単語リストなのでTF/DFや論文頻度は算出しない。旧論文PoCの1,040候補との母集団が異なり、未出現率の単純比較はできない。成果を共有する場合はSOURCE_POLICY.mdとATTRIBUTIONS.txtも添付する。
