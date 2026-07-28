# VibeStick

[English README](README.md)

![VibeStick 首页，显示 Codex 和 Claude 状态](assets/brand/home-screen-preview.png)

![VibeStick 语音输入流程，显示 StickS3 录音状态和 Mac HUD](assets/brand/voice-input-preview.png)

VibeStick 把 M5Stack StickS3 变成一个桌面 AI agent 小终端：显示状态、5H/7D 用量、提醒音，并支持长按说话后自动转写粘贴到 Mac。

VibeStick 面向 M5Stack StickS3，不是 M5Stack 官方项目。Codex、Claude 等第三方 agent 名称只用于说明本地兼容工具和集成。

## 开始前的准备

- [ ] M5 StickS3｜一根 USB-C 数据线｜一台电脑（Mac；可选 Windows 电脑运行 Wi-Fi bridge）
- [ ] Wi-Fi（必须是 2.4GHz） 名称｜Wi-Fi密码｜语音识别模型 API Key
-  语音转写API key 推荐 SiliconFlow：<https://cloud.siliconflow.cn/i/7ZCoy9fU>。国内直连、有免费额度、OpenAI 兼容；演示视频用的就是 SiliconFlow。可改用其他 OpenAI 兼容服务的 `base_url` 和模型名称。
-  如要显示 Claude 5H/7D 用量（该功能默认关闭）。需要 Claude Code CLI（在终端运行 `claude` 后执行 `/login`），并在 `.env` 中设置 `VIBE_STICK_CLAUDE_USAGE=on`。


## 安装

你可以手动执行，也可以交给 AI 编程 agent，例如 Claude Code 和 Codex。

> 说明：标 👤 的步骤是需要人亲自动手的物理操作，例如插线、长按/短按电源键、在系统设置里授权。AI agent 请按顺序执行 shell 步骤，执行到 👤 步骤时暂停，让用户完成后再继续。

1. 克隆仓库并创建本地配置文件：

```sh
git clone https://github.com/GaryGaryyy/VibeStick.git
cd VibeStick
./scripts/setup.sh
```

2. 填入人类提前准备好的配置：

```sh
open -e firmware/sticks3/include/vibe_stick_secrets.h
open -e .env
```

在 `vibe_stick_secrets.h` 里填写 Wi-Fi 名称、Wi-Fi 密码、Mac bridge host。只要文件里还保留示例占位值，`scripts/setup.sh` 会尝试把 `VIBE_STICK_BRIDGE_HOST` 自动写成检测到的 en0 局域网 IP。

在 `.env` 里填写 ASR key 和需要的 provider 设置。默认推荐 SiliconFlow：

```sh
VIBE_STICK_ASR_PROVIDER=openai-compatible
VIBE_STICK_ASR_BASE_URL=https://api.siliconflow.cn/v1
VIBE_STICK_ASR_API_KEY=your-siliconflow-key
VIBE_STICK_ASR_MODEL=FunAudioLLM/SenseVoiceSmall
```

3. 👤 用 USB-C 数据线把 StickS3 插到 Mac。

4. 👤 让 StickS3 进入下载模式：长按侧面电源键，直到蓝灯双闪、屏幕熄灭。这是 ESP32-S3 烧录必需步骤。

5. 如果本机还没有 ESP-IDF，先安装；然后把它加载到当前 shell。这是一次性工具链安装，下载较大（约 1GB），可能需要几分钟。每开一个新终端，在运行 `idf.py` 前都要先执行加载命令：

```sh
if [ ! -d "$HOME/esp/esp-idf" ]; then
  mkdir -p ~/esp && cd ~/esp
  git clone -b v5.5.1 --recursive https://github.com/espressif/esp-idf.git
  cd esp-idf && ./install.sh esp32s3
fi
. "$HOME/esp/esp-idf/export.sh"
```

也可以按 Espressif [官方指南](https://docs.espressif.com/projects/esp-idf/en/v5.5.1/esp32s3/get-started/index.html)安装。如果 `install.sh` 失败，请确认已安装 `git`、`python3`、`cmake`，或改按官方指南处理。如果 ESP-IDF 安装在其他位置，请调整路径。

6. 构建并烧录固件：

```sh
cd firmware/sticks3
idf.py -p <port> build flash
cd ../..
```

如果不知道端口，运行：

```sh
ls /dev/cu.*
```

等到终端出现 `Hash of data verified`。

7. 👤 短按电源键唤醒屏幕。蓝灯应熄灭、屏幕亮起，此时应看到 VibeStick 首页。联网前可能显示离线。

8. 安装本机 macOS bridge 和 HUD：

```sh
./scripts/install.sh
```

9. 👤 当 macOS 弹出 `python3.14` 想用辅助功能控制这台电脑时，点击“打开系统设置”并勾选允许。粘贴转写结果需要这个权限。

10. 检查安装状态：

```sh
./scripts/doctor.sh
```

尽量让必须项全部 PASS。然后看一眼 StickS3：如果本机 provider 数据可用，Codex / Claude 状态和 5H / 7D 应该出现真实值。

如果 Codex 已经能用、而 Claude 那栏显示 `--%`，这是正常的：Claude 用量默认关闭（更安全）；如需显示，请设置 `VIBE_STICK_CLAUDE_USAGE=on`，并确保 Claude Code 已通过 `claude` 和 `/login` 登录。

11. 👤 打开任意文本框，长按正面蓝键说话，松开后 VibeStick 应自动转写并粘贴。

### 可选：Windows Wi-Fi bridge

如果要在 Windows 电脑上运行 bridge，在 Windows 上安装 bridge：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install_windows.ps1
```

安装脚本会创建 bridge 和录音提示层两个当前用户的隐藏任务计划并立即启动，所以不需要一直挂着黑色窗口。录音或识别期间才会出现临时提示层，平时完全后台运行。生成的 `%APPDATA%\VibeStick\run-vibestick-wifi-bridge.cmd` 仍然保留，用于手动诊断。

语音转写前，打开 `%APPDATA%\VibeStick\.env`，填写 `VIBE_STICK_ASR_API_KEY`，以及对应的 ASR provider、base URL 和 model。不要直接把包含 Mac 专用配置的 `.env` 复制过来。Windows bridge 接收的是 S3 通过 Wi-Fi 上传的麦克风 PCM，不需要打开 Windows 麦克风；bridge 负责转写，再把结果粘贴到当前获得焦点的 Windows 程序。

S3 上的状态点表示本机 Codex/Claude 是否运行，不表示 bridge 是否在线。如果 bridge 已连接但 Windows 没有受支持的 agent 进程，S3 会显示“待命”；只有 bridge 或 Wi-Fi 不可达时才显示“离线”。电脑名称和 Wi-Fi 仍然可以正常显示。

如果任务被取消、中止、崩溃，或 agent 在运行任务时异常退出，bridge 会把状态标记为错误，S3 会播放错误提示音。

固件首次使用烧录时写入的 bridge host，之后可以搜索并保存同一局域网里的其他 bridge。运行时状态、提醒、录音转写和粘贴都走 Wi-Fi。

### 多电脑切换

如果同一局域网里有多台电脑运行 VibeStick Bridge，长按 StickS3 右侧键进入搜索。短按右侧键向下选择，按正面蓝键确认连接这台电脑。StickS3 会保存选中的 bridge host，之后运行时通信仍全部走 Wi-Fi。

搜索使用 UDP `8766` 端口；电脑端返回电脑名和 HTTP 端口。StickS3 会在搜索包里带上 bridge token，所以没有本地 token 的 bridge 可以直接记住它。Windows 如果搜不到，通常需要在防火墙里允许 Python/VibeStick Bridge 入站。

开发调试时可以用 `./scripts/dev.sh` 替代 `./scripts/install.sh`，它会在当前终端里运行 bridge。

## 常见问题排查

### `command not found: idf.py`

ESP-IDF 没有加载到当前 shell，或者还没有安装。先 source ESP-IDF 的 `export.sh`，再运行 `idf.py`：

```sh
. $HOME/esp/esp-idf/export.sh
```

如果你的 ESP-IDF 在其他位置，请调整路径。每开一个新终端，在使用 `idf.py` 前都要运行一次。

### 烧录报 "Device not configured" 或连不上串口

重新插拔 USB-C 数据线。再次进入下载模式：长按侧面电源键，直到蓝灯双闪、屏幕熄灭。运行 `ls /dev/cu.*` 找端口，然后重试 `idf.py -p <port> build flash`。

### StickS3 连不上 Wi-Fi

请使用 2.4GHz Wi-Fi。StickS3 / ESP32-S3 不支持 5GHz Wi-Fi。

### 录音能转写但没有粘贴

给执行粘贴的 Python runner 开辅助功能权限。macOS 路径：系统设置 -> 隐私与安全性 -> 辅助功能，然后允许 `python3.14` 或运行 VibeStick 的终端 / 启动器。

### "No transcription adapter configured"

在 `.env` 里配置 ASR，尤其是 `VIBE_STICK_ASR_PROVIDER`、`VIBE_STICK_ASR_BASE_URL`、`VIBE_STICK_ASR_API_KEY`，然后重新安装：

```sh
./scripts/install.sh
```

### 找不到 `.env`

`.env` 是隐藏文件。用下面命令打开：

```sh
open -e .env
```

### 录音转写失败、SSL 报错或超时

通常是当前网络访问不到所选 ASR 服务。国内用户建议换 SiliconFlow：<https://cloud.siliconflow.cn/i/7ZCoy9fU>。也可以配置其他可访问的 OpenAI 兼容 ASR，或配置网络代理。

## 配置说明

不要把真实 API key、本地 token、Wi-Fi 密码、本地日志、录音文件提交到 git。

`.env` 里的空值通常表示“使用内置默认值”。`scripts/dev.sh` 会读取仓库根目录的 `.env`。`scripts/install.sh` 会把 `.env` 复制到 `~/Library/Application Support/VibeStick/.env`，LaunchAgent 运行时读取安装后的文件。

### 核心设置

- `VIBE_STICK_PROJECT_ROOT`：本地 Codex session 观察路径。
- `VIBE_STICK_COMPUTER_NAME`：可选电脑名称覆盖值，会显示在 StickS3 首页。
- `VIBE_STICK_PROVIDER`：当前 provider，`auto`、`codex` 或 `claude`；默认 `auto`。
- `VIBE_STICK_BRIDGE_TOKEN`：bridge 绑定到非 loopback 地址时必需的共享 token，例如 `0.0.0.0`。
- `VIBE_STICK_MAX_RECORDING_AUDIO_BYTES`：`/recording/audio` 最大请求体大小，默认 `2000000`。
- `VIBE_STICK_RECORDING_USE_MAC_MIC`：设为 `0` 可关闭 Mac 麦克风兜底。
- `VIBE_STICK_AUTO_ENTER`：设为 `1` 会在粘贴后自动按 Return。

### ASR 方案 1：SiliconFlow（默认推荐）

```sh
VIBE_STICK_ASR_PROVIDER=openai-compatible
VIBE_STICK_ASR_BASE_URL=https://api.siliconflow.cn/v1
VIBE_STICK_ASR_API_KEY=your-siliconflow-key
VIBE_STICK_ASR_MODEL=FunAudioLLM/SenseVoiceSmall
VIBE_STICK_ASR_LANGUAGE=zh
VIBE_STICK_ASR_TIMEOUT_SECONDS=15
VIBE_STICK_ASR_ATTEMPTS=2
```

使用云端 ASR 时，音频会离开本机 Mac。

### ASR 方案 2：任意 OpenAI 兼容服务

只要服务支持 `POST {base_url}/audio/transcriptions` 即可。

```sh
VIBE_STICK_ASR_PROVIDER=openai-compatible
VIBE_STICK_ASR_BASE_URL=https://example.com/v1
VIBE_STICK_ASR_API_KEY=your-api-key
VIBE_STICK_ASR_MODEL=provider-model-name
```

Groq 也作为海外可选 preset 保留：

```sh
VIBE_STICK_ASR_PROVIDER=groq
VIBE_STICK_ASR_API_KEY=your-groq-key
```

旧别名 `VIBE_STICK_GROQ_API_KEY`、`VIBE_STICK_GROQ_MODEL`、`VIBE_STICK_GROQ_LANGUAGE` 仍然支持。

### ASR 方案 3：本地命令（离线）

```sh
VIBE_STICK_TRANSCRIBE_CMD=/path/to/transcribe-command
VIBE_STICK_TRANSCRIBE_TIMEOUT_SECONDS=120
```

这个命令会从 stdin 收到录音 session JSON，并应把最终转写文本打印到 stdout。

### Claude 用量

想显示 Claude 5H/7D 用量，请使用 `VIBE_STICK_PROVIDER=claude` 或 `VIBE_STICK_PROVIDER=auto`，设置 `VIBE_STICK_CLAUDE_USAGE=on`，并确保 Claude Code CLI 已在终端通过 `claude` 和 `/login` 登录。

- `VIBE_STICK_CLAUDE_USAGE`：设为 `on` 后获取真实 Claude Code 订阅用量；默认 `off`。
- `CLAUDE_CODE_OAUTH_TOKEN`：可选 Claude Code OAuth access token。未设置时，bridge 会尝试读取本机 Claude Code keychain / 文件凭据。
- `VIBE_STICK_CLAUDE_USAGE_INTERVAL_SECONDS`：Claude 用量轮询间隔，默认 `300`，最小 `30`。

Claude usage 会使用用户本机 Claude Code 订阅凭据和 client headers 调用未公开的 Anthropic endpoint。它是 opt-in，可能随时失效；bridge HTTP API 不会暴露 token 或原始 endpoint 响应。如果从未成功抓取过 Claude usage，StickS3 会显示 `--%`；成功抓取后，临时刷新失败会保留上一次值并标记 stale。

## 项目结构

```text
VibeStick/
  README.md
  README.zh-CN.md
  .env.example
  docs/
  firmware/sticks3/
  bridge/src/vibe_stick/
  app/macos/VibeStickHUD/
  scripts/
  tests/
```

## 检查命令

```sh
python3 -m compileall -q bridge/src tests
PYTHONPATH=bridge/src python3 -m unittest discover -s tests
bash -n scripts/setup.sh scripts/doctor.sh scripts/install.sh
```

固件构建仍需要 ESP-IDF：

```sh
cd firmware/sticks3
. $HOME/esp/esp-idf/export.sh
idf.py build
```

## 当前限制

- 这是整理后的原型，不是打包好的 Mac app 或 DMG。
- 固件只面向 M5Stack StickS3。
- 当前稳定首页优先显示 provider 状态和电脑名称；5H/7D 额度仍保留在 bridge 状态里，但暂不显示在屏幕上。
- 屏幕亮度比之前更低，空闲 5 秒后关闭背光，固件默认 CPU 频率降为 160 MHz。
- Windows 支持目前是脚本形式，需要 Python 3.11+；不是签名安装包。
- Codex quota 来自本地 Codex session JSONL 里的 `rate_limits`，不是官方 quota API。
- Claude usage 来自未公开的 Claude Code OAuth endpoint，默认关闭。
- ASR 可靠性取决于麦克风采集、上传 PCM 质量、provider 可达性和模型配置。

## 贡献与安全

欢迎贡献,详见 [CONTRIBUTING.md](CONTRIBUTING.md)。报告安全漏洞请见
[SECURITY.md](SECURITY.md)(请私下报告)。

## 许可证

VibeStick 使用 MIT License 发布。见 [LICENSE](LICENSE)。
