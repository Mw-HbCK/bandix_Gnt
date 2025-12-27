#!/usr/bin/env python3
import requests
import json
import sys
import argparse
import configparser
import os

def convert_size(size_bytes):
    """
    将字节大小转换为可读格式
    """
    if size_bytes == 0:
        return "0 B"
    size_name = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

def convert_speed(speed_bytes):
    """
    将字节速度转换为可读格式
    """
    if speed_bytes == 0:
        return "0 B/s"
    speed_name = ["B/s", "KB/s", "MB/s"]
    i = 0
    while speed_bytes >= 1024 and i < len(speed_name) - 1:
        speed_bytes /= 1024
        i += 1
    return f"{speed_bytes:.2f} {speed_name[i]}"

def load_config(config_file):
    """
    加载配置文件
    """
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    bandix_config = {}
    if "bandix" in config:
        bandix_config = dict(config["bandix"])
    
    return bandix_config

class BandixMonitor:
    def __init__(self, url="http://10.0.0.1/ubus", username="root", password="password", debug=False):
        self.url = url
        self.username = username
        self.password = password
        self.debug = debug
        self.sid = None
        self.session = requests.Session()
    
    def login(self):
        """
        登录获取 ubus_rpc_session
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [
                "00000000000000000000000000000000",
                "session",
                "login",
                {
                    "username": self.username,
                    "password": self.password
                }
            ]
        }
        
        try:
            response = self.session.post(self.url, json=payload)
            response.raise_for_status()
            
            if self.debug:
                print(f"登录响应状态码: {response.status_code}")
                print(f"登录响应头: {response.headers}")
                print(f"登录响应内容: {response.text}")
            
            result = response.json()
            
            if self.debug:
                print(f"登录响应 JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("result") and len(result["result"]) >= 2:
                if result["result"][0] == 0:
                    self.sid = result["result"][1]["ubus_rpc_session"]
                    if self.debug:
                        print(f"获取到 SID: {self.sid}")
                    return True
                else:
                    print(f"登录失败: {result['result'][1]}")
                    return False
            else:
                print(f"登录失败: 无效的响应格式")
                if self.debug:
                    print(f"响应结果结构: {list(result.keys())}")
                    if "result" in result:
                        print(f"result 长度: {len(result['result'])}")
                        print(f"result 内容: {result['result']}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"登录失败: 无法连接到设备 - {e}")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"登录失败: HTTP 错误 - {e}")
            if self.debug:
                print(f"响应内容: {response.text}")
            return False
        except requests.exceptions.Timeout as e:
            print(f"登录失败: 请求超时 - {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"登录失败: 网络错误 - {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"登录失败: 无效的 JSON 响应 - {e}")
            if self.debug:
                print(f"响应内容: {response.text}")
            return False
        except Exception as e:
            print(f"登录失败: 未知错误 - {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return False
    
    def get_status(self):
        """
        获取设备状态信息
        """
        if not self.sid:
            print("请先登录")
            return None
        
        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "call",
            "params": [
                self.sid,
                "luci.bandix",
                "getStatus",
                {}
            ]
        }
        
        try:
            response = self.session.post(self.url, json=payload)
            response.raise_for_status()
            
            if self.debug:
                print(f"获取状态响应状态码: {response.status_code}")
                print(f"获取状态响应内容: {response.text}")
            
            result = response.json()
            
            if self.debug:
                print(f"获取状态响应 JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("result") and len(result["result"]) >= 2:
                if result["result"][0] == 0:
                    return result["result"][1]
                else:
                    print(f"获取状态失败: {result['result'][1]}")
                    return None
            else:
                print(f"获取状态失败: 无效的响应格式")
                if self.debug:
                    print(f"响应结果结构: {list(result.keys())}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"获取状态失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"获取状态失败: 无效的 JSON 响应 - {e}")
            if self.debug:
                print(f"响应内容: {response.text}")
            return None
        except Exception as e:
            print(f"获取状态失败: 未知错误 - {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return None
    
    def get_metrics(self, mac="all"):
        """
        获取流量数据
        """
        if not self.sid:
            print("请先登录")
            return None
        
        payload = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "call",
            "params": [
                self.sid,
                "luci.bandix",
                "getMetrics",
                {"mac": mac}
            ]
        }
        
        try:
            response = self.session.post(self.url, json=payload)
            response.raise_for_status()
            
            if self.debug:
                print(f"获取流量数据响应状态码: {response.status_code}")
                print(f"获取流量数据响应内容: {response.text}")
            
            result = response.json()
            
            if self.debug:
                print(f"获取流量数据响应 JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("result") and len(result["result"]) >= 2:
                if result["result"][0] == 0:
                    return result["result"][1]
                else:
                    print(f"获取流量数据失败: {result['result'][1]}")
                    return None
            else:
                print(f"获取流量数据失败: 无效的响应格式")
                if self.debug:
                    print(f"响应结果结构: {list(result.keys())}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"获取流量数据失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"获取流量数据失败: 无效的 JSON 响应 - {e}")
            if self.debug:
                print(f"响应内容: {response.text}")
            return None
        except Exception as e:
            print(f"获取流量数据失败: 未知错误 - {e}")
            if self.debug:
                import traceback
                traceback.print_exc()
            return None
    
    def collect_data(self):
        """
        收集所有设备的流量数据，返回JSON格式
        """
        # 登录
        if not self.login():
            return None
        
        # 获取设备状态
        status = self.get_status()
        devices = []
        device_map = {}
        
        if status and "devices" in status:
            devices = status["devices"]
            for device in devices:
                device_map[device["mac"]] = {
                    "hostname": device["hostname"],
                    "ip": device["ip"]
                }
        
        # 收集所有数据
        data = {
            "devices": [],
            "total": {}
        }
        
        # 1. 获取全网流量数据
        metrics = self.get_metrics("all")
        if metrics and "metrics" in metrics:
            metrics_data = metrics["metrics"]
            
            # 检查是否是时间序列数据
            is_time_series = False
            if metrics_data and len(metrics_data) > 0 and isinstance(metrics_data[0][0], (int, float)) and metrics_data[0][0] > 1000000000000:
                is_time_series = True
            
            if is_time_series:
                # 时间序列数据，取最后一个数据点
                last_metric = None
                for metric in reversed(metrics_data):
                    if len(metric) >= 9:
                        last_metric = metric
                        break
                
                if last_metric:
                    # 提取数据
                    down_speed = last_metric[1]  # 瞬时下行速率 (Bytes/s)
                    up_speed = last_metric[2]    # 瞬时上行速率 (Bytes/s)
                    total_down = last_metric[7]  # 累计下载总量 (Bytes)
                    total_up = last_metric[8]    # 累计上传总量 (Bytes)
                    
                    data["total"] = {
                        "device_name": "全网总计",
                        "ip": "-",
                        "down_speed": down_speed,
                        "up_speed": up_speed,
                        "total_down": total_down,
                        "total_up": total_up,
                        "down_speed_human": convert_speed(down_speed),
                        "up_speed_human": convert_speed(up_speed),
                        "total_down_human": convert_size(total_down),
                        "total_up_human": convert_size(total_up)
                    }
            else:
                # 非时间序列数据，直接处理
                for metric in metrics_data:
                    if len(metric) < 9:
                        continue
                    
                    mac = metric[0]
                    if mac == "all":
                        # 提取数据
                        down_speed = metric[1]  # 瞬时下行速率 (Bytes/s)
                        up_speed = metric[2]    # 瞬时上行速率 (Bytes/s)
                        total_down = metric[7]  # 累计下载总量 (Bytes)
                        total_up = metric[8]    # 累计上传总量 (Bytes)
                        
                        data["total"] = {
                            "device_name": "全网总计",
                            "ip": "-",
                            "down_speed": down_speed,
                            "up_speed": up_speed,
                            "total_down": total_down,
                            "total_up": total_up,
                            "down_speed_human": convert_speed(down_speed),
                            "up_speed_human": convert_speed(up_speed),
                            "total_down_human": convert_size(total_down),
                            "total_up_human": convert_size(total_up)
                        }
                        break
        
        # 2. 获取每个设备的流量数据
        for device in devices:
            mac = device["mac"]
            hostname = device["hostname"]
            ip = device["ip"]
            
            # 获取该设备的流量数据
            device_metrics = self.get_metrics(mac)
            if device_metrics and "metrics" in device_metrics:
                device_metrics_data = device_metrics["metrics"]
                
                # 检查是否是时间序列数据
                is_time_series = False
                if device_metrics_data and len(device_metrics_data) > 0 and isinstance(device_metrics_data[0][0], (int, float)) and device_metrics_data[0][0] > 1000000000000:
                    is_time_series = True
                
                if is_time_series:
                    # 时间序列数据，取最后一个数据点
                    last_metric = None
                    for metric in reversed(device_metrics_data):
                        if len(metric) >= 9:
                            last_metric = metric
                            break
                    
                    if last_metric:
                        # 提取数据
                        down_speed = last_metric[1]  # 瞬时下行速率 (Bytes/s)
                        up_speed = last_metric[2]    # 瞬时上行速率 (Bytes/s)
                        total_down = last_metric[7]  # 累计下载总量 (Bytes)
                        total_up = last_metric[8]    # 累计上传总量 (Bytes)
                        
                        data["devices"].append({
                            "device_name": hostname,
                            "ip": ip,
                            "mac": mac,
                            "down_speed": down_speed,
                            "up_speed": up_speed,
                            "total_down": total_down,
                            "total_up": total_up,
                            "down_speed_human": convert_speed(down_speed),
                            "up_speed_human": convert_speed(up_speed),
                            "total_down_human": convert_size(total_down),
                            "total_up_human": convert_size(total_up)
                        })
                else:
                    # 非时间序列数据，直接处理
                    for metric in device_metrics_data:
                        if len(metric) < 9:
                            continue
                        
                        # 提取数据
                        down_speed = metric[1]  # 瞬时下行速率 (Bytes/s)
                        up_speed = metric[2]    # 瞬时上行速率 (Bytes/s)
                        total_down = metric[7]  # 累计下载总量 (Bytes)
                        total_up = metric[8]    # 累计上传总量 (Bytes)
                        
                        data["devices"].append({
                            "device_name": hostname,
                            "ip": ip,
                            "mac": mac,
                            "down_speed": down_speed,
                            "up_speed": up_speed,
                            "total_down": total_down,
                            "total_up": total_up,
                            "down_speed_human": convert_speed(down_speed),
                            "up_speed_human": convert_speed(up_speed),
                            "total_down_human": convert_size(total_down),
                            "total_up_human": convert_size(total_up)
                        })
                        break
        
        return data
    
    def run(self):
        """
        执行监控逻辑，输出表格格式
        """
        data = self.collect_data()
        if not data:
            sys.exit(1)
        
        # 打印表头
        print(f"{'设备名称':<20} {'IP 地址':<15} {'下行速度':<12} {'上行速度':<12} {'总下载量':<12} {'总上传量':<12}")
        print("=" * 85)
        
        # 打印全网总计
        if data.get("total"):
            total = data["total"]
            print(f"{total['device_name']:<20} {total['ip']:<15} {total['down_speed_human']:<12} {total['up_speed_human']:<12} {total['total_down_human']:<12} {total['total_up_human']:<12}")
        
        # 打印每个设备的数据
        for device in data["devices"]:
            print(f"{device['device_name']:<20} {device['ip']:<15} {device['down_speed_human']:<12} {device['up_speed_human']:<12} {device['total_down_human']:<12} {device['total_up_human']:<12}")
    
    def run_json(self):
        """
        执行监控逻辑，输出JSON格式
        """
        data = self.collect_data()
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"error": "Failed to collect data"}, indent=2, ensure_ascii=False))
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenWrt bandix 流量监控脚本")
    parser.add_argument("--url", default=None, help="设备 ubus URL")
    parser.add_argument("-u", "--username", default=None, help="登录用户名")
    parser.add_argument("-p", "--password", default=None, help="登录密码")
    parser.add_argument("-c", "--config", default="bandix_config.ini", help="配置文件路径 (默认: bandix_config.ini)")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")
    parser.add_argument("-f", "--format", choices=["table", "json"], default=None, help="输出格式 (默认: 配置文件中的设置)")
    
    args = parser.parse_args()
    
    # 加载配置文件
    config = load_config(args.config)
    
    # 设置默认值和优先级：命令行参数 > 配置文件 > 硬编码默认值
    url = args.url or config.get("url", "http://10.0.0.1/ubus")
    username = args.username or config.get("username", "root")
    password = args.password or config.get("password", "password")
    output_format = args.format or config.get("format", "table")
    
    # 检查配置是否完整
    if not username or not password:
        print("错误: 用户名和密码不能为空")
        print("请在配置文件中设置或通过命令行参数指定")
        sys.exit(1)
    
    monitor = BandixMonitor(
        url=url,
        username=username,
        password=password,
        debug=args.debug
    )
    
    # 根据输出格式运行
    if output_format == "json":
        monitor.run_json()
    else:
        monitor.run()
