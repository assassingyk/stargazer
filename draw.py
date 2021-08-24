#!/usr/bin/env python
import geopandas
#from shapely import geometry
import matplotlib.pyplot as plt
import contextily as cx
import io
import os
from PIL import Image


def draw_track_realistic(track, now, timeline, day=True):

    c_line = 'pink'
    c_point = 'pink'
    c_char = 'pink'

    tr = geopandas.GeoDataFrame(track)
    tr.crs = "EPSG:4322"
    # cq = geopandas.GeoSeries([geometry.Point(now).buffer(30)],crs='EPSG:4322')#默认wgs1984坐标系
    cq = geopandas.GeoDataFrame(now)
    cq.crs = "EPSG:4322"

    tl = geopandas.GeoDataFrame(timeline)
    tl.crs = "EPSG:4322"

    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(20)
    # ax.set_facecolor('white')
    ax.set(xlim=(-180, 180), ylim=(-85, 85))
    # ax.grid()
    plt.axis('off')
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.tight_layout()

    if day:
        cx.add_basemap(ax, crs='EPSG:4322', reset_extent=False, source=os.path.join(
            os.path.dirname(__file__), 'data', 'world_WorldImagery.tif'))
    else:
        land = geopandas.read_file(os.path.join(os.path.dirname(
            __file__), 'data', "land_110", "ne_110m_land.shp"))
        land.boundary.plot(ax=ax, edgecolor='#B1BCD0')
        cx.add_basemap(ax, crs='EPSG:4322', reset_extent=False, source=os.path.join(
            os.path.dirname(__file__), 'data', 'world_ViirsEarthAtNight2012.tif'))
    #cx.add_basemap(ax, attribution=None, crs=tr.crs.to_string(), source=cx.providers.Esri.WorldImagery, zoom=3)
    #cx.add_basemap(ax, attribution=None, crs=tr.crs.to_string(), source=cx.providers.GeoportailFrance.orthos, zoom=3)
    #cx.add_basemap(ax, attribution=None, crs=tr.crs.to_string(), source=cx.providers.NASAGIBS.ViirsEarthAtNight2012, zoom=3)

    tr.to_crs(crs='EPSG:4322').plot(ax=ax, color=c_line, linewidth=3, zorder=1)
    cq.to_crs(crs='EPSG:4322').plot(ax=ax, color=c_point,
                                    markersize=80, marker='o', zorder=2)
    for x, y, label in zip(cq.geometry.x, cq.geometry.y, cq.name):
        dirction = 1
        hal = 'left'
        val = 'bottom'
        if x > 120:
            dirction = -1
            hal = 'right'
        if y > 75:
            val = 'bottom'
        ax.annotate(label, xy=(x, y), xytext=(5*dirction, 0), horizontalalignment=hal,
                    verticalalignment=val, textcoords="offset points", color=c_char, fontsize=18)

    tl.to_crs(crs='EPSG:4322').plot(ax=ax, color=c_point,
                                    markersize=50, marker='o', zorder=2)
    for x, y, label in zip(tl.geometry.x, tl.geometry.y, tl.name):
        dirction = 1
        hal = 'left'
        val = 'top'
        if x > 120:
            dirction = -1
            hal = 'right'
        if y < -75:
            val = 'bottom'
        ax.annotate(label, xy=(x, y), xytext=(5*dirction, 0), horizontalalignment=hal,
                    verticalalignment=val, textcoords="offset points", color=c_char, fontsize=14)

    # plt.xticks(rotation=20)
    buf = io.BytesIO()
    # plt.savefig("MapDisplayAndprojection.png")#修改一下路径
    plt.savefig(buf, format='png', transparent=True,
                bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    img = Image.open(buf)
    return img


def draw_track_abstract(track, now, timeline, style, grid=True, bound=False):

    c_sea = style['sea']
    c_land = style['land']
    c_grid = style['grid']
    c_edge = style['edge']
    c_line = style['line']
    c_point = style['point']
    c_char = style['char']

    tr = geopandas.GeoDataFrame(track)  # 修改一下路径
    tr.crs = "EPSG:4322"
    # cq = geopandas.GeoSeries([geometry.Point(now).buffer(30)],crs='EPSG:4322')#默认wgs1984坐标系
    cq = geopandas.GeoDataFrame(now)
    cq.crs = "EPSG:4322"

    tl = geopandas.GeoDataFrame(timeline)
    tl.crs = "EPSG:4322"
    # 生成图表
    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(20)
    # ax.set_facecolor('white')
    ax.set(xlim=(-180, 180), ylim=(-85, 85))
    # plt.axis('off')
    ax.set_xticklabels([])
    ax.set_xticks(range(-180, 181, 30))
    ax.set_yticklabels([])
    ax.set_yticks(range(-90, 91, 30))
    ax.set_frame_on(False)
    ax.tick_params(tick1On=False)
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.tight_layout()

    ocean = geopandas.read_file(os.path.join(os.path.dirname(
        __file__), 'data', "ocean_110", "ne_110m_ocean.shp"))
    land = geopandas.read_file(os.path.join(os.path.dirname(
        __file__), 'data', "land_110", "ne_110m_land.shp"))
    country = geopandas.read_file(os.path.join(os.path.dirname(
        __file__), 'data', "countries_110", "ne_110m_admin_0_countries.shp"))
    if grid:
        ax.grid(color=c_grid)

    ocean.plot(ax=ax, facecolor=c_sea, edgecolor=c_edge)
    if bound:

        country.plot(ax=ax, facecolor=c_land, edgecolor=c_edge)
    else:
        land.plot(ax=ax, facecolor=c_land, edgecolor=c_edge)

    tr.to_crs(crs='EPSG:4322').plot(ax=ax, color=c_line, linewidth=3, zorder=1)
    cq.to_crs(crs='EPSG:4322').plot(ax=ax, color=c_point,
                                    markersize=80, marker='o', zorder=2)
    for x, y, label in zip(cq.geometry.x, cq.geometry.y, cq.name):
        dirction = 1
        hal = 'left'
        val = 'bottom'
        if x > 120:
            dirction = -1
            hal = 'right'
        if y > 75:
            val = 'bottom'
        ax.annotate(label, xy=(x, y), xytext=(5*dirction, 0), horizontalalignment=hal,
                    verticalalignment=val, textcoords="offset points", color=c_char, fontsize=18)

    tl.to_crs(crs='EPSG:4322').plot(ax=ax, color=c_point,
                                    markersize=50, marker='o', zorder=2)
    for x, y, label in zip(tl.geometry.x, tl.geometry.y, tl.name):
        dirction = 1
        hal = 'left'
        val = 'top'
        if x > 120:
            dirction = -1
            hal = 'right'
        if y < -75:
            val = 'bottom'
        ax.annotate(label, xy=(x, y), xytext=(5*dirction, 0), horizontalalignment=hal,
                    verticalalignment=val, textcoords="offset points", color=c_char, fontsize=14)

    # plt.xticks(rotation=20)
    buf = io.BytesIO()
    # plt.savefig("MapDisplayAndprojection.png")#修改一下路径
    plt.savefig(buf, format='png', transparent=True,
                bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    img = Image.open(buf)
    return img
