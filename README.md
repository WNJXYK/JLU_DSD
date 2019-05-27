## How to install Server into your VPS?

1. Install Python3.6

   Instal Environmental Requirements

   ```bash
   yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
   ```

   Download Python3.6 

   ```bash
   wget https://www.python.org/ftp/python/3.6.6/Python-3.6.6.tgz
   ```

   Unzip

   ```bash
   tar -zxf Python-3.6.6.tgz
   cd Python-3.6.6
   ```

   Configure & Install

   ```bash
   ./configure --prefix=/usr/bin/python3.6.6
   make && make install
   ```

   Build Links

   ```bash
   ln -s /usr/bin/python3.6.6/bin/python3 /usr/bin/python3
   ln -s /usr/bin/python3.6.6/bin/pip3 /usr/bin/pip3
   ```

2. Install Python Requirements

   ```
   pip3 install flask
   pip3 install flask_cors
   ```

3. Get Code from Github

   Install Git

   ```bash
   yum install git
   ```

   Clone Code

   ```bash
   git clone -b V2 https://github.com/WNJXYK/JLU_DSD.git
   ```

## Update Code

1. Enter the `JLU_DSD` folder

2. Pull Code

   ```bash
   git pull
   ```

## Run Code

1. Enter the `JLU_DSD` folder

2. Run Server

   ```
   python3 Server/Main.py
   ```

## Tips

You can use `screen` to run multi-tasks underground.
