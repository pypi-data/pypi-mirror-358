# 编写一个函数，将 false,true转为 bool。忽略大小写。支持传入 字符或者布尔。添加函数提示和注释。
# 支持 enable,disable,1,0
# 如果输入为None,第二个参数为默认值，支持设置默认值。
# 如果输入为None或者空字符,第二个参数为默认值，支持设置默认值。
# 函数注释由中文/英文 双语展示
def to_bool(value: str | bool | None, default: bool = False) -> bool:
    """
    此函数用于将输入值转换为布尔类型。
    支持布尔值输入，也支持 'true'、'false'、'enable'、'disable'、'1'、'0' 字符串输入（忽略大小写）。
    若输入为 None 或者空字符串，则返回默认值。

    参数:
    value (str | bool | None): 要转换为布尔值的输入，可以是字符串、布尔值或 None。
    default (bool): 当输入为 None 或者空字符串时返回的默认值，默认为 False。

    返回:
    bool: 转换后的布尔值。

    异常:
    ValueError: 若输入既不是有效的布尔值，也不是支持的字符串，会抛出此异常。

    This function is used to convert the input value to a boolean type.
    It supports boolean input and string inputs such as 'true', 'false', 'enable', 'disable', '1', '0' (case-insensitive).
    If the input is None or an empty string, the default value will be returned.

    Parameters:
    value (str | bool | None): The input to be converted to a boolean value, which can be a string, a boolean, or None.
    default (bool): The default value to be returned when the input is None or an empty string, with a default of False.

    Returns:
    bool: The converted boolean value.

    Exceptions:
    ValueError: If the input is neither a valid boolean value nor a supported string, this exception will be thrown.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        # 去除字符串首尾空白并转换为小写
        # Remove leading and trailing whitespace from the string and convert it to lowercase
        value = value.strip().lower()
        return text_to_bool(value)
    raise ValueError(f"无法将 '{value}' 转换为布尔值。 Unable to convert '{value}' to a boolean value.")

def text_to_bool(text: str, truth_values: list = None, false_values: list = None) -> bool:
    """
    Convert text to boolean with customizable values
    Args:
        text: Input text to evaluate
        truth_values: List of strings considered as True
        false_values: List of strings considered as False
    """
    truth_values = truth_values or ['true', '1', 'yes', 'on','enable']
    false_values = false_values or ['false', '0', 'no', 'off','disable']
    
    text_lower = text.lower()
    if text_lower in truth_values:
        return True
    elif text_lower in false_values:
        return False
    return False

def invert_bool_text(text: str, truth_values: list = None, false_values: list = None) -> str:
    """
    Convert text to boolean, invert it, and return as text with customizable values
    Args:
        text: Input text to evaluate
        truth_values: List of strings considered as True (default: ['true', '1', 'yes', 'on'])
        false_values: List of strings considered as False (default: ['false', '0', 'no', 'off'])
    Returns:
        'true' or 'false' string based on inverted logic
    """
    truth_values = truth_values or ['true', '1', 'yes', 'on']
    false_values = false_values or ['false', '0', 'no', 'off']
    
    text_lower = text.lower()
    if text_lower in truth_values:
        return 'false'
    elif text_lower in false_values:
        return 'true'
    return 'true'  # Default inverted value