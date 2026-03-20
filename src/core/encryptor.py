"""
RSA加密处理模块
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from typing import Optional, Tuple
import base64


class Encryptor:
    """RSA加密处理器"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self, key_size: int = 2048):
        """
        生成RSA密钥对
        
        Args:
            key_size: 密钥长度 (2048 or 4096)
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def load_private_key(self, key_path: str, password: Optional[bytes] = None):
        """
        加载私钥
        
        Args:
            key_path: 私钥文件路径
            password: 密钥密码(可选)
        """
        with open(key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=password,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
    
    def load_public_key(self, key_path: str):
        """
        加载公钥
        
        Args:
            key_path: 公钥文件路径
        """
        with open(key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
    
    def load_public_key_from_pem(self, pem_string: str):
        """
        从PEM字符串加载公钥
        
        Args:
            pem_string: PEM格式的公钥字符串
        """
        self.public_key = serialization.load_pem_public_key(
            pem_string.encode('utf-8'),
            backend=default_backend()
        )
    
    def save_private_key(self, key_path: str, password: Optional[str] = None):
        """
        保存私钥到文件
        
        Args:
            key_path: 私钥文件路径
            password: 密钥密码(可选)
        """
        if not self.private_key:
            raise ValueError("私钥未初始化")
        
        encryption = serialization.NoEncryption()
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())
        
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        with open(key_path, 'wb') as f:
            f.write(pem)
    
    def save_public_key(self, key_path: str):
        """
        保存公钥到文件
        
        Args:
            key_path: 公钥文件路径
        """
        if not self.public_key:
            raise ValueError("公钥未初始化")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(key_path, 'wb') as f:
            f.write(pem)
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密文本
        
        Args:
            plaintext: 明文
        
        Returns:
            Base64编码的密文
        """
        if not self.public_key:
            raise ValueError("公钥未初始化")
        
        ciphertext = self.public_key.encrypt(
            plaintext.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(ciphertext).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密文本
        
        Args:
            ciphertext: Base64编码的密文
        
        Returns:
            明文
        """
        if not self.private_key:
            raise ValueError("私钥未初始化")
        
        ciphertext_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        
        plaintext = self.private_key.decrypt(
            ciphertext_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext.decode('utf-8')
    
    def get_public_key_pem(self) -> str:
        """
        获取公钥的PEM格式字符串
        
        Returns:
            PEM格式的公钥字符串
        """
        if not self.public_key:
            raise ValueError("公钥未初始化")
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return pem.decode('utf-8')
    
    def get_private_key_pem(self, password: Optional[str] = None) -> str:
        """
        获取私钥的PEM格式字符串
        
        Args:
            password: 密钥密码(可选)
        
        Returns:
            PEM格式的私钥字符串
        """
        if not self.private_key:
            raise ValueError("私钥未初始化")
        
        encryption = serialization.NoEncryption()
        if password:
            encryption = serialization.BestAvailableEncryption(password.encode())
        
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        return pem.decode('utf-8')
