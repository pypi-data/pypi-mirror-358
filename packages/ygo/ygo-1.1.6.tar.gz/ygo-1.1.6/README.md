# ygo
一个轻量级 Python 工具包，底层基于 joblib 和 tqdm 、loguru 实现，支持
- 并发执行（带进度条）
- 延迟调用
- 链式绑定参数
- 函数信息获取
- 模块/函数动态加载...
- 并结合 ylog 提供日志记录能力

### 安装
```shell
pip install -U ygo
```

### 🧰 功能概览

| 模块   | 功能                                                         |
| :----- | :----------------------------------------------------------- |
| `ygo`  | 支持并发执行（带进度条）、延迟调用、函数信息获取以及模块/函数动态加载等功能 |
| `ylog` | 日志模块，提供统一的日志输出接口                             |

### 示例

```
├── a
│   ├── __init__.py
│   └── b
│       ├── __init__.py
│       └── c.py
└── test.py

c.py 中定义了目标函数
def test_fn(a, b=2):
    return a+b
```

#### 场景1: 并发执行

```python
import ygo
import ylog
from a.b.c import test_fn

with ygo.pool(n_jobs=5, show_progress=True) as go:
    for i in range(10):
        go.submit(test_fn)(a=i, b=2*i)
    for res in go.do():
        ylog.info(res)
```

#### ✅ `ygo.pool` 支持的参数

| 参数名        | 类型 | 描述                                                         |
| ------------- | ---- | ------------------------------------------------------------ |
| n_jobs        | int  | 并行任务数(<=1 表示串行)                                     |
| show_progress | bool | 是否显示进度条                                               |
| backend       | str  | 执行后端（默认 'threading'，可选 'multiprocessing' 或 'loky'） |

#### 场景2: 延迟调用

```
>>> fn = delay(test_fn)(a=1, b=2)
>>> fn()
3
>>> # 逐步传递参数
>>> fn1 = delay(lambda a, b, c: a+b+c)(a=1)
>>> fn2 = delay(fn1)(b=2)
>>> fn2(c=3)
6
>>> # 参数更改
>>> fn1 = delay(lambda a, b, c: a+b+c)(a=1, b=2)
>>> fn2 = delay(fn1)(c=3, b=5)
>>> fn2()
9
```

#### 场景3: 获取目标函数信息

```
>>> ygo.fn_info(test_fn)
=============================================================
    a.b.c.test_fn(a, b=2)
=============================================================
    def test_fn(a, b=2):
    return a+b
```

#### 🔍 其他函数信息工具

| 方法名                    | 描述                                     |
| ------------------------- | ---------------------------------------- |
| `fn_params(fn)`           | 获取函数实参                             |
| `fn_signature_params(fn)` | 获取函数定义的所有参数名                 |
| `fn_code(fn)`             | 获取函数源码字符串                       |
| `fn_path(fn)`             | 获取函数所属模块路径                     |
| `fn_from_str(s)`          | 根据字符串导入函数（如 "a.b.c.test_fn"） |
| `module_from_str(s)`      | 根据字符串导入模块                       |

#### 场景4: 通过字符串解析函数并执行

```
>>> ygo.fn_from_str("a.b.c.test_fn")(a=1, b=5)
6
```

### 📝 日志记录（ylog）

```python
import ylog

ylog.info("这是一个信息日志")
ylog.warning("这是一个警告日志")
ylog.error("这是一个错误日志", exc_info=True)



# 为不同的模块使用不同的logger
logger_app1 = ylog.get_logger("app1", )
logger_app2 = ylog.get_logger("app2", )
```

#### 🔧 配置管理：`update_config`

你可以通过 update_config 方法动态修改日志配置，例如设置日志级别、格式、是否启用颜色等。

```python
# 开启调试模式
ylog.update_config(debug_mode=True)
```

#### 🧩 获取独立的 Logger 实例：`get_logger`

在大型项目中，你可能希望为不同模块或组件创建独立的 logger 实例以区分日志来源。

```python
logger1 = ylog.get_logger("moduleA")
logger2 = ylog.get_logger("moduleB")

logger1.info("这是来自 moduleA 的日志")
logger2.warning("这是来自 moduleB 的警告")
```

#### 📌 使用建议

- 生产环境建议关闭 `debug_mode`，避免产生过多调试日志。
- 对于复杂项目，推荐使用 `get_logger` 创建命名 logger，便于日志分类与分析。
- 使用 `exc_info=True` 参数时，可自动打印异常堆栈信息，适用于错误捕获场景。
