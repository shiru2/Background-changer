# Background Changer - グリーンバック動画背景置換ツール

OpenCVを使ってグリーンバック（グリーンスクリーン）動画の背景を任意の画像に置き換えるPythonツールです。

## 機能

- グリーンバック動画から人物を抽出
- 背景画像と合成
- 複数動画の一括処理
- パラメータ調整用のテストスクリプト
- HSV色空間による正確な緑色検出

## 必要な環境

- Python 3.11以上
- ffmpeg（システムにインストール済みであること）

### ffmpegのインストール

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:**
[FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロードしてインストール

## インストール

### 方法1: uvを使用（推奨）

```bash
# uvのインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール
uv sync
```

### 方法2: pipを使用

```bash
# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## 使用方法

### ディレクトリ構成

```
.
├── remove_greenback_cv.py     # メインスクリプト
├── test_chromakey_cv.py       # テストスクリプト
├── 01.png                     # 背景画像
├── output_10fps_1080p/        # 入力動画フォルダ
│   ├── video1_greenscreen.mp4
│   └── video2_greenscreen.mp4
└── output_with_background/    # 出力先（自動作成）
```

### 1つの動画でテスト

まず1つの動画でパラメータをテストして、最適な設定を見つけます。

```bash
# デフォルトパラメータでテスト
uv run python test_chromakey_cv.py

# パラメータを調整してテスト
uv run python test_chromakey_cv.py --lower 30 60 60 --upper 90 255 255

# 特定の動画でテスト
uv run python test_chromakey_cv.py --input your_video.mp4
```

### 全動画を一括処理

テスト結果が良ければ、全動画を一括処理します。

```bash
uv run python remove_greenback_cv.py
```

## パラメータ調整

HSV色空間のパラメータを調整することで、様々な緑色に対応できます。

### HSVパラメータの意味

- **H (色相)**: 0-179 (緑色は35-85あたり)
- **S (彩度)**: 0-255 (色の鮮やかさ)
- **V (明度)**: 0-255 (明るさ)

### 調整のヒント

**緑色が背景に残ってしまう場合:**
```bash
# 緑色検出の範囲を広げる
uv run python test_chromakey_cv.py --lower 30 60 60 --upper 90 255 255
```

**人物の一部が消えてしまう場合:**
```bash
# 緑色検出の範囲を狭める
uv run python test_chromakey_cv.py --lower 40 100 100 --upper 80 255 255
```

**明るい緑だけ抜きたい場合:**
```bash
# V（明度）の下限を上げる
uv run python test_chromakey_cv.py --lower 35 80 120 --upper 85 255 255
```

**暗い緑も含めて抜きたい場合:**
```bash
# V（明度）の下限を下げる
uv run python test_chromakey_cv.py --lower 35 80 40 --upper 85 255 255
```

## ファイル説明

- **remove_greenback_cv.py** - 複数動画を一括処理するメインスクリプト
- **test_chromakey_cv.py** - パラメータ調整用のテストスクリプト
- **requirements.txt** - Python依存パッケージリスト
- **pyproject.toml** - プロジェクト設定（uv用）

## 技術仕様

- **入力形式**: mp4, mov, avi, mkv
- **出力形式**: mp4 (H.264)
- **処理方式**: OpenCV chromakey (HSV色空間)
- **フレームレート**: 元動画のFPSを維持
- **解像度**: 元動画の解像度を維持

## トラブルシューティング

### エラー: 動画ファイルが開けません

- 入力動画のパスが正しいか確認してください
- 動画ファイルが破損していないか確認してください

### エラー: 背景画像が開けません

- `01.png`がスクリプトと同じディレクトリにあるか確認してください
- 画像ファイルが破損していないか確認してください

### 緑色が完全に抜けない

- HSVパラメータを調整してください
- 照明条件によって緑色の色相が変わる場合があります

## ライセンス

MIT License

## 作者

Created with Claude Code
