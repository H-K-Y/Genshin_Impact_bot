# Genshin_Impact_bot

### This is a Genshin Impact plugin for [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)
### 这是一个[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的原神相关插件
### 这个项目目前正在扩展，加入更多原神相关娱乐和信息查询功能，敬请期待

### 如果你是在项目名称为Genshin_Impact_gacha时安装的，请删除Genshin_Impact_gacha重新Git clone

# 安装方法

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目
```
git clone https://github.com/H-K-Y/Genshin_Impact_bot.git
```
然后在 HoshinoBot\\hoshino\\config\\\__bot__.py 文件的 MODULES_ON 加入 Genshin_Impact_bot

config.py文件有插件的常用配置，你可以根据自己的情况修改

重启 HoshinoBot

### (可选)放置找神瞳的gif动态图
原神观测枢wiki上还有如何拿到神瞳的gif动态图，如果你想让机器人发送动态图可以在Releases下载

gif图包解压后放在icon路径下，安装完的路径应该是
```
HoshinoBot\hoshino\modules\Genshin_Impact_bot\seek_god_eye\icon\风神瞳\56.gif
```

### 如何修改卡池
卡池的信息是保存在gacha\config.json里的，修改时注意json文件的格式

4星和5星的武器角色up分别对照角色up池和武器up池来填

常驻角色和武器在常驻池里找，去掉当前up池的的up填写剩下的

如果出了新的角色或武器你还要加入新角色武器的图标，角色图标放在 gacha\icon\角色 文件夹，武器图标放在 gacha\icon\武器 文件夹

图标为png格式，大小最好为125*130，小了可以，大了会被裁切

改完后在群里发送 原神卡池 可以重载config.json文件

# 效果演示
### 原神抽卡
![原神抽卡](https://github.com/H-K-Y/Genshin_Impact_bot/blob/main/screenshot/genshin_impact_gacha.png) 
### 丘丘语翻译
![丘丘语翻译](https://github.com/H-K-Y/Genshin_Impact_bot/blob/main/screenshot/qiu_qiu_translation.png) 
### 找神瞳
![找神瞳](https://github.com/H-K-Y/Genshin_Impact_bot/blob/main/screenshot/search_god_eye.png) 
### 资源位置查询
![资源位置查询](https://github.com/H-K-Y/Genshin_Impact_bot/blob/main/screenshot/query_resource_points.png) 


# 指令

指令|说明
:--|:--  
原神帮助|查看插件的帮助  
原神抽卡指令|  
@bot相遇之缘|10连抽卡  
@bot纠缠之缘|90连抽卡  
@bot原之井|180连抽卡  
原神卡池|查看当前UP池，这个指令也可以用来重载卡池配置文件，config.json保存的是当前卡池信息  
原神卡池切换|切换其他原神卡池  
原神丘丘语翻译指令|  
丘丘一下 丘丘语句|翻译丘丘语,注意这个翻译只能把丘丘语翻译成中文，不能反向  
丘丘词典 丘丘语句|查询丘丘语句的单词含义  
找神瞳指令|  
找风神瞳 <神瞳编号>|让机器人发送风神瞳的位置，神瞳编号为可选参数，不写编号机器人会随机一个编号，风可以换成岩来找岩神瞳  
找到神瞳了 <神瞳编号>|让机器人记录这个神瞳编号，以后机器人不会给你发送这个编号  
@bot删除找到神瞳 <神瞳编号>|在你已经找到的神瞳记录里删除这个编号  
@bot重置风神瞳找到记录|删除所有风神瞳的找到记录，这个指令会有二次确认，风可以换成岩来重置岩神瞳的记录  
@bot找到多少神瞳了|查看当前你找到多少神瞳了  
@bot没找到的风神瞳|查看没有找到的风神瞳地图位置和编号  
资源位置查询指令|  
XXX哪里有|查询XXX的位置图，XXX是资源的名字  
原神资源列表|查询所有的资源名称  

# 更新记录

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





