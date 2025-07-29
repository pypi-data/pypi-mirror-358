""" 动作函数 """

from .scripts.applescript import Notes,Calulate,Reminder
from .scripts.aifunc import generate_schedule

class APPManager():
    def __init__(self):
        self.year = '2025年'
        self.habit ="7点-9点起床洗漱, 12点到14点吃饭+午休,19点以后就是自由时间"

    def execution_pool2calulate(self,execution_pool:str):
        if execution_pool:
            # 生成日程安排
            schedule_result = generate_schedule(execution_pool,habit =self.habit)
            print(schedule_result,'schedule_result')
            xx = [i for i in schedule_result.split('\n') if i!='']
            for xp in xx:
                v = [("2025年"+k if i<2 and k[4]!="年" else k) for i,k in enumerate(xp.split('$'))]
                Calulate.update(*v)
        else:
            print("未能解析到执行池内容")

    def memorandum2notes(self,text):
        Notes.write(text)


    def memorandum2reminder(self,text,date):
        for content in text.split("\n")[1:]:
            print(content,'content')
            Reminder.write_reminder(content, 
                list_name="工作",
                due_date=date,
                priority=2,
                notes="")
            