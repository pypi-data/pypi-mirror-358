from typing import Dict, BinaryIO, Tuple
from bitstring import Bits, BitArray
from hashlib import md5
from io import BytesIO
from math import floor
from PIL import Image
import gzip
import json


class BlueprintReader:
    img: Image

    def __init__(self, img: Image):
        self.img = img

    def read_magic_number(self) -> BitArray:
        return self.pixels_to_bitarray(0, 3)

    def read_gzip_size(self) -> int:
        return self.pixels_to_bitarray(3, 4).uintle

    def read_checksum(self) -> bytes:
        return self.pixels_to_bitarray(7, 16).bytes

    def read_compressed_data(self, gzip_size: int) -> bytes:
        return self.pixels_to_bitarray(23, gzip_size).bytes

    def pixel_to_coords(self, pixel: int) -> Tuple[int, int]:
        return (
            pixel % self.img.width,
            floor(pixel / self.img.height)
        )

    def pixels_to_bitarray(self, start: int, length: int) -> BitArray:
        ret = BitArray()

        start *= 2
        length *= 2

        for pixel in range(start, start + length, 2):
            for p in (pixel + 1, pixel):
                for band in reversed(self.img.getpixel(self.pixel_to_coords(p))):
                    ret.append(
                        Bits(uint8=band)[-1:]
                    )

        return ret


def load(fp: BinaryIO) -> Dict:
    with Image.open(fp, formats=('PNG',)) as img:
        reader = BlueprintReader(img)

        magic_number = reader.read_magic_number()

        if magic_number.bytes != b'SM\x01':
            raise ValueError('This image is not a Parkitect blueprint')

        gzip_size = reader.read_gzip_size()
        checksum = reader.read_checksum()
        compressed = reader.read_compressed_data(gzip_size)

    checksum_calculated = md5(compressed).digest()

    if checksum != checksum_calculated:
        raise ValueError(f'Checksum mismatch (stored: {checksum}; calculated: {checksum_calculated})')

    with BytesIO(gzip.decompress(compressed)) as decompressed:
        ret = {}

        for line in decompressed.readlines():
            json_line = json.loads(line.replace(b'.,', b'.0,').replace(b'.]', b'.0]').replace(b'.}', b'.0}'))
            json_line_cleaned = {
                key: value for key, value in json_line.items() if key not in ('@type', '@id')
            }

            type_ = json_line['@type']

            if type_ not in ret:
                ret[type_] = {}

            if type_ == 'BlueprintHeader':
                ret[type_] = json_line_cleaned
            else:
                id_ = json_line['@id']

                ret[type_][id_] = json_line_cleaned

        return ret


__all__ = ['load']
