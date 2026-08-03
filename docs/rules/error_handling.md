# エラーハンドリング及び例外設計ガイドライン (error_handling.md)

本ドキュメントは、You_Inc システム（`core-service` および `agent-core`）における例外設計・エラーハンドリングの判断基準と分類を定めた正本（Timeless SSOT）である。

---

## 1. 基本理念 (Core Principles)

1. **Pythonic & YAGNI (標準例外の最大活用)**:
   - 不要な独自例外クラス（`DomainException`, `TaskNotFoundException`, `ServiceException` など）の増殖・乱立を固く禁ずる。
   - Python 標準例外（`ValueError`, `FileNotFoundError`, `FileExistsError` 等）のセマンティクスを第一義として活用し、認知的負荷とボイラープレートを最小化する。
2. **Fail-Fast の原則 (不整合の即時遮断)**:
   - 不正入力、未存在リソースへの更新、ドメイン不変条件違反、循環参照などの不整合が発生した際は、**サイレントに失敗（`None` 返却や空処理）させることを禁止**し、即座に例外を送出して処理を停止（Fail-Fast）せよ。
3. **明確なエラーメッセージ**:
   - 例外送出時は、何が不正であったのか（原因・対象のID・期待値）を機械的かつ人間が読める形式でメッセージに含めること。
   - 例: `raise ValueError(f"Task with id '{task_id}' not found.")`

---

## 2. レイヤ別エラーハンドリング分類マトリクス

```
┌─────────────────────────────────────────────────────────────┐
│ 1. プレゼンテーション層 (CLI Tools / agent-core)            │
│    - 引数バリデーション / パース違反: ValueError            │
│    - 終了コード: sys.exit(1) によるプロセス即時停止         │
├─────────────────────────────────────────────────────────────┤
│ 2. アプリケーション層 (UseCases)                            │
│    - 業務ルール違反 / 未存在リソース: ValueError            │
│    - 自己参照 / 整合性違反: ValueError                      │
├─────────────────────────────────────────────────────────────┤
│ 3. ドメイン層 (Entities / Domain Services)                  │
│    - ドメイン不変条件違反: ValueError                       │
├─────────────────────────────────────────────────────────────┤
│ 4. インフラ層 (Adapters / Gateways / DB)                    │
│    - ファイル衝突: FileExistsError                          │
│    - ファイル不在: FileNotFoundError                        │
│    - セキュリティ違反 (パストラバーサル等): ValueError      │
│    - 外部API / 通信障害: ライブラリ標準例外 (HttpError 等)  │
│    - DB障害 / データ破損: SQLAlchemyError, ValueError       │
└─────────────────────────────────────────────────────────────┘
```

### レイヤごとの具体的運用ルール

| レイヤ | 発生する状況 | 使用する例外 / 対処 | 具体例 |
| :--- | :--- | :--- | :--- |
| **CLI / Tools** | 必須引数不足、型不正、UseCase例外 | `ValueError`, `sys.exit(1)` | `[ERROR] Validation failed: ...` を標準エラー出力し終了コード 1 で停止 |
| **UseCase (Application)** | 未存在タスク更新、空タイトル、不正見積もり | `ValueError` | `raise ValueError(f"Task with id '{task_id}' not found.")` |
| **Domain** | 不変条件崩壊（負数実績時間、不正状態遷移） | `ValueError` | `raise ValueError("Actual minutes cannot be negative.")` |
| **Storage (Infrastructure)** | 同名ファイル重複、対象ファイル未存在 | `FileExistsError`<br>`FileNotFoundError` | `raise FileExistsError(f"File already exists: {path}")` |
| **Security (Infrastructure)** | ディレクトリトラバーサル攻撃検知 | `ValueError` | `raise ValueError("ディレクトリトラバーサル攻撃を検知しました")` |
| **External API (Infrastructure)** | Google Calendar API エラー | `HttpError`, `RefreshError` | 上位層に伝播、または適切にログ出力 |

---

## 3. 独自例外（Custom Exception）を追加する厳格な判断基準

原則として Python 標準例外で運用する。  
独自例外クラスの定義を許容するのは、以下の**3条件をすべて満たす極めて稀なケース**に限る：

1. **呼び出し元で特定の例外のみを `except` して業務上のリカバリ（フォールバック処理やリトライ）を自律的に行う必要があること。**
   - ※単にログを出して終了するだけなら標準例外（`ValueError`）で十分である。
2. **標準例外（`ValueError`, `KeyError` 等）では他のエラーと判別が不可能なこと。**
3. **将来の Web API（FastAPI等）導入時など、HTTPステータスコード（404, 409等）への機械的マッピングがシステム要件として明示されたこと。**

---

## 4. テストにおける例外検証ルール

1. **`pytest.raises` における `match` または `exc_info` の必須化**:
   - 例外の型だけでなく、エラーメッセージの意図を必ず検証すること。
   ```python
   # 正しい例: メッセージ意図を厳格に検証
   with pytest.raises(ValueError, match="not found") as exc_info:
       usecase.execute(task_id="invalid_id")
   assert "not found" in str(exc_info.value)
   ```
2. **サイレント失敗テストの禁止**:
   - 不正入力に対して `None` を返して正常終了するようなアサーション（`assert res is None`）を不正入力時の仕様としてはならない。必ず例外送出をテストせよ。
