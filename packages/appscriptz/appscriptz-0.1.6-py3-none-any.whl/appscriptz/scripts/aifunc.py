""" ai 脚本"""

from datetime import datetime
from promptlibz import Templates,TemplateType #TODO 修改
from llmada import BianXieAdapter

def generate_schedule(text: str,habit: str="") -> str:
    """
    使用 GPT 模型生成日程安排
    :param text: 输入文本
    :return: 生成的日程安排结果
    """
    llm = BianXieAdapter()
    llm.set_model("o3-mini")
    template = Templates(TemplateType.GENERATE_SCHEDULE)
    current_utc_time = str(datetime.today())[:-7]
    prompt = template.format(text=text,habit=habit,current_utc_time = current_utc_time)
    completion = llm.product(prompt)
    return completion
