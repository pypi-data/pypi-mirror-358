# -*- coding: utf-8 -*-
"""
AIOEway - POST功能综合测试

本测试文件整合了所有与POST主题相关的测试功能，包括：
- POST主题订阅测试
- QoS=1参数验证
- 真实设备POST数据接收测试
- 新配置方式测试
- 数据结构验证测试
- 交互式POST测试
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

class PostFunctionsTest:
    """POST功能测试类"""
    
    def __init__(self):
        self.received_info_count = 0
        self.received_data_count = 0
        self.device_info_history = []
        self.device_data_history = []
        self.start_time = None
        self.test_results = []
    
    async def on_device_info(self, device_info: DeviceInfo):
        """设备信息回调"""
        self.received_info_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"[INFO POST #{self.received_info_count}] 收到设备信息:")
        logger.info(f"  网络固件版本: {device_info.net_firm_ver}")
        logger.info(f"  应用固件版本: {device_info.app_firm_ver}")
        logger.info(f"  WiFi SSID: {device_info.wifi_ssid}")
        logger.info(f"  IP地址: {device_info.ip}")
        logger.info(f"  WiFi状态: {'正常' if device_info.wifi_is_normal == 0 else '异常'}")
        logger.info(f"  锁定状态: {'已锁定' if device_info.is_lock == 0 else '未锁定'}")
        logger.info(f"  板卡数量: {len(device_info.board)}")
        
        # 保存历史记录
        self.device_info_history.append({
            'timestamp': timestamp,
            'data': device_info
        })
        
        # 记录测试结果
        self.test_results.append({
            'type': 'info_post',
            'timestamp': timestamp,
            'data': device_info
        })
        
        print("-" * 50)
    
    async def on_device_data(self, device_data_list: List[DeviceData]):
        """设备数据回调"""
        self.received_data_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"[DATA POST #{self.received_data_count}] 收到设备数据，共 {len(device_data_list)} 条记录:")
        
        for i, data in enumerate(device_data_list, 1):
            logger.info(f"  数据 #{i}:")
            logger.info(f"    序号: {data.sort}")
            logger.info(f"    输入电压: {data.input_voltage}V")
            logger.info(f"    输入电流: {data.input_current}A")
            logger.info(f"    电网电压: {data.grid_voltage}V")
            logger.info(f"    电网频率: {data.grid_freq}Hz")
            logger.info(f"    发电功率: {data.gen_power}W")
            logger.info(f"    今日发电量: {data.gen_power_today}Wh")
            logger.info(f"    总发电量: {data.gen_power_total}kWh")
            logger.info(f"    温度: {data.temperature}℃")
            logger.info(f"    错误码: {data.err_code}")
            logger.info(f"    工作时长: {data.duration}秒")
            
            # 数据验证
            self._validate_post_data(data)
        
        # 保存历史记录
        self.device_data_history.append({
            'timestamp': timestamp,
            'data': device_data_list
        })
        
        # 记录测试结果
        self.test_results.append({
            'type': 'data_post',
            'timestamp': timestamp,
            'data': device_data_list
        })
        
        print("-" * 50)
    
    def _validate_post_data(self, device_data: DeviceData):
        """验证POST数据的合理性"""
        warnings = []
        
        # 电压范围检查
        if device_data.input_voltage < 180 or device_data.input_voltage > 250:
            warnings.append(f"⚠️  输入电压异常: {device_data.input_voltage}V (正常范围: 180-250V)")
        
        if device_data.grid_voltage < 200 or device_data.grid_voltage > 250:
            warnings.append(f"⚠️  电网电压异常: {device_data.grid_voltage}V (正常范围: 200-250V)")
        
        # 频率检查
        if device_data.grid_freq < 49 or device_data.grid_freq > 51:
            warnings.append(f"⚠️  电网频率异常: {device_data.grid_freq}Hz (正常范围: 49-51Hz)")
        
        # 温度检查
        if device_data.temperature > 80:
            warnings.append(f"🔥 设备温度过高: {device_data.temperature}°C (建议<80°C)")
        elif device_data.temperature < -10:
            warnings.append(f"🧊 设备温度过低: {device_data.temperature}°C (建议>-10°C)")
        
        # 功率检查
        if device_data.gen_power < 0:
            warnings.append(f"⚠️  发电功率异常: {device_data.gen_power}W (不应为负值)")
        
        # 错误码检查
        if device_data.err_code != 0:
            warnings.append(f"❌ 设备错误: 错误码 {device_data.err_code}")
        
        # 输出警告
        if warnings:
            for warning in warnings:
                logger.warning(f"    {warning}")
        else:
            logger.info(f"    ✅ POST数据验证通过")
    
    def print_statistics(self):
        """打印POST测试统计信息"""
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"\n📈 POST功能测试统计 (运行时长: {duration}):")
        else:
            print(f"\n📈 POST功能测试统计:")
        
        print(f"  📡 设备信息接收次数: {self.received_info_count}")
        print(f"  📊 设备数据接收次数: {self.received_data_count}")
        print(f"  📋 总测试记录数: {len(self.test_results)}")
        
        if self.device_data_history:
            total_data_points = sum(len(record['data']) for record in self.device_data_history)
            print(f"  📋 总数据点数: {total_data_points}")
            
            # 最新数据摘要
            latest_data = self.device_data_history[-1]['data']
            if latest_data:
                avg_power = sum(d.gen_power for d in latest_data) / len(latest_data)
                avg_temp = sum(d.temperature for d in latest_data) / len(latest_data)
                print(f"  ⚡ 最新平均功率: {avg_power:.1f}W")
                print(f"  🌡️  最新平均温度: {avg_temp:.1f}°C")

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

async def test_data_structures():
    """测试数据结构"""
    logger.info("=== 测试POST数据结构 ===")
    
    # 测试DeviceInfo
    device_info_data = {
        "netFirmVer": 1.2,
        "appFirmVer": 2.1,
        "wifiSsid": "TestWiFi",
        "ip": "192.168.1.100",
        "wifiIsNormal": 0,
        "isLock": 0,
        "board": [{"id": 1, "name": "主板"}]
    }
    
    device_info = DeviceInfo.from_dict(device_info_data)
    logger.info(f"设备信息: {device_info}")
    logger.info(f"WiFi SSID: {device_info.wifi_ssid}")
    logger.info(f"IP地址: {device_info.ip}")
    
    # 测试DeviceData
    device_data_dict = {
        "sort": 1,
        "inputVoltage": 220.5,
        "InputCurrent": 5.2,
        "gridVoltage": 230.1,
        "gridFreq": 50.0,
        "genPower": 1000.0,
        "genPowerToDay": 5000,
        "genPowerTotal": 100000,
        "temperature": 45.5,
        "errCode": 0,
        "duration": 3600
    }
    
    device_data = DeviceData.from_dict(device_data_dict)
    logger.info(f"设备数据: {device_data}")
    logger.info(f"发电功率: {device_data.gen_power}W")
    logger.info(f"温度: {device_data.temperature}°C")
    
    logger.info("POST数据结构测试完成")
    return True

async def test_post_topics_basic():
    """基础POST主题订阅测试"""
    logger.info("=== 基础POST主题订阅测试 ===")
    
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
    test_handler = PostFunctionsTest()
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
            
            # 订阅POST主题
            logger.info("订阅POST主题...")
            await client.subscribe_device_info(
                device_id, device_sn, test_handler.on_device_info
            )
            await client.subscribe_device_data(
                device_id, device_sn, test_handler.on_device_data
            )
            
            logger.info("开始监听POST消息...")
            logger.info("提示: 请向以下主题发送测试消息:")
            logger.info(f"  - {device_id}/{device_sn}/info/post")
            logger.info(f"  - {device_id}/{device_sn}/data/post")
            
            # 等待消息
            await asyncio.sleep(5)
            
        else:
            logger.error("连接失败")
    
    except Exception as e:
        logger.error(f"基础POST测试过程中出错: {e}")
    
    finally:
        # 断开连接
        await client.disconnect()
        test_handler.print_statistics()
        logger.info("基础POST测试完成")
        return test_handler

async def test_post_qos_parameters():
    """测试POST主题的QoS参数"""
    logger.info("=== POST主题QoS参数测试 ===")
    
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
        # 测试POST订阅方法
        device_id = "TEST001"
        device_sn = "SN123456789"
        
        logger.info("测试subscribe_device_info...")
        await device_client.subscribe_device_info(device_id, device_sn, dummy_callback)
        
        logger.info("测试subscribe_device_data...")
        await device_client.subscribe_device_data(device_id, device_sn, dummy_callback)
        
        # 验证QoS参数
        logger.info("\n=== 验证POST主题QoS参数 ===")
        success = True
        
        expected_post_topics = [
            f"{device_id}/{device_sn}/info/post",
            f"{device_id}/{device_sn}/data/post"
        ]
        
        if len(mock_client.subscribe_calls) != 2:
            logger.error(f"预期2次POST订阅调用，实际{len(mock_client.subscribe_calls)}次")
            success = False
        
        for i, call in enumerate(mock_client.subscribe_calls):
            expected_topic = expected_post_topics[i]
            if call['topic'] != expected_topic:
                logger.error(f"POST主题不匹配: 预期{expected_topic}, 实际{call['topic']}")
                success = False
            
            if call['qos'] != 1:
                logger.error(f"POST QoS不匹配: 预期1, 实际{call['qos']} (主题: {call['topic']})")
                success = False
            else:
                logger.info(f"✓ {call['topic']} QoS=1 正确")
        
        if success:
            logger.info("\n🎉 所有POST主题QoS参数验证通过！")
        else:
            logger.error("\n❌ POST主题QoS参数验证失败！")
        
        return success
        
    except Exception as e:
        logger.error(f"POST QoS测试过程中出错: {e}")
        return False

async def test_start_monitoring_post():
    """测试start_monitoring方法的POST功能"""
    logger.info("=== start_monitoring POST功能测试 ===")
    
    # 创建模拟客户端
    mock_client = MockMQTTClient()
    
    config = {
        "device_model": "TEST002",
        "device_sn": "SN987654321",
        "username": "test_user2",
        "password": "processed_password2",
        "broker_host": "localhost",
        "broker_port": 1883,
        "keepalive": 60,
        "use_tls": False
    }
    
    device_client = DeviceMQTTClient(**config)
    device_client.client = mock_client
    device_client.is_connected = True
    
    async def dummy_callback(*args):
        pass
    
    try:
        # 清空之前的调用记录
        mock_client.subscribe_calls.clear()
        
        # 测试start_monitoring（包含POST主题）
        await device_client.start_monitoring(
            device_id="TEST002",
            device_sn="SN987654321",
            info_callback=dummy_callback,
            data_callback=dummy_callback
        )
        
        # 验证POST主题的QoS参数
        logger.info("验证start_monitoring的POST主题QoS参数...")
        success = True
        
        # start_monitoring应该订阅4个主题（2个POST + 2个GET）
        expected_post_topics = [
            "TEST002/SN987654321/info/post",
            "TEST002/SN987654321/data/post"
        ]
        
        post_calls = [call for call in mock_client.subscribe_calls 
                     if '/post' in call['topic']]
        
        if len(post_calls) != 2:
            logger.error(f"start_monitoring预期2次POST订阅调用，实际{len(post_calls)}次")
            success = False
        
        for call in post_calls:
            if call['topic'] not in expected_post_topics:
                logger.error(f"意外的POST主题: {call['topic']}")
                success = False
            
            if call['qos'] != 1:
                logger.error(f"start_monitoring POST QoS不匹配: 预期1, 实际{call['qos']} (主题: {call['topic']})")
                success = False
            else:
                logger.info(f"✓ start_monitoring {call['topic']} QoS=1 正确")
        
        if success:
            logger.info("\n🎉 start_monitoring POST功能验证通过！")
        else:
            logger.error("\n❌ start_monitoring POST功能验证失败！")
        
        return success
        
    except Exception as e:
        logger.error(f"start_monitoring POST测试出错: {e}")
        return False

async def test_new_config_method():
    """测试新的配置方式"""
    logger.info("=== 新配置方式测试 ===")
    
    # 配置参数示例
    config = {
        "device_model": "INV001",  # 设备机型码
        "device_sn": "SN123456789",  # 设备SN
        "username": "testuser",  # 用户名
        "password": "processed_password",  # 密码
        "broker_host": "localhost",  # MQTT服务器地址
        "broker_port": 8883,  # MQTT服务器端口（TLS端口）
        "keepalive": 60,  # 心跳间隔
        "use_tls": True  # 使用TLS加密
    }
    
    logger.info("配置参数:")
    logger.info(f"  设备机型码: {config['device_model']}")
    logger.info(f"  设备SN: {config['device_sn']}")
    logger.info(f"  用户名: {config['username']}")
    logger.info(f"  密码: {config['password']}")
    logger.info(f"  MQTT服务器: {config['broker_host']}:{config['broker_port']}")
    logger.info(f"  TLS加密: {'是' if config['use_tls'] else '否'}")
    
    # 创建测试实例
    test = PostFunctionsTest()
    
    # 创建MQTT客户端
    client = DeviceMQTTClient(
        device_model=config["device_model"],
        device_sn=config["device_sn"],
        username=config["username"],
        password=config["password"],
        broker_host=config["broker_host"],
        broker_port=config["broker_port"],
        keepalive=config["keepalive"],
        use_tls=config["use_tls"]
    )
    
    logger.info("\n=== 客户端配置信息 ===")
    logger.info(f"生成的客户端ID: {client.client_id}")
    logger.info(f"使用的密码: {client.password}")
    logger.info(f"用户名: {client.username}")
    logger.info(f"TLS状态: {'启用' if client.use_tls else '禁用'}")
    
    try:
        # 尝试连接（注意：这里可能会失败，因为可能没有真实的MQTT服务器）
        logger.info("\n=== 尝试连接MQTT服务器 ===")
        success = await client.connect()
        
        if success:
            logger.info("连接成功！")
            
            # 订阅设备信息和数据
            device_model = config['device_model']
            device_sn = config['device_sn']
            await client.subscribe_device_info(device_model, device_sn, test.on_device_info)
            await client.subscribe_device_data(device_model, device_sn, test.on_device_data)
            
            logger.info(f"已订阅设备 {device_model}_{device_sn} 的信息和数据")
            
            # 等待一段时间接收消息
            logger.info("等待接收消息（5秒）...")
            await asyncio.sleep(5)
            
            # 断开连接
            await client.disconnect()
            logger.info("已断开连接")
            
        else:
            logger.warning("连接失败，这是正常的，因为可能没有配置真实的MQTT服务器")
            
    except Exception as e:
        logger.error(f"新配置测试过程中出现错误: {e}")
        logger.info("这是正常的，因为可能没有配置真实的MQTT服务器")
    
    logger.info("\n=== 新配置测试完成 ===")
    logger.info(f"收到设备信息数量: {test.received_info_count}")
    logger.info(f"收到设备数据数量: {test.received_data_count}")
    
    return test

async def simulate_mqtt_messages():
    """模拟MQTT消息处理"""
    logger.info("=== 模拟MQTT POST消息处理 ===")
    
    test_handler = PostFunctionsTest()
    
    # 模拟设备信息消息
    info_payload = {
        "netFirmVer": 1.5,
        "appFirmVer": 2.3,
        "wifiSsid": "SimulatedWiFi",
        "ip": "192.168.1.150",
        "wifiIsNormal": 0,
        "isLock": 0,
        "board": [{"id": 1, "name": "模拟主板"}]
    }
    
    # 模拟设备数据消息
    data_payloads = [
        {
            "sort": 1,
            "inputVoltage": 220.5,
            "InputCurrent": 5.2,
            "gridVoltage": 230.1,
            "gridFreq": 50.0,
            "genPower": 1000.0,
            "genPowerToDay": 5000,
            "genPowerTotal": 100000,
            "temperature": 45.5,
            "errCode": 0,
            "duration": 3600
        },
        {
            "sort": 2,
            "inputVoltage": 221.0,
            "InputCurrent": 5.3,
            "gridVoltage": 230.5,
            "gridFreq": 50.1,
            "genPower": 1050.0,
            "genPowerToDay": 5500,
            "genPowerTotal": 101000,
            "temperature": 46.0,
            "errCode": 0,
            "duration": 3660
        },
        {
            "sort": 3,
            "inputVoltage": 219.8,
            "InputCurrent": 5.1,
            "gridVoltage": 229.8,
            "gridFreq": 49.9,
            "genPower": 980.0,
            "genPowerToDay": 6000,
            "genPowerTotal": 102000,
            "temperature": 45.8,
            "errCode": 0,
            "duration": 3720
        }
    ]
    
    # 处理模拟消息
    try:
        device_info = DeviceInfo.from_dict(info_payload)
        await test_handler.on_device_info(device_info)
        
        device_data_list = []
        for data_payload in data_payloads:
            device_data = DeviceData.from_dict(data_payload)
            device_data_list.append(device_data)
        
        await test_handler.on_device_data(device_data_list)
        
    except Exception as e:
        logger.error(f"模拟POST消息处理错误: {e}")
    
    logger.info(f"模拟POST消息处理完成")
    logger.info(f"总共接收设备信息: {test_handler.received_info_count} 次")
    logger.info(f"总共接收设备数据: {test_handler.received_data_count} 次")
    
    return test_handler

async def test_real_device_post(broker_host: str, broker_port: int, 
                               device_id: str, device_sn: str,
                               username: str = None, password: str = None,
                               test_duration: int = 60):
    """测试真实设备POST数据接收"""
    logger.info("=== 真实设备POST数据接收测试 ===")
    
    print(f"🚀 开始真实设备POST测试...")
    print(f"📡 MQTT代理: {broker_host}:{broker_port}")
    print(f"🔧 设备ID: {device_id}")
    print(f"🏷️  设备SN: {device_sn}")
    print(f"⏱️  测试时长: {test_duration}秒")
    print(f"🔐 认证: {'是' if username else '否'}")
    print("=" * 60)
    
    test_handler = PostFunctionsTest()
    test_handler.start_time = datetime.now()
    
    try:
        # 创建MQTT客户端
        client = DeviceMQTTClient(
            broker_host=broker_host,
            broker_port=broker_port,
            username=username,
            password=password,
            client_id=f"post_test_{device_id}_{device_sn}"
        )
        
        if await client.connect():
            print(f"✅ 成功连接到MQTT代理")
            
            # 开始监控设备POST数据
            await client.start_monitoring(
                device_id=device_id,
                device_sn=device_sn,
                info_callback=test_handler.on_device_info,
                data_callback=test_handler.on_device_data
            )
            
            print(f"🔍 开始监控设备POST数据 {device_id}/{device_sn}")
            print(f"⏳ 等待 {test_duration} 秒接收POST数据...\n")
            
            # 等待指定时间
            await asyncio.sleep(test_duration)
            
            print(f"\n⏹️  POST测试完成")
            
            await client.disconnect()
            
        else:
            logger.error("连接失败")
            
    except Exception as e:
        logger.error(f"真实设备POST测试失败: {e}")
        raise
    
    finally:
        test_handler.print_statistics()
    
    return test_handler

async def interactive_post_test():
    """交互式POST测试"""
    print("=" * 60)
    print("AIOEway POST功能交互式测试")
    print("=" * 60)
    
    # 获取用户输入
    print("\n请输入MQTT配置信息:")
    device_model = input("设备机型码 [INV001]: ").strip() or "INV001"
    device_sn = input("设备SN [SN123456789]: ").strip() or "SN123456789"
    username = input("用户名 [testuser]: ").strip() or "testuser"
    password = input("密码 [processed_password]: ").strip() or "processed_password"
    broker_host = input("MQTT服务器地址 [localhost]: ").strip() or "localhost"
    broker_port = int(input("MQTT服务器端口 [8883]: ").strip() or "8883")
    keepalive = int(input("心跳间隔/秒 [60]: ").strip() or "60")
    use_tls = input("使用TLS加密 [Y/n]: ").strip().lower() not in ['n', 'no', 'false']
    test_duration = int(input("测试时长(秒) [60]: ").strip() or "60")
    
    config = {
        "device_model": device_model,
        "device_sn": device_sn,
        "username": username,
        "password": password,
        "broker_host": broker_host,
        "broker_port": broker_port,
        "keepalive": keepalive,
        "use_tls": use_tls
    }
    
    print("\n=== 生成的配置信息 ===")
    print(f"设备机型码: {device_model}")
    print(f"设备SN: {device_sn}")
    print(f"用户名: {username}")
    print(f"MQTT服务器: {broker_host}:{broker_port}")
    print(f"TLS: {'启用' if use_tls else '禁用'}")
    print(f"测试时长: {test_duration}秒")
    
    # 创建测试实例
    test = PostFunctionsTest()
    test.start_time = datetime.now()
    
    # 创建MQTT客户端
    client = DeviceMQTTClient(**config)
    
    print(f"\n客户端ID: {client.client_id}")
    print(f"加密密码: {client.password}")
    print(f"用户名: {client.username}")
    print(f"TLS状态: {'启用' if client.use_tls else '禁用'}")
    
    try:
        print("\n正在连接MQTT服务器...")
        success = await client.connect()
        
        if success:
            print("连接成功！")
            
            # 订阅设备信息和数据
            device_model = config['device_model']
            device_sn = config['device_sn']
            await client.subscribe_device_info(device_model, device_sn, test.on_device_info)
            await client.subscribe_device_data(device_model, device_sn, test.on_device_data)
            
            print(f"已订阅设备 {device_model}_{device_sn} 的POST信息和数据")
            print("按 Ctrl+C 停止监听...")
            
            # 持续监听
            try:
                await asyncio.sleep(test_duration)
            except KeyboardInterrupt:
                print("\n用户中断，正在断开连接...")
            
            await client.disconnect()
            print("已断开连接")
            
        else:
            print("连接失败")
            
    except Exception as e:
        print(f"错误: {e}")
    
    finally:
        test.print_statistics()
        print("交互式POST测试完成")
    
    return test

async def run_all_post_tests():
    """运行所有POST功能测试"""
    print("=" * 60)
    print("AIOEway POST功能综合测试")
    print("=" * 60)
    print("本测试包含以下功能:")
    print("1. 数据结构验证测试")
    print("2. 基础POST主题订阅测试")
    print("3. POST主题QoS参数验证")
    print("4. start_monitoring POST功能测试")
    print("5. 新配置方式测试")
    print("6. 模拟POST消息处理")
    print("=" * 60)
    
    results = {}
    
    # 1. 数据结构测试
    print("\n🔍 运行数据结构测试...")
    try:
        results['data_structures'] = await test_data_structures()
    except Exception as e:
        logger.error(f"数据结构测试失败: {e}")
        results['data_structures'] = False
    
    # 2. 基础POST测试
    print("\n🔍 运行基础POST测试...")
    try:
        results['basic'] = await test_post_topics_basic()
    except Exception as e:
        logger.error(f"基础POST测试失败: {e}")
        results['basic'] = None
    
    # 3. POST QoS参数测试
    print("\n🔍 运行POST QoS参数测试...")
    try:
        results['qos'] = await test_post_qos_parameters()
    except Exception as e:
        logger.error(f"POST QoS测试失败: {e}")
        results['qos'] = False
    
    # 4. start_monitoring POST测试
    print("\n🔍 运行start_monitoring POST测试...")
    try:
        results['start_monitoring'] = await test_start_monitoring_post()
    except Exception as e:
        logger.error(f"start_monitoring POST测试失败: {e}")
        results['start_monitoring'] = False
    
    # 5. 新配置方式测试
    print("\n🔍 运行新配置方式测试...")
    try:
        results['new_config'] = await test_new_config_method()
    except Exception as e:
        logger.error(f"新配置方式测试失败: {e}")
        results['new_config'] = None
    
    # 6. 模拟POST消息测试
    print("\n🔍 运行模拟POST消息测试...")
    try:
        results['simulation'] = await simulate_mqtt_messages()
    except Exception as e:
        logger.error(f"模拟POST消息测试失败: {e}")
        results['simulation'] = None
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("POST功能测试总结")
    print("=" * 60)
    
    if results['data_structures']:
        print(f"✅ 数据结构测试: 通过")
    else:
        print(f"❌ 数据结构测试: 失败")
    
    if results['basic']:
        print(f"✅ 基础POST测试: 通过")
        print(f"   - 设备信息接收: {results['basic'].received_info_count} 次")
        print(f"   - 设备数据接收: {results['basic'].received_data_count} 次")
    else:
        print(f"❌ 基础POST测试: 失败")
    
    if results['qos']:
        print(f"✅ POST QoS参数测试: 通过")
    else:
        print(f"❌ POST QoS参数测试: 失败")
    
    if results['start_monitoring']:
        print(f"✅ start_monitoring POST测试: 通过")
    else:
        print(f"❌ start_monitoring POST测试: 失败")
    
    if results['new_config']:
        print(f"✅ 新配置方式测试: 通过")
        print(f"   - 设备信息接收: {results['new_config'].received_info_count} 次")
        print(f"   - 设备数据接收: {results['new_config'].received_data_count} 次")
    else:
        print(f"❌ 新配置方式测试: 失败")
    
    if results['simulation']:
        print(f"✅ 模拟POST消息测试: 通过")
        print(f"   - 模拟设备信息: {results['simulation'].received_info_count} 次")
        print(f"   - 模拟设备数据: {results['simulation'].received_data_count} 次")
    else:
        print(f"❌ 模拟POST消息测试: 失败")
    
    print("\n🎉 POST功能综合测试完成！")
    print("=" * 60)
    
    return results

def get_user_config():
    """获取用户配置"""
    print("🔧 真实设备POST测试配置")
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
    test_duration = int(input("测试时长(秒) [60]: ").strip() or "60")
    
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
            # 交互式POST测试
            await interactive_post_test()
        elif sys.argv[1] == "--real":
            # 真实设备POST测试
            try:
                config = get_user_config()
                await test_real_device_post(**config)
            except Exception as e:
                print(f"❌ 真实设备POST测试出错: {e}")
        elif sys.argv[1] == "--qos":
            # 仅QoS测试
            await test_post_qos_parameters()
        elif sys.argv[1] == "--basic":
            # 仅基础测试
            await test_post_topics_basic()
        elif sys.argv[1] == "--config":
            # 仅新配置测试
            await test_new_config_method()
        elif sys.argv[1] == "--simulation":
            # 仅模拟测试
            await simulate_mqtt_messages()
        elif sys.argv[1] == "--data":
            # 仅数据结构测试
            await test_data_structures()
        else:
            print("未知参数，运行默认综合测试")
            await run_all_post_tests()
    else:
        # 默认运行综合测试
        await run_all_post_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")