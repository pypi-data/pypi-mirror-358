# flexmerge

[![PyPI version](https://badge.fury.io/py/flexmerge.svg)](https://badge.fury.io/py/flexmerge)
[![Python versions](https://img.shields.io/pypi/pyversions/flexmerge.svg)](https://pypi.org/project/flexmerge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/flexmerge/workflows/Upload%20Python%20Package/badge.svg)](https://github.com/yourusername/flexmerge/actions)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/yourusername/flexmerge)

**flexmerge**は、Pythonで辞書を直感的かつ柔軟にマージするための軽量ライブラリです。複雑な辞書マージロジックを簡単に実装でき、カスタム戦略の登録も可能です。

## 特徴

- 🚀 **シンプルで直感的なAPI** - メソッドチェーンで簡単設定
- 🔧 **柔軟な戦略システム** - リストと辞書の異なるマージ戦略
- 🎯 **カスタム戦略対応** - 独自のマージロジックを簡単に追加
- 📦 **軽量** - 外部依存なし、純粋Python実装
- 🧪 **高品質** - 95%以上のテストカバレッジ
- 🐍 **Python 3.10+対応** - 最新のPython機能を活用

## インストール

```bash
pip install flexmerge
```

## クイックスタート

### 基本的な使用方法

```python
from flexmerge import Merger

# 基本的なマージ
merger = Merger()
result = merger.merge(
    {"a": 1, "items": [1, 2]},
    {"b": 2, "items": [3, 4]}
)
print(result)
# {'a': 1, 'b': 2, 'items': [1, 2, 3, 4]}
```

### 戦略を指定したマージ

```python
from flexmerge import Merger

# リストの重複を除去し、辞書を深くマージ
merger = Merger().lists("unique").dicts("deep")
result = merger.merge(
    {"tags": ["python", "web"], "config": {"debug": True}},
    {"tags": ["web", "api"], "config": {"port": 8000}}
)
print(result)
# {'tags': ['python', 'web', 'api'], 'config': {'debug': True, 'port': 8000}}
```

### 便利関数を使用

```python
from flexmerge import merge, merge_unique, merge_shallow

# デフォルトマージ
result = merge(dict1, dict2)

# 重複除去マージ
result = merge_unique(dict1, dict2)

# 浅いマージ
result = merge_shallow(dict1, dict2)
```

## 利用可能な戦略

### リスト戦略

| 戦略 | 説明 | 例 |
|------|------|-----|
| `append` | 右のリストを左に追加（デフォルト） | `[1,2] + [3,4] → [1,2,3,4]` |
| `prepend` | 右のリストを左の前に追加 | `[1,2] + [3,4] → [3,4,1,2]` |
| `unique` | 重複を除去して結合 | `[1,2] + [2,3] → [1,2,3]` |
| `replace` | 左のリストを右で置換 | `[1,2] + [3,4] → [3,4]` |
| `keep` | 左のリストを保持 | `[1,2] + [3,4] → [1,2]` |

### 辞書戦略

| 戦略 | 説明 | 動作 |
|------|------|------|
| `deep` | 深いマージ（デフォルト） | ネストした辞書も再帰的にマージ |
| `shallow` | 浅いマージ | 第一レベルのキーのみマージ |
| `replace` | 左の辞書を右で置換 | 右の辞書で完全に上書き |
| `keep` | 左の辞書を保持 | 左の辞書の値を優先 |

## 高度な使用方法

### カスタム戦略の登録

```python
from flexmerge import Merger

merger = Merger()

# 型安全なリスト戦略の登録
@merger.list_strategy("sorted_unique")
def sorted_unique_merge(left, right):
    """ソートされた一意のリストを作成"""
    return sorted(set(left + right))

# 型安全な辞書戦略の登録
@merger.dict_strategy("conditional_merge")
def conditional_merge(left, right):
    """条件付きマージ"""
    if left.get("mergeable") and right.get("mergeable"):
        return {**left, **right}
    return left

# カスタム戦略を使用
merger = merger.lists("sorted_unique").dicts("conditional_merge")
result = merger.merge(
    {"items": [3, 1, 2], "mergeable": True},
    {"items": [2, 4, 1], "mergeable": True}
)
print(result)
# {'items': [1, 2, 3, 4], 'mergeable': True}
```



### 関数を直接戦略として使用

```python
def custom_merge(left, right):
    return [max(left + right)]

merger = Merger().lists(custom_merge)
result = merger.merge(
    {"scores": [85, 90]},
    {"scores": [88, 92]}
)
print(result)
# {'scores': [92]}
```

### 複数辞書のマージ

```python
from flexmerge import Merger

merger = Merger().lists("unique").dicts("deep")

default_config = {
    "database": {"host": "localhost", "port": 5432},
    "features": ["auth", "logging"]
}

production_config = {
    "database": {"host": "prod.example.com"},
    "features": ["auth", "monitoring"]
}

user_config = {
    "database": {"timeout": 30},
    "features": ["custom_feature"]
}

result = merger.merge(default_config, production_config, user_config)
print(result)
# {
#     'database': {'host': 'prod.example.com', 'port': 5432, 'timeout': 30},
#     'features': ['auth', 'logging', 'monitoring', 'custom_feature']
# }
```

### Enumを使用した戦略指定

```python
from flexmerge import Merger, BuiltinListStrategies, BuiltinDictStrategies

merger = Merger().lists(BuiltinListStrategies.UNIQUE).dicts(BuiltinDictStrategies.SHALLOW)
```

## 実世界での使用例

### 設定ファイルのマージ

```python
from flexmerge import merge_unique

# デフォルト設定
default_settings = {
    "debug": False,
    "database": {
        "host": "localhost",
        "port": 5432,
        "options": ["ssl"]
    },
    "features": ["basic"]
}

# 環境固有設定
env_settings = {
    "database": {
        "host": "prod.db.example.com",
        "options": ["ssl", "pooling"]
    },
    "features": ["basic", "advanced"]
}

# ユーザー設定
user_settings = {
    "debug": True,
    "database": {"timeout": 30},
    "features": ["custom"]
}

# 最終設定
final_config = merge_unique(default_settings, env_settings, user_settings)
```

## API リファレンス

### Merger クラス

#### `Merger()`
新しいMergerインスタンスを作成します。

#### `lists(strategy)` 
リストマージ戦略を設定します。
- **strategy**: 戦略名（文字列）、Enum、または関数

#### `dicts(strategy)`
辞書マージ戦略を設定します。
- **strategy**: 戦略名（文字列）、Enum、または関数

#### `strategy(name)`
カスタム戦略を登録するデコレーター。
- **name**: 戦略名（文字列）

#### `merge(*dicts)`
辞書をマージします。
- ***dicts**: マージする辞書（可変長引数）
- **戻り値**: マージされた辞書

#### `copy()`
Mergerインスタンスのコピーを作成します。

### 便利関数

#### `merge(*dicts, lists="append", dict_strategy="deep")`
辞書を指定された戦略でマージします。

#### `merge_unique(*dicts)`
リストの重複を除去してマージします。

#### `merge_shallow(*dicts)`
浅いマージを実行します。

## 開発

### 開発環境のセットアップ

```bash
git clone https://github.com/yourusername/flexmerge.git
cd flexmerge
pip install -e ".[dev]"
```

### テストの実行

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=flexmerge --cov-report=html

# 特定のテストのみ
pytest tests/test_merger.py
```

### コード品質チェック

```bash
# フォーマット
black flexmerge/ tests/

# リンター
ruff check flexmerge/ tests/

# 型チェック
mypy flexmerge/
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 貢献

プルリクエストやイシューの報告を歓迎します！貢献する前に、以下を確認してください：

1. テストが通ること
2. コードスタイルが統一されていること
3. 新機能にはテストが含まれていること
4. ドキュメントが更新されていること

## 変更履歴

### v0.1.0 (2024-XX-XX)
- 初回リリース
- 基本的な辞書マージ機能
- 複数のリスト・辞書戦略
- カスタム戦略対応
- 便利関数の提供
- 95%以上のテストカバレッジ