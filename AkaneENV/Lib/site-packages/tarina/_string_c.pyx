# cython: boundscheck=False
# cython: cdivision=True
# cython: initializedcheck=False

from cpython.list cimport PyList_Append, PyList_SET_ITEM
from cpython.object cimport Py_SIZE, PyObject
from cpython.unicode cimport PyUnicode_GET_LENGTH, PyUnicode_Join, PyUnicode_Split


cdef extern from "Python.h":
    Py_UCS4 PyUnicode_READ_CHAR(object s, Py_ssize_t i)

cdef extern from "_op.h":
    bint contains(object chs, Py_UCS4 ch)
    bint set_contains_key(object anyset, object key) except -1

cdef set QUOTES = {'"', '\''}
cdef set CRLF = {'\r', '\n'}

def split(str text, tuple separates, char crlf=True):
    """尊重引号与转义的字符串切分

    Args:
        text (str): 要切割的字符串
        separates (tuple[str, ...]): 切割符. 默认为 " ".
        crlf (bool): 是否去除 \n 与 \r，默认为 True

    Returns:
        List[str]: 切割后的字符串, 可能含有空格
    """
    cdef char escape = 0
    cdef list result = []
    cdef Py_UCS4 quotation = 0
    cdef Py_UCS4 ch = 0
    cdef Py_ssize_t i = 0
    cdef Py_ssize_t length = PyUnicode_GET_LENGTH(text)

    while i < length:
        ch = PyUnicode_READ_CHAR(text, i)
        i += 1
        if ch == 92:  # \\
            escape = 1
            PyList_Append(result, ch)
        elif set_contains_key(QUOTES, ch):
            if quotation == 0:
                quotation = ch
            elif ch == quotation:
                quotation = 0
            else:
                PyList_Append(result, ch)
                continue
            if escape:
                PyList_SET_ITEM(result, Py_SIZE(result)-1 , ch)
        elif (quotation == 0 and contains(separates, ch)) or (crlf and set_contains_key(CRLF, ch)):
            if result and result[-1] != '\1':
                PyList_Append(result, '\1')
        else:
            PyList_Append(result, ch)
            escape = 0
    if quotation != 0:
        raise SyntaxError(f"Unterminated string: {text!r}")
    if PyUnicode_GET_LENGTH(result) == 0:
        return []
    return PyUnicode_Split(PyUnicode_Join('', result), '\1', -1)


def split_once(str text, tuple separates, char crlf=True):
    text = text.lstrip()
    cdef Py_ssize_t index = 0
    cdef list out_text = []
    cdef Py_UCS4 quotation = 0
    cdef Py_UCS4 ch = 0
    cdef char escape = 0
    cdef char sep = 0
    cdef Py_ssize_t length = PyUnicode_GET_LENGTH(text)

    while index < length:
        ch = PyUnicode_READ_CHAR(text, index)
        index += 1
        if quotation == 0 and (contains(separates, ch) or (crlf and set_contains_key(CRLF, ch))):
            sep = 1
            continue
        if sep == 1:
            index -= 1
            break
        if ch == 92:  # \\
            escape = 1
            PyList_Append(out_text, ch)
        elif set_contains_key(QUOTES, ch):  # 遇到引号括起来的部分跳过分隔
            if quotation == 0:
                quotation = ch
            elif ch == quotation:
                quotation = 0
            else:
                PyList_Append(out_text, ch)
                continue
            if escape:
                PyList_SET_ITEM(out_text, Py_SIZE(out_text) - 1, ch)
        else:
            PyList_Append(out_text, ch)
            escape = 0
    if quotation != 0:
        raise SyntaxError(f"Unterminated string: {text!r}")
    return PyUnicode_Join('', out_text), text[index:]