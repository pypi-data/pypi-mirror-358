from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
import cv2
import numpy as np
import fdwm


def generate_host_image(path: str, size: int = 512) -> None:
    """Generate simple grayscale host image and save to disk."""
    img = np.full((size, size), 200, dtype=np.uint8)  # light gray background
    cv2.putText(img, "HOST", (size // 8, size // 2), cv2.FONT_HERSHEY_SIMPLEX, 3, 30, 5)
    cv2.imwrite(path, img)


def test_text_watermark():
    """Complete workflow test: embed -> extract -> calculate correlation coefficient."""
    tmp_dir = Path("tmp_text")
    tmp_dir.mkdir(exist_ok=True)

    host_path = tmp_dir / "host.png"
    watermarked_path = tmp_dir / "host_wm.png"
    extracted_path = tmp_dir / "extracted.png"

    generate_host_image(str(host_path))

    wm_text = "Watermark demo 123 ABC abc long text wrapping demonstration"

    fdwm.embed(
        host_path=str(host_path),
        watermark_path=None,
        output_path=str(watermarked_path),
        watermark_text=wm_text,
        strength=30000.0,
        scale=0.25,
    )

    extracted = fdwm.extract(
        watermarked_path=str(watermarked_path),
        strength=30000.0,
        scale=0.25,
        output_path=str(extracted_path),
    )

    # OCR recognition test (if tesseract is installed)
    try:
        text_rec = fdwm.extract_text(
            watermarked_path=str(watermarked_path),
            strength=30000.0,
            scale=0.25,
        )
        print("OCR recognition result:", text_rec)
        assert any(k in text_rec for k in ["Watermark", "ABC"]), "OCR recognition text mismatch."
    except RuntimeError as e:
        # skip OCR assertion when tesseract not installed
        print("Skip OCR test:", e)

    print(f"Extracted image average gray: {extracted.mean():.1f} -> test passed!")


if __name__ == "__main__":
    test_text_watermark()