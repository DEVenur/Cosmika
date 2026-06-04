import zipfile
from pathlib import Path

import requests


def check_font_exists():
    """Check if Noto CJK font already exists."""
    fonts_dir = Path("assets") / "fonts"

    zip_file = fonts_dir / "03_NotoSansCJK-OTC.zip"

    # Check for zip file first
    if zip_file.exists():
        print(f"✓ ZIP file found: {zip_file}")
        print(f"  Size: {zip_file.stat().st_size / (1024 * 1024):.1f} MB")
        return True

    # Check for extracted fonts in subdirectory
    zip_extract_dir = fonts_dir / "03_NotoSansCJK-OTC"
    if zip_extract_dir.exists():
        ttc_files = list(zip_extract_dir.glob("*.ttc"))
        if ttc_files:
            print(f"✓ TTC font files found in {zip_extract_dir}:")
            for ttc in ttc_files:
                print(f"  - {ttc.name} ({ttc.stat().st_size / (1024 * 1024):.1f} MB)")
            return True

    # Check for fonts in root fonts directory (backward compatibility)
    ttc_files = list(fonts_dir.glob("*.ttc"))
    if ttc_files:
        print(f"✓ TTC font files found in {fonts_dir}:")
        for ttc in ttc_files:
            print(f"  - {ttc.name} ({ttc.stat().st_size / (1024 * 1024):.1f} MB)")
        return True

    print("✗ No Noto CJK font files found")
    return False


def download_noto_font(force=False) -> bool:
    """
    Download and extract Noto CJK font to assets/fonts/ directory.

    Args:
        force (bool): If True, download even if file exists

    Returns:
        bool: True if fonts are available (already existed or downloaded), False on failure.
    """
    fonts_dir = Path("assets") / "fonts"

    fonts_dir.mkdir(parents=True, exist_ok=True)

    url = "https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/03_NotoSansCJK-OTC.zip"
    zip_filename = fonts_dir / "03_NotoSansCJK-OTC.zip"

    zip_extract_dir = fonts_dir / "03_NotoSansCJK-OTC"
    existing_ttc_fonts = []

    if zip_extract_dir.exists():
        existing_ttc_fonts = list(zip_extract_dir.glob("*.ttc"))

    if not existing_ttc_fonts:
        existing_ttc_fonts = list(fonts_dir.glob("*.ttc"))

    if not force and existing_ttc_fonts:
        print("TTC font files already exist:")
        for font in existing_ttc_fonts:
            print(f"  - {font.name} ({font.stat().st_size / (1024 * 1024):.1f} MB)")
        print("Use force=True to re-download")
        return True

    print("Downloading Noto CJK font...")
    print(f"URL: {url}")
    print(f"Destination: {zip_filename}")

    try:
        response = requests.get(
            url, stream=True, timeout=(15, 60)
        )
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0

        print(f"📦 Total size: {total_size / (1024 * 1024):.1f} MB")

        with open(zip_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0 and downloaded_size % (5 * 1024 * 1024) < 8192:
                        progress = (downloaded_size / total_size) * 100
                        print(
                            f"📥 Progress: {progress:.1f}% ({downloaded_size / (1024 * 1024):.1f} MB)"
                        )

        if total_size > 0:
            print(
                f"✅ Download complete: 100% ({downloaded_size / (1024 * 1024):.1f} MB)"
            )

        print(f"✓ Font downloaded successfully to {zip_filename}")
        print(f"✓ File size: {zip_filename.stat().st_size / (1024 * 1024):.1f} MB")

        zip_extract_dir = fonts_dir / zip_filename.stem
        zip_extract_dir.mkdir(exist_ok=True)

        print(f"Extracting font file to {zip_extract_dir}...")
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(zip_extract_dir)

        print(f"✓ Font extracted successfully to {zip_extract_dir}")

        zip_filename.unlink()
        print("✓ Zip file deleted")

        extracted_ttc_fonts = list(zip_extract_dir.glob("*.ttc"))
        if extracted_ttc_fonts:
            print("✓ Extracted TTC font files:")
            for font in extracted_ttc_fonts:
                print(f"  - {font.name} ({font.stat().st_size / (1024 * 1024):.1f} MB)")

        return True

    except requests.exceptions.Timeout as e:
        print(f"✗ Download timeout: {e}")
        print("💡 Try running again with a better internet connection")
        if zip_filename.exists():
            zip_filename.unlink()
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Error downloading font: {e}")
        if zip_filename.exists():
            zip_filename.unlink()
        return False
    except zipfile.BadZipFile as e:
        print(f"✗ Error extracting zip file: {e}")
        if zip_filename.exists():
            zip_filename.unlink()
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        if zip_filename.exists():
            zip_filename.unlink()
        return False


def extract_existing_zip():
    """Extract existing zip file if it exists."""
    fonts_dir = Path("assets") / "fonts"
    zip_filename = fonts_dir / "03_NotoSansCJK-OTC.zip"
    zip_extract_dir = fonts_dir / "03_NotoSansCJK-OTC"

    if not zip_filename.exists():
        return False

    print(f"Found existing zip file: {zip_filename}")
    print(f"Extracting to {zip_extract_dir}...")

    try:
        zip_extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(zip_extract_dir)

        print(f"✓ Font extracted successfully to {zip_extract_dir}")

        # Delete the zip file after successful extraction
        zip_filename.unlink()
        print("✓ Zip file deleted")

        # Show extracted TTC files
        extracted_ttc_fonts = list(zip_extract_dir.glob("*.ttc"))
        if extracted_ttc_fonts:
            print("✓ Extracted TTC font files:")
            for font in extracted_ttc_fonts:
                print(f"  - {font.name} ({font.stat().st_size / (1024 * 1024):.1f} MB)")
        return True

    except zipfile.BadZipFile as e:
        print(f"✗ Error: The zip file is corrupted or invalid: {e}")
        response = input(
            "\nWould you like to delete the corrupted zip and redownload? (yes/no): "
        )
        if response.lower() == "yes":
            zip_filename.unlink()
            print("✓ Corrupted zip file deleted")
            print("\nRedownloading font...")
            download_noto_font(force=True)
        else:
            print("Extraction cancelled. Please fix the issue manually.")
        return False

    except Exception as e:
        print(f"✗ Unexpected error during extraction: {e}")
        response = input(
            "\nWould you like to delete the zip file and redownload? (yes/no): "
        )
        if response.lower() == "yes":
            zip_filename.unlink()
            print("✓ Zip file deleted")
            print("\nRedownloading font...")
            download_noto_font(force=True)
        else:
            print("Extraction cancelled. Please fix the issue manually.")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_font_exists()
        elif sys.argv[1] == "force":
            download_noto_font(force=True)
        else:
            print("Usage: python download_font.py [check|force]")
    else:
        # Default behavior: check if zip exists and extract, or check fonts, or download
        fonts_dir = Path("assets") / "fonts"
        zip_filename = fonts_dir / "03_NotoSansCJK-OTC.zip"

        # First, check if zip exists and extract it
        if zip_filename.exists():
            print("Zip file found. Extracting...")
            extract_existing_zip()
        elif not check_font_exists():
            print("\nDownloading font...")
            download_noto_font()
        else:
            print("\nFont already available. Use 'force' to re-download.")
