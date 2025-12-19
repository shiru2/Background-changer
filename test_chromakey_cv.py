#!/usr/bin/env python3
"""
OpenCV版：1つの動画でHSVパラメータをテストするスクリプト

使用方法:
    # デフォルトパラメータでテスト
    uv run python test_chromakey_cv.py

    # パラメータを指定してテスト
    uv run python test_chromakey_cv.py --lower 35 80 80 --upper 85 255 255

    # 特定の動画でテスト
    uv run python test_chromakey_cv.py --input 10deg_greenscreen.mp4
"""

import sys
from pathlib import Path
import argparse
from remove_greenback_cv import change_background, get_script_dir


def main():
    parser = argparse.ArgumentParser(
        description='OpenCV版グリーンバック除去のパラメータテスト'
    )
    parser.add_argument(
        '--lower',
        type=int,
        nargs=3,
        default=[35, 80, 80],
        metavar=('H', 'S', 'V'),
        help='緑色検出の下限値 (H:0-179, S:0-255, V:0-255)。デフォルト: 35 80 80'
    )
    parser.add_argument(
        '--upper',
        type=int,
        nargs=3,
        default=[85, 255, 255],
        metavar=('H', 'S', 'V'),
        help='緑色検出の上限値 (H:0-179, S:0-255, V:0-255)。デフォルト: 85 255 255'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='10deg_greenscreen.mp4',
        help='テストする動画ファイル名。デフォルト: 10deg_greenscreen.mp4'
    )

    args = parser.parse_args()

    # パス設定
    base_dir = get_script_dir()
    input_dir = base_dir / "output_10fps_1080p"
    output_dir = base_dir / "test_output_cv"
    background_image = base_dir / "01.png"

    # 入力ファイル
    input_video = input_dir / args.input

    # 存在チェック
    if not input_video.exists():
        print(f"Error: Video file not found: {input_video}")
        print(f"\nAvailable files in {input_dir}:")
        for f in sorted(input_dir.glob("*.mp4")):
            print(f"  - {f.name}")
        sys.exit(1)

    if not background_image.exists():
        print(f"Error: Background image not found: {background_image}")
        sys.exit(1)

    # 出力ディレクトリを作成
    output_dir.mkdir(exist_ok=True)

    # パラメータをタプルに変換
    lower_green = tuple(args.lower)
    upper_green = tuple(args.upper)

    # 出力ファイル名
    output_name = f"test_cv_L{lower_green[0]}_{lower_green[1]}_{lower_green[2]}_U{upper_green[0]}_{upper_green[1]}_{upper_green[2]}.mp4"
    output_video = output_dir / output_name

    print("=" * 60)
    print("OpenCV Chromakey Parameter Test")
    print("=" * 60)
    print(f"Input video: {input_video.name}")
    print(f"Background: {background_image.name}")
    print(f"Lower HSV: {lower_green} (H:色相, S:彩度, V:明度)")
    print(f"Upper HSV: {upper_green} (H:色相, S:彩度, V:明度)")
    print(f"Output: {output_video}")
    print("=" * 60)
    print()

    # 処理実行
    success = change_background(
        input_video,
        background_image,
        output_video,
        lower_green=lower_green,
        upper_green=upper_green
    )

    if success:
        print()
        print("=" * 60)
        print("Test completed successfully!")
        print(f"Output file: {output_video}")
        print("=" * 60)
        print()
        print("パラメータ調整のヒント:")
        print("【緑色が背景に残ってしまう場合】")
        print("  → 緑色検出の範囲を広げる")
        print("  例: --lower 30 60 60 --upper 90 255 255")
        print()
        print("【人物の一部が消えてしまう場合】")
        print("  → 緑色検出の範囲を狭める")
        print("  例: --lower 40 100 100 --upper 80 255 255")
        print()
        print("【明るい緑だけ抜きたい場合】")
        print("  → V（明度）の下限を上げる")
        print("  例: --lower 35 80 120 --upper 85 255 255")
        print()
        print("【暗い緑も含めて抜きたい場合】")
        print("  → V（明度）の下限を下げる")
        print("  例: --lower 35 80 40 --upper 85 255 255")
    else:
        print()
        print("Test failed. Please check the error message above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
