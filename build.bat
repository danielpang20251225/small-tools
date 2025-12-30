@echo off
echo 正在打包 NetFusion Lite...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
nuitka --standalone --onefile --enable-plugin=pyside6 --windows-disable-console netfusion.py
echo 打包完成！可执行文件: netfusion.exe
pause