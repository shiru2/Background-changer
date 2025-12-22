#!/usr/bin/env python3
"""
グリーンバック動画背景置換ツール - メインスクリプト

使用方法:
    # 背景画像を選択して実行
    uv run python run.py

    # 背景画像を指定して実行（bg/の中の1番目または2番目）
    uv run python run.py --bg 1
    uv run python run.py --bg 2

    # パラメータを調整して実行
    uv run python run.py --lower 30 60 60 --upper 90 255 255

ディレクトリ構造:
    bg/          背景画像（2枚まで対応）
    green/       グリーンバック動画
    output/      出力先（自動作成）
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


def get_script_dir():
    """スクリプトのディレクトリを取得"""
    return Path(__file__).parent.absolute()


def setup_directories(base_dir):
    """
    必要なディレクトリをセットアップ

    Returns:
        tuple: (bg_dir, green_dir, output_dir, success)
    """
    bg_dir = base_dir / "bg"
    green_dir = base_dir / "green"
    output_dir = base_dir / "output"

    # 出力ディレクトリは自動作成
    output_dir.mkdir(exist_ok=True)

    # bg/とgreen/のチェック
    missing_dirs = []

    if not bg_dir.exists():
        bg_dir.mkdir(exist_ok=True)
        missing_dirs.append("bg")

    if not green_dir.exists():
        green_dir.mkdir(exist_ok=True)
        missing_dirs.append("green")

    if missing_dirs:
        print("=" * 60)
        print("初期セットアップ")
        print("=" * 60)
        print(f"\n以下のフォルダを作成しました：")
        for d in missing_dirs:
            print(f"  - {d}/")

        print("\n次の手順を実行してください：")
        if "bg" in missing_dirs:
            print(f"  1. bg/ フォルダに背景画像（PNG/JPG）を配置")
        if "green" in missing_dirs:
            print(f"  2. green/ フォルダにグリーンバック動画を配置")
        print(f"  3. このスクリプトを再実行")
        print("=" * 60)
        return bg_dir, green_dir, output_dir, False

    return bg_dir, green_dir, output_dir, True


def get_background_images(bg_dir):
    """
    bg/フォルダから背景画像を取得

    Returns:
        list: 背景画像のパスリスト
    """
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]
    bg_images = []

    for ext in extensions:
        bg_images.extend(bg_dir.glob(ext))

    return sorted(bg_images)


def select_background(bg_images, bg_index=None):
    """
    背景画像を選択

    Args:
        bg_images: 背景画像のリスト
        bg_index: 指定された背景画像のインデックス（1-based）

    Returns:
        Path: 選択された背景画像のパス
    """
    if not bg_images:
        print("エラー: bg/ フォルダに画像ファイルが見つかりません")
        print("対応形式: PNG, JPG, JPEG")
        sys.exit(1)

    if len(bg_images) == 1:
        print(f"背景画像: {bg_images[0].name}")
        return bg_images[0]

    # 複数ある場合
    if bg_index is not None:
        if 1 <= bg_index <= len(bg_images):
            print(f"背景画像: {bg_images[bg_index - 1].name}")
            return bg_images[bg_index - 1]
        else:
            print(f"エラー: --bg {bg_index} は無効です（1-{len(bg_images)}を指定）")
            sys.exit(1)

    # インタラクティブに選択
    print("\n背景画像を選択してください：")
    for i, img in enumerate(bg_images, 1):
        print(f"  {i}. {img.name}")

    while True:
        try:
            choice = input(f"\n番号を入力 (1-{len(bg_images)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(bg_images):
                print(f"選択: {bg_images[idx].name}")
                return bg_images[idx]
            else:
                print(f"1-{len(bg_images)}の範囲で入力してください")
        except (ValueError, KeyboardInterrupt):
            print("\nキャンセルされました")
            sys.exit(0)


def get_video_files(green_dir):
    """
    green/フォルダから動画ファイルを取得

    Returns:
        list: 動画ファイルのパスリスト
    """
    extensions = [
        "*.mp4",
        "*.mov",
        "*.avi",
        "*.mkv",
        "*.MP4",
        "*.MOV",
        "*.AVI",
        "*.MKV",
    ]
    video_files = []

    for ext in extensions:
        video_files.extend(green_dir.glob(ext))

    return sorted(video_files)


def adjust_brightness(person_img, person_mask, bg_img, bg_mask):
    """
    人物の輝度を背景に合わせて調整

    Args:
        person_img: 人物画像（BGR）
        person_mask: 人物のマスク
        bg_img: 背景画像（BGR）
        bg_mask: 背景のマスク

    Returns:
        調整後の人物画像
    """
    # BGR → HSV変換
    person_hsv = cv2.cvtColor(person_img, cv2.COLOR_BGR2HSV).astype(np.float32)
    bg_hsv = cv2.cvtColor(bg_img, cv2.COLOR_BGR2HSV).astype(np.float32)

    # 人物領域と背景領域の平均HSV値を計算
    person_mean = cv2.mean(person_img, mask=person_mask)[:3]
    bg_mean = cv2.mean(bg_img, mask=bg_mask)[:3]

    # HSVで平均を計算
    person_hsv_mean = cv2.mean(person_hsv, mask=person_mask)
    bg_hsv_mean = cv2.mean(bg_hsv, mask=bg_mask)

    # V（明度）の調整比率を計算
    if person_hsv_mean[2] > 0:
        brightness_ratio = bg_hsv_mean[2] / person_hsv_mean[2]
    else:
        brightness_ratio = 1.0

    # 人物のV値を調整（0-255の範囲を維持）
    person_hsv[:, :, 2] = np.clip(person_hsv[:, :, 2] * brightness_ratio, 0, 255)

    # S（彩度）も軽く調整（色温度のマッチング）
    if person_hsv_mean[1] > 0:
        saturation_ratio = bg_hsv_mean[1] / person_hsv_mean[1]
        # 彩度は控えめに調整（0.7倍の影響）
        saturation_ratio = 1.0 + (saturation_ratio - 1.0) * 0.3
        person_hsv[:, :, 1] = np.clip(person_hsv[:, :, 1] * saturation_ratio, 0, 255)

    # HSV → BGR変換
    adjusted = cv2.cvtColor(person_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return adjusted


def change_background(
    video_path,
    bg_image_path,
    output_path,
    lower_green=(35, 80, 80),
    upper_green=(85, 255, 255),
    scale=0.7,
    y_position=0.2,
    brightness_match=True,
):
    """
    グリーンバック動画の背景を画像に置き換える

    Args:
        video_path: 入力動画パス
        bg_image_path: 背景画像パス
        output_path: 出力動画パス
        lower_green: 緑色検出の下限値 (H, S, V)
        upper_green: 緑色検出の上限値 (H, S, V)
        scale: 人物のサイズ倍率（デフォルト0.7）
        y_position: 人物の縦位置（0.0=上端, 1.0=下端, デフォルト0.2）
        brightness_match: 輝度マッチングを有効化（デフォルトTrue）

    Returns:
        bool: 成功したらTrue
    """
    try:
        print(f"Processing: {video_path.name}")

        cap = cv2.VideoCapture(str(video_path))
        bg_img_origin = cv2.imread(str(bg_image_path))

        if not cap.isOpened():
            print(f"  ✗ Error: 動画ファイルが開けません")
            return False

        if bg_img_origin is None:
            print(f"  ✗ Error: 背景画像が開けません")
            return False

        # 動画情報取得
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 背景画像をリサイズ
        bg_img = cv2.resize(bg_img_origin, (width, height))

        # スケール後のサイズを計算
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)

        # 配置位置を計算（中央揃え、Y位置は指定値）
        x_offset = (width - scaled_width) // 2
        y_offset = int((height - scaled_height) * y_position)

        # 出力設定
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        if not out.isOpened():
            print(f"  ✗ Error: 出力ファイルが作成できません")
            cap.release()
            return False

        # フレーム処理
        frame_count = 0
        lower_green_array = np.array(lower_green)
        upper_green_array = np.array(upper_green)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 進捗表示
            if frame_count % 10 == 0 or frame_count == 1:
                progress = (frame_count / total_frames) * 100
                print(
                    f"  Progress: {frame_count}/{total_frames} frames ({progress:.1f}%)",
                    end="\r",
                )

            # HSV変換
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # 緑色検出マスク
            mask = cv2.inRange(hsv, lower_green_array, upper_green_array)
            mask_inv = cv2.bitwise_not(mask)

            # 人物部分を抽出
            person = cv2.bitwise_and(frame, frame, mask=mask_inv)

            # 人物をスケール
            person_scaled = cv2.resize(person, (scaled_width, scaled_height))
            mask_inv_scaled = cv2.resize(mask_inv, (scaled_width, scaled_height))

            # 輝度マッチング
            if brightness_match:
                # 背景のマスクを作成（人物が配置される領域以外）
                bg_mask = np.ones((height, width), dtype=np.uint8) * 255
                bg_mask[
                    y_offset : y_offset + scaled_height,
                    x_offset : x_offset + scaled_width,
                ] = 0

                person_scaled = adjust_brightness(
                    person_scaled, mask_inv_scaled, bg_img, bg_mask
                )

            # 背景画像をコピー
            final_frame = bg_img.copy()

            # 人物を配置する領域を抽出
            roi = final_frame[
                y_offset : y_offset + scaled_height, x_offset : x_offset + scaled_width
            ]

            # マスクを3チャンネルに変換
            mask_inv_scaled_3ch = cv2.cvtColor(mask_inv_scaled, cv2.COLOR_GRAY2BGR)

            # 人物部分を合成（アルファブレンディング風に）
            # マスクで人物以外を黒くする
            person_area = cv2.bitwise_and(person_scaled, mask_inv_scaled_3ch)

            # ROIから人物領域を除去
            mask_scaled = cv2.bitwise_not(mask_inv_scaled)
            mask_scaled_3ch = cv2.cvtColor(mask_scaled, cv2.COLOR_GRAY2BGR)
            bg_area = cv2.bitwise_and(roi, mask_scaled_3ch)

            # 合成
            combined = cv2.add(person_area, bg_area)
            final_frame[
                y_offset : y_offset + scaled_height, x_offset : x_offset + scaled_width
            ] = combined

            out.write(final_frame)

        cap.release()
        out.release()

        print(f"\n  ✓ Completed: {output_path.name}")
        return True

    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="グリーンバック動画背景置換ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  uv run python run.py                              # 背景画像を選択して実行
  uv run python run.py --bg 1                       # 1番目の背景画像を使用
  uv run python run.py --scale 0.5 --y-position 0.1 # 人物を小さく上部に配置
  uv run python run.py --no-brightness-match        # 輝度マッチング無効
  uv run python run.py --lower 30 60 60             # パラメータを調整
        """,
    )

    parser.add_argument("--bg", type=int, help="使用する背景画像の番号（1または2）")

    parser.add_argument(
        "--lower",
        type=int,
        nargs=3,
        default=[35, 80, 80],
        metavar=("H", "S", "V"),
        help="緑色検出の下限値 (H:0-179, S:0-255, V:0-255)",
    )

    parser.add_argument(
        "--upper",
        type=int,
        nargs=3,
        default=[85, 255, 255],
        metavar=("H", "S", "V"),
        help="緑色検出の上限値 (H:0-179, S:0-255, V:0-255)",
    )

    parser.add_argument(
        "--scale", type=float, default=0.7, help="人物のサイズ倍率（デフォルト: 0.7）"
    )

    parser.add_argument(
        "--y-position",
        type=float,
        default=0.2,
        help="人物の縦位置 0.0=上端, 1.0=下端（デフォルト: 0.2）",
    )

    parser.add_argument(
        "--no-brightness-match", action="store_true", help="輝度マッチングを無効化"
    )

    args = parser.parse_args()

    # ディレクトリセットアップ
    base_dir = get_script_dir()
    bg_dir, green_dir, output_dir, ready = setup_directories(base_dir)

    if not ready:
        sys.exit(1)

    # 背景画像選択
    bg_images = get_background_images(bg_dir)
    bg_image = select_background(bg_images, args.bg)

    # 動画ファイル取得
    video_files = get_video_files(green_dir)

    if not video_files:
        print("\nエラー: green/ フォルダに動画ファイルが見つかりません")
        print("対応形式: MP4, MOV, AVI, MKV")
        sys.exit(1)

    # 処理開始
    print("\n" + "=" * 60)
    print(f"背景画像: {bg_image.name}")
    print(f"動画数: {len(video_files)}")
    print(f"HSV範囲: Lower{tuple(args.lower)} Upper{tuple(args.upper)}")
    print(f"人物スケール: {args.scale}")
    print(f"Y位置: {args.y_position}")
    print(f"輝度マッチング: {'OFF' if args.no_brightness_match else 'ON'}")
    print(f"出力先: {output_dir}")
    print("=" * 60 + "\n")

    # パラメータ
    lower_green = tuple(args.lower)
    upper_green = tuple(args.upper)
    brightness_match = not args.no_brightness_match

    # 処理
    success_count = 0
    failed_count = 0

    for video_file in video_files:
        output_name = video_file.stem + "_output.mp4"
        output_path = output_dir / output_name

        if change_background(
            video_file,
            bg_image,
            output_path,
            lower_green,
            upper_green,
            args.scale,
            args.y_position,
            brightness_match,
        ):
            success_count += 1
        else:
            failed_count += 1

    # 結果
    print("\n" + "=" * 60)
    print("処理完了！")
    print(f"成功: {success_count}")
    print(f"失敗: {failed_count}")
    print(f"出力先: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
