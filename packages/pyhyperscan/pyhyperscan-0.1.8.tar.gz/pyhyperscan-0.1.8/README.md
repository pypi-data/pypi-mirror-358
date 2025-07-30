# Hyperscan Python Wrapper

[![PyPI Version](https://img.shields.io/pypi/v/pyhyperscan.svg)](https://pypi.org/project/pyhyperscan/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pyhyperscan.svg)](https://pypi.org/project/pyhyperscan/)
[![License](https://img.shields.io/pypi/l/pyhyperscan.svg)](https://pypi.org/project/pyhyperscan/)
[![Build Status](https://github.com/yourusername/hyperscan_package/actions/workflows/build.yml/badge.svg)](https://github.com/yourusername/hyperscan_package/actions)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen)](https://github.com/yourusername/hyperscan_package#readme)

**Hyperscan Python Wrapper** 是一个基于 Cython 的 Python 封装库，用于 Intel 的 [Hyperscan](https://www.intel.com/content/www/us/en/developer/articles/technical/introduction-to-hyperscan.html) 库。Hyperscan 是一个高性能的正则表达式匹配库，适用于大规模数据流处理。

本项目提供了对 Hyperscan 核心功能的 Python 接口，使开发者能够轻松地在 Python 中使用 Hyperscan 的强大功能。

---

## 功能特性

- **高性能正则表达式匹配**：基于 Hyperscan 的高效匹配引擎。
- **多模式支持**：支持同时编译和匹配多个正则表达式。
- **跨平台支持**：支持 Windows、Linux 和 macOS。
- **简单易用**：提供简洁的 Python API，易于集成到现有项目中。

---

## 安装

### 从 PyPI 安装

```bash
pip install pyhyperscan
pip install -i https://test.pypi.org/simple/ pyhyperscan

```

### 从源码安装

1. 克隆仓库：

   ```bash
   git clone https://gitee.com/fgc1/regex_engine_py.git
   cd hyperscan_package
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 构建并安装：

   ```bash
   python setup.py build_ext --inplace  # 本地调试用
   pip install .
   python setup.py sdist bdist_wheel    # 打包发布用
   ```

4. 发布到python源：
```bash
twine upload --repository testpypi dist/* --verbose
twine upload --repository pypi dist/* --verbose
```
---

## 快速开始

以下是一个简单的示例，展示如何使用 `pyhyperscan` 进行正则表达式匹配。

```python
import pyhyperscan


# 定义回调函数
def match_callback(id, from_, to, flags):
    print(f"Match found: id={id}, from={from_}, to={to}, flags={flags}")


if __name__ == '__main__':
    # 编译正则表达式
    patterns = ["hello", "world"]

    ret, msg = results = pyhyperscan.check_patterns(patterns, [0, 0])
    if not ret:
        print(f"error patterns info: {msg}")
        exit(1)

    flags = [
        pyhyperscan.HS_FLAG_CASELESS_PY | pyhyperscan.HS_FLAG_SOM_LEFTMOST_PY,
        pyhyperscan.HS_FLAG_SOM_LEFTMOST_PY
    ]
    ids = [1, 2]
    db = pyhyperscan.compile_multi_patterns(patterns, flags, ids)
    # 扫描数据
    data = "Hello, world! Hello, Python!"
    # match_callback也可以是类方法
    pyhyperscan.scan_data(db, data, match_callback)

    # 释放数据库
    pyhyperscan.free_database(db)

```

---

## 文档

### API 参考

#### `compile_pattern(pattern: bytes, flags: int = 0) -> Database`

编译单个正则表达式模式。

- **参数**：
  - `pattern`: 正则表达式模式（字节串）。
  - `flags`: 匹配标志（如 `HS_FLAG_CASELESS`）。
- **返回**：编译后的数据库对象。

#### `compile_multi_patterns(patterns: List[bytes], flags: List[int], ids: List[int]) -> Database`

编译多个正则表达式模式。

- **参数**：
  - `patterns`: 正则表达式模式列表（字节串）。
  - `flags`: 匹配标志列表。
  - `ids`: 模式 ID 列表。
- **返回**：编译后的数据库对象。

#### `scan_data(db: Database, data: bytes, callback: Callable) -> int`

扫描数据并调用回调函数处理匹配结果。

- **参数**：
  - `db`: 编译后的数据库对象。
  - `data`: 待扫描的数据（字节串）。
  - `callback`: 匹配回调函数。
- **返回**：匹配次数。

#### `free_database(db: Database)`

释放数据库对象。

- **参数**：
  - `db`: 编译后的数据库对象。

---

## 贡献

欢迎贡献代码！请阅读 [贡献指南](CONTRIBUTING.md) 了解如何参与项目开发。

---

## 许可证

本项目基于 [MIT 许可证](LICENSE) 发布。

---

## 致谢

- 感谢 [Intel Hyperscan](https://www.intel.com/content/www/us/en/developer/articles/technical/introduction-to-hyperscan.html) 提供的高性能正则表达式匹配库。
- 感谢 [Cython](https://cython.org/) 提供的 Python C 扩展支持。

---

## 联系方式

如有任何问题或建议，请联系：

- 作者：FGC
- 邮箱：13654918696@163.com
- GitHub：[FGC1](https://gitee.com/fgc1)

---

## 支持

如果你觉得这个项目有用，请给它一个 ⭐️ [GitHub Star](https://github.com/yourusername/hyperscan_package)！

---

## 相关项目

- [Hyperscan](https://www.intel.com/content/www/us/en/developer/articles/technical/introduction-to-hyperscan.html)：Intel 的高性能正则表达式匹配库。
- [Cython](https://cython.org/)：Python 的 C 扩展工具。