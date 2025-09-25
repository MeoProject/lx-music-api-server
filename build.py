import subprocess
import toml
import sys
import re
import os


def setup_console_encoding():
    """设置控制台编码为UTF-8，解决Windows下的编码问题"""
    if sys.platform == "win32":
        # 设置Windows控制台编码为UTF-8
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
        # 尝试设置控制台代码页为UTF-8
        try:
            os.system("chcp 65001 > nul 2>&1")
        except:
            pass


def get_latest_tag():
    """获取最新的Git标签"""
    try:
        tags = (
            subprocess.check_output(["git", "tag", "--sort=v:refname"])
            .decode("utf-8")
            .strip()
            .split("\n")
        )
        if not tags or tags == [""]:
            return None

        current_version = toml.load("./pyproject.toml")["tool"]["poetry"]["version"]
        # 如果最新标签等于当前版本，返回倒数第二个标签
        return (
            tags[-1]
            if tags[-1] != current_version
            else tags[-2] if len(tags) > 1 else None
        )
    except subprocess.CalledProcessError:
        return None
    except Exception as e:
        print(f"[ERROR] 获取标签失败: {e}")
        return None


def get_specified_tag(index):
    """获取指定索引的Git标签"""
    try:
        result = (
            subprocess.check_output(["git", "tag", "--sort=v:refname"])
            .decode("utf-8")
            .strip()
            .split("\n")
        )
        tags = [tag.strip() for tag in result if tag.strip()]

        if not tags:
            return None

        if abs(index) > len(tags):
            return None

        return tags[index]
    except subprocess.CalledProcessError:
        return None
    except Exception as e:
        print(f"[ERROR] 获取指定标签失败: {e}")
        return None


def get_changelog():
    """生成更新日志"""
    latest_tag = get_specified_tag(-1)
    if not latest_tag:
        print("[WARNING] 无法获取最新标签，将获取所有提交记录")
        cmd = ["git", "log", "--pretty=format:%h %s"]
    else:
        cmd = ["git", "log", f"{latest_tag}..HEAD", "--pretty=format:%h %s"]

    try:
        res = subprocess.check_output(cmd, encoding="utf-8").strip()
        if not res:
            return "## 暂无更新"

        res_lines = res.split("\n")
    except subprocess.CalledProcessError as e:
        return f"## 获取更新日志失败: {e}"

    # 使用原始字符串修复正则表达式警告
    commit_pattern = r"^[a-f0-9]+\s+(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|notice|deps)(\([^)]*\))?:\s*(.+)$"

    # 分类消息
    categories = {
        "notice": {"title": "## 公告", "messages": []},
        "feat": {"title": "## 功能更新", "messages": []},
        "fix": {"title": "## Bug修复", "messages": []},
        "docs": {"title": "## 文档更新", "messages": []},
        "build": {"title": "## 构建配置", "messages": []},
        "style": {"title": "## 代码样式", "messages": []},
        "refactor": {"title": "## 代码重构", "messages": []},
        "perf": {"title": "## 性能优化", "messages": []},
        "test": {"title": "## 测试相关", "messages": []},
        "ci": {"title": "## CI/CD", "messages": []},
        "chore": {"title": "## 杂项更新", "messages": []},
        "revert": {"title": "## 回滚更改", "messages": []},
        "other": {"title": "## 其他", "messages": []},
        "deps": {"title": "## 依赖更新", "messages": []},
        "unknown": {"title": "## 未知类型的提交", "messages": []},
    }

    for line in res_lines:
        if not line.strip():
            continue

        # 尝试匹配符合规范的提交信息
        match = re.match(commit_pattern, line)
        if match:
            commit_hash = line.split()[0]
            commit_type = match.group(1)
            scope = match.group(2) if match.group(2) else ""
            message = match.group(3)

            # 格式化消息
            formatted_msg = f"{commit_hash} {commit_type}{scope}: {message}"

            if commit_type in categories:
                categories[commit_type]["messages"].append(formatted_msg)
            else:
                categories["other"]["messages"].append(formatted_msg)
        else:
            # 不符合规范的提交信息
            categories["unknown"]["messages"].append(line)

    # 生成最终的更新日志
    changelog_parts = []

    # 按照重要性排序输出
    priority_order = [
        "notice",
        "feat",
        "fix",
        "perf",
        "docs",
        "refactor",
        "build",
        "test",
        "ci",
        "style",
        "chore",
        "revert",
        "other",
        "deps",
        "unknown",
    ]

    for category_type in priority_order:
        category = categories[category_type]
        if category["messages"]:
            changelog_parts.append(category["title"])
            for msg in category["messages"]:
                # 清理可能的emoji和特殊字符，避免编码问题
                # clean_msg = msg.encode("utf-8", "ignore").decode("utf-8", "ignore")
                changelog_parts.append(f"- {msg}")

    return "\n".join(changelog_parts) if changelog_parts else "## 暂无更新"


def get_python_path():
    """获取Python可执行文件路径"""
    return sys.executable


def get_latest_commit_sha():
    """获取最新提交的SHA值（前7位）"""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip()[:7]
        )
    except subprocess.CalledProcessError:
        return "unknown"


def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller

        return True
    except ModuleNotFoundError:
        print(
            "[ERROR]: 请先安装 PyInstaller 模块。",
            "如果您已经安装了该模块，",
            "请检查是否忘记激活虚拟环境。",
            sep="\n",
        )
        return False


def run_pyinstaller(output_name):
    """运行PyInstaller构建过程"""
    if not check_pyinstaller():
        sys.exit(1)

    # 确保图标文件存在
    icon_path = "res/icon.ico"
    if not os.path.exists(icon_path):
        print(f"[WARNING] 图标文件 {icon_path} 不存在，将不使用图标")
        icon_args = []
    else:
        icon_args = ["-i", icon_path]

    # 构建命令
    cmd = [
        get_python_path(),
        "-m",
        "PyInstaller",
        "-F",  # 单文件
        *icon_args,
        "--name",
        output_name,
        "app.py",
    ]

    print(f"[INFO] 开始构建: {output_name}")
    print(f"[INFO] 执行命令: {' '.join(cmd)}")

    popen = subprocess.Popen(cmd)
    print(f"[INFO] PyInstaller 进程已启动, PID: {popen.pid}")
    print("[INFO] 请稍候...")

    popen.wait()

    if popen.returncode != 0:
        print(
            f"[ERROR]: PyInstaller 构建失败，返回代码 {popen.returncode}。",
            "请检查输出日志，",
            "可能包含错误或警告信息。",
            sep="\n",
        )
        sys.exit(popen.returncode)
    else:
        print("[SUCCESS]: PyInstaller 构建成功。")
        dist_dir = os.path.join(os.getcwd(), "dist")
        if os.path.exists(dist_dir):
            files = os.listdir(dist_dir)
            if files:
                file_path = os.path.join(dist_dir, files[0])
                print(f"[SUCCESS] 文件路径: {file_path}")
                print(
                    f"[SUCCESS] 文件大小: {os.path.getsize(file_path) / 1024 / 1024:.2f} MB"
                )


def build_test(file_name):
    """构建测试版本"""
    os.environ["build"] = "T"
    sha = get_latest_commit_sha()
    output_name = file_name if file_name else f"lx-music-api-server_{sha}"
    run_pyinstaller(output_name)


def build_release(file_name=""):
    """构建发布版本"""
    os.environ["build"] = "R"

    try:
        config = toml.load("./pyproject.toml")
        version = config["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError):
        print("[ERROR] 无法读取版本信息，请检查 pyproject.toml 文件")
        sys.exit(1)

    output_name = file_name if file_name else f"lx-music-api-server_{version}"
    run_pyinstaller(output_name)


def parse_arguments():
    """解析命令行参数"""
    argv = sys.argv[1:]

    commands = []
    options = {}

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith("-"):
            if arg in ["-f", "--fileName"]:
                if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                    options["fileName"] = argv[i + 1]
                    i += 1
                else:
                    print("[ERROR] 未指定文件名")
                    sys.exit(1)
            elif arg in ["-h", "--help"]:
                options["help"] = True
            else:
                print(f'[ERROR] 无效选项 "{arg}"')
                sys.exit(1)
        else:
            commands.append(arg)
        i += 1

    return commands, options


def show_help():
    """显示帮助信息"""
    help_text = """
使用方法: python build.py [选项] <命令>

选项:
  -f, --fileName <文件名>    指定可执行文件的名称
  -h, --help                显示此帮助信息并退出

命令:
  build test                构建测试版可执行文件
  build release             构建发布版可执行文件
  changelog                 显示更新日志

示例:
  python build.py build test
  python build.py build release -f my_server
  python build.py changelog
"""
    print(help_text)


def main():
    """主函数"""
    # 设置控制台编码
    setup_console_encoding()

    commands, options = parse_arguments()

    # 处理帮助选项
    if options.get("help"):
        show_help()
        sys.exit(0)

    # 获取文件名选项
    file_name = options.get("fileName", "")

    # 处理命令
    if not commands:
        print("[ERROR] 未指定命令")
        show_help()
        sys.exit(1)

    command = commands[0]

    if command == "build":
        if len(commands) == 1:
            print("[WARNING] 未指定构建类型，默认构建测试版")
            build_test(file_name)
        elif len(commands) >= 2:
            build_type = commands[1]
            if build_type == "test":
                build_test(file_name)
            elif build_type == "release":
                build_release(file_name)
            else:
                print(f"[ERROR] 无效的构建类型: {build_type}")
                print("[INFO] 有效的构建类型: test, release")
                sys.exit(1)

    elif command == "changelog":
        changelog = get_changelog()
        print(changelog)

    else:
        print(f"[ERROR] 无效的命令: {command}")
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 发生未预期的错误: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
