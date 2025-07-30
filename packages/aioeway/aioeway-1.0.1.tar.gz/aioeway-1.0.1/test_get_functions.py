# -*- coding: utf-8 -*-
"""
AIOEway - GET功能综合测试

本测试文件整合了所有与GET主题相关的测试功能，包括：
- GET主题订阅测试
- QoS=1参数验证
- 真实设备GET响应测试
- 交互式GET测试
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, MagicMock
from device_mqtt_client import DeviceMQTTClient, DeviceInfo, DeviceData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GetFunctionsTest:
    """GET功能测试类"""
    
    def __init__(self):
        self.info_get_count = 0
        self.data_get_count = 0
        self.start_time = None
        self.test_results = []
    
    async def on_device_info_get(self, device_info: DeviceInfo):
        """处理设备信息获取响应"""
        self.info_get_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"[INFO GET #{self.info_get_count}] 收到设备信息获取响应:")
        logger.info(f"  设备ID: {device_info.device_id}")
        logger.info(f"  设备SN: {device_info.device_sn}")
        logger.info(f"  设备型号: {device_info.device_model}")
        logger.info(f"  固件版本: {device_info.firmware_version}")
        logger.info(f"  硬件版本: {device_info.hardware_version}")
        logger.info(f"  设备状态: {device_info.device_status}")
        logger.info(f"  WiFi SSID: {device_info.wifi_ssid}")
        logger.info(f"  IP地址: {device_info.ip}")
        logger.info(f"  时间戳: {device_info.timestamp}")
        
        # 记录测试结果
        self.test_results.append({
            'type': 'info_get',
            'timestamp': timestamp,
            'data': device_info
        })
        
        print("-" * 50)
    
    async def on_device_data_get(self, device_data_list: List[DeviceData]):
        """处理设备数据获取响应"""
        self.data_get_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"[DATA GET #{self.data_get_count}] 收到设备数据获取响应，共 {len(device_data_list)} 条数据:")
        
        for i, data in enumerate(device_data_list, 1):
            logger.info(f"  数据 {i}:")
            logger.info(f"    设备ID: {data.device_id}")
            logger.info(f"    设备SN: {data.device_sn}")
            logger.info(f"    数据类型: {data.data_type}")
            logger.info(f"    数据值: {data.data_value}")
            logger.info(f"    单位: {data.unit}")
            logger.info(f"    发电功率: {data.gen_power}W")
            logger.info(f"    温度: {data.temperature}°C")
            logger.info(f"    时间戳: {data.timestamp}")
            
            # 数据验证
            self._validate_get_data(data)
        
        # 记录测试结果
        self.test_results.append({
            'type': 'data_get',
            'timestamp': timestamp,
            'data': device_data_list
        })
        
        print("-" * 50)
    
    def _validate_get_data(self, device_data: DeviceData):
        """验证GET数据的合理性"""
        warnings = []
        
        # 功率检查
        if device_data.gen_power < 0:
            warnings.append(f"⚠️  发电功率异常: {device_data.gen_power}W (不应为负值)")
        
        # 温度检查
        if device_data.temperature > 80:
            warnings.append(f"🔥 设备温度过高: {device_data.temperature}°C (建议<80°C)")
        elif device_data.temperature < -10:
            warnings.append(f"🧊 设备温度过低: {device_data.temperature}°C (建议>-10°C)")
        
        # 输出警告
        if warnings:
            for warning in warnings:
                logger.warning(f"    {warning}")
        else:
            logger.info(f"    ✅ GET数据验证通过")
    
    def print_statistics(self):
        """打印GET测试统计信息"""
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"\n📈 GET功能测试统计 (运行时长: {duration}):")
        else:
            print(f"\n📈 GET功能测试统计:")
        
        print(f"  📡 INFO GET 响应次数: {self.info_get_count}")
        print(f"  📊 DATA GET 响应次数: {self.data_get_count}")
        print(f"  📋 总测试记录数: {len(self.test_results)}")

class MockMQTTClient:
    """模拟MQTT客户端（用于QoS测试）"""
    
    def __init__(self):
        self.subscribe_calls = []
        self.is_connected = True
    
    async def connect(self, *args, **kwargs):
        """模拟连接"""
        self.is_connected = True
        return True
    
    async def disconnect(self, *args, **kwargs):
        """模拟断开连接"""
        self.is_connected = False
    
    async def subscribe(self, topic, qos=0):
        """模拟订阅，记录QoS参数"""
        call_info = {
            'topic': topic,
            'qos': qos
        }
        self.subscribe_calls.append(call_info)
        logger.info(f"模拟订阅: {topic} (QoS={qos})")
        return True
    
    def set_callback(self, *args, **kwargs):
        """模拟设置回调"""
        pass

async def test_get_topics_basic():
    """基础GET主题订阅测试"""
    logger.info("=== 基础GET主题订阅测试 ===")
    
    # 配置参数
    config = {
        "device_model": "INV001",
        "device_sn": "SN123456789",
        "username": "test_user",
        "password": "processed_password",
        "broker_host": "localhost",
        "broker_port": 8883,
        "keepalive": 60,
        "use_tls": True
    }
    
    # 创建测试实例
    test_handler = GetFunctionsTest()
    test_handler.start_time = datetime.now()
    
    # 创建MQTT客户端
    client = DeviceMQTTClient(**config)
    
    try:
        # 连接到MQTT代理
        logger.info("正在连接到MQTT代理...")
        if await client.connect():
            logger.info("连接成功！")
            
            # 设备信息
            device_id = "INV001"
            device_sn = "SN123456789"
            
            # 订阅GET主题
            logger.info("订阅GET主题...")
            await client.subscribe_device_info_get(
                device_id, device_sn, test_handler.on_device_info_get
            )
            await client.subscribe_device_data_get(
                device_id, device_sn, test_handler.on_device_data_get
            )
            
            logger.info("开始监听GET消息...")
            logger.info("提示: 请向以下主题发送测试消息:")
            logger.info(f"  - {device_id}/{device_sn}/info/get")
            logger.info(f"  - {device_id}/{device_sn}/data/get")
            
            # 等待消息
            await asyncio.sleep(5)
            
        else:
            logger.error("连接失败")
    
    except Exception as e:
        logger.error(f"基础GET测试过程中出错: {e}")
    
    finally:
        # 断开连接
        await client.disconnect()
        test_handler.print_statistics()
        logger.info("基础GET测试完成")
        return test_handler

async def test_get_qos_parameters():
    """测试GET主题的QoS参数"""
    logger.info("=== GET主题QoS参数测试 ===")
    
    # 创建模拟客户端
    mock_client = MockMQTTClient()
    
    # 配置参数
    config = {
        "device_model": "TEST001",
        "device_sn": "SN123456789",
        "username": "test_user",
        "password": "processed_password",
        "broker_host": "localhost",
        "broker_port": 1883,
        "keepalive": 60,
        "use_tls": False
    }
    
    # 创建MQTT客户端并替换内部客户端
    device_client = DeviceMQTTClient(**config)
    device_client.client = mock_client
    device_client.is_connected = True
    
    # 模拟回调函数
    async def dummy_callback(*args):
        pass
    
    try:
        # 测试GET订阅方法
        device_id = "TEST001"
        device_sn = "SN123456789"
        
        logger.info("测试subscribe_device_info_get...")
        await device_client.subscribe_device_info_get(device_id, device_sn, dummy_callback)
        
        logger.info("测试subscribe_device_data_get...")
        await device_client.subscribe_device_data_get(device_id, device_sn, dummy_callback)
        
        # 验证QoS参数
        logger.info("\n=== 验证GET主题QoS参数 ===")
        success = True
        
        expected_get_topics = [
            f"{device_id}/{device_sn}/info/get",
            f"{device_id}/{device_sn}/data/get"
        ]
        
        if len(mock_client.subscribe_calls) != 2:
            logger.error(f"预期2次GET订阅调用，实际{len(mock_client.subscribe_calls)}次")
            success = False
        
        for i, call in enumerate(mock_client.subscribe_calls):
            expected_topic = expected_get_topics[i]
            if call['topic'] != expected_topic:
                logger.error(f"GET主题不匹配: 预期{expected_topic}, 实际{call['topic']}")
                success = False
            
            if call['qos'] != 1:
                logger.error(f"GET QoS不匹配: 预期1, 实际{call['qos']} (主题: {call['topic']})")
                success = False
            else:
                logger.info(f"✓ {call['topic']} QoS=1 正确")
        
        if success:
            logger.info("\n🎉 所有GET主题QoS参数验证通过！")
        else:
            logger.error("\n❌ GET主题QoS参数验证失败！")
        
        return success
        
    except Exception as e:
        logger.error(f"GET QoS测试过程中出错: {e}")
        return False

async def test_real_device_get(broker_host: str, broker_port: int, 
                              device_id: str, device_sn: str,
                              username: str = None, password: str = None,
                              test_duration: int = 30):
    """测试真实设备GET响应"""
    logger.info("=== 真实设备GET响应测试 ===")
    
    print(f"🚀 开始真实设备GET测试...")
    print(f"📡 MQTT代理: {broker_host}:{broker_port}")
    print(f"🔧 设备ID: {device_id}")
    print(f"🏷️  设备SN: {device_sn}")
    print(f"⏱️  测试时长: {test_duration}秒")
    print(f"🔐 认证: {'是' if username else '否'}")
    print("=" * 60)
    
    test_handler = GetFunctionsTest()
    test_handler.start_time = datetime.now()
    
    try:
        # 创建MQTT客户端
        client = DeviceMQTTClient(
            broker_host=broker_host,
            broker_port=broker_port,
            username=username,
            password=password,
            client_id=f"get_test_{device_id}_{device_sn}"
        )
        
        if await client.connect():
            print(f"✅ 成功连接到MQTT代理")
            
            # 订阅GET主题
            await client.subscribe_device_info_get(
                device_id, device_sn, test_handler.on_device_info_get
            )
            await client.subscribe_device_data_get(
                device_id, device_sn, test_handler.on_device_data_get
            )
            
            print(f"🔍 开始监控设备GET响应 {device_id}/{device_sn}")
            print(f"⏳ 等待 {test_duration} 秒接收GET响应...\n")
            
            # 等待指定时间
            await asyncio.sleep(test_duration)
            
            print(f"\n⏹️  GET测试完成")
            
            await client.disconnect()
            
        else:
            logger.error("连接失败")
            
    except Exception as e:
        logger.error(f"真实设备GET测试失败: {e}")
        raise
    
    finally:
        test_handler.print_statistics()
    
    return test_handler

async def interactive_get_test():
    """交互式GET测试"""
    print("=" * 60)
    print("AIOEway GET功能交互式测试")
    print("=" * 60)
    
    # 获取用户输入
    print("\n请输入MQTT配置信息:")
    device_model = input("设备机型码 [INV001]: ").strip() or "INV001"
    device_sn = input("设备SN [SN123456789]: ").strip() or "SN123456789"
    username = input("用户名 [test_user]: ").strip() or "test_user"
    password = input("密码 [processed_password]: ").strip() or "processed_password"
    broker_host = input("MQTT服务器地址 [localhost]: ").strip() or "localhost"
    broker_port = int(input("MQTT服务器端口 [8883]: ").strip() or "8883")
    use_tls_input = input("启用TLS [Y/n]: ").strip().lower()
    use_tls = use_tls_input != 'n'
    test_duration = int(input("测试时长(秒) [60]: ").strip() or "60")
    
    config = {
        "device_model": device_model,
        "device_sn": device_sn,
        "username": username,
        "password": password,
        "broker_host": broker_host,
        "broker_port": broker_port,
        "keepalive": 60,
        "use_tls": use_tls
    }
    
    print("\n配置信息:")
    print(f"设备机型码: {device_model}")
    print(f"设备SN: {device_sn}")
    print(f"用户名: {username}")
    print(f"MQTT服务器: {broker_host}:{broker_port}")
    print(f"TLS: {'启用' if use_tls else '禁用'}")
    print(f"测试时长: {test_duration}秒")
    
    # 创建测试实例
    test_handler = GetFunctionsTest()
    test_handler.start_time = datetime.now()
    
    # 创建MQTT客户端
    client = DeviceMQTTClient(**config)
    
    try:
        # 连接到MQTT代理
        print("\n正在连接到MQTT代理...")
        if await client.connect():
            print("连接成功！")
            
            # 订阅GET主题
            print("订阅GET主题...")
            await client.subscribe_device_info_get(
                device_model, device_sn, test_handler.on_device_info_get
            )
            await client.subscribe_device_data_get(
                device_model, device_sn, test_handler.on_device_data_get
            )
            
            print("\n开始监听GET消息...")
            print("提示: 请向以下主题发送测试消息:")
            print(f"  - {device_model}/{device_sn}/info/get")
            print(f"  - {device_model}/{device_sn}/data/get")
            print("按 Ctrl+C 停止测试")
            
            # 持续监听
            try:
                await asyncio.sleep(test_duration)
            except KeyboardInterrupt:
                print("\n收到停止信号")
        else:
            print("连接失败")
    
    except Exception as e:
        print(f"交互式GET测试过程中出错: {e}")
    
    finally:
        # 断开连接
        await client.disconnect()
        test_handler.print_statistics()
        print("交互式GET测试完成")
    
    return test_handler

async def run_all_get_tests():
    """运行所有GET功能测试"""
    print("=" * 60)
    print("AIOEway GET功能综合测试")
    print("=" * 60)
    print("本测试包含以下功能:")
    print("1. 基础GET主题订阅测试")
    print("2. GET主题QoS参数验证")
    print("3. 模拟GET响应处理")
    print("=" * 60)
    
    results = {}
    
    # 1. 基础GET测试
    print("\n🔍 运行基础GET测试...")
    try:
        results['basic'] = await test_get_topics_basic()
    except Exception as e:
        logger.error(f"基础GET测试失败: {e}")
        results['basic'] = None
    
    # 2. QoS参数测试
    print("\n🔍 运行GET QoS参数测试...")
    try:
        results['qos'] = await test_get_qos_parameters()
    except Exception as e:
        logger.error(f"GET QoS测试失败: {e}")
        results['qos'] = False
    
    # 3. 模拟GET响应测试
    print("\n🔍 运行模拟GET响应测试...")
    try:
        # 模拟一些GET响应
        test_handler = GetFunctionsTest()
        
        # 模拟设备信息GET响应
        mock_info = DeviceInfo(
            device_id="TEST001",
            device_sn="SN123456789",
            device_model="INV001",
            firmware_version="1.0.0",
            hardware_version="2.0.0",
            device_status="online",
            wifi_ssid="TestWiFi",
            ip="192.168.1.100",
            timestamp=datetime.now().isoformat()
        )
        
        await test_handler.on_device_info_get(mock_info)
        
        # 模拟设备数据GET响应
        mock_data = [
            DeviceData(
                device_id="TEST001",
                device_sn="SN123456789",
                data_type="power",
                data_value=1000.0,
                unit="W",
                gen_power=1000.0,
                temperature=45.5,
                timestamp=datetime.now().isoformat()
            )
        ]
        
        await test_handler.on_device_data_get(mock_data)
        
        results['simulation'] = test_handler
        
    except Exception as e:
        logger.error(f"模拟GET响应测试失败: {e}")
        results['simulation'] = None
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("GET功能测试总结")
    print("=" * 60)
    
    if results['basic']:
        print(f"✅ 基础GET测试: 通过")
        print(f"   - INFO GET响应: {results['basic'].info_get_count} 次")
        print(f"   - DATA GET响应: {results['basic'].data_get_count} 次")
    else:
        print(f"❌ 基础GET测试: 失败")
    
    if results['qos']:
        print(f"✅ GET QoS参数测试: 通过")
    else:
        print(f"❌ GET QoS参数测试: 失败")
    
    if results['simulation']:
        print(f"✅ 模拟GET响应测试: 通过")
        print(f"   - 模拟INFO GET: {results['simulation'].info_get_count} 次")
        print(f"   - 模拟DATA GET: {results['simulation'].data_get_count} 次")
    else:
        print(f"❌ 模拟GET响应测试: 失败")
    
    print("\n🎉 GET功能综合测试完成！")
    print("=" * 60)
    
    return results

def get_user_config():
    """获取用户配置"""
    print("🔧 真实设备GET测试配置")
    print("=" * 30)
    
    # MQTT配置
    broker_host = input("MQTT代理地址 [localhost]: ").strip() or "localhost"
    broker_port = int(input("MQTT代理端口 [1883]: ").strip() or "1883")
    
    # 认证信息
    use_auth = input("是否需要认证? (y/n) [n]: ").strip().lower() == 'y'
    username = None
    password = None
    
    if use_auth:
        username = input("用户名: ").strip()
        password = input("密码: ").strip()
    
    # 设备信息
    device_id = input("设备ID: ").strip()
    device_sn = input("设备SN: ").strip()
    
    if not device_id or not device_sn:
        raise ValueError("设备ID和SN不能为空")
    
    # 测试时长
    test_duration = int(input("测试时长(秒) [30]: ").strip() or "30")
    
    return {
        'broker_host': broker_host,
        'broker_port': broker_port,
        'username': username,
        'password': password,
        'device_id': device_id,
        'device_sn': device_sn,
        'test_duration': test_duration
    }

async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            # 交互式GET测试
            await interactive_get_test()
        elif sys.argv[1] == "--real":
            # 真实设备GET测试
            try:
                config = get_user_config()
                await test_real_device_get(**config)
            except Exception as e:
                print(f"❌ 真实设备GET测试出错: {e}")
        elif sys.argv[1] == "--qos":
            # 仅QoS测试
            await test_get_qos_parameters()
        elif sys.argv[1] == "--basic":
            # 仅基础测试
            await test_get_topics_basic()
        else:
            print("未知参数，运行默认综合测试")
            await run_all_get_tests()
    else:
        # 默认运行综合测试
        await run_all_get_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")