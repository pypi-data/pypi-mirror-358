import re
import requests
from bs4 import BeautifulSoup, Tag
from .spilt_func import func_dic
from urllib.parse import urljoin

def clean_html_tags(content):
    """
    清除HTML标签并处理特殊字符
    """
    if not content:
        return ""
    
    # 使用BeautifulSoup解析内容
    soup = BeautifulSoup(content, 'html.parser')
    
    # 获取文本并清理
    text = soup.get_text(separator="\n", strip=True)
    
    # 替换常见HTML实体
    replacements = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'"
    }
    
    for entity, char in replacements.items():
        text = text.replace(entity, char)
    
    return text.strip()

def parse_page(html, config: dict, if_clean:bool = False):
    """
    解析网页内容并提取所需字段
    """
    # 提取整个内容块
    content_dic = config['content']
    func = func_dic[content_dic['spilt_func']]
    content_block = func(html, *content_dic['spilt_args'])
    
    if not content_block:
        return {}
    
    res_dict = {}
    for k, value_dic in config['value'].items():
        func = func_dic[value_dic['spilt_func']]
        content = func(content_block, *value_dic['spilt_args'])
        if if_clean:
            content = clean_html_tags(content)
        res_dict[k] = content
    
    return res_dict

def parse_url(url, config: dict, if_clean: bool = False):
    html = get_html(url)
    result = parse_page(html, config, if_clean)
    return result

def get_html(url):
    # 发送HTTP请求
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 检查请求是否成功
    response.encoding = response.apparent_encoding
    
    return response.text

def get_encoding(url):
    # 发送HTTP请求
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    response.encoding = response.apparent_encoding
    
    return response.apparent_encoding

def find_a_href(a):
    attrs = a.attrs
    if 'href' in attrs:
        return attrs['href']
    else:
        return None

def get_son_url(soup, config: dict):
    config = config['son']
    css = config['css']
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, 'html.parser')
    assert isinstance(soup, Tag)
    return [find_a_href(a) for a in soup.select(css)]

def get_Next_url(soup, config: str):
    config = config['Next']
    css = config['css']
    name = config.get('name', '')
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, 'html.parser')
    assert isinstance(soup, Tag)
    li = soup.select(css)
    if len(li) == 0: return None
    a = li[0]
    if name != '':
        for i in li:
            if i.text == name:
                a = i
                break
    return find_a_href(a)