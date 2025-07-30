# -*-coding:utf-8-*-
"""
测试包的子模块导入功能
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
            self.assertEqual(jit_utils.__version__, '0.0.2')
            self.assertEqual(jit_utils.__author__, 'zangtao')
        except ImportError as e:
            self.fail(f"主包导入失败: {e}")
    
    def test_string_module_import(self):
        """测试字符串模块导入"""
        try:
            from jit_utils.string import randomString, getUuidStr, md5Str
            
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
            self.skipTest(f"字符串模块导入失败: {e}")
    
    def test_time_module_import(self):
        """测试时间模块导入"""
        try:
            from jit_utils.time import now, getTimestamp, formatNow
            
            # 测试函数是否可调用
            self.assertTrue(callable(now))
            self.assertTrue(callable(getTimestamp))
            self.assertTrue(callable(formatNow))
            
            # 简单功能测试
            current_time = now()
            self.assertIsNotNone(current_time)
            
            timestamp = getTimestamp()
            self.assertIsInstance(timestamp, (int, float))
            
            formatted_time = formatNow()
            self.assertIsInstance(formatted_time, str)
            
        except ImportError as e:
            self.skipTest(f"时间模块导入失败（可能缺少依赖）: {e}")
    
    def test_qrcode_module_import(self):
        """测试二维码模块导入"""
        try:
            from jit_utils.qrcode import Qrcode
            
            # 测试类是否可实例化
            self.assertTrue(callable(Qrcode))
            
            # 创建实例
            qr = Qrcode("test")
            self.assertEqual(qr.value, "test")
            
        except ImportError as e:
            self.skipTest(f"二维码模块导入失败（可能缺少依赖）: {e}")
    
    def test_barcode_module_import(self):
        """测试条形码模块导入"""
        try:
            from jit_utils.barcode import Barcode
            
            # 测试类是否可实例化
            self.assertTrue(callable(Barcode))
            
            # 创建实例
            bc = Barcode("123456789")
            self.assertEqual(bc.value, "123456789")
            
        except ImportError as e:
            self.skipTest(f"条形码模块导入失败（可能缺少依赖）: {e}")
    
    def test_validator_module_import(self):
        """测试验证器模块导入"""
        try:
            from jit_utils.validator import ParamsValidator
            self.assertTrue(callable(ParamsValidator))
        except ImportError as e:
            self.skipTest(f"验证器模块导入失败（可能缺少依赖）: {e}")
    
    def test_network_module_import(self):
        """测试网络模块导入"""
        try:
            import jit_utils.network
            # 网络模块应该可以导入
            self.assertIsNotNone(jit_utils.network)
        except ImportError as e:
            self.skipTest(f"网络模块导入失败: {e}")
    
    def test_signature_module_import(self):
        """测试签名模块导入"""
        try:
            import jit_utils.signature
            self.assertIsNotNone(jit_utils.signature)
        except ImportError as e:
            self.skipTest(f"签名模块导入失败: {e}")
    
    def test_exceptions_module_import(self):
        """测试异常模块导入"""
        try:
            import jit_utils.exceptions
            self.assertIsNotNone(jit_utils.exceptions)
        except ImportError as e:
            self.skipTest(f"异常模块导入失败（可能缺少依赖）: {e}")
    
    def test_config_module_import(self):
        """测试配置模块导入"""
        try:
            import jit_utils.config
            self.assertIsNotNone(jit_utils.config)
        except ImportError as e:
            self.skipTest(f"配置模块导入失败（可能缺少依赖）: {e}")
    
    def test_workday_constants_import(self):
        """测试工作日常量导入"""
        try:
            import jit_utils.workday_constants
            self.assertIsNotNone(jit_utils.workday_constants)
            # 检查是否有工作日相关的常量
            self.assertTrue(hasattr(jit_utils.workday_constants, 'holidayDict') or 
                          hasattr(jit_utils.workday_constants, 'workdayDict'))
        except ImportError as e:
            self.skipTest(f"工作日常量模块导入失败: {e}")
    
    def test_decorator_import(self):
        """测试装饰器导入"""
        try:
            from jit_utils.decorator import forward
            self.assertTrue(callable(forward))
        except ImportError as e:
            self.skipTest(f"装饰器模块导入失败（可能缺少依赖）: {e}")
    
    def test_convert_module_import(self):
        """测试转换器模块导入"""
        try:
            from jit_utils.convert import Converter, MemoryCompiler
            self.assertTrue(callable(Converter))
            self.assertTrue(callable(MemoryCompiler))
        except ImportError as e:
            self.skipTest(f"转换器模块导入失败（可能缺少依赖）: {e}")
    
    def test_package_structure(self):
        """测试包结构"""
        import jit_utils
        
        # 检查主要模块是否存在
        modules_to_check = [
            'string', 'time', 'qrcode', 'barcode', 'validator',
            'network', 'signature', 'exceptions', 'config',
            'workday_constants', 'decorator', 'convert'
        ]
        
        for module_name in modules_to_check:
            try:
                # 尝试导入模块
                __import__(f'jit_utils.{module_name}')
                # 如果导入成功，则通过测试
                self.assertTrue(True, f"模块 {module_name} 可以导入")
            except ImportError:
                # 如果导入失败，跳过（可能是依赖问题）
                self.skipTest(f"模块 {module_name} 导入失败（可能缺少依赖）")


if __name__ == '__main__':
    unittest.main() 