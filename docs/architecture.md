# Architecture

core-service は、ステートレスで堅牢なドメインロジック/APIを提供する。
DDD（レイヤードアーキテクチャ）を採用する。

## コンテナ化不要のステートレス設計
core-service自体のコンテナ（Docker）化は行わず、純粋なPythonライブラリ群として実装する。

## DIによるシークレット管理
APIキー等を一切保持せず、実行時に agent-core 側から sops を経由して注入される仕組みを前提とする。
