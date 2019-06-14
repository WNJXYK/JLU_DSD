# Distributed Software Deleopment Course in Jilin University - Mogic

![Python](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)
![Requirements](https://img.shields.io/badge/dependencies-flask%20%7C%20json-brightgreen.svg)

## Introduction
A light-controlling system that can control and monitor the sensor (including light sensor, button, presence sensor) and devices (including light and alarm). All sensors and devices are based on `Raspberry PI 3`, all code are based on `Python` and the web is based on Bootstrap / Materilize HTML + JS

## Content

#### Version 1

* SRS Documents : 

#### Version 2

## Functions

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
- [ ] 修改智能控制模块规则 [2019.3.x] [Partly Deleted]
- [ ] 自定义开关灯时间段 [2019.4.x] [Deleted]
- [x] 增加 Building 概念 [2019.4.4]
- [ ] 新建 / 删除 Building 功能 [2019.4.11]
