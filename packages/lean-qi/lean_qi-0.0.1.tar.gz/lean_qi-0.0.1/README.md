# lean-qi

[![PyPI - Version](https://img.shields.io/pypi/v/lean-qi)](https://pypi.org/project/lean-qi/)
[![PyPI - License](https://img.shields.io/pypi/l/lean-qi)](https://pypi.org/project/lean-qi/)

`lean-qi` 是一个命令行工具，帮助用户在不同操作系统上自动安装 Lean 语言的工具链管理器 `elan`。本工具专为网络受限环境设计，自动选择并使用稳定高速的国内镜像源，无需用户手动配置。

## 特点

- 一条命令自动安装 `elan`，无需手动下载或配置镜像。
- 安装脚本已内置于包中，安装过程无需访问官方源站点。
- 支持 Linux、macOS 和 Windows。

## 安装

需要 Python 3.7 及以上版本。

通过 PyPI 安装：

```bash
pip install lean-qi
```

## 使用方法

安装完成后，在终端或命令行输入：

```bash
leanup install
```

程序会自动检测你的操作系统，并执行对应的安装流程。整个过程无需任何额外配置。

## 工作原理

`lean-qi` 在发布前会自动查询可用的国内镜像地址，并将其写入内置的安装脚本。用户在使用时，工具会直接调用这些经过优化的脚本，确保安装过程顺畅可靠。用户无需关心镜像的选择和配置，所有细节都已自动处理。

## 许可证

本项目采用 MIT 许可证。

---

作者: Hewzhew