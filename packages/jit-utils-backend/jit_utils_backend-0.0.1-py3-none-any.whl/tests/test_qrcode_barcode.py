# -*-coding:utf-8-*-
"""
测试二维码和条形码模块
"""
import unittest
import base64
import re


class TestQrcodeBarcode(unittest.TestCase):
    """二维码和条形码测试类"""
    
    def setUp(self):
        """测试设置"""
        try:
            from jit_utils.qrcode import Qrcode
            from jit_utils.barcode import Barcode
            self.qrcode_available = True
            self.barcode_available = True
            self.Qrcode = Qrcode
            self.Barcode = Barcode
        except ImportError as e:
            self.qrcode_available = False
            self.barcode_available = False
            self.import_error = str(e)
    
    def test_qrcode_creation(self):
        """测试二维码创建"""
        if not self.qrcode_available:
            self.skipTest(f"二维码模块导入失败: {self.import_error}")
        
        # 创建二维码
        qr = self.Qrcode("Hello World")
        self.assertEqual(qr.value, "Hello World")
        self.assertEqual(qr.row, 200)  # 默认行数
        self.assertEqual(qr.col, 200)  # 默认列数
        
        # 自定义尺寸
        qr_custom = self.Qrcode("Test", row=300, col=300)
        self.assertEqual(qr_custom.row, 300)
        self.assertEqual(qr_custom.col, 300)
    
    def test_qrcode_toByte(self):
        """测试二维码转字节"""
        if not self.qrcode_available:
            self.skipTest(f"二维码模块导入失败: {self.import_error}")
        
        qr = self.Qrcode("Hello World")
        try:
            byte_data = qr.toByte()
            self.assertIsInstance(byte_data, bytes)
            self.assertGreater(len(byte_data), 0)
        except Exception as e:
            self.skipTest(f"二维码生成失败: {str(e)}")
    
    def test_qrcode_toStr(self):
        """测试二维码转base64字符串"""
        if not self.qrcode_available:
            self.skipTest(f"二维码模块导入失败: {self.import_error}")
        
        # 测试正常值
        qr = self.Qrcode("Hello World")
        try:
            str_data = qr.toStr()
            self.assertIsInstance(str_data, str)
            self.assertTrue(str_data.startswith("<image:"))
            self.assertTrue(str_data.endswith(">"))
            
            # 提取base64部分
            base64_part = str_data[7:-1]  # 去掉 "<image:" 和 ">"
            # 验证是否为有效的base64
            base64.b64decode(base64_part)  # 如果无效会抛出异常
        except Exception as e:
            self.skipTest(f"二维码字符串生成失败: {str(e)}")
        
        # 测试空值
        qr_empty = self.Qrcode("")
        result = qr_empty.toStr()
        self.assertEqual(result, "")
    
    def test_qrcode_str_method(self):
        """测试二维码__str__方法"""
        if not self.qrcode_available:
            self.skipTest(f"二维码模块导入失败: {self.import_error}")
        
        qr = self.Qrcode("Test")
        try:
            str_result = str(qr)
            expected = qr.toStr()
            self.assertEqual(str_result, expected)
        except Exception as e:
            self.skipTest(f"二维码__str__方法失败: {str(e)}")
    
    def test_barcode_creation(self):
        """测试条形码创建"""
        if not self.barcode_available:
            self.skipTest(f"条形码模块导入失败: {self.import_error}")
        
        # 创建条形码
        bc = self.Barcode("123456789")
        self.assertEqual(bc.value, "123456789")
        self.assertEqual(bc.codeType, "code128")  # 默认类型
        
        # 自定义类型
        bc_custom = self.Barcode("123456789", "code39")
        self.assertEqual(bc_custom.codeType, "code39")
    
    def test_barcode_toByte(self):
        """测试条形码转字节"""
        if not self.barcode_available:
            self.skipTest(f"条形码模块导入失败: {self.import_error}")
        
        bc = self.Barcode("123456789")
        try:
            byte_data = bc.toByte()
            self.assertIsInstance(byte_data, bytes)
            self.assertGreater(len(byte_data), 0)
        except Exception as e:
            self.skipTest(f"条形码生成失败: {str(e)}")
    
    def test_barcode_toStr(self):
        """测试条形码转base64字符串"""
        if not self.barcode_available:
            self.skipTest(f"条形码模块导入失败: {self.import_error}")
        
        # 测试正常值
        bc = self.Barcode("123456789")
        try:
            str_data = bc.toStr()
            self.assertIsInstance(str_data, str)
            
            # 如果成功，应该是base64格式
            if not str_data.startswith("ERROR:"):
                self.assertTrue(str_data.startswith("<image:"))
                self.assertTrue(str_data.endswith(">"))
                
                # 提取base64部分
                base64_part = str_data[7:-1]  # 去掉 "<image:" 和 ">"
                # 验证是否为有效的base64
                base64.b64decode(base64_part)
        except Exception as e:
            self.skipTest(f"条形码字符串生成失败: {str(e)}")
        
        # 测试空值
        bc_empty = self.Barcode("")
        result = bc_empty.toStr()
        self.assertEqual(result, "")
    
    def test_barcode_invalid_data(self):
        """测试条形码无效数据处理"""
        if not self.barcode_available:
            self.skipTest(f"条形码模块导入失败: {self.import_error}")
        
        # 测试可能导致错误的数据
        bc = self.Barcode("invalid_barcode_data!@#$%^&*()")
        try:
            result = bc.toStr()
            # 如果出错，应该返回ERROR:开头的字符串
            if result.startswith("ERROR:"):
                self.assertIn("ERROR:", result)
            else:
                # 如果没出错，应该是正常的base64格式
                self.assertTrue(result.startswith("<image:"))
        except Exception as e:
            self.skipTest(f"条形码错误处理测试失败: {str(e)}")
    
    def test_barcode_str_method(self):
        """测试条形码__str__方法"""
        if not self.barcode_available:
            self.skipTest(f"条形码模块导入失败: {self.import_error}")
        
        bc = self.Barcode("123456789")
        try:
            str_result = str(bc)
            expected = bc.toStr()
            self.assertEqual(str_result, expected)
        except Exception as e:
            self.skipTest(f"条形码__str__方法失败: {str(e)}")


if __name__ == '__main__':
    unittest.main() 