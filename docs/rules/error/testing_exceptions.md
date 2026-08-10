# テストにおける例外検証ルール

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
