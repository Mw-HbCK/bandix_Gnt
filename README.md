# OpenWrt bandix 流量监控脚本

## 项目概述

这是一个基于 Python 的流量监控脚本，通过 OpenWrt 路由器上的 luci-app-bandix 插件的 ubus 接口获取实时网速和流量数据。脚本支持表格和 JSON 两种输出格式，并允许通过配置文件或命令行参数进行灵活配置。

## 功能特性

- ✅ 通过 ubus 接口与 OpenWrt 路由器通信
- ✅ 支持用户名/密码认证
- ✅ 获取所有设备的实时网速和流量数据
- ✅ 自动转换数据单位（B/KB/MB/GB）
- ✅ 支持表格和 JSON 两种输出格式
- ✅ 可通过配置文件或命令行参数进行配置
- ✅ 支持调试模式
- ✅ 可配置输出格式的默认值

## 安装要求

### 硬件要求
- OpenWrt 路由器，已安装 luci-app-bandix 插件
- 安装了 Python 3.6+ 的监控设备

### 软件要求
- Python 3.6 或更高版本
- `requests` 库（用于 HTTP 请求）
- `configparser` 库（用于配置文件解析，Python 标准库）
- `argparse` 库（用于命令行参数解析，Python 标准库）

## 安装步骤

### 1. 安装依赖库

```bash
pip install requests
```

### 2. 安装 luci-app-bandix 插件

在 OpenWrt 路由器上执行以下命令安装 bandix 插件：

```bash
opkg update
opkg install luci-app-bandix
```

安装完成后，在 OpenWrt 管理界面中启用 bandix 插件。

### 3. 下载监控脚本

将 `bandix_monitor.py` 和 `bandix_config.ini` 文件下载到本地。

## 配置说明

### 配置文件格式

脚本使用 `bandix_config.ini` 文件进行配置，格式如下：

```ini
[bandix]
# OpenWrt 设备的 ubus URL
url = http://192.168.1.1/ubus

# 登录用户名
username = root

# 登录密码
password = your_password

# 输出格式 (table 或 json)
format = table
```

### 配置项说明

| 配置项   | 说明                          | 默认值                     |
|----------|-------------------------------|----------------------------|
| url      | OpenWrt 路由器的 ubus URL     | http://10.0.0.1/ubus       |
| username | OpenWrt 路由器的登录用户名    | root                       |
| password | OpenWrt 路由器的登录密码      | password                   |
| format   | 默认的输出格式（table 或 json）| table                      |

## 使用方法

### 基本用法

```bash
python bandix_monitor.py
```

### 命令行参数

```bash
usage: bandix_monitor.py [-h] [--url URL] [-u USERNAME] [-p PASSWORD] [-c CONFIG] [-d] [-f {table,json}]

OpenWrt bandix 流量监控脚本

optional arguments:
  -h, --help            show this help message and exit
  --url URL             设备 ubus URL
  -u USERNAME, --username USERNAME
                        登录用户名
  -p PASSWORD, --password PASSWORD
                        登录密码
  -c CONFIG, --config CONFIG
                        配置文件路径 (默认: bandix_config.ini)
  -d, --debug           启用调试模式
  -f {table,json}, --format {table,json}
                        输出格式 (默认: 配置文件中的设置)
```

### 优先级规则

配置的优先级从高到低依次为：
1. 命令行参数
2. 配置文件
3. 硬编码默认值

### 输出格式示例

#### 表格格式

```
设备名称                 IP 地址           下行速度         上行速度         总下载量         总上传量
=====================================================================================
全网总计                 -               1.22 KB/s    1.16 KB/s    59.02 GB     180.72 GB
kwrt.lan             10.0.0.1        0 B/s        0 B/s        3.12 GB      8.69 GB
github-com.lan       10.0.0.199      1.12 KB/s    1.08 KB/s    34.91 GB     3.90 GB
DESKTOP-VSP2LGJ.lan  10.0.0.188      104.00 B/s   82.00 B/s    20.98 GB     168.13 GB
```

#### JSON 格式

```json
{
  "devices": [
    {
      "device_name": "DESKTOP-VSP2LGJ.lan",
      "ip": "10.0.0.188",
      "mac": "c4:c6:e6:07:de:3f",
      "down_speed": 0,
      "up_speed": 0,
      "total_down": 22528736432,
      "total_up": 180529835184,
      "down_speed_human": "0 B/s",
      "up_speed_human": "0 B/s",
      "total_down_human": "20.98 GB",
      "total_up_human": "168.13 GB"
    },
    // 更多设备...
  ],
  "total": {
    "device_name": "全网总计",
    "ip": "-",
    "down_speed": 101,
    "up_speed": 696,
    "total_down": 63374666507,
    "total_up": 194048557034,
    "down_speed_human": "101.00 B/s",
    "up_speed_human": "696.00 B/s",
    "total_down_human": "59.02 GB",
    "total_up_human": "180.72 GB"
  }
}
```

## 实现原理

### 技术栈

- **Python 3.6+**: 脚本开发语言
- **OpenWrt ubus**: 与路由器通信的接口
- **JSON-RPC**: API 调用协议
- **requests**: 处理 HTTP 请求
- **configparser**: 解析配置文件
- **argparse**: 处理命令行参数

### 工作流程

1. **读取配置**: 加载配置文件并解析命令行参数
2. **身份认证**: 通过 `session/login` 方法获取 SID
3. **获取设备列表**: 通过 `luci.bandix.getStatus` 获取设备信息
4. **获取流量数据**: 通过 `luci.bandix.getMetrics` 获取流量数据
5. **数据处理**: 解析和处理获取到的数据
6. **格式化输出**: 根据配置输出表格或 JSON 格式的数据

### 关键实现步骤

#### 1. 身份认证

脚本通过 `session/login` 方法进行身份认证，获取 `ubus_rpc_session` (SID)，后续的 API 调用都需要使用这个 SID。

```python
def login(self):
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
    # 发送请求并处理响应...
```

#### 2. 获取设备列表

通过 `luci.bandix.getStatus` 方法获取所有设备的基本信息，包括主机名、IP 地址和 MAC 地址。

```python
def get_status(self):
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "call",
        "params": [
            self.sid,
            "luci.bandix",
            "getStatus",
            {}
        ]
    }
    # 发送请求并处理响应...
```

#### 3. 获取流量数据

通过 `luci.bandix.getMetrics` 方法获取指定 MAC 地址设备的流量数据。可以通过传入 `mac:all` 获取所有设备的流量数据。

```python
def get_metrics(self, mac):
    payload = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "call",
        "params": [
            self.sid,
            "luci.bandix",
            "getMetrics",
            {"mac": mac}
        ]
    }
    # 发送请求并处理响应...
```

#### 4. 数据单位转换

为了提高可读性，脚本将字节转换为人类可读的单位（B/KB/MB/GB）。

```python
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

# 类似的，convert_speed 函数将字节/秒转换为可读格式
```

#### 5. 数据聚合与格式化

脚本将设备信息和流量数据进行聚合，并根据配置的输出格式（表格或 JSON）进行格式化输出。

```python
def collect_data(self):
    """
    收集并整合设备信息和流量数据
    """
    # 获取设备列表和流量数据
    # 整合数据...
    return data

# 根据输出格式选择运行模式
if output_format == "json":
    monitor.run_json()
else:
    monitor.run()
```

## 代码结构

### 主要文件

- **bandix_monitor.py**: 监控脚本的主文件
- **bandix_config.ini**: 配置文件
- **README.md**: 项目说明文档

### bandix_monitor.py 结构

```
├── convert_size()           # 字节大小转换函数
├── convert_speed()          # 字节速度转换函数
├── load_config()            # 配置文件加载函数
├── BandixMonitor 类         # 监控类
│   ├── __init__()           # 构造函数
│   ├── login()              # 登录方法
│   ├── get_status()         # 获取设备状态
│   ├── get_metrics()        # 获取流量数据
│   ├── collect_data()       # 数据聚合
│   ├── run()                # 表格输出
│   └── run_json()           # JSON 输出
└── main()                   # 主函数
```

### 类和方法说明

#### BandixMonitor 类

| 方法名 | 功能描述 | 参数 | 返回值 |
|--------|----------|------|--------|
| `__init__()` | 初始化监控器 | url, username, password, debug | 无 |
| `login()` | 登录获取 SID | 无 | 布尔值（登录成功/失败） |
| `get_status()` | 获取设备状态信息 | 无 | 设备列表或 None |
| `get_metrics()` | 获取流量数据 | mac | 流量数据或 None |
| `collect_data()` | 收集并整合数据 | 无 | 整合后的数据或 None |
| `run()` | 输出表格格式数据 | 无 | 无 |
| `run_json()` | 输出 JSON 格式数据 | 无 | 无 |

## 高级用法

### 使用自定义配置文件

```bash
python bandix_monitor.py -c /path/to/custom_config.ini
```

### 启用调试模式

```bash
python bandix_monitor.py -d
```

### 指定输出格式为 JSON

```bash
python bandix_monitor.py -f json
```

### 通过命令行参数指定所有配置

```bash
python bandix_monitor.py --url http://192.168.1.1/ubus -u root -p password -f table
```

## 常见问题

### 1. 连接失败

**问题**：无法连接到 OpenWrt 路由器

**解决方案**：
- 检查路由器的 IP 地址是否正确
- 确保路由器上的 ubus 服务正在运行
- 检查防火墙设置，确保允许访问 ubus 接口

### 2. 登录失败

**问题**：用户名或密码错误

**解决方案**：
- 检查配置文件中的用户名和密码是否正确
- 确保用户具有访问 ubus 接口的权限

### 3. 数据为空

**问题**：获取到的流量数据为空

**解决方案**：
- 确保 luci-app-bandix 插件已正确安装并启用
- 检查是否有设备连接到路由器

### 4. 单位转换错误

**问题**：数据单位显示不正确

**解决方案**：
- 检查 `convert_size()` 和 `convert_speed()` 函数的实现
- 确保输入的字节数是正确的

## 开发说明

### 调试模式

启用调试模式可以输出详细的请求和响应信息，有助于排查问题：

```bash
python bandix_monitor.py -d
```

### 测试

可以通过修改配置文件或命令行参数进行测试，确保脚本能够正确获取和显示数据。

## 许可证

本项目采用 MIT 许可证，详细内容请参考 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request，共同改进这个项目。

## 更新日志

### v1.0.0 (2025-12-27)
- 初始版本
- 支持表格和 JSON 输出格式
- 支持配置文件
- 实现了基本的监控功能
