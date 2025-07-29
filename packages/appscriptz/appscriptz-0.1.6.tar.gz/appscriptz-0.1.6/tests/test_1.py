from appscriptz.main import APPManager



def test_main():
    appm = APPManager()
    appm.memorandum2notes('hello world')


def test_reminder():
    appm = APPManager()
    appm.memorandum2reminder('2025-05-19 13:48:13',
                             'hello\n world\n')

