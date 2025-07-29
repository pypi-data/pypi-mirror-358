import sys
import subprocess
import platform
import os
from importlib.resources import files

def print_windows_guide():
    """
    Print a Chinese guide for users before running the official elan installer on Windows.
    This helps users understand the upcoming English prompts.
    （在 Windows 上执行 elan 安装程序前，打印一份中文操作指南，帮助用户理解后续英文界面。）
    """
    guide_text = """
----------------------------------------------------------------------
[leanup 中文操作指南]

您即将进入 elan 的官方英文安装界面。以下是您将看到的内容的中文说明：

【elan 的欢迎语会告诉您】:
它会下载并安装 Elan (Lean语言版本管理器)，以及一个默认的 Lean 工具链。
它会将 Elan 的程序路径添加到您的系统环境变量 (PATH) 中，这样您就可以在任何地方使用 lean, lake, elan 等命令。
您可以随时通过运行 `elan self uninstall` 来卸载并撤销所有更改。

【您将看到以下选项】:
Current installation options:
      default toolchain: stable   (默认安装 stable 工具链)
     modify PATH variable: yes      (会自动为您配置环境变量)

1) Proceed with installation (default)  (选项1: 继续安装 - 这是默认选项)
2) Customize installation              (选项2: 自定义安装)
3) Cancel installation                 (选项3: 取消安装)

【建议操作】:
通常，您只需直接按下键盘上的 `1` 键，然后再按 `Enter` 键即可。
----------------------------------------------------------------------

现在，即将启动 elan 安装程序...
"""
    print(guide_text)


def install_elan():
    """
    Locate and execute the appropriate installer script for elan based on the current OS.
    （根据当前操作系统，查找并执行包内的 elan 安装脚本。）
    """
    current_os = platform.system()

    try:
        if current_os in ["Linux", "Darwin"]:
            # On Linux/macOS, ensure the script is executable before running.
            # This is necessary because scripts extracted from package resources may lack execute permissions.
            # （在 Linux/macOS 上，需确保脚本有执行权限，因为从包资源解压出来的脚本可能没有执行权限。）
            print("Detected Linux/macOS. Preparing to execute bundled elan-init.sh script...")
            script_path_obj = files("leanup").joinpath("elan-init.sh")
            with script_path_obj.open() as script_file:
                script_path = script_file.name
            os.chmod(script_path, 0o755)
            subprocess.run([script_path], check=True)

        elif current_os == "Windows":
            print_windows_guide()
            # Use "-ExecutionPolicy Bypass" to allow running the PowerShell script regardless of the user's policy settings.
            # This avoids failures due to restrictive execution policies on some Windows systems.
            # （使用 "-ExecutionPolicy Bypass" 以避免因用户本地策略限制导致 PowerShell 脚本无法运行。）
            script_path_obj = files("leanup").joinpath("elan-init.ps1")
            with script_path_obj.open() as script_file:
                script_path = script_file.name
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], 
                check=True
            )

        else:
            print(f"Error: Unsupported operating system: {current_os}")
            return

        print("\nelan installer script finished.")

    except FileNotFoundError:
        print("Error: Installer script not found in package. Please check packaging configuration.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Installer script failed with exit code: {e.returncode}")


def main():
    """
    Entry point for the leanup CLI tool.
    （leanup 命令行工具的主入口。）
    """
    args = sys.argv[1:]
    if len(args) == 1 and args[0] == 'install':
        install_elan()
    else:
        print("欢迎使用 leanup！...") # 省略