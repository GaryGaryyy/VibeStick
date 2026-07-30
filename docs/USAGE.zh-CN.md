# VibeStick 使用、刷入与排障指南

这份文档面向第一次安装 VibeStick 的用户。项目目前支持 M5Stack StickS3，电脑端 bridge 支持 macOS 和 Windows。

## 0. 先确认三件事

1. StickS3 只能连接 2.4 GHz Wi-Fi，电脑和 StickS3 必须在同一个局域网。
2. USB-C 数据线只用于刷入固件和查看串口日志。运行时的状态、语音、发送和电脑切换全部走 Wi-Fi，不是 USB 有线连接。
3. 不要把真实 Wi-Fi 密码、ASR API key、bridge token、日志或录音提交到 git、Issue 或 Pull Request。

## 1. 准备环境

需要准备：

- M5Stack StickS3 和 USB-C 数据线。数据线必须支持数据传输，只有充电功能的线不能刷机。
- 一台用于刷入固件的电脑。下面以 macOS 为例；ESP-IDF 也可以按 Espressif 官方指南安装到其他系统。
- macOS 或 Windows bridge 电脑。电脑和 StickS3 使用同一个 2.4 GHz Wi-Fi。
- ESP-IDF v5.5.x，推荐 v5.5.1。
- Python 3.11 或更高版本。Windows 安装脚本使用 `py -3` 创建虚拟环境。
- SiliconFlow 或其他 OpenAI 兼容语音识别服务的 API key。

## 2. 下载项目和创建配置

在终端执行：

```sh
git clone https://github.com/GaryGaryyy/VibeStick.git
cd VibeStick
./scripts/setup.sh
```

`setup.sh` 会创建两个本地配置文件：

- `firmware/sticks3/include/vibe_stick_secrets.h`：固件使用的 Wi-Fi 和 bridge 配置。
- `.env`：电脑端 bridge 使用的配置。

打开配置文件：

```sh
open -e firmware/sticks3/include/vibe_stick_secrets.h
open -e .env
```

### 固件配置

在 `vibe_stick_secrets.h` 中填写：

```c
#define VIBE_STICK_WIFI_SSID "你的2.4G Wi-Fi名称"
#define VIBE_STICK_WIFI_PASSWORD "你的Wi-Fi密码"
#define VIBE_STICK_BRIDGE_HOST "电脑的局域网IP"
#define VIBE_STICK_BRIDGE_PORT 8765
#define VIBE_STICK_BRIDGE_TOKEN "由setup.sh生成的token"
```

`setup.sh` 会生成一个共享 bridge token，并同步写入 `.env` 和固件配置。`VIBE_STICK_BRIDGE_HOST` 不能填 `127.0.0.1`，因为 StickS3 访问的是局域网中的电脑。如果在 macOS 上执行脚本，它会尝试自动填入 `en0` 的局域网 IP；Windows bridge 则应填写 Windows 的局域网 IP，或者刷入后用电脑搜索功能选择。

### 语音识别配置

使用默认的 SiliconFlow 时，在 `.env` 中填写 key 即可：

```dotenv
VIBE_STICK_ASR_API_KEY=你的SiliconFlow_API_key
```

项目已经提供 SiliconFlow 的默认地址、模型和中文语言设置，不需要再填一长串配置。若使用其他 OpenAI 兼容服务，再额外填写：

```dotenv
VIBE_STICK_ASR_PROVIDER=openai-compatible
VIBE_STICK_ASR_BASE_URL=https://example.com/v1
VIBE_STICK_ASR_API_KEY=你的API_key
VIBE_STICK_ASR_MODEL=服务商的模型名称
```

配置文件只保存在本机。Windows bridge 使用 `%APPDATA%\VibeStick\.env`，详见下文。

## 3. 安装 ESP-IDF

如果还没有 ESP-IDF，在 macOS 终端执行一次：

```sh
mkdir -p ~/esp
cd ~/esp
git clone -b v5.5.1 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32s3
```

每次打开新终端，在使用 `idf.py` 前都要加载环境：

```sh
. "$HOME/esp/esp-idf/export.sh"
```

如果出现 `command not found: idf.py`，就是当前终端还没有执行上面的加载命令。ESP-IDF 安装可能需要下载约 1 GB 工具链，首次安装需要几分钟。

## 4. 刷入 StickS3 固件

### 4.1 进入下载模式

1. 用 USB-C 数据线把 StickS3 直接连接到电脑。尽量不要使用无源 USB Hub。
2. 长按 StickS3 右侧的电源/侧键，直到蓝色指示灯双闪、屏幕熄灭。
3. 在终端查看串口：

```sh
ls /dev/cu.*
```

通常会看到类似 `/dev/cu.usbmodemXXXX` 的设备。记下插入数据线后新出现的端口。

### 4.2 构建并刷入

在项目根目录执行：

```sh
. "$HOME/esp/esp-idf/export.sh"
cd firmware/sticks3
idf.py -p /dev/cu.usbmodemXXXX build flash
```

把 `/dev/cu.usbmodemXXXX` 换成实际端口。等待终端出现 `Hash of data verified`，并看到烧录完成或自动复位提示后再拔线。

只查看串口日志时，可以执行：

```sh
idf.py -p /dev/cu.usbmodemXXXX monitor
```

退出 monitor 使用 `Ctrl-]`。刷入过程中不要把 `monitor` 当作后台服务运行。

### 4.3 刷入完成后的启动

1. 刷入完成后拔掉 USB 数据线。USB 不参与运行时通信，拔线可以避免把下载模式或 USB 供电状态误认为运行状态。
2. 短按右侧电源/侧键唤醒屏幕。
3. 等待 StickS3 连接 Wi-Fi。首次启动时 bridge 尚未启动可能暂时显示“离线”。
4. 启动 Mac 或 Windows bridge 后，长按右侧键搜索电脑，选择对应的电脑名称。

### 4.4 常见刷入失败

- `Device not configured`、串口打不开：重新插拔数据线，再次进入下载模式，并重新运行 `ls /dev/cu.*`。
- 一直显示 `Connecting...`：设备没有真正进入下载模式。确认蓝灯双闪且屏幕熄灭后再运行 `idf.py`。
- 找不到 `/dev/cu.usbmodem...`：更换支持数据传输的 USB-C 线或 USB 端口。
- 刷完仍是旧界面或字体方块：确认命令是在本仓库的 `firmware/sticks3` 目录执行，并用同一套 ESP-IDF 版本重新构建。必要时先执行 `idf.py fullclean`，再执行 `idf.py -p <port> build flash`。
- 屏幕刷完保持熄灭：先拔掉数据线，再短按右侧电源/侧键唤醒。

## 5. 安装 macOS bridge

在项目根目录确认 `.env` 已填写 ASR key，然后执行：

```sh
./scripts/install.sh
```

安装脚本会：

- 编译 macOS HUD；
- 安装 `com.vibestick.bridge` 和 `com.vibestick.hud` 两个 LaunchAgent；
- 将配置和运行文件复制到 `~/Library/Application Support/VibeStick`；
- 立即启动 bridge，之后登录 macOS 时自动启动。

macOS 可能会请求以下权限：

- 辅助功能：允许 bridge runner 或 `python3` 控制当前应用，用于粘贴文字。
- 麦克风：只有启用 Mac 麦克风兜底采集时需要；正常流程是 StickS3 通过 Wi-Fi 上传 PCM 音频。

安装后可以关闭终端窗口。检查状态：

```sh
./scripts/doctor.sh
curl http://127.0.0.1:8765/health
```

`./scripts/dev.sh` 只适合开发和诊断，会占用当前终端；日常使用应该运行 `./scripts/install.sh` 安装后台 LaunchAgent。

## 6. 安装 Windows bridge

### 6.1 安装

Windows 需要 Python 3.11 或更高版本，并且能在 PowerShell 中使用 `py` 启动器：

```powershell
py -3 --version
```

在 Windows 上下载或克隆本仓库，进入仓库根目录后执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install_windows.ps1
```

安装脚本会创建：

- `%APPDATA%\VibeStick\.venv`：独立 Python 虚拟环境；
- `%APPDATA%\VibeStick\.env`：Windows bridge 配置；
- `%APPDATA%\VibeStick\run-vibestick-wifi-bridge.cmd`：手动诊断入口；
- `VibeStick Bridge`：隐藏的后台任务；
- `VibeStick HUD`：录音期间显示提示的后台任务。

两个计划任务会立即启动，并在当前用户登录 Windows 时自动启动。安装完成后可以关闭 PowerShell、Python 和 `.cmd` 窗口，不需要一直开着 Shell。

### 6.2 填写 Windows 配置

安装完成后打开配置文件：

```powershell
notepad "$env:APPDATA\VibeStick\.env"
```

使用默认 SiliconFlow 时只需要填写：

```dotenv
VIBE_STICK_ASR_API_KEY=你的SiliconFlow_API_key
```

可以额外指定电脑名称。名称过长时 StickS3 会自动换行，并限制显示长度：

```dotenv
VIBE_STICK_COMPUTER_NAME=Windows
```

不要只在 PowerShell 临时执行 `$env:VIBE_STICK_ASR_API_KEY=...`。关闭窗口后，后台计划任务不会继承这个临时变量。修改 `%APPDATA%\VibeStick\.env` 后重启 bridge 任务：

```powershell
Stop-ScheduledTask -TaskName "VibeStick Bridge" -ErrorAction SilentlyContinue
Start-ScheduledTask -TaskName "VibeStick Bridge"
```

修改 bridge 代码或升级仓库版本时，重新运行 `install_windows.ps1`。仅修改 `.env` 时不需要重新创建虚拟环境。

### 6.3 Windows 防火墙

首次运行如果出现防火墙提示，请允许 Python/VibeStick Bridge 在“专用网络”通信。需要允许局域网访问：

- TCP `8765`：bridge HTTP 状态、语音上传和发送；
- UDP `8766`：电脑搜索发现。

不建议在公共网络配置文件中开放端口。电脑和 StickS3 必须连接同一个局域网。

## 7. 日常操作

### 语音和发送

- 长按正面蓝色按钮开始录音，屏幕显示“正在聆听”。松开蓝色按钮后，StickS3 上传录音，bridge 进行识别并粘贴到当前获得焦点的电脑程序。
- 正面蓝色按钮短按会发送 `button_short`，相当于回车/发送。
- 语音识别、上传、转写或粘贴失败时，StickS3 播放错误提示音。

### 电脑切换

- 正常首页短按右侧键：切换 provider。
- 长按右侧键：搜索同一局域网内的 VibeStick bridge。
- 搜索页面短按右侧键：选择下一个电脑。
- 搜索页面短按蓝色按钮：确认当前电脑。搜索页中长按蓝色按钮也会确认。

选中的电脑地址会保存到 StickS3。之后拔掉 USB 仍然可以正常连接，因为运行时通信全部通过 Wi-Fi。

### 屏幕和省电

当前固件采用较低屏幕背光，空闲约 5 秒后关闭背光。息屏时第一次按任意键只点亮屏幕，不执行回车、录音、切换或搜索；屏幕点亮后再次按键才执行对应功能。固件默认 CPU 频率为 80 MHz，并启用 Wi-Fi 省电模式。屏幕熄灭只关闭背光，不会停止 bridge、Wi-Fi 或任务状态轮询。

## 8. 状态和提示音

首页状态点和文字含义：

| 显示 | 含义 |
| --- | --- |
| 绿色点，运行中 | agent 正在执行任务 |
| 绿色点，已完成 | 最近任务完成 |
| 灰色点，待命 | bridge 已连接，但当前没有执行中的任务 |
| 黄色点，待确认 | agent 等待用户审批 |
| 红色点，出错 | 任务失败、取消、中止或异常停止 |
| 深灰点，离线 | Wi-Fi 或 bridge 不可达 |

完成、等待审批、任务失败、任务取消、任务崩溃和非正常停止会触发提示音。语音识别或粘贴失败也会触发错误提示音。录音正在进行时，提示音可能被跳过，避免提示音混入录音。

状态点表示选中电脑上的本地 Codex/Claude agent 状态，不单独表示 bridge 进程是否存在。bridge 已连接但电脑上没有受支持的 agent 活动时，正常显示“待命”；只有 bridge 或 Wi-Fi 不可达才显示“离线”。

当前稳定首页优先显示 provider 状态和电脑名称，5H/7D 用量区域暂不显示。

## 9. 多电脑切换原理

在 Mac 和 Windows 上分别安装 bridge，并为每台电脑设置不同的 `VIBE_STICK_COMPUTER_NAME`，例如 `MacBook` 和 `Windows`。两台电脑都连接同一个 2.4 GHz 局域网后：

1. 长按 StickS3 右侧键进入搜索。
2. 短按右侧键在电脑列表中向下移动。
3. 短按蓝色按钮确认。

搜索使用 UDP `8766` 广播，bridge HTTP 服务使用 TCP `8765`。StickS3 在发现包中带上固件里的 bridge token，bridge 可以在首次发现时保存配对 token；不需要 USB 作为运行时数据线。Windows 搜索不到电脑时，优先检查防火墙和两个端口。

## 10. 常见问题

### S3 一直显示“离线”

检查 Wi-Fi 是否为 2.4 GHz、电脑是否与 StickS3 在同一局域网、`VIBE_STICK_BRIDGE_HOST` 是否是电脑局域网 IP。Mac 上执行：

```sh
curl http://127.0.0.1:8765/health
```

Windows 上检查计划任务：

```powershell
Get-ScheduledTask -TaskName "VibeStick Bridge"
Get-Content "$env:APPDATA\VibeStick\bridge.log" -Tail 80
```

如果 Mac 或 Windows 上同时手动启动过多个 bridge，先关闭手动进程，再用对应安装脚本重新注册后台服务。多个进程抢占 `8765` 端口会导致状态异常。

### Windows 关闭窗口后就离线

说明之前运行的是手动 `.cmd` 或 Python 进程。重新执行 `install_windows.ps1`，让它创建并启动隐藏的 `VibeStick Bridge` 计划任务。安装成功后关闭 Shell 不会影响后台 bridge；`.cmd` 只用于手动诊断。

### Windows 能发送但语音识别失败

确认 `%APPDATA%\VibeStick\.env` 中有真实的 `VIBE_STICK_ASR_API_KEY`，而不是只设置了 PowerShell 临时 `$env:` 变量。修改后重启计划任务，并检查 `bridge.log`。

### 搜索页面不显示电脑名称或显示方块

确认 bridge 是从当前项目版本启动的，并且 `VIBE_STICK_COMPUTER_NAME` 使用普通 ASCII 名称。长名称会自动换行；电脑名中的非 ASCII 控制字符会被清理。固件需要从本仓库重新构建并刷入，不能只更新电脑端 bridge 来修复固件字体问题。

### 任务完成或失败没有声音

确认 StickS3 已连接到正确的电脑，并且状态确实从运行中变化为完成或出错。首次启动时已经存在的旧 alert 不会重复播放；提示音也不会在录音期间排队。若任务进程刚退出，bridge 会从最近的 session 事件判断完成或异常停止，状态轮询通常需要几秒钟。

### 语音可以识别但没有粘贴

- macOS：在“系统设置 -> 隐私与安全性 -> 辅助功能”中允许运行 bridge 的 Python 或启动器。
- Windows：先确保目标文本框仍然获得焦点；确认 bridge 任务在当前用户会话中运行。
- 任一系统：检查 `recording.json` 和 `bridge.log`，确认录音上传、ASR 和 paste 三个步骤都成功。

### `idf.py` 或刷机失败

重新执行：

```sh
. "$HOME/esp/esp-idf/export.sh"
```

然后确认 StickS3 已进入蓝灯双闪、屏幕熄灭的下载模式，并使用新出现的 `/dev/cu.*` 串口。不要在运行模式下反复刷写，也不要使用只有充电功能的 USB-C 线。

## 11. 日志和本地文件

### macOS

```text
~/Library/Application Support/VibeStick/.env
~/Library/Application Support/VibeStick/bridge.log
~/Library/Application Support/VibeStick/bridge.err.log
~/Library/Application Support/VibeStick/recording.json
~/Library/Application Support/VibeStick/paired-token.txt
```

### Windows

```text
%APPDATA%\VibeStick\.env
%APPDATA%\VibeStick\bridge.log
%APPDATA%\VibeStick\recording.json
%APPDATA%\VibeStick\paired-token.txt
%APPDATA%\VibeStick\run-vibestick-wifi-bridge.cmd
```

日志中可能包含本机路径和错误信息。分享日志前先删除 API key、token、Wi-Fi 信息和个人路径。

## 12. 卸载后台服务

macOS：

```sh
./scripts/uninstall.sh
```

Windows：

```powershell
Unregister-ScheduledTask -TaskName "VibeStick Bridge" -Confirm:$false
Unregister-ScheduledTask -TaskName "VibeStick HUD" -Confirm:$false
```

卸载后台服务不会自动删除 `%APPDATA%\VibeStick` 或 macOS Application Support 中的配置、日志和录音；确认不再需要后再手动删除。
