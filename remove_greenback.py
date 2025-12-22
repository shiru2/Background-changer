#!/usr/bin/env python3
"""
グリーンバック動画の背景を01.pngに置き換えるスクリプト

使用方法:
    uv run python remove_greenback.py

処理内容:
    - output_10fps_1080p/ 内の全動画を検出
    - グリーンバックを01.pngに置き換え
    - output_with_background/ に出力
"""

import os
import sys
from pathlib import Path
import ffmpeg


def get_script_dir():
    """スクリプトのディレクトリを取得（相対パスの基準）"""
    return Path(__file__).parent.absolute()


def remove_greenback(input_video, background_image, output_video, similarity=0.3, blend=0.1):
    """
    グリーンバック動画の背景を画像に置き換える
    人物を残したまま、緑色の背景部分だけを01.pngに置き換える

    Args:
        input_video: 入力動画パス
        background_image: 背景画像パス
        output_video: 出力動画パス
        similarity: 緑色の類似度（0.0-1.0、高いほど広範囲の緑を透過）デフォルト0.3
        blend: エッジのブレンド量（0.0-1.0、高いほど滑らか）デフォルト0.1
    """
    try:
        print(f"Processing: {input_video.name}")

        # 入力動画を読み込み
        video = ffmpeg.input(str(input_video))

        # 背景画像を読み込み（ループ指定で動画の長さに合わせる）
        # scaleフィルタで動画と同じサイズにリサイズ
        background = (
            ffmpeg.input(str(background_image), loop=1)
            .filter('scale', 1920, 1080)
            .filter('fps', fps=10)
        )

        # chromakeyフィルタでグリーン部分を透過
        # 人物以外の緑色背景が透明になる
        keyed = video.filter(
            'chromakey',
            color='0x00FF00',  # 緑色（16進数）
            similarity=similarity,
            blend=blend,
            yuv=1  # YUVカラースペースで処理（より正確）
        )

        # 背景画像の上に、透過処理した動画（人物）を重ねる
        # これで人物は残り、緑背景だけが01.pngに置き換わる
        output = ffmpeg.overlay(
            background,
            keyed,
            x=0,
            y=0,
            shortest=1
        )

        # 出力設定
        output = ffmpeg.output(
            output,
            str(output_video),
            vcodec='libx264',
            pix_fmt='yuv420p',
            r=10,
            preset='medium',
            crf=23,  # 品質（18-28推奨、低いほど高品質）
            **{'b:v': '3M'}  # ビットレート3Mbps
        )

        # 既存ファイルを上書き
        output = ffmpeg.overwrite_output(output)

        # 実行
        ffmpeg.run(output, quiet=True)

        print(f"✓ Completed: {output_video.name}")

    except ffmpeg.Error as e:
        print(f"✗ Error processing {input_video.name}:")
        print(e.stderr.decode() if e.stderr else str(e))
        return False
    except Exception as e:
        print(f"✗ Error processing {input_video.name}: {e}")
        return False

    return True


def main():
    # スクリプトのディレクトリを基準にする
    base_dir = get_script_dir()

    # 入力・出力ディレクトリ、背景画像のパス（相対パス）
    input_dir = base_dir / "output_10fps_1080p"
    output_dir = base_dir / "output_with_background"
    background_image = base_dir / "01.png"

    # 存在チェック
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    if not background_image.exists():
        print(f"Error: Background image not found: {background_image}")
        sys.exit(1)

    # 出力ディレクトリを作成
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")

    # 動画ファイルを検出（mp4, mov, avi など）
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    video_files = []

    for ext in video_extensions:
        video_files.extend(input_dir.glob(f"*{ext}"))

    if not video_files:
        print(f"No video files found in {input_dir}")
        sys.exit(1)

    # ソート
    video_files = sorted(video_files)

    print(f"\nFound {len(video_files)} video file(s)")
    print(f"Background image: {background_image.name}")
    print("-" * 60)

    # 処理
    success_count = 0
    failed_count = 0

    for video_file in video_files:
        # 出力ファイル名（_greenscreenを_with_bgに置き換え）
        output_name = video_file.stem.replace('_greenscreen', '_with_bg') + '.mp4'
        output_path = output_dir / output_name

        if remove_greenback(video_file, background_image, output_path):
            success_count += 1
        else:
            failed_count += 1

    # 結果表示
    print("-" * 60)
    print(f"\nProcessing completed!")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
