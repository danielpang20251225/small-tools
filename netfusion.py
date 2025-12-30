# -*- coding: utf-8 -*-
"""
NetFusion Lite - Windows 网络叠加工具
作者: danielpang20251225
功能: 选择有线+无线网卡，启动本地代理实现多路径带宽叠加（加速下载）
开源地址: https://github.com/danielpang20251225/NetFusion-Lite
"""

import sys
import asyncio
import socket
import threading
from functools import partial

import psutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QRadioButton, QButtonGroup, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
import aiohttp
from aiohttp import web

# 全局变量
PROXY_PORT = 8080
running_proxy = None
proxy_thread = None

class ProxyWorker(QThread):
    status_update = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, eth_ip=None, wifi_ip=None):
        super().__init__()
        self.eth_ip = eth_ip
        self.wifi_ip = wifi_ip
        self._stop = threading.Event()

    async def fetch_with_bind(self, session, url, bind_ip):
        """通过指定本地IP发起请求"""
        try:
            # 创建绑定到指定IP的连接器
            conn = aiohttp.TCPConnector(local_addr=(bind_ip, 0))
            async with session.get(url, connector=conn, timeout=30) as resp:
                return await resp.read()
        except Exception as e:
            return None

    async def handle_request(self, request):
        """处理代理请求（简化版：仅支持GET）"""
        target_url = str(request.url)
        self.status_update.emit(f"请求: {target_url[:60]}...")

        # 准备IP列表
        ips = []
        if self.eth_ip:
            ips.append(self.eth_ip)
        if self.wifi_ip:
            ips.append(self.wifi_ip)
        
        if not ips:
            return web.Response(status=500, text="未选择网卡")

        # 简单轮询分发（实际可更智能）
        bind_ip = ips[len(asyncio.all_tasks()) % len(ips)] if asyncio.all_tasks() else ips[0]

        try:
            async with aiohttp.ClientSession() as session:
                data = await self.fetch_with_bind(session, target_url, bind_ip)
                if data is not None:
                    return web.Response(body=data, status=200)
                else:
                    return web.Response(status=502, text="上游请求失败")
        except Exception as e:
            self.error_occurred.emit(f"代理错误: {str(e)}")
            return web.Response(status=500, text="代理内部错误")

    async def start_proxy(self):
        app = web.Application()
        app.router.add_route('*', '/{path:.*}', self.handle_request)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', PROXY_PORT)
        await site.start()
        self.status_update.emit(f"代理运行中: http://127.0.0.1:{PROXY_PORT}")
        try:
            while not self._stop.is_set():
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
        finally:
            await runner.cleanup()

    def run(self):
        try:
            asyncio.run(self.start_proxy())
        except Exception as e:
            self.error_occurred.emit(f"代理启动失败: {str(e)}")

    def stop(self):
        self._stop.set()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetFusion Lite - 网络叠加工具")
        self.resize(500, 400)
        self.selected_eth = None
        self.selected_wifi = None
        self.proxy_worker = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 有线网络组
        eth_group = QGroupBox("有线网络 (Ethernet)")
        eth_layout = QVBoxLayout()
        self.eth_group = QButtonGroup(self)
        self.load_networks("Ethernet", eth_layout, self.eth_group, is_eth=True)
        eth_group.setLayout(eth_layout)

        # 无线网络组
        wifi_group = QGroupBox("无线网络 (Wi-Fi)")
        wifi_layout = QVBoxLayout()
        self.wifi_group = QButtonGroup(self)
        self.wifi_group.setExclusive(True)
        self.load_networks("Wi-Fi", wifi_layout, self.wifi_group, is_eth=False)
        wifi_group.setLayout(wifi_layout)

        layout.addWidget(eth_group)
        layout.addWidget(wifi_group)

        # 状态和按钮
        self.status_label = QLabel("状态: 就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始叠加")
        self.stop_btn = QPushButton("停止叠加")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_proxy)
        self.stop_btn.clicked.connect(self.stop_proxy)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)

        # 使用说明
        guide = QLabel(
            "使用说明:\n"
            "1. 勾选一个有线和/或一个无线网卡\n"
            f"2. 点击【开始叠加】\n"
            f"3. 在浏览器中设置代理: 127.0.0.1:{PROXY_PORT}"
        )
        guide.setWordWrap(True)
        layout.addWidget(guide)

    def load_networks(self, net_type, layout, button_group, is_eth):
        """加载网卡列表"""
        if_addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        found = False
        for iface_name, iface_addrs in if_addrs.items():
            # 判断类型
            if is_eth:
                if not any(kw in iface_name.lower() for kw in ['ethernet', '以太网', 'eth', 'enp', '本地连接']):
                    continue
            else:
                if not any(kw in iface_name.lower() for kw in ['wi-fi', 'wlan', '无线', 'wlx']):
                    continue

            # 检查是否启用且有IPv4
            if not stats.get(iface_name, None)?.isup:
                continue

            ipv4 = None
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("169.254"):
                    ipv4 = addr.address
                    break

            if not ipv4:
                continue

            found = True
            radio = QRadioButton(f"{iface_name} ({ipv4})")
            radio.setProperty("iface_name", iface_name)
            radio.setProperty("ipv4", ipv4)
            button_group.addButton(radio)
            layout.addWidget(radio)

        if not found:
            label = QLabel("未检测到可用网卡")
            label.setEnabled(False)
            layout.addWidget(label)

    def start_proxy(self):
        # 获取选中项
        eth_button = self.eth_group.checkedButton()
        wifi_button = self.wifi_group.checkedButton()

        eth_ip = eth_button.property("ipv4") if eth_button else None
        wifi_ip = wifi_button.property("ipv4") if wifi_button else None

        if not eth_ip and not wifi_ip:
            QMessageBox.warning(self, "警告", "请至少选择一个有线或无线网卡！")
            return

        self.proxy_worker = ProxyWorker(eth_ip=eth_ip, wifi_ip=wifi_ip)
        self.proxy_worker.status_update.connect(self.update_status)
        self.proxy_worker.error_occurred.connect(self.show_error)
        self.proxy_worker.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.update_status("启动中...")

    def stop_proxy(self):
        if self.proxy_worker:
            self.proxy_worker.stop()
            self.proxy_worker.wait()
            self.proxy_worker = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.update_status("已停止")

    def update_status(self, msg):
        self.status_label.setText(f"状态: {msg}")

    def show_error(self, msg):
        QMessageBox.critical(self, "错误", msg)
        self.stop_proxy()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())