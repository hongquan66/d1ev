import requests
import re
import json
import pymysql
from bs4 import BeautifulSoup

# 第一电动
# https://www.d1ev.com

# 首页
# https://www.d1ev.com/home/v1000/main/leftNews.do?f=index&pageNumber=1&pageSize=10&type=0&p=index
# 新车
# https://www.d1ev.com/home/v1000/main/leftNews.do?f=index&pageNumber=1&pageSize=25&type=1&p=xinche

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Cookie': 'UM_distinctid=167f9356ab990d-0eb4f6d609934c-10306653-240000-167f9356abaa53; wm_d1ev_meid=e112bbd8ecc5cb3ef9983bb5bb5d485b; wm_csrf_token=2b7dcdf676a2ecbc09a314d4b1ae32a5; Hm_lvt_c877d2cab576bff779ecdc5df9de4065=1546506822; CNZZDATA1262291853=528624861-1546070851-https%253A%252F%252Fwww.google.com%252F%7C1546507017; Hm_lvt_c1d54a092f01be0215b4487856c2c6f6=1546074287,1546486202,1546506804,1546507727; CNZZDATA1254528018=1670824803-1546072814-https%253A%252F%252Fwww.google.com%252F%7C1546507983; wm_d1ev_search_words=%255B%2522%25E6%2596%25B0%25E8%25BD%25A6%2522%2C%2522%25E5%25A5%2587%25E7%2591%259E%25E6%2596%25B0%25E8%2583%25BD%25E6%25BA%2590%2522%255D; Hm_lpvt_c877d2cab576bff779ecdc5df9de4065=1546508003; JSESSIONID=619CE1A585CDD83821813F4694D35921; Hm_lpvt_c1d54a092f01be0215b4487856c2c6f6=1546508246',
}


# 获取文章链接
def get_links(count):
    links = []
    response = requests.get(url='https://www.d1ev.com/home/v1000/main/leftNews.do?'
                                'f=index&pageNumber=1&pageSize=%d&type=0&p=index' % count, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data['code'] == 1000:
            data = data['data']
            for art in data:
                links.append('https://www.d1ev.com' + art['pcUrl'])
        else:
            print('接口返回错误, code =', data['code'])
    else:
        print('获取文章链接失败')
    return links


# 获取文章信息
def get_article(link):
    response = requests.get(url=link, headers=headers)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        title = soup.select('.ws-title h1')[0].get_text()
        content = soup.select('#showall233')[0].prettify()
        content = clean(content)
        return title, content
    else:
        print('获取数据失败 code =', response.status_code)
        return None


# 清洗内容
def clean(content):
    content = re.sub(r'<\s*div[^>]*>', '', content)
    content = re.sub(r'</div>', '', content)
    content = re.sub(r'<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', '', content)
    content = re.sub(r'<!--[\s\S]*?-->', '', content)
    content = re.sub(r'\n', '', content)
    return content


# 文章数据持久化
def save_article(db, title, content):
    try:
        cursor = db.cursor()
        sql = 'code your sql here'
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print(e)
        db.rollback()
    return False


# 获取数据库版本
def get_database_version(db):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute()  方法执行 SQL 查询
    cursor.execute("SELECT VERSION()")
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    return data


if __name__ == '__main__':
    # 获取数据库连接
    db = pymysql.connect('localhost', 'news', 'root', 'your pass')
    print("Database version : %s " % get_database_version(db=db))

    # 获取文章链接
    links = get_links(200)
    print('获取文章链接 %d 条' % len(links))
    for link in links:
        print('当前文章链接 > ', link)
        title, content = get_article(link=link)
        print(title, '入库' + ('成功' if save_article(db=db, title=title, content=content) else '失败'))

    db.close()
