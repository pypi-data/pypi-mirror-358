import re
from typing import Any, Union, Dict, List, Callable, BinaryIO, TextIO, Optional, Tuple
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from pathlib import Path
import base64
import uuid

class JSONError(Exception):
    """JSON 处理基类异常"""
    pass

class JSONEncodeError(JSONError):
    """JSON 编码异常"""
    pass

class JSONDecodeError(JSONError):
    """JSON 解码异常"""
    pass

class JSONEncoder:
    """
    增强版 JSON 编码器
    
    特性:
    - 支持常见 Python 类型的序列化
    - 可扩展的自定义类型处理
    - 格式化输出控制
    - 循环引用检测
    - 特殊字符转义
    """
    
    def __init__(
        self,
        *,
        indent: Optional[int] = None,
        ensure_ascii: bool = True,
        sort_keys: bool = False,
        skipkeys: bool = False,
        allow_nan: bool = True,
        default: Optional[Callable[[Any], Any]] = None,
        use_decimal: bool = False,
        datetime_format: str = '%Y-%m-%d %H:%M:%S',
        date_format: str = '%Y-%m-%d',
        time_format: str = '%H:%M:%S'
    ):
        """
        初始化编码器
        
        参数:
            indent: 缩进空格数
            ensure_ascii: 是否确保 ASCII 输出
            sort_keys: 是否按键排序
            skipkeys: 是否跳过非字符串键
            allow_nan: 是否允许 NaN/Infinity
            default: 默认转换函数
            use_decimal: 是否使用 Decimal 处理浮点数
            datetime_format: 日期时间格式
            date_format: 日期格式
            time_format: 时间格式
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        self.sort_keys = sort_keys
        self.skipkeys = skipkeys
        self.allow_nan = allow_nan
        self.default = default
        self.use_decimal = use_decimal
        self.datetime_format = datetime_format
        self.date_format = date_format
        self.time_format = time_format
        self._current_indent = 0
        self._memo = set()
    
    def encode(self, obj: Any) -> str:
        """编码 Python 对象为 JSON 字符串"""
        self._memo.clear()
        return self._encode(obj)
    
    def _encode(self, obj: Any) -> str:
        """内部编码方法"""
        obj_id = id(obj)
        
        # 检查循环引用
        if obj_id in self._memo:
            raise JSONEncodeError("Circular reference detected")
        self._memo.add(obj_id)
        
        try:
            if obj is None:
                return "null"
            elif isinstance(obj, bool):
                return "true" if obj else "false"
            elif isinstance(obj, (int, float)):
                return self._encode_number(obj)
            elif isinstance(obj, str):
                return self._encode_string(obj)
            elif isinstance(obj, (list, tuple, set, frozenset)):
                return self._encode_array(obj)
            elif isinstance(obj, dict):
                return self._encode_object(obj)
            elif isinstance(obj, (datetime, date, time)):
                return self._encode_datetime(obj)
            elif isinstance(obj, Decimal):
                return self._encode_decimal(obj)
            elif isinstance(obj, (bytes, bytearray)):
                return self._encode_bytes(obj)
            elif isinstance(obj, Enum):
                return self._encode(obj.value)
            elif isinstance(obj, (Path, uuid.UUID)):
                return self._encode_string(str(obj))
            elif self.default is not None:
                return self._encode(self.default(obj))
            else:
                raise JSONEncodeError(f"Object of type {type(obj)} is not JSON serializable")
        finally:
            self._memo.discard(obj_id)
    
    def _encode_number(self, num: Union[int, float]) -> str:
        """编码数字"""
        if isinstance(num, int):
            return str(num)
        
        if not self.allow_nan:
            if num != num:  # NaN
                raise JSONEncodeError("NaN is not allowed")
            if num in (float('inf'), float('-inf')):
                raise JSONEncodeError("Infinity is not allowed")
        
        if self.use_decimal and isinstance(num, float):
            return str(Decimal.from_float(num).normalize())
        
        if num.is_integer():
            return str(int(num))
        
        return str(num)
    
    def _encode_string(self, s: str) -> str:
        """编码字符串"""
        if not self.ensure_ascii:
            return f'"{s}"'
        
        escape_map = {
            '\"': '\\"',
            '\\': '\\\\',
            '\b': '\\b',
            '\f': '\\f',
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
        }
        
        result = []
        for char in s:
            if char in escape_map:
                result.append(escape_map[char])
            elif ord(char) < 0x20:
                result.append(f"\\u{ord(char):04x}")
            elif ord(char) > 0x7f:
                result.append(f"\\u{ord(char):04x}")
            else:
                result.append(char)
        
        return f'"{"".join(result)}"'
    
    def _encode_array(self, array: Union[List[Any], Tuple[Any, ...], set, frozenset]) -> str:
        """编码数组"""
        if not array:
            return "[]"
        
        if self.indent is None:
            items = [self._encode(item) for item in array]
            return f"[{','.join(items)}]"
        else:
            self._current_indent += self.indent
            indent_str = "\n" + " " * self._current_indent
            items = [f"{indent_str}{self._encode(item)}" for item in array]
            self._current_indent -= self.indent
            return f"[{','.join(items)}\n{' ' * self._current_indent}]"
    
    def _encode_object(self, obj: Dict[str, Any]) -> str:
        """编码对象"""
        if not obj:
            return "{}"
        
        if self.sort_keys:
            items = sorted(obj.items(), key=lambda x: x[0])
        else:
            items = obj.items()
        
        if self.indent is None:
            pairs = []
            for k, v in items:
                if not isinstance(k, str):
                    if self.skipkeys:
                        continue
                    raise JSONEncodeError("Keys must be strings")
                pairs.append(f"{self._encode_string(k)}:{self._encode(v)}")
            return f"{{{','.join(pairs)}}}"
        else:
            self._current_indent += self.indent
            indent_str = "\n" + " " * self._current_indent
            pairs = []
            for k, v in items:
                if not isinstance(k, str):
                    if self.skipkeys:
                        continue
                    raise JSONEncodeError("Keys must be strings")
                key_str = self._encode_string(k)
                value_str = self._encode(v)
                pairs.append(f"{indent_str}{key_str}: {value_str}")
            self._current_indent -= self.indent
            return f"{{{','.join(pairs)}\n{' ' * self._current_indent}}}"
    
    def _encode_datetime(self, dt: Union[datetime, date, time]) -> str:
        """编码日期时间"""
        if isinstance(dt, datetime):
            return self._encode_string(dt.strftime(self.datetime_format))
        elif isinstance(dt, date):
            return self._encode_string(dt.strftime(self.date_format))
        elif isinstance(dt, time):
            return self._encode_string(dt.strftime(self.time_format))
    
    def _encode_decimal(self, dec: Decimal) -> str:
        """编码 Decimal"""
        if self.use_decimal:
            return str(dec.normalize())
        return str(float(dec))
    
    def _encode_bytes(self, b: Union[bytes, bytearray]) -> str:
        """编码字节数据"""
        return self._encode_string(base64.b64encode(b).decode('ascii'))

class JSONDecoder:
    """
    增强版 JSON 解码器
    
    特性:
    - 严格的 JSON 语法验证
    - 支持自定义对象钩子
    - 日期时间自动解析
    - 错误位置报告
    """
    
    def __init__(
        self,
        *,
        object_hook: Optional[Callable[[Dict[str, Any]], Any]] = None,
        parse_float: Optional[Callable[[str], Any]] = None,
        parse_int: Optional[Callable[[str], Any]] = None,
        parse_constant: Optional[Callable[[str], Any]] = None,
        datetime_format: str = '%Y-%m-%d %H:%M:%S',
        date_format: str = '%Y-%m-%d',
        time_format: str = '%H:%M:%S',
        strict: bool = True
    ):
        """
        初始化解码器
        
        参数:
            object_hook: 对象解析钩子
            parse_float: 浮点数解析函数
            parse_int: 整数解析函数
            parse_constant: 常量解析函数
            datetime_format: 日期时间格式
            date_format: 日期格式
            time_format: 时间格式
            strict: 是否严格模式
        """
        self.object_hook = object_hook
        self.parse_float = parse_float or float
        self.parse_int = parse_int or int
        self.parse_constant = parse_constant or (lambda x: None)
        self.datetime_format = datetime_format
        self.date_format = date_format
        self.time_format = time_format
        self.strict = strict
    
    def decode(self, json_str: str) -> Any:
        """解码 JSON 字符串为 Python 对象"""
        if not isinstance(json_str, str):
            raise JSONDecodeError("Input must be a string")
        
        parser = _JSONParser(
            json_str,
            object_hook=self.object_hook,
            parse_float=self.parse_float,
            parse_int=self.parse_int,
            parse_constant=self.parse_constant,
            datetime_format=self.datetime_format,
            date_format=self.date_format,
            time_format=self.time_format,
            strict=self.strict
        )
        return parser.parse()

class _JSONParser:
    """JSON 解析器实现"""
    
    WHITESPACE = re.compile(r'[\s\n\r\t]*')
    NUMBER_RE = re.compile(
        r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
        re.ASCII
    )
    
    def __init__(
        self,
        json_str: str,
        *,
        object_hook: Optional[Callable[[Dict[str, Any]], Any]] = None,
        parse_float: Optional[Callable[[str], Any]] = None,
        parse_int: Optional[Callable[[str], Any]] = None,
        parse_constant: Optional[Callable[[str], Any]] = None,
        datetime_format: str = '%Y-%m-%d %H:%M:%S',
        date_format: str = '%Y-%m-%d',
        time_format: str = '%H:%M:%S',
        strict: bool = True
    ):
        self.json_str = json_str
        self.idx = 0
        self.len = len(json_str)
        self.object_hook = object_hook
        self.parse_float = parse_float
        self.parse_int = parse_int
        self.parse_constant = parse_constant
        self.datetime_format = datetime_format
        self.date_format = date_format
        self.time_format = time_format
        self.strict = strict
    
    def parse(self) -> Any:
        """解析 JSON 字符串"""
        self._skip_whitespace()
        value = self._parse_value()
        self._skip_whitespace()
        
        if self.idx != self.len:
            raise JSONDecodeError(
                f"Extra data at position {self.idx}",
                self.json_str,
                self.idx
            )
        
        return value
    
    def _parse_value(self) -> Any:
        """解析 JSON 值"""
        char = self.json_str[self.idx]
        
        if char == '{':
            return self._parse_object()
        elif char == '[':
            return self._parse_array()
        elif char == '"':
            return self._parse_string()
        elif char == 'n' and self._match('null'):
            return None
        elif char == 't' and self._match('true'):
            return True
        elif char == 'f' and self._match('false'):
            return False
        elif char == '-' or char.isdigit():
            return self._parse_number()
        elif char == 'N' and self._match('NaN'):
            return self.parse_constant('NaN')
        elif char == 'I' and self._match('Infinity'):
            return self.parse_constant('Infinity')
        elif char == '-' and self._match('-Infinity'):
            return self.parse_constant('-Infinity')
        else:
            raise JSONDecodeError(
                f"Unexpected character at position {self.idx}: {char}",
                self.json_str,
                self.idx
            )
    
    def _parse_object(self) -> Dict[str, Any]:
        """解析 JSON 对象"""
        obj = {}
        self._consume('{')
        self._skip_whitespace()
        
        if self.json_str[self.idx] == '}':
            self._consume('}')
            return obj
        
        while True:
            # 解析键
            key = self._parse_string()
            self._skip_whitespace()
            self._consume(':')
            self._skip_whitespace()
            
            # 解析值
            value = self._parse_value()
            obj[key] = value
            
            self._skip_whitespace()
            if self.json_str[self.idx] == '}':
                self._consume('}')
                break
            self._consume(',')
            self._skip_whitespace()
        
        if self.object_hook is not None:
            return self.object_hook(obj)
        return obj
    
    def _parse_array(self) -> List[Any]:
        """解析 JSON 数组"""
        arr = []
        self._consume('[')
        self._skip_whitespace()
        
        if self.json_str[self.idx] == ']':
            self._consume(']')
            return arr
        
        while True:
            # 解析元素
            arr.append(self._parse_value())
            self._skip_whitespace()
            
            if self.json_str[self.idx] == ']':
                self._consume(']')
                break
            self._consume(',')
            self._skip_whitespace()
        
        return arr
    
    def _parse_string(self) -> str:
        """解析 JSON 字符串"""
        self._consume('"')
        chars = []
        
        while self.json_str[self.idx] != '"':
            char = self.json_str[self.idx]
            
            if char == '\\':
                self._consume('\\')
                esc_char = self.json_str[self.idx]
                
                if esc_char == 'u':
                    # Unicode 转义
                    self._consume('u')
                    hex_str = self.json_str[self.idx:self.idx+4]
                    if len(hex_str) != 4:
                        raise JSONDecodeError(
                            "Invalid Unicode escape sequence",
                            self.json_str,
                            self.idx
                        )
                    self.idx += 4
                    chars.append(chr(int(hex_str, 16)))
                else:
                    # 简单转义字符
                    escape_map = {
                        '"': '"',
                        '\\': '\\',
                        '/': '/',
                        'b': '\b',
                        'f': '\f',
                        'n': '\n',
                        'r': '\r',
                        't': '\t',
                    }
                    chars.append(escape_map.get(esc_char, esc_char))
                    self._consume(esc_char)
            else:
                if ord(char) < 0x20 and self.strict:
                    raise JSONDecodeError(
                        "Invalid control character in string",
                        self.json_str,
                        self.idx
                    )
                chars.append(char)
                self._consume(char)
        
        self._consume('"')
        s = ''.join(chars)
        
        # 尝试解析日期时间
        try:
            if len(s) == len(self.datetime_format):
                return datetime.strptime(s, self.datetime_format)
            elif len(s) == len(self.date_format):
                return datetime.strptime(s, self.date_format).date()
            elif len(s) == len(self.time_format):
                return datetime.strptime(s, self.time_format).time()
        except ValueError:
            pass
        
        return s
    
    def _parse_number(self) -> Union[int, float]:
        """解析 JSON 数字"""
        match = self.NUMBER_RE.match(self.json_str, self.idx)
        if not match:
            raise JSONDecodeError(
                "Invalid number literal",
                self.json_str,
                self.idx
            )
        
        integer, fraction, exponent = match.groups()
        self.idx = match.end()
        
        if fraction or exponent:
            num_str = integer + (fraction or '') + (exponent or '')
            return self.parse_float(num_str)
        else:
            return self.parse_int(integer)
    
    def _skip_whitespace(self) -> None:
        """跳过空白字符"""
        while self.idx < self.len and self.json_str[self.idx] in ' \t\n\r':
            self.idx += 1
    
    def _consume(self, expected: str) -> None:
        """消费指定字符"""
        if self.idx >= self.len or self.json_str[self.idx] != expected:
            raise JSONDecodeError(
                f"Expected '{expected}' at position {self.idx}",
                self.json_str,
                self.idx
            )
        self.idx += 1
    
    def _match(self, literal: str) -> bool:
        """匹配指定字符串"""
        if self.json_str.startswith(literal, self.idx):
            self.idx += len(literal)
            return True
        return False

# 高级接口函数
def dumps(
    obj: Any,
    *,
    indent: Optional[int] = None,
    ensure_ascii: bool = True,
    sort_keys: bool = False,
    skipkeys: bool = False,
    allow_nan: bool = True,
    default: Optional[Callable[[Any], Any]] = None,
    use_decimal: bool = False,
    **kwargs
) -> str:
    """
    将 Python 对象序列化为 JSON 字符串
    
    参数:
        obj: 要序列化的对象
        indent: 缩进空格数
        ensure_ascii: 是否确保 ASCII 输出
        sort_keys: 是否按键排序
        skipkeys: 是否跳过非字符串键
        allow_nan: 是否允许 NaN/Infinity
        default: 默认转换函数
        use_decimal: 是否使用 Decimal 处理浮点数
        kwargs: 其他编码器参数
        
    返回:
        JSON 字符串
    """
    encoder = JSONEncoder(
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        skipkeys=skipkeys,
        allow_nan=allow_nan,
        default=default,
        use_decimal=use_decimal,
        **kwargs
    )
    return encoder.encode(obj)

def loads(
    json_str: str,
    *,
    object_hook: Optional[Callable[[Dict[str, Any]], Any]] = None,
    parse_float: Optional[Callable[[str], Any]] = None,
    parse_int: Optional[Callable[[str], Any]] = None,
    parse_constant: Optional[Callable[[str], Any]] = None,
    strict: bool = True,
    **kwargs
) -> Any:
    """
    将 JSON 字符串解析为 Python 对象
    
    参数:
        json_str: JSON 字符串
        object_hook: 对象解析钩子
        parse_float: 浮点数解析函数
        parse_int: 整数解析函数
        parse_constant: 常量解析函数
        strict: 是否严格模式
        kwargs: 其他解码器参数
        
    返回:
        Python 对象
    """
    decoder = JSONDecoder(
        object_hook=object_hook,
        parse_float=parse_float,
        parse_int=parse_int,
        parse_constant=parse_constant,
        strict=strict,
        **kwargs
    )
    return decoder.decode(json_str)

def dump(
    obj: Any,
    file: TextIO,
    *,
    indent: Optional[int] = None,
    ensure_ascii: bool = True,
    sort_keys: bool = False,
    skipkeys: bool = False,
    allow_nan: bool = True,
    default: Optional[Callable[[Any], Any]] = None,
    use_decimal: bool = False,
    **kwargs
) -> None:
    """
    将 Python 对象序列化为 JSON 并写入文件
    
    参数:
        obj: 要序列化的对象
        file: 文件对象
        indent: 缩进空格数
        ensure_ascii: 是否确保 ASCII 输出
        sort_keys: 是否按键排序
        skipkeys: 是否跳过非字符串键
        allow_nan: 是否允许 NaN/Infinity
        default: 默认转换函数
        use_decimal: 是否使用 Decimal 处理浮点数
        kwargs: 其他编码器参数
    """
    json_str = dumps(
        obj,
        indent=indent,
        ensure_ascii=ensure_ascii,
        sort_keys=sort_keys,
        skipkeys=skipkeys,
        allow_nan=allow_nan,
        default=default,
        use_decimal=use_decimal,
        **kwargs
    )
    file.write(json_str)

def load(
    file: TextIO,
    *,
    object_hook: Optional[Callable[[Dict[str, Any]], Any]] = None,
    parse_float: Optional[Callable[[str], Any]] = None,
    parse_int: Optional[Callable[[str], Any]] = None,
    parse_constant: Optional[Callable[[str], Any]] = None,
    strict: bool = True,
    **kwargs
) -> Any:
    """
    从文件读取 JSON 数据并解析为 Python 对象
    
    参数:
        fp: 文件对象
        object_hook: 对象解析钩子
        parse_float: 浮点数解析函数
        parse_int: 整数解析函数
        parse_constant: 常量解析函数
        strict: 是否严格模式
        kwargs: 其他解码器参数
        
    返回:
        Python 对象
    """
    return loads(file.read(), object_hook=object_hook, parse_float=parse_float,
                parse_int=parse_int, parse_constant=parse_constant,
                strict=strict, **kwargs)

# 便捷函数
# 便捷函数
def dump_to_file(
    obj: Any,
    filepath: Union[str, Path],
    encoding: str = 'utf-8',
    *,
    indent: Optional[int] = None,
    ensure_ascii: bool = True,
    sort_keys: bool = False,
    skipkeys: bool = False,
    allow_nan: bool = True,
    default: Optional[Callable[[Any], Any]] = None,
    use_decimal: bool = False,
    **kwargs
) -> None:
    """
    将 Python 对象序列化为 JSON 并写入文件
    
    参数:
        obj: 要序列化的对象
        filepath: 文件路径
        encoding: 文件编码
        indent: 缩进空格数
        ensure_ascii: 是否确保 ASCII 输出
        sort_keys: 是否按键排序
        skipkeys: 是否跳过非字符串键
        allow_nan: 是否允许 NaN/Infinity
        default: 默认转换函数
        use_decimal: 是否使用 Decimal 处理浮点数
        kwargs: 其他编码器参数
    """
    with open(filepath, 'w', encoding=encoding) as f:
        dump(
            obj,
            f,  # 添加文件对象参数
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
            skipkeys=skipkeys,
            allow_nan=allow_nan,
            default=default,
            use_decimal=use_decimal,
            **kwargs
        )

def load_from_file(
    filepath: Union[str, Path],
    encoding: str = 'utf-8',
    *,
    object_hook: Optional[Callable[[Dict[str, Any]], Any]] = None,
    parse_float: Optional[Callable[[str], Any]] = None,
    parse_int: Optional[Callable[[str], Any]] = None,
    parse_constant: Optional[Callable[[str], Any]] = None,
    strict: bool = True,
    **kwargs
) -> Any:
    """
    从文件读取 JSON 数据并解析为 Python 对象
    
    参数:
        filepath: 文件路径
        encoding: 文件编码
        object_hook: 对象解析钩子
        parse_float: 浮点数解析函数
        parse_int: 整数解析函数
        parse_constant: 常量解析函数
        strict: 是否严格模式
        kwargs: 其他解码器参数
        
    返回:
        Python 对象
    """
    with open(filepath, 'r', encoding=encoding) as f:
        return load(
            f, 
            object_hook=object_hook, 
            parse_float=parse_float,
            parse_int=parse_int, 
            parse_constant=parse_constant,
            strict=strict, 
            **kwargs
        )