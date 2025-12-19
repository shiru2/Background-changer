#!/usr/bin/env python3
"""
OpenCVを使ってグリーンバック動画の背景を01.pngに置き換えるスクリプト
HSV色空間で緑色を検出し、人物を残して背景だけを置き換えます。

使用方法:
    uv run python remove_greenback_cv.py

処理内容:
    - output_10fps_1080p/ 内の全動画を検出
    - 緑色背景を01.pngに置き換え（人物は残す）
    - output_with_background/ に出力
"""

import cv2
import numpy as np
from pathlib import Path
import sys


def get_script_dir():
    """スクリプトのディレクトリを取得（相対パスの基準）"""
    return Path(__file__).parent.absolute()


def change_background(video_path, bg_image_path, output_path,
                      lower_green=(35, 80, 80), upper_green=(85, 255, 255)):
    """
    グリーンバック動画の背景を画像に置き換える
    人物を残したまま、緑色の背景部分だけを01.pngに置き換える

    Args:
        video_path: 入力動画パス
        bg_image_path: 背景画像パス
        output_path: 出力動画パス
        lower_green: 緑色検出の下限値 (H, S, V)
        upper_green: 緑色検出の上限値 (H, S, V)

    Returns:
        bool: 成功したらTrue、失敗したらFalse
    """
    try:
        print(f"Processing: {video_path.name}")

        # 1. 動画と背景画像の読み込み
        cap = cv2.VideoCapture(str(video_path))
        bg_img_origin = cv2.imread(str(bg_image_path))

        # 動画が正しく開けたか確認
        if not cap.isOpened():
            print(f"✗ Error: 動画ファイルが開けません: {video_path}")
            return False

        if bg_img_origin is None:
            print(f"✗ Error: 背景画像が開けません: {bg_image_path}")
            return False

        # 2. 動画の情報を取得（幅、高さ、FPS）
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 3. 背景画像を動画のサイズに合わせてリサイズ
        bg_img = cv2.resize(bg_img_origin, (width, height))

        # 4. 保存用の設定 (mp4形式、H.264コーデック)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        if not out.isOpened():
            print(f"✗ Error: 出力ファイルが作成できません: {output_path}")
            cap.release()
            return False

        # 5. フレームごとに処理
        frame_count = 0
        lower_green_array = np.array(lower_green)
        upper_green_array = np.array(upper_green)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 進捗表示（10フレームごと）
            if frame_count % 10 == 0 or frame_count == 1:
                progress = (frame_count / total_frames) * 100
                print(f"  Progress: {frame_count}/{total_frames} frames ({progress:.1f}%)", end='\r')

            # --- ここから画像処理 ---

            # 6. 画像をHSV色空間に変換
            # (RGBよりHSVの方が「特定の色」を抜き出しやすいため)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 7. 指定した緑色の範囲だけを「白」、それ以外を「黒」にしたマスク画像を作成
            mask = cv2.inRange(hsv, lower_green_array, upper_green_array)

            # 8. マスクを反転（人物部分を白にする）
            mask_inv = cv2.bitwise_not(mask)

            # 9. 合成処理
            # 背景画像から、マスクが「白（元が緑）」の部分だけを切り抜く
            bg_part = cv2.bitwise_and(bg_img, bg_img, mask=mask)

            # 元動画から、マスクが「黒（人物）」の部分だけを切り抜く
            fg_part = cv2.bitwise_and(frame, frame, mask=mask_inv)

            # 2つを足し合わせる（人物 + 新しい背景）
            final_frame = cv2.add(bg_part, fg_part)

            # --- ここまで画像処理 ---

            # 書き出し
            out.write(final_frame)

        # 終了処理
        cap.release()
        out.release()

        print(f"\n✓ Completed: {output_path.name}")
        return True

    except Exception as e:
        print(f"\n✗ Error processing {video_path.name}: {e}")
        return False


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
    print("\nHSV Green Detection Parameters:")
    print("  Lower: (H:35, S:80, V:80)")
    print("  Upper: (H:85, S:255, V:255)")
    print("-" * 60)

    # 処理
    success_count = 0
    failed_count = 0

    # 緑色検出のパラメータ（調整可能）
    # H（色相）: 0-179, S（彩度）: 0-255, V（明度）: 0-255
    lower_green = (35, 80, 80)      # 緑色の下限
    upper_green = (85, 255, 255)    # 緑色の上限

    for video_file in video_files:
        # 出力ファイル名（_greenscreenを_with_bgに置き換え）
        output_name = video_file.stem.replace('_greenscreen', '_with_bg') + '.mp4'
        output_path = output_dir / output_name

        if change_background(video_file, background_image, output_path,
                           lower_green, upper_green):
            success_count += 1
        else:
            failed_count += 1

    # 結果表示
    print("-" * 60)
    print(f"\nProcessing completed!")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Output directory: {output_dir}")
    print("\nパラメータ調整のヒント:")
    print("  緑が残る場合 → lower_green の値を下げる、upper_green を上げる")
    print("  人物が消える場合 → lower_green の値を上げる、upper_green を下げる")


if __name__ == "__main__":
    main()
