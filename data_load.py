import csv
import os
#import numpy as np
#import random
#import requests
import re
import json
#from PIL import Image

from hoshino import aiorequests
from pypinyin import lazy_pinyin, Style

satcat_file = os.path.join(os.path.dirname(__file__), 'data', 'satcat.csv')
noradtle_file = os.path.join(os.path.dirname(__file__), 'data', 'active.txt')
source_file = os.path.join(os.path.dirname(
    __file__), 'data', 'source_code.csv')
lanch_file = os.path.join(os.path.dirname(
    __file__), 'data', 'launch_site_codes.csv')
status_file = os.path.join(os.path.dirname(
    __file__), 'data', 'status_code.csv')
center_file = os.path.join(os.path.dirname(
    __file__), 'data', 'center_code.csv')

satcat_url = r'https://celestrak.com/pub/satcat.csv'
noradtle_url = r'https://celestrak.com/NORAD/elements/active.txt'

satcat_dict = {}
norad_dict = {}
cospar_2_norad = {}

type_dict = {'PAY': '卫星', 'R/B': '火箭箭体', 'DEB': '残骸', 'UNK': '未知'}
source_dict = {}
lanch_dict = {}
status_dict = {}
center_dict = {}


def init_data():
    global satcat_dict, norad_dict, cospar_2_norad, source_dict, lanch_dict, status_dict, center_dict
    satcat_dict = read_satcat()
    norad_dict = read_norad()
    source_dict = read_translate(source_file)
    lanch_dict = read_translate(lanch_file)
    status_dict = read_translate(status_file)
    center_dict = read_translate(center_file)
    for sat in satcat_dict:
        cospar_2_norad[satcat_dict[sat]['OBJECT_ID']] = sat


async def update_data():
    satcat_res = await aiorequests.get(satcat_url)
    satcat_data = await satcat_res.content
    with open(satcat_file, 'wb+') as f:
        f.write(satcat_data)

    norad_res = await aiorequests.get(noradtle_url)
    norad_data = await norad_res.content
    with open(noradtle_file, 'wb+') as f:
        f.write(norad_data)


def read_satcat():
    res_dict = {}
    with open(satcat_file, encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        satcat_header = next(csv_reader)
        for row in csv_reader:
            temp = {}
            for i, k in enumerate(satcat_header):
                temp[k] = row[i]
            res_dict[row[2]] = temp
    return res_dict


def read_translate(file):
    res_dict = {}
    with open(file, encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        satcat_header = next(csv_reader)
        for row in csv_reader:
            res_dict[row[0]] = row[2]
    return res_dict


def read_norad():
    res_dict = {}
    with open(noradtle_file, encoding='utf-8-sig') as f:
        content = f.read().strip()
        tlelist = content.split('\n')
        for i in range(0, len(tlelist)//3):
            name = tlelist[3*i].strip()
            line1 = tlelist[3*i+1].strip()
            line2 = tlelist[3*i+2].strip()
            if not(line1[0] == '1' and line2[0] == '2'):
                print('tls data error!')
                continue
            noradid = str(int(line2.split(' ')[1]))
            res_dict[noradid] = {'name': name, 'line1': line1, 'line2': line2}
    return res_dict


def format_sat_info(norad_id):
    if re.match('\d{4}-\d{3}.*', norad_id):
        if str(norad_id) in norad_dict:
            norad_id = cospar_2_norad[norad_id]
        else:
            return None
    if str(int(norad_id)) not in satcat_dict:
        return None
    satdata = satcat_dict[norad_id]
    format_info = []
    format_info.append(f"名称：{satdata['OBJECT_NAME']}")
    format_info.append(f"NORAD id：{norad_id}")
    format_info.append(f"COSPAR id：{satdata['OBJECT_ID']}")
    if satdata['OBJECT_TYPE'] != 'PAY':
        format_info.append(f"*类型：{type_dict[satdata['OBJECT_TYPE']]}")
    format_info.append(f"发射日期：{satdata['LAUNCH_DATE']}")
    format_info.append(f"发射地点：{lanch_dict[satdata['LAUNCH_SITE']]}")
    format_info.append(f"所有者：{source_dict[satdata['OWNER']]}")
    format_info.append(f"状态：{status_dict[satdata['OPS_STATUS_CODE']]}")
    if satdata['DECAY_DATE']:
        format_info.append(f"*再入日期：{satdata['DECAY_DATE']}")
    format_info.append(f" ")

    if satdata['ORBIT_CENTER'] == 'EA':
        format_info.append(f"轨道周期：{satdata['PERIOD']}min")
        format_info.append(f"轨道倾角：{satdata['INCLINATION']}°")
        format_info.append(f"远地点：{satdata['APOGEE']}km")
        format_info.append(f"近地点：{satdata['PERIGEE']}km")

    if satdata['ORBIT_CENTER'] != 'EA':
        format_info.append(
            f"*轨道中心：{center_dict[satdata['ORBIT_CENTER']] if satdata['ORBIT_CENTER'] in center_dict else satdata['ORBIT_CENTER']}")

    return '\n'.join(format_info)


def check_lan(string):
    result = []
    for ch in string:
        if ch.isdigit():
            result.append('3')
        elif ch.isalpha():
            result.append('2')
        elif u'\u4e00' <= ch <= u'\u9fff':
            result.append('1')
        else:
            result.append('0')
    return result


def find_sat_by_name(keyword, target='active'):
    keywords = re.split('\s|-', keyword)
    keywordsp = []
    for key in keywords:
        res = check_lan(key)
        las = None
        lasi = 0
        for i, k in enumerate(res):
            if i == 0:
                las = k
            if las != k:
                keywordsp.append(key[lasi:i])
                lasi = i
            las = k
        keywordsp.append(key[lasi:i+1])
    keywordsq = []
    for key in keywordsp:
        pinyin = ''.join(lazy_pinyin(key))
        keywordsq.append(pinyin.upper())
    ans = []
    if target == 'active':
        for nid in norad_dict.keys():
            if all(i in norad_dict[nid]['name'] for i in keywordsq):
                ans.append((nid, norad_dict[nid]['name']))
        return ans
    elif target == 'all':
        for nid in satcat_dict.keys():
            if all(i in satcat_dict[nid]['OBJECT_NAME'] for i in keywordsq):
                ans.append((nid, satcat_dict[nid]['OBJECT_NAME']))
        return ans


def find_sat_by_norad(nid):
    if str(nid) in norad_dict:
        sat = norad_dict[nid]
        return (sat['name'], sat['line1'], sat['line2'])
    else:
        return None


def find_sat_by_cospar(cid):
    if str(cid) in cospar_2_norad:
        nid = cospar_2_norad[cid]
        return find_sat_by_norad(nid)
    else:
        return None


def save_json(jsonpath, data: dict):
    try:
        with open(jsonpath, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False


def load_json(jsonpath):
    try:
        with open(jsonpath, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
            return config
    except Exception as ex:
        print(ex)
        return {}


radarstyle = {'sea': '#022803',
              'land': '#015601',
              'grid': '#01C801',
              'edge': '#01C801',
              'line': '#01C801',
              'point': '#01C801',
              'char': '#01C801'}

blueprintstyle = {'sea': '#06142E',
                  'land': '#06142E',
                  'grid': '#B1BCD0',
                  'edge': '#B1BCD0',
                  'line': '#B1BCD0',
                  'point': '#B1BCD0',
                  'char': '#B1BCD0'}

webstyle = {'sea': 'black',
            'land': 'black',
            'grid': '#88BB88',
            'edge': '#88BB88',
            'line': 'red',
            'point': 'pink',
            'char': 'pink'}
