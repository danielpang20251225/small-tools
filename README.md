# NetFusion Lite

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue)]()
[![Release](https://img.shields.io/github/v/release/danielpang20251225/small-tools?label=latest)](https://github.com/danielpang20251225/small-tools/releases)

一款轻量级 **Windows 网络叠加工具**，通过同时使用 **有线 + 无线网络**，提升大文件下载/上传速度。

> 💡 适用于 AI 模型下载（如 ComfyUI、Stable Diffusion）、系统镜像、大型软件更新等**多连接下载场景**。

---

## ✨ 核心特性

- ✅ **自动识别**系统中的有线（Ethernet）和无线（Wi-Fi）网卡  
- ✅ **图形界面**：勾选网卡 → 点击【开始叠加】→ 立即生效  
- ✅ **随开随停**：点击【停止叠加】立即释放所有资源  
- ✅ **绿色便携**：单文件 `.exe`，无需安装、无注册表、无后台残留  
- ✅ **完全开源**：代码透明，无广告、无隐私收集  

---

## 📥 下载与使用

### ▶️ 普通用户（推荐）

1. 前往 [Releases 页面](https://github.com/danielpang20251225/small-tools/releases) 下载 `NetFusion-Lite-v1.0.exe`
2. 解压到任意文件夹
3. **双击运行 `netfusion.exe`**
4. 勾选网卡 → 点【开始叠加】
5. 在浏览器中设置 **HTTP 代理**：  
   
   ```
   地址：127.0.0.1
   端口：8080
   ```
6. 开始下载，享受叠加带宽！

> 📖 [点击查看详细代理设置指南](docs/proxy-setup-guide.md)

### ⚙️ 开发者（自行构建）

```bash
git clone https://github.com/danielpang20251225/small-tools.git
cd small-tools
pip install -r requirements.txt
pip install nuitka
build.bat
```

---

## ⚠️ 重要说明

- **支持场景**：HTTP/HTTPS 多线程下载（如浏览器、IDM、Aria2、迅雷）
- **不支持场景**：在线视频（YouTube）、游戏、远程桌面、普通网页加载（因这些依赖单 TCP 连接）
- **无需管理员权限**，但 Windows Defender 可能提示“未知发布者” → 选择“仍要运行”即可

---

## 📂 项目结构

```
small-tools/
├── netfusion.py          # 主程序源码
├── netfusion.exe         # 绿色便携版（Release 提供）
├── build.bat             # 一键打包脚本
├── requirements.txt      # 依赖列表
├── LICENSE               # 开源许可证
├── README.md
└── docs/
    └── proxy-setup-guide.md  # 代理设置教程
```

---

## 📬 反馈与贡献

- 🐞 遇到问题？[提交 Issue](https://github.com/danielpang20251225/small-tools/issues)
- 💡 有新功能建议？欢迎 Pull Request！
- ❤️ 觉得有用？给项目点个 **Star** 吧！

---
### 📥 下载便携版
- [NetFusion-Lite-v1.0.exe](https://github.com/.../releases)（绿色单文件，解压即用）
- 首次运行需安装 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

> Made with ❤️ by [danielpang20251225](https://github.com/danielpang20251225)  
> 本项目采用 [MIT 许可证](LICENSE) —— 免费用于个人及商业用途。

