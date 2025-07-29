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
    """
    解析网页内容并提取所需字段
    """
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
    """用于从a中获得url"""
    attrs = a.attrs
    if 'href' in attrs:
        return attrs['href']
    else:
        return None

def get_son_url(soup, config: dict):
    """
    获得二级页面url的函数
    """
    config = config['son']
    css = config['css']
    if isinstance(soup, str):
        soup = BeautifulSoup(soup, 'html.parser')
    assert isinstance(soup, Tag)
    return [find_a_href(a) for a in soup.select(css)]

def get_Next_url(soup, config: str):
    """
    获得下一页url的函数
    """
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


def Spider(config: dict):
    """
    根据配置进行二级爬取
    """
    url_base = config['base_url']

    cur_url = url_base
    
    key_list = list(config['value'].keys())
    result = [key_list]
    try:
        while True:
            html = get_html(cur_url)
            for url in get_son_url(html, config):
                son_url = urljoin(url_base, url)
                print('spider_son: ', son_url)
                res = parse_url(son_url, config, True)
                li = []
                for k in key_list:
                    li.append(res[k])
                result.append(li)
                # break
            # break
            next_url = get_Next_url(html, config)
            if next_url is None:
                break
            cur_url = urljoin(url_base, next_url)
            print('~ next_url: ', next_url)
    except Exception as e:
        print("提取失败:", str(e))
    
    # # 打印结果
    print("提取结果:")
    print(result)
    
    return result