import argparse
import subprocess
import re
import requests
import ipaddress


def is_public_ip(ip_address):
    """
    проверяет, является ли IP-адрес публичным.
    :param ip_address: ip-адрес (строка)
    :return: True, если публичный,
             False, если частный.
             None, если недействителеный
    """

    try:
        ip = ipaddress.ip_address(ip_address)
        return not ip.is_private
    except ValueError:
        return None


def get_AS_info(ip):

    """Получить информацию об автономной системе по IP-адресу."""

    url = f'http://ip-api.com/json/{ip}'
    try:
        response = requests.get(url)
        data = response.json()
        asn = data.get("as", "не известно")
        return asn
    except Exception as e:
        return f"Ошибка: {e}"


def decode_line(line, count):
    decoded_line = line.decode('CP866')
    local_ip = re.findall(r"192\.168\.\d{1,3}\.\d{1,3}", decoded_line)
    ip = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", decoded_line)
    match_miss = re.findall(r"\* {8}\* {8}\*", decoded_line)

    if local_ip:
        return f"{count} {ip[0]} local ip"
    elif ip:
        if is_public_ip(ip[0]):
            as_info = get_AS_info(ip[0])
            return f"{count} {ip[0]} {as_info}"
        else:
            return f"{count} {ip[0]} private ip"
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
