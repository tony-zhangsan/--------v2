#!/usr/bin/env bash
# ============================================================
#  新大地五金官网 —— 演示环境一键部署（远端执行）
#
#  用法（在服务器上以 root 运行）：
#    bash xindadi-remote-setup.sh /root/xindadi-demo.tar.gz
#
#  做四件事：
#    1. 装 nginx（已装则跳过）
#    2. 解包站点到 /var/www/xindadi
#    3. 写 /etc/nginx/conf.d/xindadi.conf（同时监听 80 与 8080）
#    4. 放行防火墙端口并 reload
#
#  不碰域名、不配 HTTPS、不动系统已有站点（只移除发行版默认页，
#  否则 80 端口 default_server 冲突）。
# ============================================================

set -euo pipefail

PKG="${1:-}"
WEB_ROOT=/var/www/xindadi
CONF=/etc/nginx/conf.d/xindadi.conf

if [ -z "$PKG" ]; then
  echo "用法: bash $0 <站点包路径.tar.gz>" >&2
  exit 1
fi
if [ ! -f "$PKG" ]; then
  echo "找不到包: $PKG" >&2
  exit 1
fi
if [ "$(id -u)" -ne 0 ]; then
  echo "需要 root 权限，请用 sudo 或在 root 下执行" >&2
  exit 1
fi

echo "==> 0/5 系统信息"
. /etc/os-release 2>/dev/null || true
echo "    ${PRETTY_NAME:-未知系统} / $(uname -m)"

echo "==> 1/5 检查 nginx"
if command -v nginx >/dev/null 2>&1; then
  echo "    已安装: $(nginx -v 2>&1)"
else
  echo "    未安装，开始安装"
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx
  elif command -v dnf >/dev/null 2>&1; then
    dnf install -y -q nginx
  elif command -v yum >/dev/null 2>&1; then
    yum install -y -q nginx
  else
    echo "    无法识别的包管理器，请手动安装 nginx 后重试" >&2
    exit 1
  fi
  echo "    安装完成: $(nginx -v 2>&1)"
fi

echo "==> 2/5 解包站点到 $WEB_ROOT"
mkdir -p "$WEB_ROOT"
# 清掉上一版静态文件，但保留上一版备份目录
find "$WEB_ROOT" -mindepth 1 -maxdepth 1 ! -name '.prev' -exec rm -rf {} +
tar xzf "$PKG" -C "$WEB_ROOT"
# macOS 打包会带出 AppleDouble（._xxx）垃圾文件，会导致文件数翻倍、HTML 计数错乱
find "$WEB_ROOT" -name '._*' -delete
chown -R root:root "$WEB_ROOT"
echo "    HTML: $(find "$WEB_ROOT" -name '*.html' | wc -l) 个 / 文件总数: $(find "$WEB_ROOT" -type f | wc -l)"
test -f "$WEB_ROOT/index.html" || { echo "    解包后缺 index.html，中止" >&2; exit 1; }

echo "==> 3/5 清理发行版默认站点（避免 80 端口冲突）"
rm -f /etc/nginx/sites-enabled/default
if [ -f /etc/nginx/conf.d/default.conf ] && [ ! -f /etc/nginx/conf.d/default.conf.bak ]; then
  mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
  echo "    已备份 conf.d/default.conf"
fi

echo "==> 4/5 写入 $CONF"
cat > "$CONF" <<'NGINX'
# 新大地五金官网 —— 演示环境（仅 IP 访问，不绑域名）
server {
    listen       80 default_server;
    listen       [::]:80 default_server;
    listen       8080 default_server;
    listen       [::]:8080 default_server;
    server_name  _;

    root  /var/www/xindadi;
    index index.html;
    charset utf-8;

    # 隐藏点文件（.workbuddy / .git 之类不该被下载）
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # 静态资源长缓存
    location ~* \.(?:css|js|webp|jpg|jpeg|png|gif|svg|ico|woff2?|ttf|map)$ {
        expires 30d;
        add_header Cache-Control "public, max-age=2592000, immutable";
        access_log off;
        try_files $uri =404;
    }

    location / {
        try_files $uri $uri/ =404;
    }

    gzip              on;
    gzip_comp_level   6;
    gzip_min_length   1024;
    gzip_vary         on;
    gzip_types        text/plain text/css text/xml application/javascript
                      application/json image/svg+xml;

    access_log /var/log/nginx/xindadi.access.log;
    error_log  /var/log/nginx/xindadi.error.log;
}
NGINX

echo "==> 5/5 放行防火墙并重载 nginx"
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
  ufw allow 80/tcp   >/dev/null 2>&1 || true
  ufw allow 8080/tcp >/dev/null 2>&1 || true
  echo "    ufw 已放行 80 / 8080"
elif command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state >/dev/null 2>&1; then
  firewall-cmd --permanent --add-port=80/tcp   >/dev/null 2>&1 || true
  firewall-cmd --permanent --add-port=8080/tcp >/dev/null 2>&1 || true
  firewall-cmd --reload >/dev/null 2>&1 || true
  echo "    firewalld 已放行 80 / 8080"
else
  echo "    未检测到活跃的系统防火墙，跳过（注意腾讯云安全组仍需放行 80/8080）"
fi

nginx -t
if command -v systemctl >/dev/null 2>&1; then
  systemctl enable nginx  >/dev/null 2>&1 || true
  systemctl restart nginx
else
  nginx -s reload 2>/dev/null || nginx
fi

IP=$(curl -s --max-time 5 https://ifconfig.me 2>/dev/null || echo "服务器公网IP")
echo
echo "==================== 部署完成 ===================="
echo "  站点目录 : $WEB_ROOT"
echo "  访问地址 : http://$IP/"
echo "  备用端口 : http://$IP:8080/"
echo "  本地自检 : curl -I http://127.0.0.1/"
echo "  注意     : 腾讯云安全组需放行 80（或 8080）入站"
echo "=================================================="
