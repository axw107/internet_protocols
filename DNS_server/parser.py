from dataclasses import asdict, dataclass


@dataclass
class Header:
    """
    Класс, представляющий заголовок DNS-запроса или ответа
    """
    ID: bytes = b'\xAA\xAA'  # Идентификатор запроса
    FLAGS: bytes | dict[str, str] = b'\x01\x00' # Флаги запроса
    QDCOUNT: bytes | int = b'\x00\x01' # Количество вопросов в запросе
    ANCOUNT: bytes | int = b'\x00\x00' # Количество ответов в ответе
    NSCOUNT: bytes | int = b'\x00\x00' # Количество записей авторитетных серверов
    ARCOUNT: bytes | int = b'\x00\x00' # Количество дополнительных записей

    def __bytes__(self):
        return b''.join(self.__dict__.values())


@dataclass
class Flags:
    """
    Класс, представляющий флаги DNS-запроса или ответа
    """
    OPCODE: str
    QR: str = '1'
    AA: str = '1'
    TC: str = '0'
    RD: str = '1'
    RA: str = '1'
    Z: str = '000'
    RCODE: str = '0000'

    def get_part1(self):
        return self.QR + self.OPCODE + self.AA + self.TC + self.RD

    def get_part2(self):
        return self.RA + self.Z + self.RCODE


class Parser:
    """
    Класс, содержащий статические методы для разбора DNS-запросов и ответов
    """
    @staticmethod
    def parse_incoming_request(data: bytes) -> dict:
        """
        Разбирает входящий DNS-запрос и возвращает заголовок и вопрос.
        :param data: Данные запроса в формате байтов.
        :return: Словарь с заголовком и вопросом
        """
        header = Parser.parse_header(data)
        domain, question_type = Parser.get_question_domain(data[12:])
        parsed_type = Parser.make_type_from_number(int.from_bytes(question_type, 'big'))
        question = {
            'QNAME': domain,
            'QTYPE': parsed_type,
            'QCLASS': 'internet'
        }
        return {'header': header, 'question': question}

    @staticmethod
    def parse_header(data: bytes) -> dict:
        """
        Разбирает заголовок из данных запроса
        :param data:
        :return:
        """
        return asdict(
            Header(
                ID=data[0:2],
                FLAGS=Parser.parse_flags(data[2:4]),
                QDCOUNT=int.from_bytes(data[4:6], 'big'),
                ANCOUNT=int.from_bytes(data[6:8], 'big'),
                NSCOUNT=int.from_bytes(data[8:10], 'big'),
                ARCOUNT=int.from_bytes(data[10:12], 'big'),
            )
        )

    @staticmethod
    def parse_flags(flags: bytes) -> dict:
        """
        Разбирает флаги из данных запроса
        :param flags:
        :return:
        """
        first_byte = flags[:1]
        second_byte = flags[1:2]

        return asdict(
            Flags(
                QR=Parser.get_bit_in_byte(first_byte, 0),
                OPCODE=''.join([Parser.get_bit_in_byte(first_byte, bit) for bit in range(1, 5)]),
                AA=Parser.get_bit_in_byte(first_byte, 5),
                TC=Parser.get_bit_in_byte(first_byte, 6),
                RD=Parser.get_bit_in_byte(first_byte, 7),
                RA=Parser.get_bit_in_byte(second_byte, 8),
                Z='0000',
                RCODE=''.join([Parser.get_bit_in_byte(first_byte, bit) for bit in range(4, 8)]),
            )
        )

    @staticmethod
    def get_question_domain(data: bytes) -> tuple[str, bytes]:
        """
        Извлекает домен и тип вопроса из данных запроса
        :param data:
        :return:
        """
        domain = ''
        byte = 0

        while data[byte] != 0:
            length = data[byte]
            domain += ''.join([chr(i) for i in data[byte + 1: byte + length + 1]]) + '.'
            byte += length + 1

        question_type = data[byte + 1: byte + 3]
        return domain, question_type

    @staticmethod
    def get_bit_in_byte(byte: bytes, position: int) -> str:
        return str(ord(byte) & (1 << position))

    @staticmethod
    def make_type_from_number(current_type: int) -> str:
        if current_type == 1:
            return 'a'
        elif current_type == 2:
            return 'ns'
