# Keplore MDS

一个简单的 MCP (Model Context Protocol) 服务器，提供数学加法操作。

## 安装

### 开发模式安装
```bash
pip install -e .
```

### 普通安装
```bash
pip install .
```

## 使用方法

### 1. 作为 MCP 服务器运行

#### 方法 1: 使用命令行入口
```bash
keplore-mds
```

#### 方法 2: 使用 Python 模块
```bash
python -m mds.main
```

#### 方法 3: 直接运行主文件
```bash
python mds/main.py
```

### 2. 作为 Python 包导入使用

```python
# 导入整个包
import mds

# 使用加法函数
result = mds.add(5, 3)
print(f"5 + 3 = {result}")  # 输出: 5 + 3 = 8

# 创建 MCP 服务器实例
server = mds.create_server()
```

### 3. 导入具体模块

```python
# 只导入工具函数
from mds.tools import add
result = add(10, 20)

# 导入服务器相关功能
from mds.server import create_server, run_server

# 创建服务器
server = create_server()

# 运行服务器
run_server()
```

## 项目结构

```
mds/
├── __init__.py          # 包初始化文件
├── main.py             # 主入口点
├── server.py           # MCP 服务器配置
├── tools.py            # 业务逻辑函数
└── test_tools.py       # 测试文件
```

## 开发

### 运行测试
```bash
python test_package.py
```

### 安装开发依赖
```bash
pip install -e .[dev]
```

## MCP 工具

这个服务器提供以下 MCP 工具：

### add
- **描述**: 添加两个数字
- **参数**: 
  - `a` (int): 第一个数字
  - `b` (int): 第二个数字
- **返回**: 两个数字的和

## 示例

### 作为 MCP 服务器
当作为 MCP 服务器运行时，其他应用程序可以通过 stdio 协议与之通信，调用 `add` 工具。

### 作为 Python 库
```python
from mds import add

# 简单使用
print(add(1, 2))  # 输出: 3
print(add(-5, 10))  # 输出: 5
```


