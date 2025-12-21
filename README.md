# Background Changer - グリーンバック動画背景置換ツール

OpenCVを使ってグリーンバック（グリーンスクリーン）動画の背景を任意の画像に置き換えるPythonツールです。

## 特徴

- **シンプルな構造**: bg/, green/, output/ の3つのフォルダのみ
- **複数背景対応**: 最大2枚の背景画像から選択可能
- **一括処理**: green/フォルダ内の全動画を自動処理
- **パラメータ調整**: HSV色空間で正確な緑色検出
- **サイズ・配置調整**: 人物のサイズと位置を自由に調整
- **輝度マッチング**: 背景と人物の明るさを自動調整して自然な合成
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
# デフォルトパラメータでテスト（人物0.7倍、上部20%に配置、輝度マッチングON）
uv run python test_run.py

# 背景画像を指定してテスト（2枚ある場合）
uv run python test_run.py --bg 1
uv run python test_run.py --bg 2

# サイズと配置を調整
uv run python test_run.py --scale 0.5 --y-position 0.1    # 小さく上部に
uv run python test_run.py --scale 1.0 --y-position 0.5    # 原寸大で中央に

# 輝度マッチングを無効化（元の色を維持）
uv run python test_run.py --no-brightness-match

# HSVパラメータを調整
uv run python test_run.py --lower 30 60 60 --upper 90 255 255

# 特定の動画でテスト
uv run python test_run.py --video your_video.mp4

# 全てを組み合わせ
uv run python test_run.py --scale 0.6 --y-position 0.15 --lower 30 60 60
```

テスト結果は `test_output/` フォルダに保存されます。

### 4. 本番実行

テスト結果が良ければ、全動画を一括処理：

```bash
# 全動画を処理（デフォルト設定）
uv run python run.py

# 背景画像を指定して処理（2枚ある場合）
uv run python run.py --bg 1
uv run python run.py --bg 2

# サイズと配置を調整して処理
uv run python run.py --scale 0.7 --y-position 0.2

# 輝度マッチング無効で処理
uv run python run.py --no-brightness-match

# 全パラメータを指定して処理
uv run python run.py --scale 0.6 --y-position 0.15 --lower 30 60 60 --upper 90 255 255
```

処理結果は `output/` フォルダに保存されます。

## パラメータ調整

### サイズと配置

人物のサイズと画面上の位置を調整できます。

**--scale** (デフォルト: 0.7)
- `0.5`: 人物を小さく（50%）
- `0.7`: 標準（70%）
- `1.0`: 原寸大（100%）

**--y-position** (デフォルト: 0.2)
- `0.0`: 画面上端
- `0.2`: 上部（デフォルト）
- `0.5`: 中央
- `0.8`: 下部

```bash
# 例: 人物を小さく画面上部に配置
uv run python run.py --scale 0.5 --y-position 0.1
```

### 輝度マッチング

人物と背景の明るさを自動調整して自然な合成を実現します。

**デフォルト: ON（自動調整）**
- 背景の平均輝度を計算
- 人物の輝度を背景に合わせて調整
- 色温度（彩度）も軽く調整

**--no-brightness-match**
- 輝度マッチングを無効化
- 元の色を維持したい場合に使用

```bash
# 例: 輝度マッチングを無効化
uv run python run.py --no-brightness-match
```

### HSVパラメータ

HSV色空間のパラメータを調整することで、様々な緑色に対応できます。

**HSVパラメータの意味:**
- **H (色相)**: 0-179 (緑色は35-85あたり)
- **S (彩度)**: 0-255 (色の鮮やかさ)
- **V (明度)**: 0-255 (明るさ)

### 問題別の調整方法

#### 人物が浮いて見える・色が合わない

輝度マッチング機能を使用します（デフォルトON）：

```bash
# デフォルトで輝度マッチングON
uv run python test_run.py

# より強く調整したい場合は背景画像を変更
```

#### 人物が大きすぎる・小さすぎる

スケールを調整します：

```bash
# 人物を小さく
uv run python test_run.py --scale 0.5

# 人物を大きく
uv run python test_run.py --scale 1.0
```

#### 人物の位置を変更したい

Y位置を調整します：

```bash
# 上部に配置
uv run python test_run.py --y-position 0.1

# 中央に配置
uv run python test_run.py --y-position 0.5
```

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
- **人物スケール**: デフォルト0.7倍（調整可能）
- **人物配置**: デフォルト上部20%（調整可能）
- **輝度マッチング**: デフォルトON（背景の明るさに自動調整）

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
