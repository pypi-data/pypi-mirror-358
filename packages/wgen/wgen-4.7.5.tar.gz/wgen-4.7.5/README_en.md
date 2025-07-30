**To run this script**

to install source code: `git clone https://gitee.com/lucasliu71/wgen.git`, and install requirements: `pip install rich`

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

default arguments:

- CHARSET: characters, default: `0aA@`
- METHOD: Compression algorithm for ZIP file, default: `LZMA`
- PROCESSORS: number of processors, default: `5`
- OUTPUT: output path, default: `./wordlists.txt`