#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
告警分析系统使用示例

展示如何使用改进后的工作流进行告警分类和分析
"""

from workflow import analyze_alert

def test_aladdin_error():
    """测试Aladdin错误分析"""
    alert_details = """
    告警时间: 2024-01-15 14:30:22
    告警级别: ERROR
    错误信息: Aladdin bridge call failed with error code 10015
    用户ID: user_12345
    设备型号: iPhone 14 Pro
    APP版本: 3.2.1
    操作系统: iOS 16.1
    错误详情: 调用aladdin.getUserInfo()时返回错误码10015，无法获取用户信息
    """
    
    print("=" * 60)
    print("测试 Aladdin 错误分析")
    print("=" * 60)
    result = analyze_alert(alert_details)
    print("\n分析结果:")
    print(result)

def test_javascript_error():
    """测试JavaScript错误分析"""
    alert_details = """
    告警时间: 2024-01-15 15:45:33
    告警级别: ERROR
    错误类型: TypeError
    错误信息: Cannot read property 'length' of undefined
    堆栈信息:
      at processData (https://example.com/js/main.js:245:12)
      at handleResponse (https://example.com/js/api.js:89:5)
      at XMLHttpRequest.onload (https://example.com/js/api.js:156:7)
    浏览器: Chrome 120.0.0.0
    用户代理: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
    页面URL: https://example.com/dashboard
    用户ID: user_67890
    """
    
    print("=" * 60)
    print("测试 JavaScript 错误分析")
    print("=" * 60)
    result = analyze_alert(alert_details)
    print("\n分析结果:")
    print(result)

def test_backend_api_error():
    """测试后端API错误分析"""
    alert_details = """
    告警时间: 2024-01-15 16:20:15
    告警级别: CRITICAL
    接口路径: /api/v1/user/profile
    HTTP状态码: 500
    错误信息: Internal Server Error
    响应时间: 5.2秒
    请求方法: GET
    请求参数: user_id=12345
    服务器: web-server-03
    数据库连接池状态: 95% 使用率
    错误日志: 
      java.sql.SQLException: Connection timeout
      at com.example.service.UserService.getProfile(UserService.java:156)
      at com.example.controller.UserController.getProfile(UserController.java:89)
    """
    
    print("=" * 60)
    print("测试 后端API 错误分析")
    print("=" * 60)
    result = analyze_alert(alert_details)
    print("\n分析结果:")
    print(result)

if __name__ == "__main__":
    print("智能告警分析系统示例\n")
    
    # 可以选择运行特定测试
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "aladdin":
            test_aladdin_error()
        elif test_type == "javascript":
            test_javascript_error()
        elif test_type == "backend":
            test_backend_api_error()
        else:
            print(f"未知测试类型: {test_type}")
            print("可用选项: aladdin, javascript, backend")
    else:
        # 运行所有测试
        test_aladdin_error()
        print("\n" + "="*80 + "\n")
        test_javascript_error()
        print("\n" + "="*80 + "\n")
        test_backend_api_error() 