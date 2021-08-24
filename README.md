# stargazer
适用hoshino的人造卫星轨道信息查询插件

原本只想写个单纯的娱乐插件，结果越写越复杂了就干脆完善了下（虽说这么偏门的功能大概也没人会用就是了）

星下点计算部分代码来自[Groundtrack](https://github.com/KyubiSystems/Groundtrack)，卫星数据来自https://celestrak.com/

## 安装方法

1. 将插件文件夹放到`HoshinoBot/hoshino/modules`目录下

2. 安装依赖   `pip install -r requirements.txt`

* 注意，windows下可能有部分依赖包无法自动安装，可前往[Unofficial Windows Binaries for Python Extension Packages]https://www.lfd.uci.edu/~gohlke/pythonlibs/ 下载相应whl包手动安装

3. 在`HoshinoBot/hoshino/config/__bot__.py`中添加stargazer模块

## 指令列表

- `[观星] 卫星名/NORAD编号/COSPAR编号`  查询指定卫星当前状态及6小时内星下点轨迹，仅能查询目前仍在轨工作的卫星（目前大约4600颗）

- `[寻星] 卫星名/NORAD编号/COSPAR编号`  查询指定卫星详细信息，可查询所有卫星记录（目前大约49000颗，包含卫星碎片残骸等）

- `[更新卫星数据]`  更新卫星数据库，正常一般不需要频繁更新）

## to do

- 增加往期活动档线数据查询
- 增加分群默认区服设置或区服单独查询
- 将数据拉取部分改为异步（虽然影响应该不大）