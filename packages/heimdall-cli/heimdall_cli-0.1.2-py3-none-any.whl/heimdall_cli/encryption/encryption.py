import os, hashlib, time
from .s_box import SBOX, INV_S_BOX


class AESEncryption:
    def __init__(self, key=None):
        self.__key = self.gen_key(key)
        self.__round_keys = self.round_key(self.__key)

    def gen_key(self, base_key: str = None) -> bytes:
        """
        ## Gen Function for AES Encryption scheme
        in this function we take an optional base_key as input and then
        returns a 128 bit key in 32 bytes
        **Notice:**  if base_key is not given then it generates a new random key
        """
        if base_key is None:
            key = os.urandom(16)
        else:
            key = hashlib.md5(base_key.encode()).digest()
        return key

    def round_key(self, key: bytes) -> list[bytes]:
        """
        ## Round key function
        in this function we take a key and return 44 round key from the key
        """
        words = [key[i * 4 : i * 4 + 4] for i in range(4)]
        rc = 1
        for i in range(4, 44):
            previous = words[i - 1]
            if i % 4 == 0:
                previous = self.__g(previous, rc=rc)
                rc << 1
            new = int(words[i - 4].hex(), base=16) ^ int(previous.hex(), base=16)
            words.append(new.to_bytes(4))
        return words

    def __g(self, word: bytes, rc: int) -> bytes:
        word = word[1:] + word[:1]
        new_bytes = b""
        for byte_index in range(0, 4):
            new_bytes += self.__sub_byte(word[byte_index : byte_index + 1])
        new_bytes = (new_bytes[0] ^ rc).to_bytes() + new_bytes[1:]
        return new_bytes

    def encrypt(self, plaintext: bytes) -> bytes:
        # padding
        padding_size = 16 - ((len(plaintext)) % 16)
        plaintext = plaintext + (padding_size * padding_size.to_bytes())
        # spilt
        blocks = [plaintext[i * 16 : i * 16 + 16] for i in range(len(plaintext) // 16)]
        # encrypt blocks
        blocks = list(map(lambda block: self.encrypt_block(block), blocks))
        # join cipher blocks
        blocks = b"".join(blocks)
        return blocks
        # encrypt

    def decrypt(self, cipher: bytes) -> bytes:
        # split
        blocks = [cipher[i * 16 : i * 16 + 16] for i in range(len(cipher) // 16)]
        # decrypt
        blocks = list(map(lambda block: self.decrypt_block(block), blocks))
        # join
        blocks = b"".join(blocks)
        # unpadding
        end = blocks[-1]
        blocks = blocks[:-end]
        return blocks

    def decrypt_block(self, block: bytes) -> bytes:        
        table = [block[4 * i : 4 * i + 4] for i in range(4)]
        table = self.__add_round_key(table, self.__round_keys[40:])
        for round in range(10, 0, -1):
            table = self.__inv_shift_rows(table)
            table = self.__inv_sub_bytes(table)
            table = self.__add_round_key(
                table, self.__round_keys[round * 4 - 4 : round * 4]
            )
            if round != 1:
                table = self.__inv_mix_columns(table)
        block = b"".join(table)
        return block

    def encrypt_block(self, block: bytes) -> bytes:
        # create table

        table = [block[4 * i : 4 * i + 4] for i in range(4)]
        table = self.__add_round_key(table, self.__round_keys[:4])
        for round in range(1, 11):
            table = self.__sub_bytes(table)
            table = self.__shift_rows(table)
            if round != 10:
                table = self.__mix_columns(table)
            table = self.__add_round_key(
                table, self.__round_keys[round * 4 : round * 4 + 4]
            )
        block = b"".join(table)
        return block

    def __inv_sub_bytes(self, table: list[bytes]) -> list[bytes]:
        for column_index in range(4):
            new_col = b""
            for i in range(4):
                new_col += self.__inv_sub_byte(table[column_index][i : i + 1])
            table[column_index] = new_col
        return table

    def __sub_bytes(self, table: list[bytes]) -> list[bytes]:
        for column_index in range(4):
            new_col = b""
            for i in range(4):
                new_col += self.__sub_byte(table[column_index][i : i + 1])
            table[column_index] = new_col
        return table

    def __inv_sub_byte(self, word: bytes) -> bytes:
        word = word[0]
        # c_1, c_2 = word[0], word[1]
        # byte  = INV_S_BOX[int(c_1, base=16)][int(c_2, base=16)]
        byte = INV_S_BOX[word]
        byte = byte.to_bytes()
        return byte

    def __sub_byte(self, word: bytes) -> bytes:
        word = word.hex()
        c_1, c_2 = word[0], word[1]
        byte = SBOX[int(c_1, base=16)][int(c_2, base=16)]
        byte = byte.to_bytes()
        return byte

    def __add_round_key(self, table: list[bytes], keys: list[bytes]) -> list[bytes]:
        for i in range(4):
            r = int(table[i].hex(), base=16) ^ int(keys[i].hex(), base=16)
            table[i] = r.to_bytes(4)
        return table

    def __shift_rows(self, table: list[bytes]) -> list[bytes]:
        new_table = []
        for counter in range(4):
            string = b"".join(
                [table[(i + counter) % 4][i : i + 1] for i in range(0, 4)]
            )
            new_table.append(string)
        return new_table

    def __inv_shift_rows(self, table: list[bytes]) -> list[bytes]:
        new_table = []
        for counter in range(4):
            string = b"".join(
                [
                    table[(i + counter) % 4][j : j + 1]
                    for j, i in enumerate(range(0, -4, -1))
                ]
            )
            new_table.append(string)
        return new_table

    def __gmul(self, a, b):
        """Galois Field (256) Multiplication of two Bytes"""
        p = 0
        for _ in range(8):
            if b & 1:
                p ^= a
            high_bit = a & 0x80
            a = (a << 1) & 0xFF
            if high_bit:
                a ^= 0x1B
            b >>= 1
        return p

    def __mix_columns(self, table: list[bytes]) -> list[bytes]:
        new_table = []
        for c in table:
            col = b""
            for r in range(4):
                val: int = (
                    self.__gmul(2, c[r])
                    ^ self.__gmul(3, c[(r + 1) % 4])
                    ^ c[(r + 2) % 4]
                    ^ c[(r + 3) % 4]
                )
                col += val.to_bytes()
            new_table.append(col)
        return new_table

    def __inv_mix_columns(self, table: list[bytes]) -> list[bytes]:
        new_table = []
        for c in table:
            col = b""
            for r in range(4):
                val: int = (
                    self.__gmul(0xE, c[r])
                    ^ self.__gmul(0xB, c[(r + 1) % 4])
                    ^ self.__gmul(0xD, c[(r + 2) % 4])
                    ^ self.__gmul(0x9, c[(r + 3) % 4])
                )
                col += val.to_bytes()
            new_table.append(col)
        return new_table
