# Background Changer - グリーンバック動画背景置換ツール

OpenCVを使ってグリーンバック（グリーンスクリーン）動画の背景を任意の画像に置き換えるPythonツールです。

## 特徴

- **シンプルな構造**: bg/, green/, output/ の3つのフォルダのみ
- **複数背景対応**: 最大2枚の背景画像から選択可能
- **一括処理**: green/フォルダ内の全動画を自動処理
- **パラメータ調整**: HSV色空間で正確な緑色検出
- **テスト機能**: 1つの動画でパラメータをテスト

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
# リポジトリをクローン
git clone https://github.com/shiru2/Background-changer.git
cd Background-changer

# uvのインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール
uv sync
```

### 方法2: pipを使用

```bash
# リポジトリをクローン
git clone https://github.com/shiru2/Background-changer.git
cd Background-changer

# 仮想環境の作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## 使用方法

### 1. フォルダ構成

初回実行時、必要なフォルダが自動作成されます：

```
Background-changer/
├── bg/              # 背景画像を配置（最大2枚）
├── green/           # グリーンバック動画を配置
├── output/          # 処理結果が出力される（自動作成）
├── test_output/     # テスト結果が出力される（自動作成）
├── run.py           # メインスクリプト
└── test_run.py      # テストスクリプト
```

### 2. ファイルを配置

**背景画像（bg/フォルダ）:**
- 対応形式: PNG, JPG, JPEG
- 最大2枚まで配置可能

**グリーンバック動画（green/フォルダ）:**
- 対応形式: MP4, MOV, AVI, MKV
- 複数の動画を配置可能（一括処理されます）

### 3. テスト実行（推奨）

まず1つの動画でパラメータをテストします：

```bash
# デフォルトパラメータでテスト
uv run python test_run.py

# 背景画像を指定してテスト（2枚ある場合）
uv run python test_run.py --bg 1
uv run python test_run.py --bg 2

# パラメータを調整してテスト
uv run python test_run.py --lower 30 60 60 --upper 90 255 255

# 特定の動画でテスト
uv run python test_run.py --video your_video.mp4
```

テスト結果は `test_output/` フォルダに保存されます。

### 4. 本番実行

テスト結果が良ければ、全動画を一括処理：

```bash
# 全動画を処理
uv run python run.py

# 背景画像を指定して処理（2枚ある場合）
uv run python run.py --bg 1
uv run python run.py --bg 2

# パラメータを調整して処理
uv run python run.py --lower 30 60 60 --upper 90 255 255
```

処理結果は `output/` フォルダに保存されます。

## パラメータ調整

HSV色空間のパラメータを調整することで、様々な緑色に対応できます。

### HSVパラメータの意味

- **H (色相)**: 0-179 (緑色は35-85あたり)
- **S (彩度)**: 0-255 (色の鮮やかさ)
- **V (明度)**: 0-255 (明るさ)

### 問題別の調整方法

#### 緑色が背景に残ってしまう場合

緑色検出の範囲を広げます：

```bash
uv run python test_run.py --lower 30 60 60 --upper 90 255 255
```

#### 人物の一部が消えてしまう場合

緑色検出の範囲を狭めます：

```bash
uv run python test_run.py --lower 40 100 100 --upper 80 255 255
```

#### 明るい緑だけ抜きたい場合

V（明度）の下限を上げます：

```bash
uv run python test_run.py --lower 35 80 120 --upper 85 255 255
```

#### 暗い緑も含めて抜きたい場合

V（明度）の下限を下げます：

```bash
uv run python test_run.py --lower 35 80 40 --upper 85 255 255
```

## ファイル説明

- **run.py** - 全動画を一括処理するメインスクリプト
- **test_run.py** - 1動画でパラメータをテストするスクリプト
- **requirements.txt** - Python依存パッケージリスト
- **pyproject.toml** - プロジェクト設定（uv用）

## 技術仕様

- **入力形式**: MP4, MOV, AVI, MKV
- **出力形式**: MP4 (H.264)
- **処理方式**: OpenCV chromakey (HSV色空間)
- **フレームレート**: 元動画のFPSを維持
- **解像度**: 元動画の解像度を維持
- **背景画像**: 自動的に動画サイズにリサイズ

## トラブルシューティング

### 初回実行時にフォルダが作成される

これは正常な動作です。以下の手順を実行してください：

1. `bg/` フォルダに背景画像（PNG/JPG）を配置
2. `green/` フォルダにグリーンバック動画を配置
3. スクリプトを再実行

### エラー: 動画ファイルが開けません

- 動画ファイルが破損していないか確認
- 対応形式（MP4, MOV, AVI, MKV）か確認

### エラー: 背景画像が開けません

- 画像ファイルが破損していないか確認
- 対応形式（PNG, JPG, JPEG）か確認

### 緑色が完全に抜けない

- `test_run.py` でパラメータを調整してください
- 照明条件によって緑色の色相が変わる場合があります

## 実行例

### ケース1: 背景画像1枚、動画3本

```bash
# ファイル配置
bg/background.png
green/video1.mp4
green/video2.mp4
green/video3.mp4

# 実行
uv run python run.py

# 結果
output/video1_output.mp4
output/video2_output.mp4
output/video3_output.mp4
```

### ケース2: 背景画像2枚、動画1本

```bash
# ファイル配置
bg/background1.png
bg/background2.png
green/video.mp4

# 背景1で実行
uv run python run.py --bg 1

# 背景2で実行
uv run python run.py --bg 2

# 結果
output/video_output.mp4  # 選択した背景で処理
```

## ライセンス

MIT License

## 作者

Created with Claude Code

## 貢献

プルリクエストを歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成
