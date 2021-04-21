# MyScan
本项目的目标是在 Airsim 中，模拟倾斜摄影进行图像采集。

该项目目前只在 Airsim 提供的 CityEnviron 虚拟环境中进行过测试。

## install

本项目依赖于 Airsim 提供的 python api 以及 Airsim 提供好的虚拟环境的 release 版本。

本项目的安装分为三部分：
1. Airsim 的 python api, 可参考 [Airsim 官方文档](https://microsoft.github.io/AirSim/apis/)
   
   对于 windows 用户，推荐先安装 anonoconda 作为包管理器。在激活 conda 虚拟环境之后，按照下述步骤安装 Airsim 的 python api
   
   ```bash
   pip install msgpack-rpc-python
   pip install airsim
   ```

2. 下载及解压 Airsim 提供的虚拟环境的 Release 版本，[Airsim Releases](https://github.com/Microsoft/AirSim/releases)

    提醒：本项目目前仅使用 v1.4.0 - Windows 中的 CityEnviron 进行过测试。

3. 使用本项目根目录下的 airsim_settings 的内容替换 Airsim 的配置文件内容

    对于 Windows 用户，Airsim 的配置文件存放在 ~/Documents/Airsim/settings.json

## run

1. 运行 CityEnviron 环境的可执行文件，等待虚拟环境启动

2. 运行 cv_capture，-s 指定图像保存路径，-c 指定项目的配置文件

    ```bash
    python cv_capture.py -s ./imgs -c ./configs/city.json
    ```