<div align="center">
    <img alt="QsignDEV" src="https://qsign.dev/img/logo.png"/>

# qsign-onekey


本项目用于一键启动qsign

请自行将qsign内容文件和go-cqhttp放到同级别文件夹，脚本会自行读取<br>

<img src="https://img.shields.io/github/issues/rhwong/unidbg-fetch-qsign-onekey"> <img src="https://img.shields.io/github/forks/rhwong/unidbg-fetch-qsign-onekey"> 
<img src="https://img.shields.io/github/stars/rhwong/unidbg-fetch-qsign-onekey"> <img src="https://img.shields.io/badge/Version-1.2.3.1-blue">
<img src="https://img.shields.io/github/downloads/rhwong/unidbg-fetch-qsign-onekey/total">


<img src="https://img.shields.io/badge/Windows-x64-red?style=flat-square&logo=Windows"> <img src="https://img.shields.io/badge/Windows-x86-red?style=flat-square&logo=Windows"> 

</div>
<!-- projectInfo end -->

## ✨安装说明

请直接点击 `Code - Download ZIP` 下载本项目，直接解压缩到任意不包含中文和空格的路径中。

然后将qsign内容文件和go-cqhttp放到同级别文件夹，脚本会自行读取。

文件目录结构如下

```
└─ qsign-onekey-1.1.9-bitterest
     └─bin
     └─jre
     └─lib
     └─txlib
         └─8.9.70
         └─8.9.80
         └─8.9.85
         └─8.9.88
         └─...
     └─README.md
     └─go-cqhttp.bat
     └─go-cqhttp.exe
     └─Start_Qsign.bat
```

## ✨使用方法

### 如何使用go-cqhttp联动运行

1. 首先，运行 `go-cqhttp.bat`，按照提示生成 `config.yml` 。

2. 双击 `Start_Qsign.bat` 启动Qsign Deamon窗口，按照提示依次键入 `txlib_version` 参数、设定`host`、`port`、`key`的值。 (👈如果不知道这些是干什么的，请直接依次按下Enter）

3. 如果脚本检测到 `config.yml` 尚未设定账号和密码，那么会提示你输入账号(Account uin)和密码(password)，输入后会同步进 `config.yml` 。

4. 输入完成后，会启动Core窗口，用于启动Qsign Core窗口

5. 在启动完成后，qsign会告诉您当前运行api的地址，如果您没设定过host和key，那么默认是 `http://127.0.0.1:13579`。key已经在开始时设定过，如果您没设定，那么默认是 `1145141919810`。(👈这些东西会自动写入到 `config.yml` ）

6. 切勿关闭启动完成后的两个窗口，`Qsign Deamon`窗口用于监测`Qsign Core`是否存活，若探活失败将按照pid结束进程并重启Core。

7. 如果日后需要修改 `txlib_version` 的版本，您可以删除文件夹根目录下的 `txlib_version.json` 来重新进入设定流程，不建议对此文件进行修改。


## ✨免责声明

- 本仓库代码仅供学习参考，用于自动化程序的启动，并无任何侵权内容。


## Stargazers over time

[![Stargazers over time](https://starchart.cc/rhwong/unidbg-fetch-qsign-onekey.svg)](https://starchart.cc/rhwong/unidbg-fetch-qsign-onekey)

