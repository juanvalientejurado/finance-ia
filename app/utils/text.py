def normalize_ocr_output(ocr_output: str | list[str]) -> str:
    if isinstance(ocr_output, list):
        return "\n".join(ocr_output)
    return ocr_output
