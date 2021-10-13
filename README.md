# Genshin_Impact_bot

<img src="https://img.shields.io/github/license/H-K-Y/Genshin_Impact_bot.svg"/> <img src="https://img.shields.io/github/repo-size/H-K-Y/Genshin_Impact_bot.svg"/> <img src="https://img.shields.io/github/last-commit/H-K-Y/Genshin_Impact_bot.svg"/> <img src="https://img.shields.io/badge/language-python-3572A5.svg"/>


>This is a Genshin Impact plugin for [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)
>
>这是一个[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)和[nonebot2](https://github.com/nonebot/nonebot2)的原神相关插件

**这个项目目前正在扩展，加入更多原神相关娱乐和信息查询功能，敬请期待**

## 简介

这个插件帮助群员在QQ群内进行诸如查询资源点位等功能。

相应的，也加入了一些趣味性的功能如原神抽卡，黄历，抽签等；

## 目录

- **部署**
  - [安装(HoshinoBot)](https://github.com/H-K-Y/Genshin_Impact_bot/wiki/%E5%AE%89%E8%A3%85%EF%BC%88Hoshino%EF%BC%89)
  - [安装(NoneBot2)](https://github.com/H-K-Y/Genshin_Impact_bot/wiki/%E5%AE%89%E8%A3%85%EF%BC%88Nonebot2%EF%BC%89)
- **使用**
  - [命令](https://github.com/H-K-Y/Genshin_Impact_bot/wiki/%E5%91%BD%E4%BB%A4)
  - [演示](https://github.com/H-K-Y/Genshin_Impact_bot/wiki/%E6%95%88%E6%9E%9C%E6%BC%94%E7%A4%BA)
  - [常见问题](https://github.com/H-K-Y/Genshin_Impact_bot/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)

## 致谢

特别感谢[刘老板](https://github.com/noahzark)对插件的赞助

**[米游社|观测枢wiki](https://bbs.mihoyo.com/ys/obc/?bbs_presentation_style=no_header)**

**[可莉特调](https://genshin.pub)**

## 许可

[GPL-3.0](https://github.com/H-K-Y/Genshin_Impact_bot/blob/main/LICENSE) © H-K-Y


## 更新记录

### 2021-9-27

* 抽卡现在可以自动更新了
* 加入新指令 更新原神卡池

### 2021-8-16

* 项目移植到nonebot 2 

### 2021-8-14

* 加入 [圣遗物评分](https://github.com/H-K-Y/Genshin_Impact_bot/issues/31)
* 更新卡池

### 2021-7-27

* 对资源查询的代码逻辑进行调整，防止资源查询时出现killed
* 加入新命令 更新原神地图 用于爬取大地图文件

### 2021-6-2
* 加入抽签功能
* 更新README.md
* 部分代码依照PEP标准进行格式化


### 2021-3-28
* 圣遗物收集修改冰本的圣遗物名称，增加岩本
* 加入每日素材提醒

### 2021-3-24
* 加入了原神黄历，黄历的数据来源于 [可莉特调](https://genshin.pub/)

### 2021-3-11
* 对抽卡的概率进行调整现在更接近游戏里的效果
* 对抽卡逻辑优化防止在非武器UP池抽出限定4星武器
* 修正千岩系列武器图标星级错误的问题

### 2020-12-13
* 资源列表查询现在改为直接抓取米游社地图的数据，每天自动更新
* 修复查询资源列表消息过长导致发送失败的问题

### 2020-11-26
* 修复模拟抽卡武器UP池保底次数错误的问题

### 2020-11-20
* 加入圣遗物收集功能

### 2020-11-3
* 修复了找神瞳可以添加相同名称的编号导致报错的问题

### 2020-10-31
* 加入了查询资源位置的功能

### 2020-10-29
* 加入了找神瞳的功能

### 2020-10-26
* 加入了丘丘语翻译功能

### 2020-10-22
* 修复了4星概率写错了导致4星只能保底抽出的问题.............
* 加入了更多抽卡的统计结果，比如抽出最多的武器是啥，第一个4星和5星事多少抽出的

### 2020-10-21
* 在config.py加入了抽卡限制功能，限制每个人一天最多抽多少次，感谢[corvo007](https://github.com/corvo007)提出的粪pr (粪pr是他自己说的
* 修复了第一次切换卡池后不能再切换卡池的问题
* 修复了查看UP信息时报错的问题

### 2020-10-20
* 重构了项目代码，~~第二天就重写？~~，~~过几天怕是忘了写的啥了........~~
* 加入的武器UP池和常驻池
* 加入了切换卡池的功能

### 2020-10-19
* 加入10连抽，90连抽和180连抽
* 加入抽卡发送图片功能
* 修复了Windows系统发送图片时可能出现的路径问题，图片全部改为base64发送

