"""
secure_zip.py - 支持加密的ZIP文件操作库

功能：
1. 支持AES加密(128/192/256位)和传统PKWARE加密
2. 创建/解压加密ZIP文件
3. 查看加密ZIP内容
4. 完整性检查
"""

import os
import struct
import zlib
import shutil
import hashlib
import random
from typing import List, Union, Optional, Dict, BinaryIO, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# ZIP文件格式常量
ZIP_SIGNATURE = b'PK\x03\x04'
ZIP_CENTRAL_DIR_SIGNATURE = b'PK\x01\x02'
ZIP_END_OF_CENTRAL_DIR_SIGNATURE = b'PK\x05\x06'

# 加密相关常量
COMPRESSION_STORED = 0
COMPRESSION_DEFLATED = 8
ENCRYPTION_TRADITIONAL = 0x01
ENCRYPTION_AES128 = 0x02
ENCRYPTION_AES192 = 0x03
ENCRYPTION_AES256 = 0x04
AES_BLOCK_SIZE = 16
AES_SALT_SIZE = 16
AES_PASSWORD_VERIFIER_SIZE = 2
AES_MAC_SIZE = 10
AES_KEY_LENGTHS = {
    ENCRYPTION_AES128: 16,
    ENCRYPTION_AES192: 24,
    ENCRYPTION_AES256: 32
}

@dataclass
class ZipFileHeader:
    version: int
    flags: int
    compression: int
    mod_time: int
    mod_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    filename: str
    extra: bytes
    file_offset: int
    is_encrypted: bool = False
    encryption_method: int = 0
    aes_strength: int = 0
    salt: bytes = b''
    password_verifier: bytes = b''

class SecureZipFile:
    def __init__(self, filename: Union[str, Path], mode: str = 'r', password: Optional[str] = None):
        """
        初始化加密ZIP文件对象
        
        参数:
            filename: ZIP文件路径
            mode: 打开模式 ('r'读取, 'w'写入, 'a'追加)
            password: 加密密码(可选)
        """
        self.filename = Path(filename)
        self.mode = mode
        self.password = password
        self.file_headers: Dict[str, ZipFileHeader] = {}
        self.fp: Optional[BinaryIO] = None
        
        if mode == 'r':
            self._read_zip_file()
        elif mode == 'w':
            self.fp = open(self.filename, 'wb')
        elif mode == 'a':
            if self.filename.exists():
                self._read_zip_file()
                self.fp = open(self.filename, 'r+b')
                # 定位到中央目录前
                self.fp.seek(self.end_of_central_dir_offset)
            else:
                self.fp = open(self.filename, 'wb')
        else:
            raise ValueError("Invalid mode, must be 'r', 'w' or 'a'")

    def _read_zip_file(self):
        """读取ZIP文件并解析文件头信息"""
        if not self.filename.exists():
            raise FileNotFoundError(f"ZIP file not found: {self.filename}")
        
        self.fp = open(self.filename, 'rb')
        self._find_end_of_central_dir()
        self._read_central_directory()
    
    def _find_end_of_central_dir(self):
        """定位并读取ZIP文件尾部的中央目录结束记录"""
        file_size = self.filename.stat().st_size
        max_comment_len = 65535
        search_size = min(file_size, max_comment_len + 22)
        
        self.fp.seek(file_size - search_size)
        data = self.fp.read()
        
        pos = data.rfind(ZIP_END_OF_CENTRAL_DIR_SIGNATURE)
        if pos < 0:
            raise ValueError("Not a valid ZIP file (end of central directory signature not found)")
        
        end_record = data[pos:pos+22]
        (
            self.disk_number,
            self.central_dir_disk,
            self.disk_entries,
            self.total_entries,
            self.central_dir_size,
            self.central_dir_offset,
            self.comment_length
        ) = struct.unpack('<HHHHIIH', end_record[4:22])
        
        self.end_of_central_dir_offset = file_size - (search_size - pos)
    
    def _read_central_directory(self):
        """读取中央目录并解析文件头信息"""
        self.fp.seek(self.central_dir_offset)
        
        while True:
            signature = self.fp.read(4)
            if signature != ZIP_CENTRAL_DIR_SIGNATURE:
                break
                
            header_data = self.fp.read(42)
            (
                version_made_by, version_needed, flags, compression,
                mod_time, mod_date, crc32, compressed_size, uncompressed_size,
                filename_len, extra_len, comment_len, disk_num_start,
                internal_attrs, external_attrs, local_header_offset
            ) = struct.unpack('<HHHHHHIIIHHHHHII', header_data)
            
            filename = self.fp.read(filename_len).decode('utf-8')
            extra = self.fp.read(extra_len)
            comment = self.fp.read(comment_len)
            
            is_encrypted = (flags & 0x1) != 0
            encryption_method = 0
            aes_strength = 0
            salt = b''
            password_verifier = b''
            
            if is_encrypted:
                # 检查AES加密标志
                if (flags & 0x40) != 0:
                    # AES加密
                    encryption_method = (flags >> 8) & 0xFF
                    aes_strength = AES_KEY_LENGTHS.get(encryption_method, 0)
                    
                    # 从额外字段中读取salt和验证器
                    extra_pos = 0
                    while extra_pos < len(extra):
                        header_id, data_size = struct.unpack_from('<HH', extra, extra_pos)
                        extra_pos += 4
                        if header_id == 0x9901:  # AE-x ID
                            aes_data = extra[extra_pos:extra_pos+data_size]
                            if len(aes_data) >= 7:
                                aes_version, vendor_id, strength = struct.unpack_from('<HBB', aes_data, 0)
                                salt = aes_data[7:7+AES_SALT_SIZE]
                                password_verifier = aes_data[7+AES_SALT_SIZE:7+AES_SALT_SIZE+AES_PASSWORD_VERIFIER_SIZE]
                            break
                        extra_pos += data_size
                else:
                    # 传统PKWARE加密
                    encryption_method = ENCRYPTION_TRADITIONAL
            
            # 保存文件头信息
            self.file_headers[filename] = ZipFileHeader(
                version=version_needed,
                flags=flags,
                compression=compression,
                mod_time=mod_time,
                mod_date=mod_date,
                crc32=crc32,
                compressed_size=compressed_size,
                uncompressed_size=uncompressed_size,
                filename=filename,
                extra=extra,
                file_offset=local_header_offset,
                is_encrypted=is_encrypted,
                encryption_method=encryption_method,
                aes_strength=aes_strength,
                salt=salt,
                password_verifier=password_verifier
            )
    
    def close(self):
        """关闭ZIP文件"""
        if self.fp is not None:
            if self.mode in ('w', 'a'):
                self._write_central_directory()
            self.fp.close()
            self.fp = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _generate_aes_key(self, salt: bytes, key_length: int) -> Tuple[bytes, bytes]:
        """生成AES密钥和验证器"""
        if not self.password:
            raise ValueError("Password is required for AES encryption")
        
        # 使用PBKDF2生成密钥
        key = hashlib.pbkdf2_hmac(
            'sha1',
            self.password.encode('utf-8'),
            salt,
            1000,  # 迭代次数
            key_length * 2 + 2  # 密钥+MAC密钥+验证器
        )
        
        encryption_key = key[:key_length]
        mac_key = key[key_length:key_length*2]
        password_verifier = key[key_length*2:key_length*2+2]
        
        return encryption_key, mac_key, password_verifier
    
    def _traditional_encrypt(self, data: bytes) -> bytes:
        """传统PKWARE加密"""
        if not self.password:
            raise ValueError("Password is required for traditional encryption")
        
        # 初始化加密密钥
        keys = [0x12345678, 0x23456789, 0x34567890]
        for c in self.password.encode('utf-8'):
            keys = self._update_keys(keys, c)
        
        # 加密数据
        encrypted_data = bytearray()
        for i, b in enumerate(data):
            c = b ^ self._crc32_crypt_byte(keys[2])
            encrypted_data.append(c)
            keys = self._update_keys(keys, c)
        
        return bytes(encrypted_data)
    
    def _traditional_decrypt(self, data: bytes) -> bytes:
        """传统PKWARE解密"""
        if not self.password:
            raise ValueError("Password is required for traditional decryption")
        
        # 初始化加密密钥
        keys = [0x12345678, 0x23456789, 0x34567890]
        for c in self.password.encode('utf-8'):
            keys = self._update_keys(keys, c)
        
        # 解密数据
        decrypted_data = bytearray()
        for i, b in enumerate(data):
            c = b ^ self._crc32_crypt_byte(keys[2])
            decrypted_data.append(c)
            keys = self._update_keys(keys, c)
        
        return bytes(decrypted_data)
    
    def _update_keys(self, keys: List[int], c: int) -> List[int]:
        """更新传统加密密钥"""
        keys[0] = zlib.crc32(bytes([c]), keys[0]) & 0xFFFFFFFF
        keys[1] = (keys[1] + (keys[0] & 0xFF)) & 0xFFFFFFFF
        keys[1] = (keys[1] * 134775813 + 1) & 0xFFFFFFFF
        keys[2] = zlib.crc32(bytes([keys[1] >> 24]), keys[2]) & 0xFFFFFFFF
        return keys
    
    def _crc32_crypt_byte(self, key: int) -> int:
        """传统加密的字节加密函数"""
        temp = (key | 2) & 0xFFFF
        return ((temp * (temp ^ 1)) >> 8) & 0xFF
    
    def _write_central_directory(self):
        """写入中央目录和结束记录"""
        if self.fp is None:
            raise ValueError("ZIP file not open")
        
        central_dir_start = self.fp.tell()
        
        for header in self.file_headers.values():
            self.fp.write(ZIP_CENTRAL_DIR_SIGNATURE)
            self.fp.write(struct.pack(
                '<HHHHHHIIIHHHHHII',
                20,         # version made by
                20,         # version needed to extract
                header.flags,
                header.compression,
                header.mod_time,
                header.mod_date,
                header.crc32,
                header.compressed_size,
                header.uncompressed_size,
                len(header.filename.encode('utf-8')),
                len(header.extra),
                0,          # file comment length
                0,          # disk number start
                0,          # internal file attributes
                0o644 << 16, # external file attributes
                header.file_offset
            ))
            self.fp.write(header.filename.encode('utf-8'))
            self.fp.write(header.extra)
        
        central_dir_end = self.fp.tell()
        central_dir_size = central_dir_end - central_dir_start
        
        self.fp.write(ZIP_END_OF_CENTRAL_DIR_SIGNATURE)
        self.fp.write(struct.pack(
            '<HHHHIIH',
            0,              # number of this disk
            0,              # disk where central directory starts
            len(self.file_headers),
            len(self.file_headers),
            central_dir_size,
            central_dir_start,
            0               # ZIP file comment length
        ))
    
    def write(self, filename: str, data: bytes, compress: bool = True, 
              encryption_method: int = 0) -> None:
        """
        向ZIP文件中写入一个文件
        
        参数:
            filename: ZIP内的文件名
            data: 文件数据
            compress: 是否压缩数据
            encryption_method: 加密方法 (0=不加密, 1=传统加密, 2=AES128, 3=AES192, 4=AES256)
        """
        if self.fp is None or self.mode not in ('w', 'a'):
            raise ValueError("ZIP file not open for writing")
        
        # 计算CRC32校验和
        crc32 = zlib.crc32(data) & 0xFFFFFFFF
        
        if compress:
            compressed_data = zlib.compress(data)
            compression = COMPRESSION_DEFLATED
        else:
            compressed_data = data
            compression = COMPRESSION_STORED
        
        # 加密数据
        is_encrypted = encryption_method != 0
        salt = b''
        password_verifier = b''
        extra = b''
        
        if is_encrypted:
            if not self.password:
                raise ValueError("Password is required for encryption")
            
            if encryption_method == ENCRYPTION_TRADITIONAL:
                # 传统PKWARE加密
                encrypted_data = self._traditional_encrypt(compressed_data)
                flags = 0x1  # 加密标志
            elif encryption_method in (ENCRYPTION_AES128, ENCRYPTION_AES192, ENCRYPTION_AES256):
                # AES加密
                key_length = AES_KEY_LENGTHS[encryption_method]
                salt = get_random_bytes(AES_SALT_SIZE)
                encryption_key, mac_key, password_verifier = self._generate_aes_key(salt, key_length)
                
                # 创建AES加密器
                cipher = AES.new(encryption_key, AES.MODE_CBC, iv=salt)
                padded_data = pad(compressed_data, AES_BLOCK_SIZE)
                encrypted_data = cipher.encrypt(padded_data)
                
                # 添加HMAC-SHA1验证码(简化实现)
                mac = hashlib.sha1(encrypted_data).digest()[:AES_MAC_SIZE]
                encrypted_data += mac
                
                # 设置AES额外字段
                aes_extra = struct.pack('<HBB', 0x9901, 7, encryption_method - 1)
                extra = aes_extra + salt + password_verifier
                flags = 0x41  # 加密标志 + AES标志
            else:
                raise ValueError("Unsupported encryption method")
        else:
            encrypted_data = compressed_data
            flags = 0
        
        # 记录本地文件头位置
        file_offset = self.fp.tell()
        
        # 写入本地文件头
        self.fp.write(ZIP_SIGNATURE)
        self.fp.write(struct.pack(
            '<HHHHHIII',
            20,             # version needed to extract
            flags,          # general purpose bit flag
            compression,
            0,              # last mod time (simplified)
            0,              # last mod date (simplified)
            crc32,
            len(encrypted_data),
            len(data)
        ))
        
        # 写入文件名和额外字段
        self.fp.write(filename.encode('utf-8'))
        if extra:
            self.fp.write(extra)
        
        # 写入加密数据
        self.fp.write(encrypted_data)
        
        # 保存文件头信息
        self.file_headers[filename] = ZipFileHeader(
            version=20,
            flags=flags,
            compression=compression,
            mod_time=0,
            mod_date=0,
            crc32=crc32,
            compressed_size=len(encrypted_data),
            uncompressed_size=len(data),
            filename=filename,
            extra=extra,
            file_offset=file_offset,
            is_encrypted=is_encrypted,
            encryption_method=encryption_method,
            aes_strength=AES_KEY_LENGTHS.get(encryption_method, 0),
            salt=salt,
            password_verifier=password_verifier
        )
    
    def extract(self, member: str, path: Optional[Union[str, Path]] = None) -> None:
        """
        从ZIP文件中提取一个文件
        
        参数:
            member: 要提取的文件名
            path: 提取目标路径(默认为当前目录)
        """
        if self.fp is None or self.mode != 'r':
            raise ValueError("ZIP file not open for reading")
        
        if member not in self.file_headers:
            raise KeyError(f"File not found in ZIP: {member}")
        
        header = self.file_headers[member]
        target_path = Path(path or '.') / member
        
        # 确保目标目录存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 定位到文件数据
        self.fp.seek(header.file_offset)
        signature = self.fp.read(4)
        if signature != ZIP_SIGNATURE:
            raise ValueError("Invalid local file header signature")
        
        # 读取本地文件头
        local_header = self.fp.read(26)
        (
            version, flags, compression, mod_time, mod_date,
            crc32, compressed_size, uncompressed_size,
            filename_len, extra_len
        ) = struct.unpack('<HHHHHIIIHH', local_header)
        
        # 跳过文件名和额外字段
        filename = self.fp.read(filename_len).decode('utf-8')
        extra = self.fp.read(extra_len)
        
        # 读取加密数据
        encrypted_data = self.fp.read(compressed_size)
        
        # 解密数据
        if header.is_encrypted:
            if not self.password:
                raise ValueError("Password is required for encrypted file")
            
            if header.encryption_method == ENCRYPTION_TRADITIONAL:
                # 传统PKWARE解密
                decrypted_data = self._traditional_decrypt(encrypted_data)
            elif header.encryption_method in (ENCRYPTION_AES128, ENCRYPTION_AES192, ENCRYPTION_AES256):
                # AES解密
                key_length = header.aes_strength
                encryption_key, mac_key, password_verifier = self._generate_aes_key(header.salt, key_length)
                
                # 验证密码
                if header.password_verifier != password_verifier:
                    raise ValueError("Incorrect password")
                
                # 分离数据和MAC
                if len(encrypted_data) < AES_MAC_SIZE:
                    raise ValueError("Invalid encrypted data length")
                
                data_part = encrypted_data[:-AES_MAC_SIZE]
                mac = encrypted_data[-AES_MAC_SIZE:]
                
                # 验证MAC(简化实现)
                computed_mac = hashlib.sha1(data_part).digest()[:AES_MAC_SIZE]
                if mac != computed_mac:
                    raise ValueError("MAC verification failed")
                
                # 解密数据
                cipher = AES.new(encryption_key, AES.MODE_CBC, iv=header.salt)
                decrypted_padded_data = cipher.decrypt(data_part)
                decrypted_data = unpad(decrypted_padded_data, AES_BLOCK_SIZE)
            else:
                raise ValueError("Unsupported encryption method")
        else:
            decrypted_data = encrypted_data
        
        # 解压数据
        if compression == COMPRESSION_STORED:
            data = decrypted_data
        elif compression == COMPRESSION_DEFLATED:
            data = zlib.decompress(decrypted_data)
        else:
            raise ValueError(f"Unsupported compression method: {compression}")
        
        # 验证CRC32
        if zlib.crc32(data) & 0xFFFFFFFF != header.crc32:
            raise ValueError("CRC32 checksum failed")
        
        # 写入目标文件
        with open(target_path, 'wb') as f:
            f.write(data)
    
    def namelist(self) -> List[str]:
        """返回ZIP文件中所有文件的名称列表"""
        return list(self.file_headers.keys())
    
    def testzip(self) -> Optional[str]:
        """
        测试ZIP文件中所有文件的完整性
        
        返回:
            第一个损坏的文件名，如果所有文件都完好则返回None
        """
        if self.fp is None or self.mode != 'r':
            raise ValueError("ZIP file not open for reading")
        
        for filename, header in self.file_headers.items():
            try:
                self.extract(filename, '/dev/null')  # 尝试提取到虚拟位置
            except:
                return filename
        
        return None

# 高级API函数
def create_secure_zip(
    zip_path: Union[str, Path],
    files_to_zip: List[Union[str, Path]],
    password: Optional[str] = None,
    encryption_method: int = 0,
    compression: bool = True,
    overwrite: bool = False
) -> None:
    """
    创建加密的ZIP文件
    
    参数:
        zip_path: 要创建的ZIP文件路径
        files_to_zip: 要压缩的文件/文件夹列表
        password: 加密密码
        encryption_method: 加密方法 (0=不加密, 1=传统加密, 2=AES128, 3=AES192, 4=AES256)
        compression: 是否压缩数据
        overwrite: 是否覆盖已存在的ZIP文件
        
    异常:
        FileExistsError: 当ZIP文件已存在且不允许覆盖时
        FileNotFoundError: 当要压缩的文件不存在时
        ValueError: 当需要密码但未提供时
    """
    zip_path = Path(zip_path)
    if zip_path.exists() and not overwrite:
        raise FileExistsError(f"ZIP file already exists: {zip_path}")

    with SecureZipFile(zip_path, 'w', password) as zipf:
        for item in files_to_zip:
            item = Path(item)
            if not item.exists():
                raise FileNotFoundError(f"File not found: {item}")

            if item.is_file():
                with open(item, 'rb') as f:
                    data = f.read()
                zipf.write(str(item.name), data, compress=compression, encryption_method=encryption_method)
            elif item.is_dir():
                for root, _, files in os.walk(item):
                    for file in files:
                        file_path = Path(root) / file
                        rel_path = str(file_path.relative_to(item.parent))
                        with open(file_path, 'rb') as f:
                            data = f.read()
                        zipf.write(rel_path, data, compress=compression, encryption_method=encryption_method)

def extract_secure_zip(
    zip_path: Union[str, Path],
    extract_to: Union[str, Path],
    password: Optional[str] = None,
    members: Optional[List[str]] = None,
    overwrite: bool = False
) -> None:
    """
    解压加密的ZIP文件
    
    参数:
        zip_path: ZIP文件路径
        extract_to: 解压目标目录
        password: 解密密码
        members: 可选,只解压指定的文件
        overwrite: 是否覆盖已存在的文件
        
    异常:
        FileNotFoundError: 当ZIP文件不存在时
        ValueError: 当ZIP文件损坏或密码错误时
    """
    zip_path = Path(zip_path)
    extract_to = Path(extract_to)

    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    if not overwrite:
        # 检查是否会覆盖已有文件
        with SecureZipFile(zip_path, 'r', password) as zipf:
            for member in members or zipf.namelist():
                dest = extract_to / member
                if dest.exists():
                    raise FileExistsError(f"File exists and overwrite=False: {dest}")

    with SecureZipFile(zip_path, 'r', password) as zipf:
        for member in members or zipf.namelist():
            zipf.extract(member, extract_to)

def is_encrypted_zip(zip_path: Union[str, Path]) -> bool:
    """
    检查ZIP文件是否加密
    
    参数:
        zip_path: ZIP文件路径
        
    返回:
        如果ZIP文件包含加密文件则返回True，否则返回False
        
    异常:
        FileNotFoundError: 当ZIP文件不存在时
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    with SecureZipFile(zip_path, 'r') as zipf:
        return any(header.is_encrypted for header in zipf.file_headers.values())