def extract_json_from_markdown(markdownStr: str) -> str:
    return markdownStr[7:-3].replace('\n', "")