from .base import mcp
import json
import requests
import os
key = os.environ.get('GAODE_KEY')

@mcp.tool()
def get_poi_info(page:int = 1):
    '''
    获得中原工学院(新郑市)周边的餐饮店信息
    :param 
        page:int = 1 页码
    
    :return
        json
            包含键: 
                tag:str 餐品种类,
                name:str 店名,
                alias:str 别名,
                address:str 地址, 
                tel:str 电话,
                photos:lsit(dict) = list({url:str}) 相关图片链接的列表,
                biz_ext: dict = {rating: 评分, cost: 人均消费}
    '''
    offset = 5
    base_url = 'https://restapi.amap.com/v3/place/text'
    city = '410184'  # 新郑市
    citylimit = 'true'
    types = '050000'
    page = 1
    extensions = 'all'

    url = f'{base_url}?types={types}&city={city}&offset={offset}&page={page}&key={key}&extensions={extensions}&citylimit={citylimit}'

    response = requests.get(url)
    data = response.json()

    res_li = []
    keys = ['tag', 'name', 'alias', 'address', 'tel', 'photos', 'biz_ext']
    for dic in data['pois']:
        li = {}
        for k in keys:
            li[k] = str(dic[k])
        res_li.append(li)
    return json.dumps(res_li)