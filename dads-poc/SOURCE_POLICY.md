# DADSの取得範囲と利用条件（2026-11-07）

- 原典: [NIST Dictionary of Algorithms and Data Structures](https://xlinux.nist.gov/dads/)。編集者Paul E. Black。索引1ページの見出し・別名関係・参照URLを処理した。取得日時・SHA-256はdata/source.json。
- 現行索引1,306行、うち参照先への別名183行。異なる参照URLは1,123件。英語見出しの下付き・上付き表示はプレーンテキスト化し、表記上の空白は保持する。
- [NIST公式データカタログ](https://catalog.data.gov/dataset/dictionary-of-algorithms-and-data-structures-dads)は、一部の定義がCRC Pressの著作権対象で、それ以外はパブリックドメインと明示している。**今回は定義本文を一括取得・翻訳・複製していない**。depoissonization等も見出しへの訳案だけで、定義文は含まない。
- 本実行のrobots.txt応答は404だった。ログ用ファイルをローカル保存。収集プログラムは将来の新規取得時にもrobotsを確認し、禁止または404/410以外の取得障害なら停止する。2 MB上限、索引とrobots各1回、再帰巡回なし、自動リトライなし。
- data/translations.tsvは英語見出しに基づくAIの対訳案。確認できない名称は原語維持または暫定訳と明示。人間による翻訳・専門家校閲済みではない。英語別名は参照先の日本語訳に正規化し、独立した直訳ではない。
- 読みを確認したe-Wordsの個別項目と執筆者ブログはdata/external_checks.jsonにURL・確認範囲を記録。DADSから既に得た候補の対訳・読みを照合したもので、これらのサイトの索引や定義本文をコーパス化していない。参照先の著作物をパブリックドメイン扱いしない。
- 旧PoCの論文・IPSJ用語リストは今回の入力データに使っていない。再利用したのはMecabra測定コードと評価方式。学会事典の見出しリストを複製していない。
- 配布ZIPにはサイトHTML・原PDF・依存辞書本体を含めない。出典・編集者・変更内容を記したATTRIBUTIONS.txtを成果と併せて保存する。
- 依存するUniDic-lite/Sudachi等には各配布元のライセンスが適用される。取得した索引データ、AIによる対訳、コード、依存辞書の権利を一括してCC0やCC BYと宣言しない。本公開版のコードはMIT、辞書データは保有する権利の範囲でCC0。詳細は ../LICENSING.md。
