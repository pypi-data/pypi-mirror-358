""" 开发支持工具 """

import functools
from itertools import islice
import subprocess
from contextlib import contextmanager
import traceback
import sys
import ast
import os
from llama_index.core.tools.types import ToolOutput
from llama_index.core.tools import FunctionTool
## locust 压力测试


def struct():
    """装饰器, 主要是通过注解来严格校验输入与输出的格式, 推荐工程化时使用
    """
    def outer_packing(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            ann_dict = func.__annotations__

            if len(args) !=0:
                remaining_items = islice(ann_dict.items(), None, len(args))
                args_result_dict = dict(remaining_items)
                args_result_list = list(args_result_dict.values())
                try:
                    for i,j in enumerate(args_result_list):
                        assert isinstance(args[i],j)
                except AssertionError as e:
                    raise AssertionError(f"位置: {i} 预期的输入是: {j}") from e

            try:
                for k,v in kwargs.items():
                    assert isinstance(v,ann_dict[k])
            except AssertionError as e:
                raise AssertionError(f"位置: {k} 预期的输入是: {v}") from e
            try:
                assert isinstance(result,ann_dict.get('return',object))
            except AssertionError as e:
                raise AssertionError("返回值格式不准确") from e

            return result
        return wrapper
    return outer_packing

@contextmanager
def safe_operation():
    """上下文方式的异常管理"""
    try:
        yield
    except Exception as e:
        error_info = traceback.format_exc()
        print(e,error_info) #详细信息
        raise Exception(" exception!") from e
        # log记录


####
class GitHubManager():
    """一个将当前github仓库的提交历史打印出来的工具
    获取可以用作它途
    """
    def __init__(self):
        self.mermaid_format = """
        ```mermaid
        {mermaid_code}
        ```
        """

    def get_origin(self):
        home = "/Users/zhaoxuefeng/GitHub/"

        for repo in ['toolsz',
                    'llmada',
                    'clientz',
                    'commender',
                    'mermaidz',
                    'kanbanz',
                    'querypipz',
                    'appscriptz',
                    'reallife-client-mac',
                    'designerz',
                    'algorithmz',
                    'reallife',
                    'promptlibz'
                    ]:
            os.system(f"git -C {os.path.join(home,repo)} push origin main")

    def generate_mermaid_git_graph(self,simulated_git_log):
        """
        # This is a simplified example. In a real scenario, you would run git log.
        # Here we simulate the output of git log --all --graph --pretty=format:%h,%d,%s
        # based on a simple history.
        """

        mermaid_code = "gitGraph\n"
        commits_seen = {} # To track commits and avoid duplicates if needed

        for line in simulated_git_log.strip().split('\n'):
            line = line.strip()
            if line.startswith('*'):
                # Parse the commit line
                # Handle potential extra space after * and split by the first two commas
                parts = line[1:].strip().split(',', 2)
                if len(parts) >= 2:
                    hash_val = parts[0].strip()
                    refs = parts[1].strip()
                    message = parts[2].strip() if len(parts) > 2 else ""

                    commit_line = f'    commit id: "{hash_val}"'

                    # Process references (branches, tags)
                    if refs:
                        # Remove parentheses and split by comma
                        ref_list = [r.strip() for r in refs.replace('(', '').replace(')', '').split(',') if r.strip()]
                        processed_refs = []
                        for ref in ref_list:
                            if '->' in ref:
                                ref = ref.split('->')[-1].strip() # Get the branch name after ->
                            if ref and ref != 'HEAD': # Exclude the simple HEAD reference
                                processed_refs.append(f'"{ref}"')
                        if processed_refs:
                            # Join with comma and space as it's a single tag attribute
                            commit_line += f' tag: {", ".join(processed_refs)}'


                    if message:
                        # Escape double quotes in message
                        message = message.replace('"', '\\"')
                        commit_line += f' msg: "{message}"'

                    mermaid_code += commit_line + "\n"
                    commits_seen[hash_val] = True

            # Note: Handling merge lines (|/ \) is more complex and not fully covered
            # in this simple parser, requires analyzing the graph structure.

        # print(mermaid_code)
        return mermaid_code

    def work(self):
        """运行

        """
        # 将命令拆分成一个列表，这是更安全的方式
        command = [
            "git",
            "log",
            "--all",
            "--graph",
            "--pretty=format:%h,%d,%s"
        ]

        try:
            # 执行命令
            # capture_output=True: 捕获标准输出和标准错误
            # text=True: 将捕获到的输出(bytes)解码为文本(str)
            # check=True: 如果命令返回非零退出码（表示有错误），则会抛出异常
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8' # 明确指定编码，避免乱码问题
            )

            # 捕获的输出存储在 result.stdout 属性中
            git_log_output = result.stdout

            # 现在你可以对这个字符串做任何你想做的事情了
            print("--- 捕获到的 Git Log 输出 ---")
            print(git_log_output)

            # 你甚至可以把它按行分割成一个列表
            log_lines = git_log_output.strip().split('\n')
            print("\n--- 输出的第一行 ---")
            print(log_lines[0])

        except FileNotFoundError:
            print("错误: 'git' 命令未找到。请确保 Git 已经安装并且在系统的 PATH 环境变量中。")
        except subprocess.CalledProcessError as e:
            # 如果 git 命令执行失败 (例如，不在一个 git 仓库中)
            print(f"执行 Git 命令时出错，返回码: {e.returncode}")
            print(f"错误信息 (stderr):\n{e.stderr}")
        return git_log_output


    def run(self):
        """运行

        Returns:
            _type_: _description_
        """
        git_log_output = self.work()
        mermaid_code = self.generate_mermaid_git_graph(git_log_output)
        return self.mermaid_format.format(mermaid_code = mermaid_code)

def package(fn,name:str = None,description:str = None):
    """将一般的函数打包成工具

    Args:
        fn (function): 编写的函数
        name (str, optional): 函数名.
        description (str, optional): 函数描述. Defaults to None.

    Returns:
        FunctionTool: functioncall
    """

    if name is not None or description is not None:
        return FunctionTool.from_defaults(fn=fn,
                                      name = name,
                                      description = description)
    else:
        return FunctionTool.from_defaults(fn=fn)

def input_multiline():
    """解决某些时候换行代表enter 的情况

    Returns:
        _type_: _description_
    """
    print("请输入内容（按 Ctrl+D 或 Ctrl+Z 后按回车结束输入）：")
    multi_line_input = sys.stdin.read()
    print("你输入的内容是：")
    print(multi_line_input)
    return multi_line_input


class AutoAPIMD():
    """
    
    input_file = '/Users/zhaoxuefeng/GitHub/llmada/src/llmada/core.py'  # 替换为你的 Python 文件路径
    output_file = 'api_documentation.md'
    AutoAPIMD().generate_api_docs(input_file, output_file)
    """
    def __init__(self):
        pass

    def parse_python_file(self,file_path):
        """
        解析 Python 文件，提取类和函数的信息，包括注解和数据类型。
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        tree = ast.parse(content)

        classes = []
        functions = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': []
                }
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        method_info = self.parse_function_or_method(sub_node, 'method')
                        class_info['methods'].append(method_info)
                classes.append(class_info)
            elif isinstance(node, ast.FunctionDef):
                function_info = self.parse_function_or_method(node, 'function')
                functions.append(function_info)

        return classes, functions

    def parse_function_or_method(self,node, kind):
        """
        解析函数或方法的详细信息，包括注解和数据类型。
        """
        info = {
            'kind': kind,
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'args': [],
            'return_type': None,
            'signature': None
        }

        # 构建函数签名
        args_list = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f': {ast.unparse(arg.annotation)}'
            if arg in node.args.defaults:
                default_index = node.args.args.index(arg) - len(node.args.defaults)
                default_value = ast.unparse(node.args.defaults[default_index])
                arg_str += f' = {default_value}'
            args_list.append(arg_str)

        # 处理返回值类型
        return_type_str = ''
        if node.returns:
            return_type_str = f' -> {ast.unparse(node.returns)}'

        # 构建完整的函数签名字符串
        info['signature'] = f'def {node.name}({", ".join(args_list)}){return_type_str}:'

        return info

    def generate_markdown(self,classes, functions, output_file):
        """
        生成 Markdown API 文档，使用类似 Python 语法的格式。
        """
        with open(output_file, 'w', encoding='utf-8') as file:
            # 写入标题
            file.write('# API Documentation\n\n')
            file.write(f'# {output_file}')
            # 写入类信息
            if classes:
                file.write('## Classes\n\n')
                for cls in classes:
                    file.write(f'### {cls["name"]}\n')
                    if cls['docstring']:
                        file.write(f'{cls["docstring"]}\n\n')
                    else:
                        file.write('No docstring provided.\n\n')

                    # 写入方法信息
                    if cls['methods']:
                        file.write('#### Methods\n')
                        for method in cls['methods']:
                            file.write(f'```python\n{method["signature"]}\n```\n')
                            if method['docstring']:
                                file.write(f'{method["docstring"]}\n\n')
                            else:
                                file.write('No docstring provided.\n\n')

            # 写入函数信息
            if functions:
                file.write('## Functions\n\n')
                for func in functions:
                    file.write(f'```python\n{func["signature"]}\n```\n')
                    if func['docstring']:
                        file.write(f'{func["docstring"]}\n\n')
                    else:
                        file.write('No docstring provided.\n\n')

    def generate_api_docs(self,file_path, output_file):
        """
        生成 API 文档的主函数。
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        if not file_path.endswith('.py'):
            print(f"Only Python files are supported: {file_path}")
            return

        classes, functions = self.parse_python_file(file_path)
        self.generate_markdown(classes, functions, output_file)
        print(f"API documentation generated successfully and saved to {output_file}")

        with open(output_file,'r') as f:
            text = f.read()
        return text
