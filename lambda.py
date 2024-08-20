import asyncio
import html2text
from DrissionPage import ChromiumPage
from DrissionPage.common import Keys

def html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    return h.handle(html_content)

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
    windows1252_bytes = text.encode('Windows-1252', errors='replace')
    utf8_text = windows1252_bytes.decode('utf-8', errors='replace')
    return utf8_text

async def monitor_network(page):
    for packet in page.listen.steps():
        if packet.response.body:
            if isinstance(packet.response.body, str):
                return True
        await asyncio.sleep(0.01)
    return False


async def monitor_chat(page):
    total_markdown = ''
    no_change_count = 0
    max_no_change = 100

    while True:
        removeEles = page.eles('css:[title="Copy to clipboard"]')
        if removeEles:
            for removeEle in removeEles:
                page.remove_ele(removeEle)
        elements = page.eles('css:.group.relative.justify-start')
        if elements:
            new_total_html = elements[-1].html
            new_total_markdown = html_to_markdown(new_total_html)

            if new_total_markdown != total_markdown:
                if total_markdown:
                    # 找到新增的部分
                    delta = new_total_markdown[len(total_markdown):]
                else:
                    delta = new_total_markdown

                print(delta, end='', flush=True)
                total_markdown = new_total_markdown
                no_change_count = 0
            else:
                no_change_count += 1
        else:
            no_change_count += 1

        if no_change_count >= max_no_change:
            print("\n聊天内容似乎已经停止更新")
            return

        await asyncio.sleep(1)


async def main():
    page = ChromiumPage()
    page.get('https://lambda.chat/chatui/')

    text_areas = page.eles('tag:textarea')

    page.listen.start('https://lambda.chat/chatui/conversation')

    if text_areas:
        text_areas[0].click()
        text_areas[0].input('你好 帮我写一个冒泡排序')
        text_areas[0].input(Keys.ENTER)
    else:
        print('没有找到textarea')

    # network_task = asyncio.create_task(monitor_network(page))
    chat_task = asyncio.create_task(monitor_chat(page))

    done, pending = await asyncio.wait(
        [chat_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    try:
        await asyncio.gather(*pending)
    except asyncio.CancelledError:
        pass

    # if network_task in done:
    #     print("\n网络请求已完成")
    # else:
    #     print("\n聊天监控已结束")

if __name__ == "__main__":
    asyncio.run(main())
