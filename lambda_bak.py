import codecs

from DrissionPage import ChromiumPage
from DrissionPage.common import Keys

def safe_decode(data):
    if isinstance(data, str):
        return data
    elif isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data.decode('utf-8', errors='replace')
    else:
        return str(data)

def represent_unicode(text):
    return ''.join(char if ord(char) < 128 else f'\\u{ord(char):04x}' for char in text)

def fix_encoding(data, show_raw=False):
    text = safe_decode(data)
    if show_raw:
        print("Raw data:", repr(data))
    return represent_unicode(text)


def windows1252_to_utf8(text):

    text = text.replace('\\u0000', '')
    # 首先，将文本编码为 Windows-1252（假设它是 Windows-1252）
    windows1252_bytes = text.encode('Windows-1252', errors='replace')
    # 首先，将文本编码为 iso-8859-2（假设它是 iso-8859-2）
    # windows1252_bytes = text.encode('iso-8859-2', errors='replace')

    # 替换所有的?
    # windows1252_bytes = windows1252_bytes.replace(b'?', b'')
    # windows1252_bytes = windows1252_bytes.replace(b'\\u0000', b'')

    # 然后，将这些字节解码为 UTF-8
    utf8_text = windows1252_bytes.decode('utf-8', errors='replace')

    return utf8_text

page = ChromiumPage()
page.get('https://lambda.chat/chatui/')  # 访问网址，这行产生的数据包不监听

page.listen.start('https://lambda.chat/chatui/conversation')  # 开始监听，指定获取包含该文本的数据包

text_areas = page.eles('tag:textarea')  # 获取所有textarea

# 判定是否有textarea
if text_areas:
    text_areas[0].click()  # 点击第一个textarea
    text_areas[0].input('你好 帮我写一个冒泡排序')  # 输入文本
    text_areas[0].input(Keys.ENTER)  # 输入文本
else:
    print('没有找到textarea')
for packet in page.listen.steps():
    if packet.response.body:
        # 打印packet.response.body的类型
        print(type(packet.response.body))
        # 打印packet.response.body的内容
        # print(packet.response.body)
        # 判断 是不是 str类型
        if type(packet.response.body) == str:
            print(windows1252_to_utf8(packet.response.body))
            # fixed_text = fix_encoding(packet.response.body, show_raw=True)
            # print(fixed_text)
