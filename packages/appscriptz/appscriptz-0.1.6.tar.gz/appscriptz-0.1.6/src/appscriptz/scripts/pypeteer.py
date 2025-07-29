""" pyppeteer 脚本"""

import asyncio
import pyppeteer

async def get_page_html(url: str) -> str | None:
    """
    使用 pypeteer 访问指定 URL，等待页面完全加载后获取 HTML 内容。

    Args:
        url: 要访问的网页 URL。

    Returns:
        页面的 HTML 内容字符串，如果发生错误则返回 None。
    """
    browser = None # 初始化 browser 变量，以便在 finally 块中检查
    try:
        # 启动浏览器
        # headless=True 表示无头模式运行（不显示浏览器窗口）
        # 可以设置为 headless=False 进行调试，会弹出一个浏览器窗口
        print("正在启动浏览器...")
        browser = await pyppeteer.launch(headless=True, 
                                         userDataDir='/Users/zhaoxuefeng/GitHub/test1/userdata3', 
                                         args=['--no-sandbox']) # 添加 --no-sandbox 参数，某些环境下可能需要

        page = await browser.newPage()

        print(f"正在访问网页: {url}")
        # 导航到指定 URL 并等待页面完全加载
        # waitUntil='networkidle0' 会等待直到网络连接数降至 0 且持续 500ms
        # 这通常意味着页面上的主要资源（包括通过 JS 加载的）都已经加载完成
        # 其他选项包括 'load', 'domcontentloaded', 'networkidle2'
        await page.goto(url, waitUntil='networkidle0')
        print("页面加载完毕，正在获取 HTML 内容...")

        # 获取页面的完整 HTML 内容
        html_content = await page.content()
        print("HTML 内容获取成功。")

        return html_content

    except pyppeteer.errors.TimeoutError:
        print(f"访问 {url} 超时。")
        return None
    except Exception as e:
        print(f"访问 {url} 时发生错误: {e}")
        return None
    finally:
        # 关闭浏览器实例
        if browser:
            print("正在关闭浏览器...")
            await browser.close()
            print("浏览器已关闭。")

#######  !###########
        def _get_articlie_link():
            # 目标网页的 URL
            url = "https://www.jiqizhixin.com"
            file_links = ["https://www.jiqizhixin.com/articles/2025-05-07-9",
                          "https://www.jiqizhixin.com/articles/2025-05-07-8",
                          "https://www.jiqizhixin.com/articles/2025-05-07-7",
                          "https://www.jiqizhixin.com/articles/2025-05-07-6",
                          ]
            return file_links
        
        def _get_articlie_link_2():
            # 目标网页的 URL
            url = "https://www.jiqizhixin.com"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/91.0.4472.124 Safari/537.36"
            }
            # 发送 HTTP 请求获取网页内容
            # response = requests.get(url)
            response = requests.get(url, headers=headers)

            # 检查请求是否成功
            if response.status_code == 200:
                # 解析 HTML 内容
                soup = BeautifulSoup(response.content, 'html.parser')

                # 提取所有文件链接
                file_links = []
                for link in soup.find_all('a', href=True,attrs={
                    'class': 'article-item__title t-strong js-open-modal',
                }):
                    href = link['href']
                    file_links.append(url + href)
            else:
                print("请求失败，状态码：", response.status_code)
            return file_links
        
        async def _get_context_from_jq_url(url):
            # 目标网页的 URL
             
            target_url = url
            html = await get_page_html(target_url)


            soup = BeautifulSoup(html, 'html.parser')

            # 提取网页中的文字内容
            text = soup.get_text()
            return text
            
        @lru_cache(maxsize=100)
        def _extra_text(text):
            template = """
            我希望你可以对一个内容进行汇总和总结, 我会给你一段网页的内容，你来用一些简短的文字告诉我这篇内容的主要信息, 以及列出其中相关的重点和链接

            网页内容:
            ---
            {text}
            ---

            输出信息:
            """

            llm = BianXieAdapter()
            llm.set_model("gpt-4o")
            prompt = template.format(text = text)
            completion = llm.product(prompt)
            return completion
        
        file_links = _get_articlie_link()
        print(file_links,'file_links')
        article = []
        for file_link in file_links:
            print(file_link)
            result = asyncio.run(_get_context_from_jq_url(file_link))
            xx = _extra_text(result)
            article.append(xx)
