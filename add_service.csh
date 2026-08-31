# 1. 重新加载 systemd 守护进程，使其读取新的 service 文件
sudo systemctl daemon-reload

# 2. 启用开机自启
sudo systemctl enable snps-lmgrd.service

# 3. 立即启动该服务（如果您之前手动启动的 lmgrd 还在运行，请先手动 kill 掉，否则会报端口占用错误）
sudo systemctl start snps-lmgrd.service

# 查看服务状态
sudo systemctl status snps-lmgrd.service

if ($?SCL_HOME) then
    lmstat -a -c $SCL_HOME/admin/license/synopsys.lic | head -n 14
endif
