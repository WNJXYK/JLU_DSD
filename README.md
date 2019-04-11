# Distributed Software Deleopment Course in Jilin University - 吉林大学分布式软件开发课程

![Python](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)
![Requirements](https://img.shields.io/badge/dependencies-flask%20%7C%20json-brightgreen.svg)

## 项目简介
一个带有 Web 端用户界面的智能照明控制系统，包含 HTML+JS 的纯静态前端界面，Python 编写的服务器后端与数据库，同时提供了编写传感器内置程序的 Python 模版。 （硬件均适用树莓派实现）
* 远程查看传感器、照明灯状态。
* 使用独立于照明灯的传感器为智能控制模块提供数据，用于智能判断灯的开与关。
* 给用户分配不同角色，以享有对照明系统的不同控制权限。

## 内容说明
* Documents 文件夹中包含部分开发文档（服务器部分）
* Demo 文件夹中包含 Server / Intelligent Controller / Database / Hardware 四部分的完整 Python 代码，其中 Server 部分认真重构并添加了详细的函数注释，其他部分的重构与注释工作待完善
* docs 文件夹中包含项目的 Github 主页
* docs/web 文件夹中包含完整的前端代码
* Hardware_Test 文件夹包含对树莓派传感器的测试代码

## 支持功能

1. 分层管理：Building -> Room -> Hardware
  * 添加、修改、删除 Room
  * 添加、删除 Hardware
  * Hardware 与 Room 绑定与解绑
  * 更改 Room 所属 Building
  
2. 多种传感器：Presence Sensor, Light Sensor, Button...
  * 远程查看传感器在线状态与当前值
  * 远程控制照明灯
  
3. 多种角色权限：Admin > Teacher > Student
  * Teacher 以上可以强制开/关灯不受智能系统限制
  * 低权限用户一定时间内（Demo中为30S）无法改变高权限用户开灯操作
  * Student 一段时间无操作后，将照明灯将被智能控制系统接管

## 来自各势力的需求修改
- [ ] 自定义开关灯时间段 [2019.4.x] [Deleted]
- [x] 增加 Building 概念 [2019.4.4]
- [ ] 新建 / 删除 Building 功能 [2019.4.11]
