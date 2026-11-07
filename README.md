# TecKana

**専門用語の日本語入力辞書 / A Japanese input dictionary for specialized terminology**

専門用語を、自然なまとまりで一発変換するための日本語ユーザ辞書です。まず情報科学から始め、数学・化学・建築などの分野にも広げていく予定です。

A Japanese user dictionary for converting specialized terminology as complete terms. The initial release covers computing; mathematics, chemistry, architecture, and other fields are planned.

[日本語](#日本語) · [English](#english)

## 日本語

### このプロジェクトについて

「にぶんぎ → 二分木」のように、分割すれば入力できる用語でも、ひとまとまりで変換できるようにすることを目指しています。英字略称も、かなから変換する使い道があれば対象に含めます。

NISTの **Dictionary of Algorithms and Data Structures（DADS）** を手がかりに日本語表記と読みの候補を作り、macOSのMecabraで変換候補を測定しました。その後、Web画面で候補を人手でレビューしました。NISTやAppleの公式辞書ではありません。

### 現在の成果

2026年11月7日時点のスナップショットです。件数は基本的に「読み・表記」の組数であり、異なる概念の数ではありません。

| 段階 | 件数 |
| --- | ---: |
| DADS索引の見出し・別名 | 1,306 |
| 異なる参照URL | 1,123 |
| 略称・別読みを含む評価行 | 1,191 |
| 人手レビュー対象 | 178 |
| 採用 | **129** |
| 保留 | 49 |
| 不採用・未確認 | 各0 |

採用129件をMac用のユーザ辞書ファイルにまとめました。保留候補は削除せず、後から見直せるように残しています。採用は入力上の有用性についての判断であり、全項目の定訳・読みを専門家が検証したという意味ではありません。

### Macへの導入

1. [採用129件のユーザ辞書](mac-install-129/DADS_採用129件_ユーザ辞書.plist)を保存します。GitHub上ではファイルの「Download raw file」を使ってください。
2. Macを日本語入力に切り替えます。
3. メニューバーの入力メニューから「ユーザ辞書を編集」を開きます。
4. 保存した `.plist` ファイルを、Finderからユーザ辞書の一覧にドラッグします。
5. 「にぶんぎ」を入力して「二分木」が候補に出るか試します。

既存の登録語は、ユーザ辞書の一覧から書き出してバックアップできます。操作の詳細は[Appleの公式ガイド](https://support.apple.com/ja-jp/guide/japanese-input-method/jpim10228/mac)を参照してください。

ファイルは129件、読み・表記の組の重複なし、読み32文字以内・表記64文字以内であることを検査しています。ファイルの検査と、実機での読み込み・変換動作の確認は別です。本README作成時点では、129件すべてのGUI取り込み・変換成功は確認していません。

### iPhoneで使う

Macに取り込んだユーザ辞書は、同じApple AccountとiCloud Driveを使ってiPhoneにも同期できます。iPhoneの「設定」→自分の名前→「iCloud」→「Drive」で同期設定を確認してください。同期した単語は「設定」→「一般」→「キーボード」→「ユーザ辞書」で確認できます。

詳しくは[AppleのiPhoneユーザ辞書ガイド](https://support.apple.com/ja-jp/guide/iphone/iph6d01d862/ios)を参照してください。レビュー用Web画面の判定・コメントはブラウザ内の保存であり、この辞書同期とは別です。

### 作成・評価方法と限界

1. DADSの索引から見出し・別名関係・原典URLを収集。
2. AIで日本語対訳案を作成し、UniDic-liteなどで読みを推定・点検。
3. Mecabraで入力全体に対応する候補を取得し、表記・読みを照合。
4. 未出現候補を列挙上限10,000件で再測定し、表記揺れや別読みでの出現を区別。
5. 178件をWeb画面で人手レビューし、129件を採用。

レビュー対象178件の内訳は、対訳・読みの外部根拠を確認した10件と、AI点検段階の168件です。今回の人手レビューと、外部資料による用語・読みの裏付けは区別しています。

測定記録の環境は `macOS-27.2-arm64-arm-64bit` です。MecabraはmacOSの非公開APIであり、APIの列挙順は実際の入力画面の候補順位と同じとは限りません。**「今回の条件で候補が出なかった」ことは、Appleの辞書に未収録であることを証明しません。** OS・読み・表記・入力条件が変わると結果も変わります。分割変換できる用語も採用対象です。未測定は未測定として扱います。

### ファイルと再実行

- [元の全単語リスト（1,306行）](dads-poc/outputs/index_master.csv)：DADSの見出し・別名、原典URL、対訳案と読み。すべてが検証済み・採用済みという意味ではありません。
- [全評価行（1,191行）](dads-poc/outputs/master.csv)：略称・別読みを含む評価台帳。
- [採用129件CSV](dictionary.csv)／[全178件の採否](review.csv)：自由記述コメントは含みません。

採用辞書は `python3 scripts/build_dictionary.py` で `review.csv` から再生成できます（Python 3標準ライブラリのみ）。公開パッケージには生候補の証拠ファイルを含めていません。評価CSV内の証拠パスは元の実験記録への参照で、同梱ファイルへのリンクではありません。

- [採用129件の辞書](mac-install-129/DADS_採用129件_ユーザ辞書.plist)：Mac取り込み用。
- [DADS PoCのREADME](dads-poc/README.md)：実行手順、評価データ、測定方式。
- [調査レポート](dads-poc/REPORT.md)：候補抽出と評価の結果。
- [レビュー画面のREADME](dads-review/README.md)：採用・不採用・保留、コメント、バックアップの扱い。

PoCの再実行で生成される178件のレビュー候補と、人手採用済み129件は別の成果物です。再実行だけでは人手の判定を再現できません。

### 出典・利用条件

原典は [NIST DADS](https://xlinux.nist.gov/dads/)（編集者 Paul E. Black）です。本プロジェクトでは見出しに基づく対訳案を扱い、DADSの定義本文を一括翻訳・転載していません。学会事典の見出しリストも入力に使用していません。

取得範囲と権利の調査記録は [SOURCE_POLICY.md](dads-poc/SOURCE_POLICY.md)、帰属情報は [ATTRIBUTIONS.txt](dads-poc/outputs/ATTRIBUTIONS.txt)に記載しています。第三者の資料や依存辞書には、それぞれの利用条件が適用されます。**コードと本プロジェクトの説明文書は[MIT License](LICENSE)、辞書データは[CC0 1.0 Universal](LICENSE-DATA-CC0.txt)で公開します。** CC0は本プロジェクトが保有する権利の範囲で適用します。原典や依存辞書など第三者の権利を変更するものではありません。適用範囲は[LICENSING.md](LICENSING.md)を参照してください。

## English

### About

This project aims to make Japanese computing terms available as complete conversion candidates—for example, `にぶんぎ → 二分木`—even when they can already be entered by converting smaller segments. Latin abbreviations are also considered when conversion from a kana reading is useful.

We used NIST's **Dictionary of Algorithms and Data Structures (DADS)** as a starting point for Japanese terms and readings, measured conversion candidates using Mecabra on macOS, and reviewed the resulting shortlist in a web interface. This is not an official NIST or Apple dictionary.

### Current results

Snapshot: November 7, 2026. Counts generally refer to reading–written-form pairs, not distinct concepts.

| Stage | Count |
| --- | ---: |
| DADS index entries, including aliases | 1,306 |
| Distinct referenced URLs | 1,123 |
| Evaluation rows, including abbreviations and alternative readings | 1,191 |
| Candidates for human review | 178 |
| Accepted | **129** |
| On hold | 49 |
| Rejected / unreviewed | 0 each |

The 129 accepted pairs are packaged as a macOS user dictionary. Candidates on hold are retained for later review. Acceptance reflects a judgment about typing usefulness; it does not mean every translation and reading has been verified by a subject-matter expert.

### Install on Mac

1. Download the [129-entry user dictionary](mac-install-129/DADS_採用129件_ユーザ辞書.plist). On GitHub, use **Download raw file**.
2. Switch to a Japanese input source.
3. Open the input menu in the menu bar and select **Edit User Dictionary**.
4. Drag the downloaded `.plist` file from Finder into the user dictionary list.
5. Try entering `にぶんぎ` and look for `二分木`.

You can export existing entries from the dictionary list to make a backup. See [Apple's official guide](https://support.apple.com/guide/japanese-input-method/jpim10228/mac) for details.

The file has been checked for 129 entries, unique reading–written-form pairs, and limits of 32 characters per reading and 64 per written form. File validation is separate from testing import and conversion on a device. At the time of writing, successful GUI import and conversion of all 129 entries have not been verified.

### Use on iPhone

After importing on Mac, the user dictionary can sync to an iPhone using the same Apple Account and iCloud Drive. Check synchronization under **Settings → your name → iCloud → Drive**. Synced entries appear under **Settings → General → Keyboard → Text Replacement** (ユーザ辞書 in Japanese).

See [Apple's iPhone user dictionary guide](https://support.apple.com/guide/iphone/iph6d01d862/ios). Review decisions and comments in the web interface are stored in the browser; they are separate from Apple dictionary synchronization.

### Method and limitations

1. Collect DADS index headings, alias relationships, and source URLs.
2. Draft Japanese translations using AI and estimate/check readings with tools including UniDic-lite.
3. Retrieve Mecabra candidates corresponding to the entire input and compare readings and written forms.
4. Recheck unobserved candidates with an enumeration limit of 10,000, distinguishing spelling variations and matches under other readings.
5. Review 178 candidates in a web interface and accept 129.

The 178-item shortlist contains 10 pairs with external evidence for the term and reading, plus 168 pairs checked by AI. Human selection for this release is distinct from external verification of terminology and pronunciation.

The recorded environment was `macOS-27.2-arm64-arm-64bit`. Mecabra is a private macOS API, and its enumeration order does not necessarily match candidate ranking in the input UI. **Failure to observe a candidate under these conditions does not prove its absence from Apple's dictionaries.** Results depend on the OS, reading, spelling, and input conditions. Terms that can be converted in smaller segments remain eligible. Unmeasured cases are reported as unmeasured.

### Files and reproduction

- [Complete original list (1,306 rows)](dads-poc/outputs/index_master.csv): DADS headings, aliases, source URLs, proposed translations, and readings. Inclusion does not imply verification or acceptance.
- [All evaluation rows (1,191 rows)](dads-poc/outputs/master.csv): includes abbreviations and alternative readings.
- [129 accepted pairs](dictionary.csv) / [decisions for all 178 pairs](review.csv): free-text reviewer comments are omitted.

Run `python3 scripts/build_dictionary.py` to regenerate the accepted dictionary from `review.csv` using only the Python 3 standard library. Raw candidate evidence files are not bundled. Evidence paths in evaluation CSVs refer to the original experiment records, not files included in this package.

- [129-entry dictionary](mac-install-129/DADS_採用129件_ユーザ辞書.plist): macOS import file.
- [DADS PoC README](dads-poc/README.md): execution instructions, evaluation data, and methodology (Japanese).
- [Investigation report](dads-poc/REPORT.md): candidate extraction and evaluation results (Japanese).
- [Review interface README](dads-review/README.md): decisions, comments, and backups (Japanese).

The 178 review candidates generated by the pipeline and the 129 human-accepted pairs are separate outputs. Running the pipeline alone does not reproduce the human decisions.

### Sources and licensing

The source is [NIST DADS](https://xlinux.nist.gov/dads/), edited by Paul E. Black. This project works with translation proposals based on headings; it does not bulk-translate or reproduce DADS definitions. Lists of entries from academic society encyclopedias were not used as input.

See [SOURCE_POLICY.md](dads-poc/SOURCE_POLICY.md) for the recorded collection scope and rights review, and [ATTRIBUTIONS.txt](dads-poc/outputs/ATTRIBUTIONS.txt) for attribution. Third-party materials and dependency dictionaries retain their respective terms. **Code and project documentation are released under the [MIT License](LICENSE); dictionary data are released under [CC0 1.0 Universal](LICENSE-DATA-CC0.txt).** CC0 applies to rights held by this project and does not change third-party rights in sources or dependency dictionaries. See [LICENSING.md](LICENSING.md) for scope.
