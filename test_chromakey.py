#!/usr/bin/env python3
"""
1つの動画でchromakeyパラメータをテストするスクリプト

使用方法:
    # デフォルトパラメータでテスト
    uv run python test_chromakey.py

    # パラメータを指定してテスト
    uv run python test_chromakey.py --similarity 0.4 --blend 0.2
"""

import sys
from pathlib import Path
import argparse
from remove_greenback import remove_greenback, get_script_dir


def main():
    parser = argparse.ArgumentParser(
        description='グリーンバック除去のパラメータテスト'
    )
    parser.add_argument(
        '--similarity',
        type=float,
        default=0.3,
        help='緑色の類似度（0.0-1.0）高いほど広範囲の緑を透過。デフォルト: 0.3'
    )
    parser.add_argument(
        '--blend',
        type=float,
        default=0.1,
        help='エッジのブレンド量（0.0-1.0）高いほど滑らか。デフォルト: 0.1'
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
    output_dir = base_dir / "test_output"
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

    # 出力ファイル名
    output_name = f"test_sim{args.similarity}_blend{args.blend}.mp4"
    output_video = output_dir / output_name

    print("=" * 60)
    print("Chromakey Parameter Test")
    print("=" * 60)
    print(f"Input video: {input_video.name}")
    print(f"Background: {background_image.name}")
    print(f"Similarity: {args.similarity}")
    print(f"Blend: {args.blend}")
    print(f"Output: {output_video}")
    print("=" * 60)
    print()

    # 処理実行
    success = remove_greenback(
        input_video,
        background_image,
        output_video,
        similarity=args.similarity,
        blend=args.blend
    )

    if success:
        print()
        print("=" * 60)
        print("Test completed successfully!")
        print(f"Output file: {output_video}")
        print("=" * 60)
        print()
        print("パラメータ調整のヒント:")
        print("- similarity を上げる → より広範囲の緑を透過（人物の縁に緑が残る場合）")
        print("- similarity を下げる → より厳密な緑のみ透過（背景が残る場合）")
        print("- blend を上げる → エッジを滑らかに（人物の輪郭をソフトに）")
        print("- blend を下げる → エッジをシャープに（人物の輪郭をくっきり）")
    else:
        print()
        print("Test failed. Please check the error message above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
