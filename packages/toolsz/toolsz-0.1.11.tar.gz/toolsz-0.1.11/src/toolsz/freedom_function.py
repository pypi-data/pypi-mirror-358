import re
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_python_code(text: str) -> str:
    """从文本中提取python代码
    Args:
        text (str): 输入的文本。
    Returns:
        str: 提取出的python文本
    """
    pattern = r"```python([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        return matches[0].strip()  # 添加strip()去除首尾空白符
    else:
        logging.warning("未能在文本中提取到Python代码块。")
        return ""  # 返回空字符串或抛出异常，此处返回空字符串


def work(x="帮我将 日期 2025/12/03 向前回退12天", **kwargs):
    try:
        from llmada.core import BianXieAdapter

        params = locals()

        # 优化提示信息，只在kwargs不为空时添加入参信息
        prompt_user_part = f"{x}"
        if kwargs:
            prompt_user_part += f' 入参 {params["kwargs"]}'

        bx = BianXieAdapter()
        result = bx.product(
            prompt=f"""
# 用户输入案例：
# [用户指令和输入参数的组合，例如：帮我将 日期 2025/12/03 向前回退12天 入参 data_str = "2025/12/03"]
#
# 根据用户输入案例，自动识别用户指令，提取所有“入参”信息及其名称和值。
# 编写一个 Python 函数，函数名称固定为 `Function`。
# 函数的输入参数应严格按照识别出的“入参”名称和类型来定义。
# 函数只包含一个定义，不依赖外部库或复杂结构。
# 函数应根据用户指令实现对应功能。
# 代码应简洁且易于执行。
# 输出格式应为完整的 Python 函数定义，包括文档字符串（docstring）。
{prompt_user_part}
"""
        )
        xx = extract_python_code(result)

        if not xx:
            logging.error("提取到的Python代码为空，无法执行。")
            return None  # 返回None或抛出异常

        runs = xx + "\n" + f'result = Function(**{params["kwargs"]})'
        logging.info(f"即将执行的代码：\n{runs}")

        rut = {"result": ""}
        # 使用exec执行代码，并捕获可能的错误
        try:
            exec(
                runs, globals(), rut
            )  # 将globals()作为全局作用域，避免依赖外部locals()
        except Exception as e:
            logging.error(f"执行动态生成的代码时发生错误: {e}")
            return None  # 返回None或抛出异常

        return rut.get("result")

    except ImportError:
        logging.error("无法导入 llmada.core，请确保已安装相关库。")
        return None
    except Exception as e:
        logging.error(f"在 work 函数中发生未知错误: {e}")
        return None


# 示例调用
if __name__ == "__main__":
    pass
    # 示例1：带参数
    # result1 = work(x="帮我将 日期 2025/12/03 向前回退12天", data_str="2025/12/03", days=12)
    # print(f"示例1 执行结果: {result1}")

    # 示例2：不带参数
    # result2 = work(x="帮我计算 1加1")
    # print(f"示例2 执行结果: {result2}")
