# SecondBrainService Specifications

## [SCENARIO-01] アイデアの取り込み (Register Knowledge)
- **前提**: Orchestratorから未整理のアイデア（タイトル、本文、画像）が渡される。
- **結果**: Zettelkastenのテンプレートが適用され、適切なファイル名でInboxにMarkdownが保存される。

## [SCENARIO-02] 知識の検索 (Search Notes)
- **前提**: キーワードを指定して検索を行う。
- **結果**: Repositoryから拡張子 `.md` のファイルの中身を検索し、一致するファイル名のリストが返る。

## [SCENARIO-03] 監査 (Audit Rules)
- **前提**: Validatorを呼び出し、全ノートのコンプライアンスチェックを行う。
- **結果**: 必須キーの欠落や禁止ディレクトリへのアウトバウンドリンクが存在する場合、エラーリストが返る。
