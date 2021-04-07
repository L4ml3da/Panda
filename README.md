# Panda
1、结合masscan进行快速web信息探测。

2、实时导出结果到panda.xls

## Usage 
Usage: Panda (Web sevice scanner) Version 1.0

Options:
  -h, --help            show this help message and exit
  
  -n HOSTS, --hosts=HOSTS
                        The hosts network, like 192.168.23.0/16
                        
  -t NUMBER, --threads=NUMBER
                        Number of scan thread (default:10)
                        
  -p PORTS, --ports=PORTS
                        Web ports (default:80,81,82,443,7001-7003,8000-8100,81
                        81,8282,8383,8585,8686,8787,8888,8989)
                        
  -s SPEED, --speed=SPEED
                        masscan speed(default:10000)
                        
  -i TIMEOUT, --timeout=TIMEOUT
                        http timeout(default:5)



## TODO

1、添加https web 探测

2、web指纹探测

3、其他常用应用端口探测

