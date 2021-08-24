import re
import nonebot

from hoshino import Service, priv
from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import FreqLimiter, DailyNumberLimiter, pic2b64

from .draw import draw_track_realistic, draw_track_abstract
from .track_data import geojson
from .data_load import *

lmt = DailyNumberLimiter(10)
flmt = FreqLimiter(120)

sv = Service('stargazer', help_='[观星 (id)] 查看卫星轨道参数', enable_on_default=False)


@nonebot.on_startup
async def startup():
    init_data()


@sv.on_prefix(('观星'))
async def gen_sat_pic(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid = ev.message_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        if not lmt.check(uid):
            await bot.send(ev, f'您本日观测配额已耗尽，请明日5点后再提交观测申请~', at_sender=True)
            return
        if not flmt.check(uid):
            await bot.send(ev, f'观测装置冷却中，请{int(flmt.left_time(uid)) + 1}秒后再来~', at_sender=True)
            return
    flmt.start_cd(gid, 120)
    keyword = str(ev.message.extract_plain_text().strip())
    if not keyword:
        await bot.send(ev, '请输入卫星NORAD ID或COSPAR ID~')
        return
    tleset = ()

    if keyword.isdigit():
        # is NORAD ID
        tleset = find_sat_by_norad(keyword)
        if not tleset:
            await bot.send(ev, '未找到此ID……观星搜索仅能查询地球轨道运行中卫星')
            return
    elif re.match('\d{4}-\d{3}.*', keyword):
        # is COSPAR ID
        tleset = find_sat_by_cospar(keyword)
        if not tleset:
            await bot.send(ev, '未找到此ID……观星搜索仅能查询地球轨道运行中卫星~')
            return
    else:
        ans = find_sat_by_name(keyword, target='active')
        if not ans:
            await bot.send(ev, '未找到结果……请尝试换用其他关键词或英文缩写~观星搜索仅能查询地球轨道运行中卫星~')
            return
        if len(ans) == 1:
            nid = (ans[0][0])
            tleset = find_sat_by_norad(nid)
        elif len(ans) > 10:
            await bot.send(ev, f'共找到{len(ans)}个结果，数量过多仅显示前十条……请尝试选用更精确的关键词~')
            ans = ans[0:10]
            search = ['NORAD | NAME']
            for sat in ans:
                search.append(f' {sat[0]}  | {sat[1]}')
            await bot.send(ev, '\n'.join(search))
            return
        else:
            await bot.send(ev, f'共找到{len(ans)}个结果，请使用NORAD编号选择需要查看的卫星~')
            search = ['NORAD | NAME']
            for sat in ans:
                search.append(f' {sat[0]}  | {sat[1]}')
            await bot.send(ev, '\n'.join(search))
            return

    orbitdata = geojson(name=tleset[0], line1=tleset[1], line2=tleset[2])
    await bot.send(ev, f'{tleset[0]}\n当前轨道高度：{round(orbitdata[3],2)}km\n当前运行速度：{round(orbitdata[4],2)}km/s')

    img = draw_track_realistic(orbitdata[0], orbitdata[1], orbitdata[2])
    img = draw_track_realistic(orbitdata[0], orbitdata[1], orbitdata[2])
    img = str(MessageSegment.image(pic2b64(img)))

    await bot.send(ev, img)
    lmt.increase(uid)



@sv.on_prefix(('寻星'))
async def search_sat_info(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid = ev.message_id

    # try:
    keyword = str(ev.message.extract_plain_text().strip())
    if not keyword:
        await bot.send(ev, '请输入关键词或NORAD ID或COSPAR ID~')
        return
    tleset = ()

    if keyword.isdigit() or re.match('\d{4}-\d{3}.*', keyword):
        # is NORAD ID
        info = format_sat_info(keyword)
        if not info:
            await bot.send(ev, '未找到此卫星数据……')
            return
        await bot.send(ev, info)
    else:
        ans = find_sat_by_name(keyword, target='all')
        if not ans:
            await bot.send(ev, '未找到结果……请尝试换用其他关键词或英文缩写~')
            return
        if len(ans) == 1:
            info = format_sat_info(ans[0][0])
            await bot.send(ev, info)
            return
        elif len(ans) > 10:
            await bot.send(ev, f'共找到{len(ans)}个结果，仅显示前十条……请尝试选用更精确的关键词~')
            ans = ans[0:10]
        search = ['NORAD | NAME']
        for sat in ans:
            search.append(f' {sat[0]}  | {sat[1]}')
        await bot.send(ev, '\n'.join(search))


@sv.on_fullmatch(('更新卫星数据'))
async def update_sat_info(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    mid = ev.message_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '此命令仅维护组可用，请联系维护组~')
        return
    try:
        await bot.send(ev, '正在更新……')
        await update_data()
        init_data()
        await bot.send(ev, '更新数据成功!')
    except Exception as e:
        await bot.send(ev, f'更新失败……{e}')
