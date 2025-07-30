# -*-coding:utf-8-*-
"""
测试字符串工具模块
"""
import unittest
import re
import os
import tempfile
from jit_utils.string import (
    randomString, randomNum, getUuidStr, md5Bytes, md5Str, 
    lowercase, capitalize, getFileMd5, getRandomField, getRandom,
    genrSublist, renderTemplateString
)


class TestStringUtils(unittest.TestCase):
    """字符串工具测试类"""
    
    def test_randomString(self):
        """测试随机字符串生成"""
        # 测试默认长度
        result = randomString()
        self.assertEqual(len(result), 8)
        self.assertTrue(result.isalnum())
        
        # 测试自定义长度
        result = randomString(12)
        self.assertEqual(len(result), 12)
        self.assertTrue(result.isalnum())
        
        # 测试两次生成的结果不同（概率很高）
        result1 = randomString(20)
        result2 = randomString(20)
        self.assertNotEqual(result1, result2)
    
    def test_randomNum(self):
        """测试随机数字生成"""
        # 测试默认6位数字
        result = randomNum()
        self.assertEqual(len(result), 6)
        self.assertTrue(result.isdigit())
        
        # 测试自定义位数
        result = randomNum(4)
        self.assertEqual(len(result), 4)
        self.assertTrue(result.isdigit())
        
        # 测试两次生成的结果不同（概率很高）
        result1 = randomNum(8)
        result2 = randomNum(8)
        self.assertNotEqual(result1, result2)
    
    def test_getUuidStr(self):
        """测试UUID字符串生成"""
        result = getUuidStr()
        # UUID去掉连字符后应该是32位十六进制字符串
        self.assertEqual(len(result), 32)
        self.assertTrue(re.match(r'^[a-f0-9]{32}$', result))
        
        # 测试两次生成的UUID不同
        result1 = getUuidStr()
        result2 = getUuidStr()
        self.assertNotEqual(result1, result2)
    
    def test_md5Bytes(self):
        """测试字节数据MD5加密"""
        test_data = b"hello world"
        result = md5Bytes(test_data)
        expected = "5eb63bbbe01eeed093cb22bb8f5acdc3"
        self.assertEqual(result, expected)
        
        # 测试空字节
        result = md5Bytes(b"")
        expected = "d41d8cd98f00b204e9800998ecf8427e"
        self.assertEqual(result, expected)
    
    def test_md5Str(self):
        """测试字符串MD5加密"""
        test_str = "hello world"
        result = md5Str(test_str)
        expected = "5eb63bbbe01eeed093cb22bb8f5acdc3"
        self.assertEqual(result, expected)
        
        # 测试不同编码
        result = md5Str("你好", "utf-8")
        self.assertEqual(len(result), 32)
        self.assertTrue(re.match(r'^[a-f0-9]{32}$', result))
    
    def test_lowercase(self):
        """测试首字母小写"""
        self.assertEqual(lowercase("Hello"), "hello")
        self.assertEqual(lowercase("WORLD"), "wORLD")
        self.assertEqual(lowercase("a"), "a")
        self.assertEqual(lowercase(""), "")
    
    def test_capitalize(self):
        """测试首字母大写"""
        self.assertEqual(capitalize("hello"), "Hello")
        self.assertEqual(capitalize("world"), "World")
        self.assertEqual(capitalize("A"), "A")
        self.assertEqual(capitalize(""), "")
    
    def test_getFileMd5(self):
        """测试文件MD5计算"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("hello world")
            temp_file = f.name
        
        try:
            result = getFileMd5(temp_file)
            expected = "5eb63bbbe01eeed093cb22bb8f5acdc3"
            self.assertEqual(result, expected)
        finally:
            os.unlink(temp_file)
        
        # 测试不存在的文件
        result = getFileMd5("non_existent_file.txt")
        self.assertIsNone(result)
    
    def test_getRandomField(self):
        """测试随机字段名生成"""
        result = getRandomField()
        self.assertTrue(result.startswith("fk"))
        self.assertEqual(len(result), 6)  # "fk" + 4个字符
        
        result = getRandomField(6)
        self.assertTrue(result.startswith("fk"))
        self.assertEqual(len(result), 8)  # "fk" + 6个字符
    
    def test_getRandom(self):
        """测试随机字符串生成（小写字母+数字）"""
        result = getRandom()
        self.assertEqual(len(result), 8)
        self.assertTrue(re.match(r'^[a-z0-9]+$', result))
        
        result = getRandom(12)
        self.assertEqual(len(result), 12)
        self.assertTrue(re.match(r'^[a-z0-9]+$', result))
    
    def test_genrSublist(self):
        """测试列表分割"""
        test_list = list(range(10))
        result = list(genrSublist(test_list, 3))
        
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        self.assertEqual(result, expected)
        
        # 测试整除的情况
        test_list = list(range(9))
        result = list(genrSublist(test_list, 3))
        expected = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        self.assertEqual(result, expected)
    
    def test_renderTemplateString(self):
        """测试模板字符串渲染"""
        template = "Hello {{name}}, you are {{age}} years old"
        result = renderTemplateString(template, name="Alice", age=25)
        expected = "Hello Alice, you are 25 years old"
        self.assertEqual(result, expected)
        
        # 测试缺失变量
        result = renderTemplateString("Hello {{name}}", age=25)
        expected = "Hello "
        self.assertEqual(result, expected)
        
        # 测试无变量
        result = renderTemplateString("Hello World")
        expected = "Hello World"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main() 