#!/usr/bin/env bash
# Read-only runtime capability inventory. Does not install, modify files, start
# daemons, read application configuration, collect passwords or use sudo.
set -u
printf '%s\n' '=== Cari / ERPNext salt-okunur ortam kontrolü ==='
printf 'Tarih (UTC): '; date -u '+%Y-%m-%dT%H:%M:%SZ'
printf 'Sistem: '; uname -s -m
printf 'Kullanıcı UID: '; id -u
printf '\n%s\n' '=== Komutların varlığı (servis çalıştırma yetkisi anlamına gelmez) ==='
for program in python3 pip3 redis-server redis-cli docker podman mariadb mysql nginx supervisorctl systemctl wkhtmltopdf; do
  if command -v "$program" >/dev/null 2>&1; then
    printf 'VAR: %s\n' "$program"
  else
    printf 'YOK: %s\n' "$program"
  fi
done
if command -v python3 >/dev/null 2>&1; then
  printf '\n'; python3 --version 2>&1
fi
if command -v php >/dev/null 2>&1; then
  printf '\n'; php -v 2>/dev/null | head -n 1
fi
printf '\n%s\n' \
  '=== Bu kontrolün doğrulamadıkları ===' \
  'Python web trafik yönlendirmesi: TEYİT GEREKİR' \
  'Kalıcı worker/scheduler/websocket çalıştırma izni: TEYİT GEREKİR' \
  'Redis servis erişimi ve yetkisi: TEYİT GEREKİR' \
  'Desteklenen MariaDB sunucu sürümü ve DB yetkisi: TEYİT GEREKİR' \
  'TLS/proxy/backup/restore: TEYİT GEREKİR' \
  'Sonuç: Bilgi envanteri; kurulum veya teslim onayı değildir.'
