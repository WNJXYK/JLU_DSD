# Distributed Software Deleopment Course in Jilin University - Mogic

![Python](https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7-blue.svg)
![Requirements](https://img.shields.io/badge/dependencies-flask%20%7C%20json-brightgreen.svg)

## Introduction
A light-controlling system that can control and monitor the sensor (including light sensor, button, presence sensor) and devices (including light and alarm). All sensors and devices are based on `Raspberry PI 3`, all code are based on `Python` and the web is based on Bootstrap / Materilize HTML + JS

Mogic Group's responsibility is to build a server which could transfer data between other groups.

Mogic's Website : https://dsd.keji.moe

## Content

#### Version 1

* SRS Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/V1/SRS_For_Server-V1-4.10.docx
* IS Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/V1/IS_For_Server-V1-4.10.docx
* SDS Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/V1/SDS_For_Server-V1-4.10.docx
* PPT Slides : 
* Server Code : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V1.0/Server
* Hardware Code : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V1.0/Hardware
* Simulated DB : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V1.0/Database
* Simulated Web : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V1.0/Web
* Simulated Controller : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V1.0/Controller
* There are some legacy Wiki for V1:
  * https://github.com/WNJXYK/JLU_DSD/wiki/%5BLegacy%5D-Interface
  * https://github.com/WNJXYK/JLU_DSD/wiki/%5BLegacy%5D-System-Architecture
  * https://github.com/WNJXYK/JLU_DSD/wiki/%5BLegacy%5D-数据库面向服务器的API
  * https://github.com/WNJXYK/JLU_DSD/wiki/%5BLegacy%5D-数据库面向终端的API
  * https://github.com/WNJXYK/JLU_DSD/wiki/%5BLegacy%5D-硬件如何与服务器交流

You can also find code and instructions for installing in `production` branch : https://github.com/WNJXYK/JLU_DSD/tree/production

#### Version 2

* SRS Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/V2/SRS_For_All-V2-6.5.docx
* IS Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/V2/IS_For_Server-V2-6.5.docx
* SDS Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/V2/SDS_For_Server-V2-6.5.docx
* Server Code ( Including a bulit-in Database and Controller ) : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V2.0/Server
* Hardware Code : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V2.0/Hardware
* Alternative Web Code : https://github.com/WNJXYK/JLU_DSD/tree/master/Code/V2.0/Web
* API Wiki :
  * https://github.com/WNJXYK/JLU_DSD/wiki/Command-API-Documents-For-V2
  * https://github.com/WNJXYK/JLU_DSD/wiki/Hardware-API-Documents-For-V2
  * https://github.com/WNJXYK/JLU_DSD/wiki/Interface-API-Documents-For-V2
  * https://github.com/WNJXYK/JLU_DSD/wiki/Open-API-Documents-For-V2

You can also find code and instructions for installing in `V2` branch : https://github.com/WNJXYK/JLU_DSD/tree/V2

#### Other

Question Documents : https://github.com/WNJXYK/JLU_DSD/blob/master/Documents/Other/2019.4.3-Questions_Version1.docx

Web Page : https://github.com/WNJXYK/JLU_DSD/tree/master/docs

## Functions

1. Building

   * Add a building
   * Delete a building
2. Room

   * Add a room in a building
   * Delete a room in a building
   * Modify a room's attributes ( Including `timeout` and `default` for lights )
3. Hardware

   * Add hardware ( Based on a GPIO of a Raspberry PI)

   * Delete hardware

   * View sensors' real-time data

   * Control light
4. Raspberry PI
   * View Raspberry PI which has registered in server
   * Delete Raspberry PI
5. User
   * Add a user
   * Delete a user
   * Modify a user ( Give / Revoke permission of `build`, `admin` and `force`)
6. Role
   * Modify Role ( Change the command priority of role)
7. Log
   * View Emergency Log
   * Solve Emergency Log



Tips:

About permission :

`building` gives users the permission to ( add / del / modify) (room / building / hardware/ raspberry pi)

`admin` gives users the permission to (add / modify / del) (user / role)

`force` gives users the permission to force the light to be opened / closed.

And user's initial permission is same as its role's permission.

About Log : 

When panic button is pressed, the building is entered emergency mode and the all the alarm and lights in this building is opened.

When solving the emergency log, the alarm is closed at the same time and the lights will close when timeout.

## Other Groups

1. Learning Ducks ( Web ) : https://github.com/learningducks/DSD2019

2. Apostle ( Android APP ) : https://github.com/sakurajinja/DSD

3. Double Bloom ( Intelligence Controller ) : https://github.com/lyj3516/groupdb.github.io

4. Beauty and the Beast ( Database ) : https://github.com/JLUTAQCS/Beauty-and-the-Beast