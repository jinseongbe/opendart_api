import requests
import xml.etree.ElementTree as ET
import io
import os
from zipfile import ZipFile
import json
import xmltodict
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("TOKEN")
group_chat_id = os.getenv("GROUP_CHAT_ID")
apikey = os.getenv("API_KEY")

date = 20230111

def tel_send_message_to_group(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendmessage?chat_id={chat_id}&text={text}'   
    r = requests.post(url)
    return r

def load_opendart_data(apikey, date):
    os.chdir("./files/")
    res1 = requests.get("https://opendart.fss.or.kr/api/list.json?crtfc_key={}&bgn_de={}&end_de={}&pblntf_ty=D&page_no=1&page_count=100".format(apikey, date, date))
    doc_num_lst = []
    doc_lst = json.loads(res1.content)
    
    for dc in doc_lst['list']:
      doc_num_lst.append(dc['rcept_no'])

    for i in range(0, len(doc_num_lst)):
        doc_id = doc_num_lst[i]
        doc_name = doc_num_lst[i] + ".xml"

        try:
            response = requests.get("https://opendart.fss.or.kr/api/document.xml?crtfc_key={}&rcept_no={}".format(apikey, doc_id))

            with ZipFile(io.BytesIO(response.content)) as zip_file:
                xml_file = zip_file.extract(doc_name)

            file_list = os.listdir("./")
            
            with open(doc_name,'r') as f:
                xmlString = f.read()
            check1 = xmlString.find("장내매수")
            check2 = xmlString.find("장내 매수")

            if check1 != -1 or check2 != -1 :
                print("장내 매수 발생")
                try:
                    jsonString = json.dumps(xmltodict.parse(xmlString), indent=4, ensure_ascii = False)
                    document = json.loads(jsonString)
                    print("문서링크 : https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(doc_id))
                    print(document['DOCUMENT']['COMPANY-NAME']['#text'], document['DOCUMENT']['DOCUMENT-NAME']['#text'])
                    print()
                    # 텔레그램에 메세지 보내는 부분
                    link = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(doc_id)
                    companyname = document['DOCUMENT']['COMPANY-NAME']['#text']
                    doc_title =  document['DOCUMENT']['DOCUMENT-NAME']['#text']
                    tele_msg = "장내 매수 발생\n회사명 : {}\n일시 : {}\n문서 제목 : {}\n링크 : {}\n".format(companyname, date, doc_title, link)
                    tel_send_message_to_group(group_chat_id, tele_msg)
                except:
                    print("json load 실패, 문서 정보 불러오기 실패")
                    print("문서링크 :", "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(doc_id))
                    print()
                    # 텔레그램에 메세지 보내는 부분
                    link = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(doc_id)
                    companyname = "불러오기 실패"
                    doc_title = "불러오기 실패"
                    tele_msg = "장내 매수 발생\n회사명 : {}\n일시 : {}\n문서 제목 : {}\n링크 : {}\n".format(companyname, date, doc_title, link)
                    tel_send_message_to_group(group_chat_id, tele_msg)
            xmlString = ""
        except:
            print("파일 다운로드 실패, ", xmlString)
            print("문서링크 :", "https://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(doc_id))
            print()

        if doc_name in file_list:
            os.remove(doc_name)


load_opendart_data(apikey, date)