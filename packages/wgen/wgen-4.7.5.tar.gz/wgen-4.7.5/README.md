**运行改程序**

用 Source code 安装: `git clone https://gitee.com/lucasliu71/wgen.git`, 安装第三方依赖: `pip install rich`

```bash
$ cd wgen
$ python wgen.py -h
usage: wgen.py [-h] [-c CHARS] [-add STRING_ADDED] [-m METHOD] [-o OUTPUT] [-p PROCESSES] min max

██╗    ██╗ ██████╗ ██████╗ ██████╗ ██╗     ██╗███████╗████████╗     ██████╗ ███████╗███╗   ██╗
██║    ██║██╔═══██╗██╔══██╗██╔══██╗██║     ██║██╔════╝╚══██╔══╝    ██╔════╝ ██╔════╝████╗  ██║
██║ █╗ ██║██║   ██║██████╔╝██║  ██║██║     ██║███████╗   ██║       ██║  ███╗█████╗  ██╔██╗ ██║
██║███╗██║██║   ██║██╔══██╗██║  ██║██║     ██║╚════██║   ██║       ██║   ██║██╔══╝  ██║╚██╗██║
╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝███████╗██║███████║   ██║       ╚██████╔╝███████╗██║ ╚████║
 ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝╚══════╝   ╚═╝        ╚═════╝ ╚══════╝╚═╝  ╚═══╝

positional arguments:
  min                   Minimum password length
  max                   Maximum password length

options:
  -h, --help            show this help message and exit
  -c CHARS, --chars CHARS
                        Charset to use: Int `0`, Str-Lower `a`, Str-Upper `A`, Punc `@`
  -add STRING_ADDED, --string-added STRING_ADDED
                        String added to the end of the password
  -m METHOD, --method METHOD
                        Compression method: Normal `normal`, BZip2 `bzip2`, LZMA `lzma`
  -o OUTPUT, --output OUTPUT
                        Output file path
  -p PROCESSES, --processes PROCESSES
                        Number of processes
```

默认参数:

- CHARSET: 创建密码字典的字符串, 默认为 `0aA@`
- METHOD: 压缩文件的压缩算法, 默认为 `LZMA`
- PROCESSORS: CPU 的个数, 默认为 `5`
- OUTPUT: 输出文件, 默认为 `./wordlists.txt`
