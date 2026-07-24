# Review Process

コードレビューや品質ゲートについてのドキュメント。
AIエージェント（および人間）がPRをレビューする際は、以下の「5大原則」に基づくチェック観点を厳格に適用すること。

## 1. DDDの観点 (ドメインの純度)
- Domain層のコードに技術依存（SQLAlchemy, boto3, `requests`等）が混入していないか？
- Namingはユビキタス言語に準拠しているか？（`Manager`, `Helper` 等の無意味なシステム用語を排除しているか）
- Port/Adapterの境界が守られているか？

## 2. SOLID / アーキテクチャの観点
- クラスが単一責任（SRP）を遵守しているか？ Application層が「ファットサービス」になっておらず、UseCaseに委譲されているか？
- 機密情報やパスがDI（コンストラクタ注入）を通じて渡されているか？（Service-Configパターンの遵守）

## 3. SDD & TDD の観点 (トレーサビリティと品質)
- 実装が `spec.md` に定義されたシナリオと1対1で対応しているか？
- すべてのテストコードのDocStringに、担保する仕様ID（例: `[TM-PLAN-01]`）が記載されているか？
- Integration Testにおいて、DBへの副作用（アサーション）が確実に記述されているか？（Semantic Reward Hacking の排除）

## 4. Context Engineering の観点 (隔離と凝集)
- コンテキストノイズの排除: DTOやUseCaseなど、独立して動く要素が「1 Concept = 1 File」として物理分離されているか？
- コンテキストの凝集: `planning_rules.py` のように、AIが全体整合性を保つために視界に入れておくべき兄弟クラス（戦略群）が、無闇に分割されず適切に同梱されているか？

## 5. CI/CD 品質ゲート
- GitHub Actionsによる自動化テストがPassしているか？
- `make test` におけるカバレッジが 90% 以上であるか？
- `../agent-core/tools/validate_sdd.py` がエラーを出力していないか？
