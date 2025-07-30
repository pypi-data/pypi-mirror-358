import argparse
from . import LM, load, extract

def main():
    p = argparse.ArgumentParser(prog="pdf2seg", description="PDF to OCR-based segment extractor")
    p.add_argument("-i", "--input", required=True, help="Input PDF file")
    p.add_argument("-o", "--output", required=True, help="Output directory")
    p.add_argument("-m", "--model", default=LM, help=f"spaCy model (default: {LM})")
    args = p.parse_args()
    nlp = load(args.model)
    extract(args.input, args.output, nlp)

if __name__ == "__main__":
    main()