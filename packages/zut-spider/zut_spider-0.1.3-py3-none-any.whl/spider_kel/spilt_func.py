def extract_content(html, start_marker, end_marker):
    """
    根据起始和结束标记提取内容
    """ 
    start_index = html.find(start_marker)
    if start_index == -1:
        return ""
    start_index += len(start_marker)
    
    end_index = html.find(end_marker, start_index)
    if end_index == -1:
        return ""
    
    return html[start_index:end_index].strip()

func_dic = {
    'extract_content': extract_content
}