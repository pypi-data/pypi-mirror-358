from .base import zut_mcp
import wikipedia
wikipedia.set_lang("zh")

@zut_mcp.tool()
def wikipedia_search(query) -> str:
    """使用Wikipedia搜索功能
    
    参数：
    query: 搜索的标题
    return: Wikipedia中与query相关的标题列表(str)"""
    return str(wikipedia.search(query))

@zut_mcp.tool()
def wikipedia_summary(title) -> str:
    """使用Wikipedia摘要功能
    
    参数：
    title: 搜索的标题(必须存在!否则报错!)
    """
    return wikipedia.summary(title, auto_suggest=False)

@zut_mcp.tool()
def wikipedia_page(title) -> str:
    """使用Wikipedia页面功能
    
    参数：
    title: 搜索的标题(必须存在!否则报错!)
    """
    
    page = wikipedia.page(title, auto_suggest=False)
    
    title = page.title
    content = page.content
    url = page.url
    
    res = f'''
    标题：{title}
    链接：{url}
    内容：{content}
    '''
    return res