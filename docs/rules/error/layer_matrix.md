# レイヤ別エラーハンドリング分類マトリクス

## 1. 基本理念 (Core Principles)
1. **Pythonic & YAGNI (標準例外の最大活用)**:
   - 不要な独自例外クラス（`DomainException` など）の増殖・乱立を固く禁ずる。
   - Python 標準例外（`ValueError`, `FileNotFoundError`, `FileExistsError` 等）のセマンティクスを第一義として活用する。
2. **Fail-Fast の原則 (不整合の即時遮断)**:
   - 不整合が発生した際は、**サイレントに失敗（`None` 返却や空処理）させることを禁止**し、即座に例外を送出して処理を停止（Fail-Fast）せよ。
3. **明確なエラーメッセージ**:
   - 例外送出時は、何が不正であったのか（原因・対象のID・期待値）を機械的かつ人間が読める形式でメッセージに含めること。

## 2. マトリクスと具体的運用ルール
| レイヤ | 発生する状況 | 使用する例外 / 対処 | 具体例 |
| :--- | :--- | :--- | :--- |
| **CLI / Tools** | 必須引数不足、型不正、UseCase例外 | `ValueError`, `sys.exit(1)` | `[ERROR] Validation failed: ...` を標準エラー出力し終了コード 1 で停止 |
| **UseCase (Application)** | 未存在タスク更新、空タイトル、不正見積もり | `ValueError` | `raise ValueError(f"Task with id '{task_id}' not found.")` |
| **Domain** | 不変条件崩壊（負数実績時間、不正状態遷移） | `ValueError` | `raise ValueError("Actual minutes cannot be negative.")` |
| **Storage (Infrastructure)** | 同名ファイル重複、対象ファイル未存在 | `FileExistsError`<br>`FileNotFoundError` | `raise FileExistsError(f"File already exists: {path}")` |
| **Security (Infrastructure)** | ディレクトリトラバーサル攻撃検知 | `ValueError` | `raise ValueError("ディレクトリトラバーサル攻撃を検知しました")` |
| **External API (Infrastructure)** | Google Calendar API エラー | `HttpError`, `RefreshError` | 上位層に伝播、または適切にログ出力 |
