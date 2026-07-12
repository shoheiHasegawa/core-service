# SecondBrainService Specification

## 1. Domain Overview (ドメイン概要)
`SecondBrainService` は、You_Inc のナレッジベースである「Second Brain (Zettelkasten)」に対する単一のアクセスポイント（Application Service）である。
Agent やツールが直接ファイルシステムを操作することによる品質劣化（タグのルール違反、テンプレートの崩れなど）を防ぐため、すべてのナレッジの登録・読み出しはこのサービスを経由して行われなければならない。

## 2. Directory Structure & Rules
ナレッジは情報の成熟度（ライフサイクル）に応じて以下のディレクトリに保存される。
- `00_Inbox/`: 未処理のアイデアやメモ（Fleeting Notes）。
- `20_Sense_Making/`: プロジェクトでの学びや、深掘り・考察の対象となる知見（Incubation Notes）。
- `40_Permanent_Notes/`: Socratic Interview などを経て蒸留された、普遍的な知識ネットワーク。

## 3. Interfaces & Methods
Service は以下の登録メソッドを提供する。これらは内部で `ZettelkastenFormatter` と `ZettelkastenValidator`（実装予定または連携）を呼び出し、ガバナンスを確保する。

### 3.1 `register_inbox_note`
- **責務**: 新規のアイデアやメモを Inbox テンプレートを用いて `00_Inbox` へ登録する。
- **引数**: `title`, `content`, `tags`

### 3.2 `register_sense_making_note`
- **責務**: プロジェクトでの教訓などを Sense Making テンプレートを用いて `20_Sense_Making` へ登録する。
- **引数**: `title`, `content` (incubation space用), `source` (抽出元), `tags`

### 3.3 `register_permanent_note`
- **責務**: 蒸留が完了した普遍的知識を Permanent Note テンプレートを用いて `40_Permanent_Notes` へ登録する。
- **引数**: `title`, `claim`, `context`, `connections`, `aliases`, `tags`

## 4. Architectural Constraints
- **依存関係**: インフラストラクチャ層への直接アクセスを避けるため、ファイルI/Oはすべて `SecondBrainRepository` （または `LocalFileRepository`）の抽象を介して行う。
- **ガバナンス**: このServiceをラップした CLI ツール (`register_zettelkasten_note.py`) が提供され、Agent はコード編集ではなくこのツールを用いて情報を保存しなければならない。
