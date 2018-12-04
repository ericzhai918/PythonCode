import configparser

import requests
import re
import json
import random
import math
import time
from meituan_food_db import *


def get_all_city(city_list):
    url = 'http://%s.meituan.com/meishi/pn%s/'
    for city in city_list.split(','):
        for i in range(32):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
                'Upgrade-Insecure-Requests': '1',
                'Host': '%s.meituan.com' % (city),
                'Referer': 'http://%s.meituan.com/' % (city)
            }
            r = requests.get(url % (city, i + 1), headers=headers)
            shop_Ids = re.findall('"poiId":(\d+),', r.text)
            uuid = re.findall('"uuid":"(.*?)",', r.text)
            get_shop_info(city, uuid, shop_Ids)


def get_shop_info(city, uuid, shop_Ids):
    for shop_Id in shop_Ids:
        url = 'http://www.meituan.com/meishi/%s/' % (id)
        headers = {
            'Host': 'www.meituan.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }

        for n in range(11):
            number = random.randint(0, 11)
            cookieStr = cookieList[number]
            cookies = {}
            for i in cookieStr.split(';'):
                cookies[i.split('=')[0]] = i.split('=')[1]
            try:
                r = requests.get(url=url, headers=headers, cookies=cookies)
                break
            except:
                pass

        if r:
            if 'detailInfo' in r.text:
                shop_info = {}
                recommended_food_info = {}
                # 先用正则匹配，再转为Json格式
                all = re.findall('("\$meta":.*),"crumbNav"', r.text)
                all_json = json.loads("{%s}" % all[0])

                # 获取店铺信息
                shop_info['shop_city'] = city
                shop_info['shop_id'] = shop_Id
                shop_info['shop_name'] = all_json['detailInfo']['name']
                shop_info['shop_address'] = all_json['detailInfo']['address']
                shop_info['shop_phone'] = all_json['detailInfo']['phone']
                shop_info['shop_openTime'] = all_json['detailInfo']['openTime']
                shop_info['shop_avgScore'] = all_json['detailInfo']['avgScore']
                shop_info['shop_latitude'] = all_json['detailInfo']['latitude']
                shop_info['shop_longitude'] = all_json['detailInfo']['longitude']

                # 获取推荐菜和价格信息
                recommended_food = all_json['recommended']
                for i in recommended_food:
                    recommended_food_info[i['name']] = i['price']

                # 入库
                shop_db(shop_info)

                get_shop_comments(uuid[0], shop_Id)


def get_shop_comments(uuid, shop_Id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    url = 'http://www.meituan.com/meishi/api/poi/getMerchantComment?uuid=%s&platform=1&partner=126&originUrl=https%3A%2F%2Fwww.meituan.com%2Fmeishi%2F6903956%2F&riskLevel=1&optimusCode=1&id=%s&userId=&offset=%s&pageSize=10&sortType=1'
    r = requests.get(url % (uuid, shop_Id, '0'), headers=headers)
    total = r.json()['data']['total']

    for i in range(math.ceil(int(total) / 10)):
        offset = str(10 * i)
        r = requests.get(url % (uuid, shop_Id, offset), headers=headers)

        # 获取评论信息
        for c in r.json()['data']['comments']:
            comment_info = {}
            comment_info['shop_Id'] = shop_Id
            comment_info['userId'] = c.get('userId', '')
            comment_info['reviewId'] = c.get('reviewId', '')
            comment_info['userName'] = c.get('userName', '')
            comment_info['userScore'] = str(int(c.get('star', '')) / 10)
            comment_info['comment'] = c.get('comment', '')
            comment_info['commentTime'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                        time.localtime(int(c.get('commentTime', '0')) / 1000))
            comment_info['merchantComment'] = c.get('merchantComment','')
            # 入库
            comment_db(comment_info)

if __name__ == "__main__":
    # Cookies列表，每条Cookies可以在谷歌浏览器的无痕模式获取
    # 由于发送请求要cookies，而且多次访问使用同一个cookies会封，因此设置列表
    cookieList = [
        'uuid=cd2c133a9de3404abeff.1530839677.1.0.0; __mta=214276008.1530839721718.1530839721718.1530839721718.1; ci=20; rvct=20; _lxsdk_cuid=1646d28e328bb-09eb8d7819b322-3c3c590b-100200-1646d28e329c8; client-id=633cc50c-0123-4590-83f4-8cf0d237c4d8; _lxsdk=1646d28e328bb-09eb8d7819b322-3c3c590b-100200-1646d28e329c8; lat=23.134149; lng=113.339257; _lxsdk_s=1646d28e32a-160-260-705%7C%7C12',
        'client-id=1bc12fd0-cca1-430c-8003-4b85c1163939; uuid=0fc677ab-960e-418f-8bdd-b6e8a54d3b68; _lxsdk_cuid=1646d2f22c20-09bf00baec4f26-3c3c590b-100200-1646d2f22c34f; _lxsdk=1646d2f22c20-09bf00baec4f26-3c3c590b-100200-1646d2f22c34f; lat=23.134149; lng=113.339257; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=92; _lxsdk_s=1646d2f22c5-28a-b2e-a8b%7C%7C10',
        'client-id=257253a9-c25c-4dfa-b878-c871c03759d8; uuid=91b7cee5-8290-4ce0-9dde-7bbe695fe523; _lxsdk_cuid=1646d681708c8-0452f6a6b668e7-3c3c590b-100200-1646d6817085e; _lxsdk=1646d681708c8-0452f6a6b668e7-3c3c590b-100200-1646d6817085e; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=504; rvct=504; _lxsdk_s=1646d68170a-c91-0d3-d24%7C%7C7; lat=22.7698; lng=112.966987',
        'client-id=da36535f-abbc-4fec-ac11-a09329192775; uuid=163a9d99-c187-43b0-88d4-3f2d05d9ecaf; _lxsdk_cuid=1646d56afe61-0ccb5ece0a811c-3c3c590b-100200-1646d56afe880; _lxsdk=1646d56afe61-0ccb5ece0a811c-3c3c590b-100200-1646d56afe880; lat=23.100169; lng=113.327754; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=92; __mta=255783863.1530842950644.1530842950644.1530842950644.1; _lxsdk_s=1646d56afeb-054-e56-2df%7C%7C10',
        'client-id=2e2bf506-f6b1-4093-8e83-86ebd69729c6; uuid=890d6232-fae5-49c7-bce4-13c282eb2b72; ci=538; rvct=538; _lxsdk_cuid=1646d606e7aad-01714d0979d793-3c3c590b-100200-1646d606e7bc8; _lxsdk=1646d606e7aad-01714d0979d793-3c3c590b-100200-1646d606e7bc8; _lxsdk_s=1646d606e7c-bb1-4ac-df1%7C%7C2; lat=39.953599; lng=116.78469',
        'client-id=77087f78-a459-4bd5-9715-4f83e7aa12f3; uuid=edb53243-fa64-452e-8450-965461edbd08; _lxsdk_cuid=1646d662b4cb-09e66ca84192f5-3c3c590b-100200-1646d662b4db4; _lxsdk=1646d662b4cb-09e66ca84192f5-3c3c590b-100200-1646d662b4db4; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=406; rvct=406; lat=22.831938; lng=113.271251; _lxsdk_s=1646d662b4f-dbc-912-c5f%7C%7C9',
        'client-id=7c8ee692-d1a3-487f-be39-88c7dbf20422; uuid=2a2a7020-c570-4971-979b-ea745d4c46d0; _lxsdk_cuid=1646d69d22659-0987aed9a3ffca-3c3c590b-100200-1646d69d22759; _lxsdk=1646d69d22659-0987aed9a3ffca-3c3c590b-100200-1646d69d22759; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=20; rvct=20; lat=23.124033; lng=113.397598; _lxsdk_s=1646d69d228-c11-69c-62%7C%7C9',
        'client-id=2fe9ecdd-3599-42c7-8e60-97eea73bd671; uuid=c78283c8-1b17-46ef-b75d-372e833d4b8c; _lxsdk_cuid=1646d6c253539-06d3fdca38c069-3c3c590b-100200-1646d6c2537c8; _lxsdk=1646d6c253539-06d3fdca38c069-3c3c590b-100200-1646d6c2537c8; lat=23.124033; lng=113.397598; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=92; _lxsdk_s=1646d6c2539-61c-b56-192%7C%7C2',
        'client-id=31d75d49-675a-4493-a25b-522721390fd7; uuid=25b46b29-5151-4114-a7d1-af4186dbf7d1; lat=23.124033; lng=113.397598; webloc_geo=23.000075%2C113.104244%2Cwgs84; _lxsdk_cuid=1646d6d9561c8-01fba6c82c6cc5-3c3c590b-100200-1646d6d95614; _lxsdk=1646d6d9561c8-01fba6c82c6cc5-3c3c590b-100200-1646d6d95614; ci=92; _lxsdk_s=1646d6d9563-2cb-8e4-c2c%7C%7C2',
        'client-id=0c71d765-581a-4593-ab25-1e1a471d4582; uuid=f55c750d-a84f-4ccb-b45b-dff82d3c73b0; _lxsdk_cuid=1646d6e3a3cc8-0dd47214699431-3c3c590b-100200-1646d6e3a3cc8; _lxsdk=1646d6e3a3cc8-0dd47214699431-3c3c590b-100200-1646d6e3a3cc8; lat=23.124033; lng=113.397598; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=92; _lxsdk_s=1646d6e3a3e-658-6f9-57c%7C%7C2',
        'client-id=60e58b77-d0c9-4faf-bc8b-6b400405fbe3; uuid=e7e1639e-af9b-412b-bee1-25846f3fedc6; _lxsdk_cuid=1646d6f4287c8-04ac35e4a5929b-3c3c590b-100200-1646d6f428770; _lxsdk=1646d6f4287c8-04ac35e4a5929b-3c3c590b-100200-1646d6f428770; lat=23.124033; lng=113.397598; webloc_geo=23.000075%2C113.104244%2Cwgs84; ci=92; _lxsdk_s=1646d6f428d-f17-5e5-20%7C%7C2',
        'uuid=475376bc6e554904962b.1530844373.1.0.0; ci=92; rvct=92; _lxsdk_cuid=1646d6fe270c8-02ace3b33e129-3c3c590b-100200-1646d6fe27052; client-id=e5b040a2-ca2c-46c9-bbec-d64ae88c39ff; _lxsdk=1646d6fe270c8-02ace3b33e129-3c3c590b-100200-1646d6fe27052; lat=23.114442; lng=113.158431; _lxsdk_s=1646d6fe272-6e5-682-4f2%7C%7C6',
    ]
    # 读取配置文件
    cf = configparser.ConfigParser()
    cf.read("meishi.conf")
    city_list = str(cf.get('meishi', 'city'))
    get_all_city(city_list)
