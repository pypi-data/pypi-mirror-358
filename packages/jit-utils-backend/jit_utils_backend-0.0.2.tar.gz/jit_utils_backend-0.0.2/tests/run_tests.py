#!/usr/bin/env python3
# -*-coding:utf-8-*-
"""
JIT Utils Backend 测试运行器

运行所有测试并生成报告
"""
import sys
import unittest
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_all_tests():
    """运行所有测试"""
    # 发现测试目录中的所有测试
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    if result.skipped:
        print("\n跳过的测试:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n成功率: {success_rate:.1f}%")
    
    return result.wasSuccessful()


def run_specific_test(test_name):
    """运行特定的测试模块"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # 动态导入测试模块
        test_module = __import__(f'tests.{test_name}', fromlist=[test_name])
        
        # 创建测试套件
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"无法导入测试模块 '{test_name}': {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        if not test_name.startswith('test_'):
            test_name = f'test_{test_name}'
        
        print(f"运行测试模块: {test_name}")
        success = run_specific_test(test_name)
    else:
        # 运行所有测试
        print("运行所有测试...")
        success = run_all_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 