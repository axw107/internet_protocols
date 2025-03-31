import argparse
import subprocess
import re
import requests


def is_public_ip(ip):

    """Проверка, является ли IP-адрес публичным."""

    private_ranges = [
        (10 ** 8, 10 ** 8 + (2 ** 24 - 1)),  # 10.0.0.0 - 10.255.255.255
        (172 ** 8 + 16 ** 4, 172 ** 8 + 31 ** 4 + (2 ** 20 - 1)),  # 172.16.0.0 - 172.31.255.255
        (192 ** 8 + 168 ** 4, 192 ** 8 + 168 ** 4 + (2 ** 16 - 1)),  # 192.168.0.0 - 192.168.255.255
        (169 ** 8 + 254 ** 4, 169 ** 8 + 254 ** 4 + (2 ** 16 - 1)),  # 169.254.0.0 - 169.254.255.255
    ]
    ip_parts = list(map(int, ip.split('.')))
    ip_num = (ip_parts[0] * 256 ** 3) + (ip_parts[1] * 256 ** 2) + (ip_parts[2] * 256) + ip_parts[3]

    for start, end in private_ranges:
        if start <= ip_num <= end:
            return False  # Это частный IP
    return True  # Это публичный IP


def get_AS_info(ip):

    """Получить информацию об автономной системе по IP-адресу."""

    url = f'http://ipinfo.io/{ip}/json'
    try:
        response = requests.get(url)
        data = response.json()
        asn = data.get("org", "Неизвестно")
        return asn
    except Exception as e:
        return f"Ошибка: {e}"


def decode_line(line, count):
    decoded_line = line.decode('CP866')
    local_ip = re.findall(r"192\.168\.\d{1,3}\.\d{1,3}", decoded_line)
    ip = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", decoded_line)
    match_miss = re.findall(r"\* {8}\* {8}\*", decoded_line)

    if local_ip:
        return f"{count} {ip[0]} local"
    elif ip:
        if is_public_ip(ip[0]):
            as_info = get_AS_info(ip[0])
            return f"{count} {ip[0]} {as_info}"
        else:
            return f"{count} {ip[0]} private"
    elif match_miss:
        return f"***"


def trace(address: str):

    """Трассировка до указанного узла."""

    route = []
    count = 1
    try:
        data = subprocess.check_output(["tracert", address]).splitlines()
        for line in data:
            dec_line = decode_line(line, count)
            if dec_line is not None:
                if "***" in dec_line:
                    break  # Останавливаемся при появлении ***
                route.append(dec_line)
                count += 1
    except subprocess.CalledProcessError as e:
        print(f"Не удалось выполнить трассировку: {e}")
    return route


def main():
    parser = argparse.ArgumentParser(description="Tracerouter")
    parser.add_argument("address", help="Доменное имя или IP адрес")
    args = parser.parse_args()
    return trace(args.address)


if __name__ == '__main__':
    for line in main():
        print(line)
