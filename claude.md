# 動画変換プロジェクト

## 概要
dougaフォルダ内の動画ファイルをffmpegを使ってH264、mp4、10fpsに変換するプロジェクト

## 環境構築
```bash
# uvで環境構築
uv init
uv add ffmpeg-python
```

## 使用方法
```bash
# 仮想環境でスクリプトを実行
uv run python convert_videos.py
```

## 変換仕様
- コーデック: H264
- フォーマット: mp4
- フレームレート: 10fps
- 入力: dougaフォルダ内の全動画ファイル
- 出力: douga/converted フォルダ

## 処理内容
1. dougaフォルダ内の動画ファイルを検出
2. 各ファイルをH264、mp4、10fpsに変換
3. convertedフォルダに保存
