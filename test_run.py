#!/usr/bin/env python3
"""
グリーンバック動画背景置換 - テストスクリプト

1つの動画でパラメータをテストします

使用方法:
    # デフォルトパラメータでテスト
    uv run python test_run.py

    # 背景画像を指定してテスト
    uv run python test_run.py --bg 1

    # パラメータを調整してテスト
    uv run python test_run.py --lower 30 60 60 --upper 90 255 255

    # 特定の動画でテスト
    uv run python test_run.py --video your_video.mp4
"""

import sys
from pathlib import Path
import argparse
from run import (
    get_script_dir,
    setup_directories,
    get_background_images,
    select_background,
    get_video_files,
    change_background
)


def main():
    parser = argparse.ArgumentParser(
        description='グリーンバック除去テストツール（1動画でテスト）',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--bg',
        type=int,
        help='使用する背景画像の番号（1または2）'
    )

    parser.add_argument(
        '--video',
        type=str,
        help='テストする動画ファイル名（green/フォルダ内）'
    )

    parser.add_argument(
        '--lower',
        type=int,
        nargs=3,
        default=[35, 80, 80],
        metavar=('H', 'S', 'V'),
        help='緑色検出の下限値。デフォルト: 35 80 80'
    )

    parser.add_argument(
        '--upper',
        type=int,
        nargs=3,
        default=[85, 255, 255],
        metavar=('H', 'S', 'V'),
        help='緑色検出の上限値。デフォルト: 85 255 255'
    )

    args = parser.parse_args()

    # ディレクトリセットアップ
    base_dir = get_script_dir()
    bg_dir, green_dir, output_dir, ready = setup_directories(base_dir)

    if not ready:
        sys.exit(1)

    # テスト出力ディレクトリ
    test_output_dir = base_dir / "test_output"
    test_output_dir.mkdir(exist_ok=True)

    # 背景画像選択
    bg_images = get_background_images(bg_dir)
    bg_image = select_background(bg_images, args.bg)

    # 動画ファイル取得
    video_files = get_video_files(green_dir)

    if not video_files:
        print("\nエラー: green/ フォルダに動画ファイルが見つかりません")
        sys.exit(1)

    # テストする動画を選択
    if args.video:
        # 指定された動画を検索
        test_video = None
        for vf in video_files:
            if vf.name == args.video:
                test_video = vf
                break

        if not test_video:
            print(f"\nエラー: {args.video} が見つかりません")
            print("\ngreen/ フォルダ内の動画:")
            for vf in video_files:
                print(f"  - {vf.name}")
            sys.exit(1)
    else:
        # 最初の動画を使用
        test_video = video_files[0]

    # パラメータ
    lower_green = tuple(args.lower)
    upper_green = tuple(args.upper)

    # 出力ファイル名
    param_str = f"L{lower_green[0]}_{lower_green[1]}_{lower_green[2]}_U{upper_green[0]}_{upper_green[1]}_{upper_green[2]}"
    output_name = f"test_{test_video.stem}_{param_str}.mp4"
    output_path = test_output_dir / output_name

    # テスト実行
    print("=" * 60)
    print("パラメータテスト")
    print("=" * 60)
    print(f"テスト動画: {test_video.name}")
    print(f"背景画像: {bg_image.name}")
    print(f"Lower HSV: {lower_green}")
    print(f"Upper HSV: {upper_green}")
    print(f"出力: {output_path}")
    print("=" * 60 + "\n")

    success = change_background(
        test_video,
        bg_image,
        output_path,
        lower_green=lower_green,
        upper_green=upper_green
    )

    if success:
        print("\n" + "=" * 60)
        print("テスト完了！")
        print(f"出力ファイル: {output_path}")
        print("=" * 60)
        print("\nパラメータ調整のヒント:")
        print("【緑色が背景に残る場合】")
        print("  → 緑色検出の範囲を広げる")
        print("  例: --lower 30 60 60 --upper 90 255 255")
        print("\n【人物の一部が消える場合】")
        print("  → 緑色検出の範囲を狭める")
        print("  例: --lower 40 100 100 --upper 80 255 255")
        print("\n【明るい緑だけ抜きたい場合】")
        print("  → V（明度）の下限を上げる")
        print("  例: --lower 35 80 120 --upper 85 255 255")
        print("\n【暗い緑も含めて抜きたい場合】")
        print("  → V（明度）の下限を下げる")
        print("  例: --lower 35 80 40 --upper 85 255 255")
    else:
        print("\nテスト失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()
