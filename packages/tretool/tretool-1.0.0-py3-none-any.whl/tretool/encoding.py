import chardet
import logging
import warnings
from typing import Union, BinaryIO, Optional, List, Dict, Tuple
from io import BytesIO, SEEK_SET
import re
from collections import OrderedDict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncodingDetectionError(Exception):
    """编码检测异常基类"""
    pass

class InvalidInputError(EncodingDetectionError):
    """无效输入异常"""
    pass

class EncodingValidationError(EncodingDetectionError):
    """编码验证异常"""
    pass

class SmartEncodingDetector:
    """
    终极智能文本编码检测器
    
    主要特性：
    - 多阶段智能检测流程
    - 支持BOM自动检测
    - 高级编码验证机制
    - 可配置的检测策略
    - 完善的错误处理
    - 性能优化
    - 详细的文档和类型提示
    """
    
    # BOM标记定义
    BOM_MARKERS: Dict[str, bytes] = {
        'utf-8-sig': b'\xef\xbb\xbf',
        'utf-16': b'\xff\xfe',
        'utf-16be': b'\xfe\xff',
        'utf-32': b'\xff\xfe\x00\x00',
        'utf-32be': b'\x00\x00\xfe\xff',
    }
    
    # 默认优先编码列表（按优先级排序）
    DEFAULT_PREFERRED_ENCODINGS = [
        'utf-8',        # 最通用的Unicode编码
        'gb18030',      # 中文国家标准
        'gbk',          # 中文扩展
        'gb2312',       # 中文基本集
        'big5',         # 繁体中文
        'shift_jis',    # 日文
        'euc-jp',       # 日文
        'euc-kr',       # 韩文
        'iso-8859-1',   # 西欧
        'windows-1252', # 西欧扩展
        'ascii',        # 基本ASCII
    ]
    
    # 常见编码别名映射
    ENCODING_ALIASES: Dict[str, str] = {
        'ascii': 'utf-8',       # ASCII是UTF-8的子集
        'latin1': 'iso-8859-1',
        'cp936': 'gbk',
        'ms936': 'gbk',
        'csgb2312': 'gb2312',
        'ms950': 'big5',
        'cp950': 'big5',
    }
    
    def __init__(
        self,
        preferred_encodings: Optional[List[str]] = None,
        min_confidence: float = 0.7,
        enable_bom_detection: bool = True,
        enable_heuristics: bool = True,
        enable_validation: bool = True,
        sample_size: int = 4096,
        max_retries: int = 3
    ):
        """
        初始化编码检测器
        
        参数:
            preferred_encodings: 自定义优先编码列表
            min_confidence: chardet的最小置信度阈值(0-1)
            enable_bom_detection: 是否启用BOM检测
            enable_heuristics: 是否启用启发式规则
            enable_validation: 是否启用严格验证
            sample_size: 采样数据大小(字节)
            max_retries: 最大重试次数
        """
        self.preferred_encodings = self._normalize_encodings(
            preferred_encodings or self.DEFAULT_PREFERRED_ENCODINGS
        )
        self.min_confidence = min(min_confidence, 1.0)
        self.enable_bom_detection = enable_bom_detection
        self.enable_heuristics = enable_heuristics
        self.enable_validation = enable_validation
        self.sample_size = max(sample_size, 128)
        self.max_retries = max(max_retries, 1)
        
        # 编译常用正则表达式
        self._chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        self._japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]')
        self._korean_pattern = re.compile(r'[\uac00-\ud7a3]')
    
    def detect(self, input_data: Union[bytes, str, BinaryIO], sample_size: Optional[int] = None) -> str:
        """
        检测文本数据的编码
        
        参数:
            input_data: 输入数据(bytes/str/文件对象)
            sample_size: 可选自定义采样大小
            
        返回:
            检测到的编码名称
            
        异常:
            InvalidInputError: 输入数据无效
            EncodingDetectionError: 编码检测失败
        """
        sample_size = sample_size or self.sample_size
        
        try:
            # 获取样本数据
            raw_data = self._get_sample_data(input_data, sample_size)
            if not raw_data:
                raise InvalidInputError("输入数据为空")
            
            # 多阶段检测
            return self._detect_in_stages(raw_data)
            
        except Exception as e:
            logger.error(f"编码检测失败: {str(e)}")
            raise EncodingDetectionError(f"无法检测编码: {str(e)}")
    
    def detect_and_decode(self, input_data: Union[bytes, BinaryIO], sample_size: Optional[int] = None) -> str:
        """
        检测编码并解码数据
        
        参数:
            input_data: 字节数据或文件对象
            sample_size: 可选采样大小
            
        返回:
            解码后的字符串
            
        异常:
            InvalidInputError: 输入数据无效
            EncodingDetectionError: 编码检测失败
            UnicodeDecodeError: 解码失败
        """
        if isinstance(input_data, bytes):
            encoding = self.detect(input_data, sample_size)
            return self._safe_decode(input_data, encoding)
        
        if hasattr(input_data, 'read'):
            # 保存原始位置
            original_pos = input_data.tell()
            
            try:
                # 读取样本检测编码
                sample = input_data.read(sample_size or self.sample_size)
                if not isinstance(sample, bytes):
                    raise InvalidInputError("文件对象必须返回bytes")
                
                encoding = self.detect(sample, sample_size)
                
                # 重置并读取全部内容
                input_data.seek(original_pos, SEEK_SET)
                full_data = input_data.read()
                
                if not isinstance(full_data, bytes):
                    raise InvalidInputError("文件对象必须返回bytes")
                
                return self._safe_decode(full_data, encoding)
            
            finally:
                # 确保文件指针被恢复
                input_data.seek(original_pos, SEEK_SET)
        
        raise InvalidInputError("输入必须是bytes或文件对象")
    
    def _detect_in_stages(self, data: bytes) -> str:
        """多阶段编码检测流程"""
        # 阶段1: BOM检测
        if self.enable_bom_detection:
            bom_encoding = self._detect_bom(data)
            if bom_encoding:
                logger.debug(f"通过BOM检测到编码: {bom_encoding}")
                return bom_encoding
        
        # 阶段2: chardet统计分析
        detected_encoding = self._detect_with_chardet(data)
        if detected_encoding:
            logger.debug(f"chardet检测到编码: {detected_encoding}")
            return detected_encoding
        
        # 阶段3: 启发式规则
        if self.enable_heuristics:
            heuristic_encoding = self._apply_heuristics(data)
            if heuristic_encoding:
                logger.debug(f"启发式检测到编码: {heuristic_encoding}")
                return heuristic_encoding
        
        # 阶段4: 优先编码列表验证
        for encoding in self.preferred_encodings:
            if self._validate_encoding(data, encoding):
                logger.debug(f"通过优先编码列表验证: {encoding}")
                return encoding
        
        # 最终回退
        warnings.warn("无法确定精确编码，使用utf-8作为回退", RuntimeWarning)
        return 'utf-8'
    
    def _get_sample_data(self, input_data: Union[bytes, str, BinaryIO], sample_size: int) -> bytes:
        """安全获取样本数据"""
        if isinstance(input_data, bytes):
            return input_data[:sample_size]
        
        if isinstance(input_data, str):
            try:
                # 尝试用latin-1编码获取原始字节（不会失败）
                return input_data.encode('latin-1')[:sample_size]
            except Exception as e:
                raise InvalidInputError(f"字符串转换失败: {str(e)}")
        
        if hasattr(input_data, 'read'):
            try:
                # 保存原始位置
                original_pos = input_data.tell()
                
                # 读取样本数据
                data = input_data.read(sample_size)
                
                # 确保返回的是bytes
                if not isinstance(data, bytes):
                    raise InvalidInputError("文件对象必须返回bytes")
                
                # 恢复文件指针
                input_data.seek(original_pos, SEEK_SET)
                return data
            except Exception as e:
                raise InvalidInputError(f"文件读取失败: {str(e)}")
        
        raise InvalidInputError("不支持的输入数据类型")
    
    def _detect_bom(self, data: bytes) -> Optional[str]:
        """检测BOM标记"""
        for encoding, bom in self.BOM_MARKERS.items():
            if data.startswith(bom):
                return encoding
        return None
    
    def _detect_with_chardet(self, data: bytes) -> Optional[str]:
        """使用chardet检测编码"""
        try:
            result = chardet.detect(data)
            confidence = result['confidence']
            encoding = result['encoding'].lower()
            
            # 处理编码别名
            encoding = self.ENCODING_ALIASES.get(encoding, encoding)
            
            if confidence >= self.min_confidence:
                if not self.enable_validation or self._validate_encoding(data, encoding):
                    return encoding
            return None
        except Exception as e:
            logger.warning(f"chardet检测失败: {str(e)}")
            return None
    
    def _apply_heuristics(self, data: bytes) -> Optional[str]:
        """应用启发式规则检测编码"""
        # 尝试解码为常见编码并检查字符分布
        for encoding in ['utf-8', 'gb18030', 'big5', 'shift_jis', 'euc-kr']:
            try:
                decoded = data.decode(encoding, errors='strict')
                
                # 中文字符检测
                if self._chinese_pattern.search(decoded):
                    if encoding in ['gb18030', 'gbk', 'gb2312']:
                        return encoding
                    if 'big5' in encoding:
                        return 'big5'
                
                # 日文字符检测
                if self._japanese_pattern.search(decoded):
                    if 'shift_jis' in encoding or 'euc-jp' in encoding:
                        return encoding
                
                # 韩文字符检测
                if self._korean_pattern.search(decoded):
                    if 'euc-kr' in encoding:
                        return 'euc-kr'
                
                # 如果解码成功但没有特定字符，返回该编码
                return encoding
                
            except UnicodeError:
                continue
        
        return None
    
    def _validate_encoding(self, data: bytes, encoding: str) -> bool:
        """严格验证编码是否有效"""
        if not data:
            return False
            
        for _ in range(self.max_retries):
            try:
                # 尝试严格解码
                decoded = data.decode(encoding, errors='strict')
                
                # 验证是否可以重新编码
                reencoded = decoded.encode(encoding, errors='strict')
                
                # 对于UTF-8系列编码，不要求完全可逆（因为BOM可能被去除）
                if encoding.startswith('utf-8'):
                    return True
                
                # 验证数据一致性
                return reencoded == data
                
            except UnicodeError as e:
                logger.debug(f"编码验证失败 {encoding}: {str(e)}")
                return False
            except Exception as e:
                logger.warning(f"编码验证异常 {encoding}: {str(e)}")
                continue
        
        return False
    
    def _safe_decode(self, data: bytes, encoding: str) -> str:
        """安全解码数据"""
        for _ in range(self.max_retries):
            try:
                return data.decode(encoding, errors='strict')
            except UnicodeError as e:
                logger.warning(f"解码失败 {encoding}, 尝试替代方案: {str(e)}")
                # 尝试用错误处理器
                return data.decode(encoding, errors='replace')
            except Exception as e:
                logger.error(f"解码异常: {str(e)}")
                raise EncodingValidationError(f"无法用 {encoding} 解码数据: {str(e)}")
    
    def _normalize_encodings(self, encodings: List[str]) -> List[str]:
        """标准化编码名称并去重"""
        seen = set()
        normalized = []
        
        for enc in encodings:
            # 转换为小写并处理别名
            lower_enc = enc.lower().replace('-', '_')
            norm_enc = self.ENCODING_ALIASES.get(lower_enc, lower_enc)
            
            if norm_enc not in seen:
                seen.add(norm_enc)
                normalized.append(norm_enc)
        
        return normalized


# 全局默认检测器实例
_default_detector = SmartEncodingDetector()

# 便捷函数
def detect_encoding(
    input_data: Union[bytes, str, BinaryIO],
    sample_size: Optional[int] = None,
    preferred_encodings: Optional[List[str]] = None,
    min_confidence: float = 0.7
) -> str:
    """
    自动检测文本数据的字符编码（便捷函数）
    
    参数:
        input_data: 输入数据
        sample_size: 采样大小
        preferred_encodings: 优先编码列表
        min_confidence: 最小置信度
        
    返回:
        检测到的编码名称
        
    异常:
        EncodingDetectionError: 编码检测失败
    """
    detector = SmartEncodingDetector(
        preferred_encodings=preferred_encodings,
        min_confidence=min_confidence
    )
    return detector.detect(input_data, sample_size)


def detect_and_decode(
    input_data: Union[bytes, BinaryIO],
    sample_size: Optional[int] = None,
    preferred_encodings: Optional[List[str]] = None
) -> str:
    """
    检测编码并解码数据（便捷函数）
    
    参数:
        input_data: 输入数据
        sample_size: 采样大小
        preferred_encodings: 优先编码列表
        
    返回:
        解码后的字符串
        
    异常:
        EncodingDetectionError: 编码检测失败
        UnicodeDecodeError: 解码失败
    """
    detector = SmartEncodingDetector(preferred_encodings=preferred_encodings)
    return detector.detect_and_decode(input_data, sample_size)