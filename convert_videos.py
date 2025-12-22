#!/usr/bin/env python3
"""
dougaフォルダ内の動画ファイルをffmpegでH264、mp4、10fpsに変換するスクリプト
"""

import os
from pathlib import Path
import ffmpeg


def convert_video(input_path: Path, output_path: Path, fps: int = 10, resolution: str = "1920:1080"):
    """
    動画ファイルをH264、mp4、指定のfpsと解像度に変換

    Args:
        input_path: 入力動画ファイルのパス
        output_path: 出力動画ファイルのパス
        fps: フレームレート（デフォルト: 10）
        resolution: 解像度（デフォルト: "1920:1080" = 1080p）
    """
    try:
        print(f"変換中: {input_path.name} -> {output_path.name} (1080p)")

        # ffmpegで変換
        stream = ffmpeg.input(str(input_path))
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vcodec='libx264',  # H264コーデック
            vf=f'scale={resolution}',  # 解像度変更
            r=fps,  # フレームレート
            format='mp4'  # mp4フォーマット
        )

        # 上書き確認なしで実行
        ffmpeg.run(stream, overwrite_output=True, quiet=True)

        print(f"完了: {output_path.name}")
        return True

    except ffmpeg.Error as e:
        print(f"エラー: {input_path.name} の変換に失敗しました")
        print(f"詳細: {e.stderr.decode() if e.stderr else str(e)}")
        return False


def main():
    """メイン処理"""
    # パス設定
    douga_dir = Path("douga")
    output_dir = douga_dir / "converted"

    # 出力ディレクトリ作成
    output_dir.mkdir(exist_ok=True)

    # 動画拡張子のリスト
    video_extensions = {'.mov', '.MOV', '.mp4', '.MP4', '.avi', '.AVI', '.mkv', '.MKV'}

    # dougaフォルダ内の動画ファイルを取得
    video_files = [
        f for f in douga_dir.iterdir()
        if f.is_file() and f.suffix in video_extensions
    ]

    if not video_files:
        print("変換する動画ファイルが見つかりませんでした")
        return

    print(f"見つかった動画ファイル: {len(video_files)}個")
    print("-" * 50)

    # 各動画ファイルを変換
    success_count = 0
    failed_count = 0

    for video_file in video_files:
        # 出力ファイル名（拡張子を.mp4に変更）
        output_file = output_dir / f"{video_file.stem}.mp4"

        # 変換実行
        if convert_video(video_file, output_file, fps=10):
            success_count += 1
        else:
            failed_count += 1

    # 結果表示
    print("-" * 50)
    print(f"変換完了: {success_count}個")
    if failed_count > 0:
        print(f"変換失敗: {failed_count}個")
    print(f"出力先: {output_dir}")


if __name__ == "__main__":
    main()
