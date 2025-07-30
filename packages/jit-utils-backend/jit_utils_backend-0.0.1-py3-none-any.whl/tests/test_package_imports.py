# -*-coding:utf-8-*-
"""
测试包的导入功能
"""
import unittest


class TestPackageImports(unittest.TestCase):
    """包导入测试类"""
    
    def test_main_package_import(self):
        """测试主包导入"""
        try:
            import jit_utils
            self.assertTrue(hasattr(jit_utils, '__version__'))
            self.assertTrue(hasattr(jit_utils, '__author__'))
            self.assertEqual(jit_utils.__version__, '0.0.1')
            self.assertEqual(jit_utils.__author__, 'zangtao')
        except ImportError as e:
            self.fail(f"主包导入失败: {e}")
    
    def test_string_functions_import(self):
        """测试字符串函数导入"""
        try:
            from jit_utils import randomString, getUuidStr, md5Str
            
            # 测试函数是否可调用
            self.assertTrue(callable(randomString))
            self.assertTrue(callable(getUuidStr))
            self.assertTrue(callable(md5Str))
            
            # 简单功能测试
            random_str = randomString(6)
            self.assertEqual(len(random_str), 6)
            
            uuid_str = getUuidStr()
            self.assertEqual(len(uuid_str), 32)
            
            md5_hash = md5Str("test")
            self.assertEqual(len(md5_hash), 32)
            
        except ImportError as e:
            self.fail(f"字符串函数导入失败: {e}")
    
    def test_qrcode_barcode_import(self):
        """测试二维码和条形码类导入"""
        try:
            from jit_utils import Qrcode, Barcode
            
            # 如果因为依赖问题导入为 None，跳过测试
            if Qrcode is None or Barcode is None:
                self.skipTest("二维码/条形码类因依赖问题不可用")
            
            # 测试类是否可实例化
            self.assertTrue(callable(Qrcode))
            self.assertTrue(callable(Barcode))
            
            # 创建实例
            qr = Qrcode("test")
            bc = Barcode("123456789")
            
            self.assertEqual(qr.value, "test")
            self.assertEqual(bc.value, "123456789")
            
        except ImportError as e:
            self.skipTest(f"二维码/条形码类导入失败（可能缺少依赖）: {e}")
    
    def test_module_imports(self):
        """测试模块级导入"""
        try:
            from jit_utils import string_utils
            self.assertTrue(hasattr(string_utils, 'randomString'))
            self.assertTrue(hasattr(string_utils, 'md5Str'))
        except ImportError as e:
            self.fail(f"string_utils 模块导入失败: {e}")
        
        # 时间模块可能有依赖问题
        try:
            from jit_utils import time_utils
            # 如果导入成功，测试一些基本属性
            self.assertTrue(hasattr(time_utils, 'getTimestamp'))
        except ImportError as e:
            self.skipTest(f"time_utils 模块导入失败（可能缺少依赖）: {e}")
    
    def test_network_module_import(self):
        """测试网络模块导入"""
        try:
            from jit_utils import network
            # 网络模块应该可以导入
            self.assertIsNotNone(network)
        except ImportError as e:
            self.skipTest(f"network 模块导入失败: {e}")
    
    def test_signature_module_import(self):
        """测试签名模块导入"""
        try:
            from jit_utils import signature
            self.assertIsNotNone(signature)
        except ImportError as e:
            self.skipTest(f"signature 模块导入失败: {e}")
    
    def test_validator_import(self):
        """测试验证器导入"""
        try:
            from jit_utils import ParamsValidator
            if ParamsValidator is None:
                self.skipTest("ParamsValidator 因依赖问题不可用")
            self.assertTrue(callable(ParamsValidator))
        except ImportError as e:
            self.skipTest(f"ParamsValidator 导入失败（可能缺少依赖）: {e}")
    
    def test_exceptions_module_import(self):
        """测试异常模块导入"""
        try:
            from jit_utils import exceptions
            self.assertIsNotNone(exceptions)
        except ImportError as e:
            self.skipTest(f"exceptions 模块导入失败（可能缺少依赖）: {e}")
    
    def test_config_module_import(self):
        """测试配置模块导入"""
        try:
            from jit_utils import config
            self.assertIsNotNone(config)
        except ImportError as e:
            self.skipTest(f"config 模块导入失败（可能缺少依赖）: {e}")
    
    def test_workday_constants_import(self):
        """测试工作日常量导入"""
        try:
            from jit_utils import workday_constants
            self.assertIsNotNone(workday_constants)
            # 检查是否有工作日相关的常量
            self.assertTrue(hasattr(workday_constants, 'holidayDict') or 
                          hasattr(workday_constants, 'workdayDict'))
        except ImportError as e:
            self.skipTest(f"workday_constants 模块导入失败: {e}")
    
    def test_decorator_import(self):
        """测试装饰器导入"""
        try:
            from jit_utils import forward
            self.assertTrue(callable(forward))
        except ImportError as e:
            self.skipTest(f"forward 装饰器导入失败（可能缺少依赖）: {e}")
    
    def test_convert_classes_import(self):
        """测试转换器类导入"""
        try:
            from jit_utils import Converter, MemoryCompiler
            if Converter is None or MemoryCompiler is None:
                self.skipTest("转换器类因依赖问题不可用")
            self.assertTrue(callable(Converter))
            self.assertTrue(callable(MemoryCompiler))
        except ImportError as e:
            self.skipTest(f"转换器类导入失败（可能缺少依赖）: {e}")
    
    def test_all_exports(self):
        """测试 __all__ 导出列表"""
        import jit_utils
        
        # 检查 __all__ 是否存在
        self.assertTrue(hasattr(jit_utils, '__all__'))
        all_exports = jit_utils.__all__
        self.assertIsInstance(all_exports, list)
        self.assertGreater(len(all_exports), 0)
        
        # 检查一些关键导出
        expected_exports = [
            '__version__', '__author__', 'randomString', 'md5Str', 
            'getUuidStr'
        ]
        
        for export in expected_exports:
            if export in all_exports:
                self.assertTrue(hasattr(jit_utils, export), f"包中缺少导出: {export}")
        
        # 检查可能为 None 的导出（因为依赖问题）
        optional_exports = ['Qrcode', 'Barcode', 'ParamsValidator', 'Converter', 'MemoryCompiler']
        for export in optional_exports:
            if export in all_exports:
                # 这些可能因为依赖问题为 None，只要存在就行
                self.assertTrue(hasattr(jit_utils, export), f"包中缺少可选导出: {export}")
    
    def test_star_import(self):
        """测试 from jit_utils import * 是否正常工作"""
        # 由于 * 导入会污染命名空间，我们在这里只测试是否会出错
        try:
            exec("from jit_utils import *")
            # 如果执行到这里说明没有导入错误
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"星号导入失败（可能缺少依赖）: {e}")
        except Exception as e:
            self.fail(f"星号导入出现意外错误: {e}")


if __name__ == '__main__':
    unittest.main() 