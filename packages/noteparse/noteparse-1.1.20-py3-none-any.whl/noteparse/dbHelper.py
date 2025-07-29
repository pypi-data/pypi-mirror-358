import pymysql
from datetime import datetime
import traceback
from noteparse.configReader import readConfig
import atexit

db_config = readConfig('host','port','user','password','db',section='dbConfig')


# 创建数据库连接
def create_connection():
    try:
        print(datetime.now(),'开启数据库链接')
        # 连接数据库
        connection = pymysql.connect(host=db_config['host'], port=int(db_config['port']),
                        user=db_config['user'], password=db_config['password'],
                        db=db_config['db'])
        print(datetime.now(),'数据库链接成功')
    except pymysql.MySQLError as e:
        print(datetime.now(),'数据库链接失败',e)
    return connection

# 确保在程序退出时关闭数据库连接
def close_connection():
    if connection and connection.open:
        print(datetime.now(),'关闭SQL连接')
        cursor.close()
        connection.close()
        
connection = create_connection()
cursor = connection.cursor()

def getConnection():
    return connection

atexit.register(close_connection)
# 通过城市名称查询城市信息
def queryCityInfo(cityName):
    query = f'''
    (SELECT 
        a.areaid,
        a.area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.areas a
    JOIN 
        unvbasicx_khgz.cities c ON a.cityid = c.cityid
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        a.area like '%{cityName}%')
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.cities c
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        c.city like '%{cityName}%'
        AND NOT EXISTS (
            SELECT 1 FROM unvbasicx_khgz.areas WHERE area like '%{cityName}%'
        )
    )
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        '' AS cityid,
        '' AS city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.provinces p
    WHERE 
        p.province like '%{cityName}%'
        AND NOT EXISTS (
            SELECT 1 FROM unvbasicx_khgz.cities WHERE city like '%{cityName}%'
        )
        AND NOT EXISTS (
            SELECT 1 FROM unvbasicx_khgz.areas WHERE area like '%{cityName}%'
        )
    )
    LIMIT 1
    '''
    if connection == None:
        create_connection()
    try:
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchall()  # 获取所有查询结果
        return result
    except Exception as e:
        print(datetime.now(),'通过城市名查询城市信息异常',e)
        traceback.print_exc()



# 通过城市名称查询城市信息
def queryCityInfoByAreaId(cityCode):
    query = f'''
    SELECT 
        a.areaid,
        a.area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.areas a
    JOIN 
        unvbasicx_khgz.cities c ON a.cityid = c.cityid
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        a.areaid like '%{cityCode}%'
    
    LIMIT 1
    '''
    if connection == None:
        create_connection()
    try:
        # 先检查是否端口,断开就重连
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchall()  # 获取所有查询结果
        return result
    # except pymysql.OperationalError:
    #     connection = create_connection()
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchall()  # 获取所有查询结果
    #     return result
    except Exception as e:
        print(datetime.now(),'通过城市code查询城市信息异常',e)
        traceback.print_exc()

# 通过城市名称查询城市信息
def queryProvinceId(provinceName):
    query = f'''
    SELECT 
        p.provinceid
    FROM 
        unvbasicx_khgz.provinces p
    WHERE 
        p.province like '%{provinceName}%'
    
    LIMIT 1
    '''
    if connection == None:
        create_connection()
    try:
        # 先检查是否端口,断开就重连
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchone()  # 获取所有查询结果
        return result
    # except pymysql.OperationalError:
    #     connection = create_connection()
    #     cursor = connection.cursor()
    #     cursor.execute(query)
    #     result = cursor.fetchall()  # 获取所有查询结果
    #     return result
    except Exception as e:
        print(datetime.now(),'通过城市code查询城市信息异常',e)
        traceback.print_exc()

# 通过城市名称查询城市信息
def queryCityInProvince(cityName,provinceId):
    # 构建provinceId的条件判断
    province_filter = f"AND p.provinceid = '{provinceId}'" if provinceId else ""


    query = f'''
    (SELECT 
        a.areaid,
        a.area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.areas a
    JOIN 
        unvbasicx_khgz.cities c ON a.cityid = c.cityid
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        a.area like '%{cityName}%'
        {province_filter}
    )
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        c.cityid,
        c.city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.cities c
    JOIN 
        unvbasicx_khgz.provinces p ON c.provinceid = p.provinceid
    WHERE 
        c.city like '%{cityName}%'
        {province_filter}
    )
    UNION ALL
    (SELECT 
        '' AS areaid,
        '' AS area,
        '' AS cityid,
        '' AS city,
        p.provinceid,
        p.province
    FROM 
        unvbasicx_khgz.provinces p
    WHERE 
        p.province like '%{cityName}%'
        {province_filter}
    )
    '''
    if connection == None:
        create_connection()
    try:
        connection.ping(reconnect=True)
        cursor.execute(query)
        result = cursor.fetchall()  # 获取所有查询结果
        return result
    except Exception as e:
        print(datetime.now(),'通过城市名查询城市信息异常',e)
        traceback.print_exc()


# 设定main函数,程序起点
if __name__ == '__main__':
    try:
    #    noteInfo = testMatch('电话：ABC公司')
        pStr = 'zho'
        # text = re.sub('\s+','',pStr.replace(u'\xa0','').strip().replace('\n','').replace(':','：'))
        # print('======text:',text)
        # a = remove_space(text)
        # print(a)
        # a = getProvinceId(pStr)
        # data = json.loads(a.replace('```','').replace('json','').replace(' ',''))
        # print(data['provinceId'])
        a = queryCityInProvince(pStr,'440000')
        print(a)
    #    a = ' 1.2852万元。收取对象：中标（成交）供应商。2.采购预算总金额：1,000,000.00元，最高限价：978,000.00元。地址：中国(四川)自由贸易试验区成都高新区益州大道中段722号3栋1单元603号中标（成交）金额：952,000.00元金额(元)：952,000.00'
    #    amount = getAmount(a[:1000])
    #    print('noteInfo',amount)

    except Exception as err:
        print(f'任务执行失败',err)
        traceback.print_exc()
        