#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################
# Author : cndaqiang             #
# Update : 2024-08-29            #
# Build  : 2024-08-29            #
# What   : 网站签到         #
##################################
try:
    from airtest_mobileauto.control import *
except ImportError:
    print("模块[airtest_mobileauto]不存在, 尝试安装")
    import pip
    try:
        pip.main(['install', 'airtest_mobileauto', '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'])
    except:
        print("安装失败")
        exit(1)
import sys


class web_url():
    def __init__(self, url="http://127.0.0.1/"):
        self.prefix = self.__class__.__name__  # 类的名字
        # device
        self.mynode = Settings.mynode
        self.totalnode = Settings.totalnode
        self.LINK = Settings.LINK_dict[Settings.mynode]
        self.移动端 = deviceOB(mynode=self.mynode, totalnode=self.totalnode, LINK=self.LINK)
        self.设备类型 = self.移动端.设备类型
        # 打开网址，并将默认的浏览器设置为APPID
        self.url = url
        self.移动端.打开网址(self.url)
        self.APPOB = appOB(big=True, device=self.移动端)
        self.Tool = DQWheel(var_dict_file=f"{self.移动端.设备类型}.var_dict_{self.prefix}.yaml",
                            mynode=self.mynode, totalnode=self.totalnode)
        #
        self.dayFILE = f"{self.prefix}.txt"
        self.timelimit = 60*10
        self.运行时间 = [3.0, 4.0]
    #

    def stop(self):
        self.APPOB.关闭APP()
    #

    def run(self, times=0):
        if not connect_status():
            self.移动端.连接设备()
        if not connect_status():
            return
        #
        self.APPOB.重启APP()
        self.移动端.打开网址(self.url)
        step = 0
        for url in self.Tool.readfile(self.dayFILE):
            if len(url) > 0 and "://" in url:
                #每5个网页重启一次浏览器
                if step % 5 == 4:
                   self.APPOB.重启APP()
                TimeECHO("="*10+url+"="*10)
                self.移动端.打开网址(url)
                sleep(5)
                step = step + 1
        return
    #

    def looprun(self, times=0):
        times = times + 1
        startclock = self.运行时间[0]
        endclock = self.运行时间[1]
        while True:
            leftmin = self.Tool.hour_in_span(startclock, endclock)*60.0
            if leftmin > 0:
                TimeECHO("剩余%d分钟进入新的一天" % (leftmin))
                self.APPOB.关闭APP()
                self.移动端.重启重连设备(leftmin*60)
                continue
            times = times+1
            TimeECHO("="*10)
            self.run()

def main():
    config_file = ""
    if len(sys.argv) > 1:
        config_file = str(sys.argv[1])
    Settings.Config(config_file)
    ce = web_url()
    ce.run()
    exit()

if __name__ == "__main__":
    main()