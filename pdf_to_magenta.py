#!/usr/bin/env python3import sys
import os
import argparse
import io

import fitz  # PyMuPDF
from PIL import Image, ImageFilter, ImageChops


MAGENTA = (0xFF, 0x00, 0xFF)  # FF00FF
WHITE = (0xFF, 0xFF, 0xFF)


def convert_page_to_magenta(pix, threshold: int, outline_only: bool, border_px: int) -> Image.Image:
    """
    fitz Pixmap -> PIL Image -> shudhu Magenta o White color e convert kore

    outline_only=True hole: boro/thick filled color-r jayga gulo ke pura
    magenta diye bhorat na kore, khali oigulor CHARIDIKE ekta magenta border
    likhe dey (mane fill khali kore, shudhu border rakhe) - fole print
    korar somoy ink onek kom lagbe. Kintu patla line ba text (jeta already
    thin/hollow) oi rokom e thakbe, karon segulo eroded hoye 0 hoye jay.
    """
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # Grayscale banaye brightness ber kora
    gray = img.convert("L")

    # ink_mask: 255 = "ei jaygay kichu ache" (mane light/white na), 0 = white/blank
    ink_mask = gray.point(lambda p: 255 if p < threshold else 0)

    if outline_only and border_px > 0:
        # Erosion: boro filled block gulo k charidik theke shrink kore dey.
        # Patla line/text (border_px er thekeo chikon) shrink hote hote
        # shomponno 0 hoye jay - fole segulo pore abar "ink - eroded" e
        # nijer purota ferot pay (unaffected thake).
        kernel_size = max(3, border_px * 2 + 1)
        if kernel_size % 2 == 0:
            kernel_size += 1
        eroded = ink_mask.filter(ImageFilter.MinFilter(kernel_size))
        # border/ring = ink_mask theke eroded (interior) baad
        final_mask = ImageChops.subtract(ink_mask, eroded)
    else:
        final_mask = ink_mask

    # notun blank canvas - shuru te shob white diye fill kori
    out = Image.new("RGB", img.size, WHITE)
    magenta_layer = Image.new("RGB", img.size, MAGENTA)
    out.paste(magenta_layer, mask=final_mask)

    return out


def pdf_to_magenta(
    input_path: str,
    output_path: str,
    dpi: int = 300,
    threshold: int = 200,
    outline_only: bool = True,
    border_px: int = 3,
):
    src = fitz.open(input_path)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    converted_images = []

    print(f"Total {len(src)} page(s) pawa gelo. Processing shuru hocche (dpi={dpi}, outline_only={outline_only})...")

    for i, page in enumerate(src, start=1):
        pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
        magenta_img = convert_page_to_magenta(
            pix, threshold=threshold, outline_only=outline_only, border_px=border_px
        )
        converted_images.append(magenta_img)
        print(f"  Page {i}/{len(src)} done.")

    src.close()

    # Shob image ke ekta multi-page PDF e save kora
    first, rest = converted_images[0], converted_images[1:]
    first.save(
        output_path,
        "PDF",
        resolution=dpi,
        save_all=True,
        append_images=rest,
    )

    print(f"\nDone! Magenta+White PDF save hoyeche: {output_path}")


def find_batch_pdfs(folder: str):
    """
    Script jei folder e ache, oi folder er shob .pdf file khuje ber kore.
    Age theke banano "_magenta.pdf" output file gulo baad diye dey, jate
    barbar run korle purono output ke abar input hishebe convert na kore.
    """
    pdfs = []
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith(".pdf"):
            continue
        if name.lower().endswith("_magenta.pdf"):
            continue
        pdfs.append(os.path.join(folder, name))
    return pdfs


def main():
    parser = argparse.ArgumentParser(description="Convert any-color PDF to Magenta(FF00FF)+White only PDF")
    parser.add_argument("input", nargs="?", default=None, help="Input PDF file path (optional - na dile batch mode e script-er folder er shob PDF convert hobe)")
    parser.add_argument("output", nargs="?", default=None, help="Output PDF file path (optional - shudhu single-file mode e lagbe)")
    parser.add_argument("--dpi", type=int, default=300, help="Output resolution (default 300, print quality-r jonno bhalo)")
    parser.add_argument(
        "--threshold",
        type=int,
        default=200,
        help=(
            "0-255 er moddhe. Ekhane theke beshi brightness hole oi pixel white hobe, "
            "kom hole magenta hobe. Default 200. Jodi lekha/light color gulo magenta "
            "na hoye white thake jachche, tahole threshold aro kom(e.g. 150) diye try korun. "
            "Jodi onek beshi jinis magenta hoye jachche (background o magenta hoye jachche), "
            "tahole threshold aro beshi (e.g. 230) diye try korun."
        ),
    )
    parser.add_argument(
        "--no-outline",
        action="store_true",
        help="Ei flag dile boro filled color area gulo pura magenta diye bhorat kore dibe (outline banabe na). Default e outline mode ON thake, ink bachanor jonno.",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=3,
        help="Outline mode e border koto pixel(ish) thick hobe (default 3). Beshi dile border mota hobe, kom dile patla.",
    )
    args = parser.parse_args()

    if args.input is None:
        # ---- BATCH MODE ----
        # script nijer folder e thaka shob PDF khuje ber kore convert kore
        script_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_files = find_batch_pdfs(script_dir)

        if not pdf_files:
            print(f"Kono input PDF pawa jayni ei folder e: {script_dir}")
            print("Apnar PDF file(gulo) ei script-er sathe SAME folder e rakhun, tarpor abar run korun.")
            return

        print(f"Total {len(pdf_files)} ta PDF file pawa gelo. Batch conversion shuru hocche...\n")

        for idx, input_path in enumerate(pdf_files, start=1):
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_magenta{ext}"
            print(f"[{idx}/{len(pdf_files)}] {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            pdf_to_magenta(
                input_path,
                output_path,
                dpi=args.dpi,
                threshold=args.threshold,
                outline_only=not args.no_outline,
                border_px=args.border,
            )
            print()

        print("Shob file convert hoye geche!")
    else:
        # ---- SINGLE FILE MODE (purono niyom) ----
        if args.output is None:
            print("Single file mode e output file er nam o dite hobe. Jemon:")
            print(f"    python3 pdf_to_magenta.py {args.input} output.pdf")
            return
        pdf_to_magenta(
            args.input,
            args.output,
            dpi=args.dpi,
            threshold=args.threshold,
            outline_only=not args.no_outline,
            border_px=args.border,
        )


if __name__ == "__main__":
    main()