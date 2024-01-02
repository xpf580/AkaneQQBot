from __future__ import annotations

QUOTATION = {"'", '"'}
CRLF = {"\n", "\r"}


def split_once(text: str, separates: tuple[str, ...], crlf: bool = True):
    """尊重引号与转义的字符串切分, 只切割一次

    Args:
        text (str): 要切割的字符串
        separates (tuple[str, ...]): 切割符.
        crlf (bool): 是否去除 \n 与 \r，默认为 True
    Returns:
        Tuple[str, str]: 切割后的字符串, 可能含有空格
    """
    index, out_text, quotation, escape, sep = 0, "", "", False, False
    text = text.lstrip()
    for char in text:
        index += 1
        if (char in separates or (crlf and char in CRLF)) and not quotation:
            sep = True
            continue
        if sep:
            index -= 1
            break
        if char == "\\":
            escape = True
            out_text += char
        elif char in QUOTATION:  # 遇到引号括起来的部分跳过分隔
            if not quotation:
                quotation = char
            elif char == quotation:
                quotation = ""
            else:
                out_text += char
                continue
            if escape:
                out_text = out_text[:-1] + char
        else:
            out_text += char
            escape = False
    if quotation:
        raise SyntaxError(f"Unterminated string: {text!r}")
    return out_text, text[index:]


def split(text: str, separates: tuple[str, ...], crlf: bool = True):
    """尊重引号与转义的字符串切分

    Args:
        text (str): 要切割的字符串
        separates (tuple[str, ...]): 切割符. 默认为 " ".
        crlf (bool): 是否去除 \n 与 \r，默认为 True

    Returns:
        List[str]: 切割后的字符串, 可能含有空格
    """
    result, quotation, escape = "", "", False
    for char in text:
        if char == "\\":
            escape = True
            result += char
        elif char in QUOTATION:
            if not quotation:
                quotation = char
            elif char == quotation:
                quotation = ""
            else:
                result += char
                continue
            if escape:
                result = result[:-1] + char
        elif (not quotation and char in separates) or (crlf and char in CRLF):
            if result and result[-1] != "\0":
                result += "\0"
        else:
            result += char
            escape = False
    if quotation:
        raise SyntaxError(f"Unterminated string: {text!r}")
    return result.split('\0') if result else []
