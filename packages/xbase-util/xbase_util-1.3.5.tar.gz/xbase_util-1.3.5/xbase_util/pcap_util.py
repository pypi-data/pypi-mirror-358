import copy
import gzip
import math
import os
import re
import struct
import time
import traceback
import zlib
from functools import cmp_to_key
from ipaddress import IPv6Address

from Crypto.Cipher import AES
from scapy.layers.inet import TCP, IP
from scapy.packet import Raw
from zstandard import ZstdDecompressor

from xbase_util.common_util import parse_chunked_body, filter_visible_chars
from xbase_util.xbase_constant import pattern_chuncked, pattern_gzip


def fix_pos(pos, packetPosEncoding):
    if pos is None or len(pos) == 0:
        return
    if packetPosEncoding == "gap0":
        last = 0
        lastgap = 0
        for i, pos_item in enumerate(pos):
            if pos[i] < 0:
                last = 0
            else:
                if pos[i] == 0:
                    pos[i] = last + lastgap
                else:
                    lastgap = pos[i]
                    pos[i] += last
                last = pos[i]


def group_numbers(nums):
    result = []
    for num in nums:
        if num < 0:
            result.append([num])
        elif result:
            result[-1].append(num)
    return result


def decompress_streaming(compressed_data, session_id):
    try:
        decompressor = ZstdDecompressor()
        with decompressor.stream_reader(compressed_data) as reader:
            decompressed_data = reader.read()
            return decompressed_data
    except Exception as e:
        print(f"解码错误：{e}  {session_id}")
        return bytearray()


def readUInt32BE(buffer, offset):
    return struct.unpack('>I', buffer[offset:offset + 4])[0]


def readUInt32LE(buffer, offset):
    return struct.unpack('<I', buffer[offset:offset + 4])[0]


def writeUInt32BE(buffer, pos, value):
    struct.pack_into('>I', buffer, pos, value)
    return buffer


def readUInt16BE(buffer, offset):
    return struct.unpack('>H', buffer[offset:offset + 2])[0]


def readUInt16LE(buffer, offset):
    return struct.unpack('<H', buffer[offset:offset + 2])[0]


def tcp(buffer, obj, pos):
    obj['tcp'] = {
        '_pos': pos,
        'length': len(buffer),
        'sport': readUInt16BE(buffer, 0),
        'dport': readUInt16BE(buffer, 2),
        'seq': readUInt32BE(buffer, 4),
        'ack': readUInt32BE(buffer, 8),
        'off': ((buffer[12] >> 4) & 0xf),
        'res1': (buffer[12] & 0xf),
        'flags': buffer[13],
        'res2': (buffer[13] >> 6 & 0x3),
        'urgflag': (buffer[13] >> 5 & 0x1),
        'ackflag': (buffer[13] >> 4 & 0x1),
        'pshflag': (buffer[13] >> 3 & 0x1),
        'rstflag': (buffer[13] >> 2 & 0x1),
        'synflag': (buffer[13] >> 1 & 0x1),
        'finflag': (buffer[13] >> 0 & 0x1),
        'win': readUInt16BE(buffer, 14),
        'sum': readUInt16BE(buffer, 16),
        'urp': readUInt16BE(buffer, 18)
    }
    if 4 * obj['tcp']['off'] > len(buffer):
        obj['tcp']['data'] = b''
    else:
        obj['tcp']['data'] = buffer[4 * obj['tcp']['off']:]


def ip6(buffer, obj, pos):
    obj['ip'] = {
        'length': len(buffer),
        'v': ((buffer[0] >> 4) & 0xf),
        'tc': ((buffer[0] & 0xf) << 4) | ((buffer[1] >> 4) & 0xf),
        'flow': ((buffer[1] & 0xf) << 16) | (buffer[2] << 8) | buffer[3],
        'len': readUInt16BE(buffer, 4),
        'p': buffer[6],
        'hopLimt': buffer[7],
        # todo:need test
        'addr1': str(IPv6Address(buffer[8:24])),
        'addr2': str(IPv6Address(buffer[8:24]))
    }
    offset = 40
    buffer_data = buffer[offset:offset + obj['ip']['len']]
    while offset < len(buffer):
        p = obj['ip']['p']
        if p == 0 or p == 60 or p == 43:
            obj['ip']['p'] = buffer[offset]
            offset += ((buffer[offset + 1] + 1) << 3)
        elif p == 1 or p == 58:
            icmp(buffer_data, obj, pos + offset)
        elif p == 4:
            ip4(buffer_data, obj, pos + offset)
            break
        elif p == 6:
            tcp(buffer_data, obj, pos + offset)
            break
        elif p == 17:
            udp(buffer_data, obj, pos + offset)
            break
        elif p == 47:
            gre(buffer_data, obj, pos + offset)
            break
        elif p == 50:
            esp(buffer_data, obj, pos + offset)
            break
        elif p == 132:
            sctp(buffer_data, obj, pos + offset)
            break
        else:
            obj['ip']['data'] = buffer_data


def udp(buffer, obj, pos):
    obj['udp'] = {
        '_pos': pos,
        'length': len(buffer),
        'sport': readUInt16BE(buffer, 0),
        'dport': readUInt16BE(buffer, 2),
        'ulen': readUInt16BE(buffer, 4),
        'sum': readUInt16BE(buffer, 6),
        'data': buffer[8:]
    }
    data = obj['udp']['data']
    if (obj['udp']['dport'] == 4789) and (len(data) > 8) and ((data[0] & 0x77) == 0) and ((data[1] & 0xb7) == 0):
        ether(buffer[16:], obj, pos + 16)
    if (obj['udp']['dport'] == 4790) and (len(data) > 8) and ((data[0] & 0xf0) == 0) and ((data[1] & 0xff) == 0):
        if data[3] == 1:
            ip4(buffer[16:], obj, pos + 16)
        elif data[3] == 2:
            ip6(buffer[16:], obj, pos + 16)
        elif data[3] == 3:
            ether(buffer[16:], obj, pos + 16)
    if (obj['udp']['dport'] == 6081) and (len(data) > 8) and ((data[0] & 0xc0) == 0) and ((data[1] & 0x3f) == 0):
        optlen = data[0] & 0x3f
        protocol = (data[2] << 8) | data[3]
        offset = 8 + optlen * 4
        if 8 + offset < len(buffer):
            ether_type_run(protocol, buffer[8 + offset:], obj, pos + 8 + offset)
    if (obj['udp']['dport'] == 2152) and (len(data) > 8) and ((data[0] & 0xf0) == 0x30) and (data[1] == 0xff):
        offset = 8
        next_offset = 0
        if data[0] & 0x7:
            offset += 3
            next_offset = data[offset]
            offset = offset + 1
        while next_offset != 0:
            ext_len = data[offset]
            offset = offset + 1
            offset += ext_len * 4 - 2
            next_offset = data[offset]
            offset = offset + 1
        if (data[offset] & 0xf0) == 0x60:
            ip6(data[offset:], obj, pos + offset)
        else:
            ip4(data[offset:], obj, pos + offset)


def esp(buffer, obj, pos):
    obj['esp'] = {
        '_pos': pos,
        'length': len(buffer),
        'data': buffer,
    }


def gre(buffer, obj, pos):
    flags_version = readUInt16BE(buffer, 0)
    obj['gre'] = {
        'flags_version': flags_version,
        'type': readUInt16BE(buffer, 2)
    }
    b_pos = 4

    if flags_version & (0x8000 | 0x4000):
        b_pos += 4
    if flags_version & 0x2000:
        b_pos += 4
    if flags_version & 0x1000:
        b_pos += 4
    if flags_version & 0x4000:
        while True:
            b_pos += 3
            length = readUInt16BE(buffer, b_pos)
            b_pos = b_pos + 1
            if length == 0:
                break
            b_pos += length
    if flags_version & 0x0080:
        b_pos += 4
    if ether_type_run(obj['gre']['type'], buffer[b_pos:], obj, pos + b_pos):
        return
    if obj['gre']['type'] == 0x88be:
        ether(buffer[b_pos + 8:], obj, pos + b_pos + 8)


def sctp(buffer, obj, pos):
    obj['sctp'] = {
        '_pos': pos,
        'length': len(buffer),
        'sport': readUInt16BE(buffer, 0),
        'dport': readUInt16BE(buffer, 2),
        'data': buffer[12:]
    }


def inet_ntoa(num):
    return f'{(num >> 24 & 0xff)}.{(num >> 16 & 0xff)}.{(num >> 8 & 0xff)}.{(num & 0xff)}'


def icmp(buffer, obj, pos):
    obj['icmp'] = {
        '_pos': pos,
        'length': len(buffer),
        'type': buffer[0],
        'code': buffer[1],
        'sum': readUInt16BE(buffer, 2),
        'data': buffer
    }


def ip4(buffer, obj, pos):
    obj['ip'] = {
        'length': len(buffer),
        'hl': (buffer[0] & 0xf),
        'v': ((buffer[0] >> 4) & 0xf),
        'tos': buffer[1],
        'len': readUInt16BE(buffer, 2),
        'id': readUInt16BE(buffer, 4),
        'off': readUInt16BE(buffer, 6),
        'ttl': buffer[8],
        'p': buffer[9],
        'sum': readUInt16BE(buffer, 10),
        'addr1': inet_ntoa(readUInt32BE(buffer, 12)),
        'addr2': inet_ntoa(readUInt32BE(buffer, 16))
    }
    p = obj['ip']['p']
    buffer_data = buffer[obj['ip']['hl'] * 4:obj['ip']['len']]
    position = pos + obj['ip']['hl'] * 4
    if p == 1:
        icmp(buffer_data, obj, position)
    elif p == 6:
        tcp(buffer_data, obj, position)
    elif p == 17:  # line 664
        udp(buffer_data, obj, position)
    elif p == 41:
        ip6(buffer_data, obj, position)
    elif p == 50:
        esp(buffer_data, obj, position)
    elif p == 47:
        gre(buffer_data, obj, position)
    elif p == 132:
        sctp(buffer_data, obj, position)
    else:
        obj['ip']['data'] = buffer_data


def pppoe(buffer, obj, pos):
    obj['pppoe'] = {
        'len': readUInt16BE(buffer, 4) - 2,
        'type': readUInt16BE(buffer, 6)
    }
    if obj['pppoe']['type'] == 0x21:
        ip4(buffer[8:8 + obj['pppoe']['len']], obj, pos + 8)
    elif obj['pppoe']['type'] == 0x57:
        ip6(buffer[8:8 + obj['pppoe']['len']], obj, pos + 8)


def mpls(buffer, obj, pos):
    offset = 0
    while offset + 5 < len(buffer):
        S = buffer[offset + 2] & 0x1
        offset += 4
        if S == 1:
            unit = buffer[offset] >> 4
            if unit == 4:
                ip4(buffer[offset:], obj, pos + offset)
                break
            elif unit == 6:
                ip6(buffer[offset:], obj, pos + offset)
                break
            else:
                print(f"Unknown mpls.type:{buffer[offset] >> 4, obj}  {offset}")
                break


def framerelay(buffer, obj, pos):
    if buffer[2] == 0x03 or buffer[3] == 0xcc:
        ip4(buffer.slice(4), obj, pos + 4)
    elif buffer[2] == 0x08 or buffer[3] == 0x00:
        ip4(buffer.slice(4), obj, pos + 4)
    elif buffer[2] == 0x86 or buffer[3] == 0xdd:
        ip6(buffer.slice(4), obj, pos + 4)


def ppp(buffer, obj, pos):
    net_type = readUInt16BE(buffer, 2)
    obj['pppoe'] = {
        'type': net_type
    }
    if net_type == 0x21:
        ip4(buffer[4:], obj, pos + 4)
    elif net_type == 0x57:
        ip6(buffer[4:], obj, pos + 4)


def ether_type_run(net_type, buffer, obj, pos):
    if net_type == 0x0800:
        ip4(buffer, obj, pos)
    elif net_type == 0x0806:  # arp
        if 'ether' not in obj:
            obj['ether'] = {'data': buffer}
    elif net_type == 0x86dd:
        ip6(buffer, obj, pos)
    elif net_type == 0x8864:
        pppoe(buffer, obj, pos)
    elif net_type == 0x8847:
        mpls(buffer, obj, pos)
    elif net_type == 0x6558:
        ether(buffer, obj, pos)
    elif net_type == 0x6559:
        framerelay(buffer, obj, pos)
    elif net_type == 0x880b:
        ppp(buffer, obj, pos)
    else:
        return False
    return True


def ethertype(buffer, obj, pos):
    obj['ether']['type'] = readUInt16BE(buffer, 0)
    if ether_type_run(obj['ether']['type'], buffer[2:], obj, pos + 2):
        return
    if obj['ether']['type'] == 0x8100 or obj['ether']['type'] == 0x88a8:
        ethertype(buffer[4:], obj, pos + 4)
    else:
        obj['ether']['data'] = buffer[2:]


def ether(buffer, obj, pos):
    obj['ether'] = {
        'length': len(buffer),
        'addr1': buffer[:6].hex(),
        'addr2': buffer[6:12].hex(),
    }
    ethertype(buffer[12:], obj, pos + 12)


def radiotap(buffer, obj, pos):
    length = buffer[2] + 24 + 6
    if ether_type_run(readUInt16BE(buffer, length), buffer[length + 2:], obj, pos + length + 2):
        return


def nflog(buffer, obj, pos):
    offset = 4
    while offset + 4 < len(buffer):
        length = readUInt16LE(buffer, offset)
        if buffer[offset + 3] == 0 and buffer[offset + 2] == 9:
            if buffer[0] == 2:
                ip4(buffer[offset + 4:], obj, pos + offset + 4)
            else:
                ip6(buffer[offset + 4:], obj, pos + offset + 4)
        else:
            offset += (length + 3) & 0xfffc
    length = buffer[2] + 24
    if buffer[length + 6] == 0x08 and buffer[length + 7] == 0x00:
        ip4(buffer[length + 8:], obj, pos + length + 8)
    elif buffer[length + 6] == 0x86 and buffer[length + 7] == 0xdd:
        ip6(buffer[length + 8:], obj, pos + length + 8)


def decode_obj(buffer, bigEndian, linkType, nanosecond):
    if bigEndian is False:
        pcap = {
            'ts_sec': readUInt32BE(buffer, 0),
            'ts_usec': readUInt32BE(buffer, 4),
            'incl_len': readUInt32BE(buffer, 8),
            'orig_len': readUInt32BE(buffer, 12)
        }
    else:
        pcap = {
            'ts_sec': readUInt32LE(buffer, 0),
            'ts_usec': readUInt32LE(buffer, 4),
            'incl_len': readUInt32LE(buffer, 8),
            'orig_len': readUInt32LE(buffer, 12)
        }
    if nanosecond is False:
        pcap['ts_usec'] = math.floor(pcap['ts_usec'] / 1000)
    obj = {'pcap': pcap}

    buffer_16 = buffer[16:obj['pcap']['incl_len'] + 16]
    if linkType == 0:
        if buffer[16] == 30:
            ip6(buffer[20:obj['pcap']['incl_len'] + 16], obj, 20)
        else:
            ip4(buffer[20:obj['pcap']['incl_len'] + 16], obj, 20)
    elif linkType == 1:
        ether(buffer_16, obj, 16)
    elif linkType == 12 or linkType == 101:
        if (buffer[16] & 0xF0) == 0x60:
            ip6(buffer_16, obj, 16)
        else:
            ip4(buffer_16, obj, 16)
    elif linkType == 107:
        framerelay(buffer_16, obj, 16)
    elif linkType == 113:
        obj['ether'] = {}
        ethertype(buffer[30:obj['pcap']['incl_len'] + 16], obj, 30)
    elif linkType == 127:
        radiotap(buffer_16, obj, 16)
    elif linkType == 228:
        ip4(buffer_16, obj, 16)
    elif linkType == 239:
        nflog(buffer_16, obj, 16)
    elif linkType == 276:
        ip4(buffer[36:obj['pcap']['incl_len'] + 20], obj, 36)
    else:
        print(f"Unsupported pcap file:{linkType}")
    return obj


def read_header(param_map, session_id):
    shortHeader = None
    headBuffer = os.read(param_map['fd'], 64)
    if param_map['encoding'] == 'aes-256-ctr':
        if 'iv' in param_map:
            param_map['iv'][12:16] = struct.pack('>I', 0)
            headBuffer = bytearray(
                AES.new(param_map['encKey'], AES.MODE_CTR, nonce=param_map['iv']).decrypt(bytes(headBuffer)))
        else:
            print("读取头部信息失败，iv向量为空")
    elif param_map['encoding'] == 'xor-2048':
        for i in range(len(headBuffer)):
            headBuffer[i] ^= param_map['encKey'][i % 256]
    if param_map['uncompressedBits']:
        if param_map['compression'] == 'gzip':
            headBuffer = zlib.decompress(bytes(headBuffer), zlib.MAX_WBITS | 16)
        elif param_map['compression'] == 'zstd':
            headBuffer = decompress_streaming(headBuffer, session_id)
    headBuffer = headBuffer[:24]
    magic = struct.unpack('<I', headBuffer[:4])[0]
    bigEndian = (magic == 0xd4c3b2a1 or magic == 0x4d3cb2a1)
    nanosecond = (magic == 0xa1b23c4d or magic == 0x4d3cb2a1)
    if not bigEndian and magic not in {0xa1b2c3d4, 0xa1b23c4d, 0xa1b2c3d5}:
        raise ValueError("Corrupt PCAP header")
    if magic == 0xa1b2c3d5:
        shortHeader = readUInt32LE(headBuffer, 8)
        headBuffer[0] = 0xd4  # Reset header to normal
    if bigEndian:
        linkType = readUInt32BE(headBuffer, 20)
    else:
        linkType = readUInt32LE(headBuffer, 20)
    return headBuffer, shortHeader, bigEndian, linkType, nanosecond


def create_decipher(pos, param_map):
    writeUInt32BE(param_map['iv'], pos, 12)
    return AES.new(param_map['encKey'], AES.MODE_CTR, nonce=param_map['iv'])


def read_packet_internal(pos_arg, hp_len_arg, param_map, session_id):
    pos = pos_arg
    hp_len = hp_len_arg
    if hp_len == -1:
        if param_map['compression'] == "zstd":
            hp_len = param_map['uncompressedBitsSize']
        else:
            hp_len = 2048
    inside_offset = 0
    if param_map['uncompressedBits']:
        inside_offset = pos & param_map['uncompressedBitsSize'] - 1
        pos = math.floor(pos / param_map['uncompressedBitsSize'])
    pos_offset = 0
    if param_map['encoding'] == 'aes-256-ctr':
        pos_offset = pos % 16
        pos = pos - pos_offset
    elif param_map['encoding'] == 'xor-2048':
        pos_offset = pos % 256
        pos = pos - pos_offset

    hp_len = 256 * math.ceil((hp_len + inside_offset + pos_offset) / 256)
    buffer = bytearray(hp_len)
    os.lseek(param_map['fd'], pos, os.SEEK_SET)
    read_buffer = os.read(param_map['fd'], len(buffer))
    if len(read_buffer) - pos_offset < 16:
        return None
    if param_map['encoding'] == 'aes-256-ctr':
        decipher = create_decipher(pos // 16, param_map)
        read_buffer = bytearray(decipher.decrypt(read_buffer))[pos_offset:]
    elif param_map['encoding'] == 'xor-2048':
        read_buffer = bytearray(b ^ param_map['encKey'][i % 256] for i, b in enumerate(read_buffer))[pos_offset:]
    if param_map['uncompressedBits']:
        try:
            if param_map['compression'] == 'gzip':
                read_buffer = zlib.decompress(read_buffer, zlib.MAX_WBITS | 16)
            elif param_map['compression'] == 'zstd':
                read_buffer = decompress_streaming(read_buffer, session_id)
        except Exception as e:
            print(f"PCAP uncompress issue:  {pos} {len(buffer)} {read_buffer} {e}")
            return None
    if inside_offset:
        read_buffer = read_buffer[inside_offset:]
    header_len = 16 if param_map['shortHeader'] is None else 6
    if len(read_buffer) < header_len:
        if hp_len_arg == -1 and param_map['compression'] == 'zstd':
            return read_packet_internal(pos_arg, param_map['uncompressedBitsSize'] * 2, param_map, session_id)
        print(f"Not enough data {len(read_buffer)} for header {header_len}")
        return None
    packet_len = struct.unpack('>I' if param_map['bigEndian'] else '<I', read_buffer[8:12])[
        0] if param_map['shortHeader'] is None else \
        struct.unpack('>H' if param_map['bigEndian'] else '<H', read_buffer[:2])[0]
    if packet_len < 0 or packet_len > 0xffff:
        return None
    if header_len + packet_len <= len(read_buffer):
        if param_map['shortHeader'] is not None:
            t = struct.unpack('<I', read_buffer[2:6])[0]
            sec = (t >> 20) + param_map['shortHeader']
            usec = t & 0xfffff
            new_buffer = bytearray(16 + packet_len)
            struct.pack_into('<I', new_buffer, 0, sec)
            struct.pack_into('<I', new_buffer, 4, usec)
            struct.pack_into('<I', new_buffer, 8, packet_len)
            struct.pack_into('<I', new_buffer, 12, packet_len)
            new_buffer[16:] = read_buffer[6:packet_len + 6]
            return new_buffer
        return read_buffer[:header_len + packet_len]

    if hp_len_arg != -1:
        return None

    return read_packet_internal(pos_arg, 16 + packet_len, param_map, session_id)


def read_packet(pos, param_map, session_id):
    if 'fd' not in param_map or not param_map['fd']:
        time.sleep(0.01)
        return read_packet(pos, param_map['fd'], session_id)
    return read_packet_internal(pos, -1, param_map, session_id)


def get_file_and_read_pos(session_id, file, pos_list):
    filename = file['name']
    if not os.path.isfile(filename):
        print(f"文件不存在:{filename}")
        return None,None
    encoding = file.get('encoding', 'normal')
    encKey = None
    iv = None
    compression = None
    if 'dek' in file:
        dek = bytes.fromhex(file['dek'])
        encKey = AES.new(file['kek'].encode(), AES.MODE_CBC).decrypt(dek)

    if 'uncompressedBits' in file:
        uncompressedBits = file['uncompressedBits']
        uncompressedBitsSize = 2 ** uncompressedBits
        compression = 'gzip'
    else:
        uncompressedBits = None
        uncompressedBitsSize = 0
    if 'compression' in file:
        compression = file['compression']

    if 'iv' in file:
        iv_ = bytes.fromhex(file['iv'])
        iv = bytearray(16)
        iv[:len(iv_)] = iv_
    fd = os.open(filename, os.O_RDONLY)
    param_map = {
        "fd": fd,
        "encoding": encoding,
        "iv": iv,
        "encKey": encKey,
        "uncompressedBits": uncompressedBits,
        "compression": compression,
        "uncompressedBitsSize": uncompressedBitsSize
    }
    res = bytearray()
    headBuffer, shortHeader, bigEndian, linkType, nanosecond = read_header(param_map, session_id)
    res.extend(headBuffer)
    param_map['shortHeader'] = shortHeader
    param_map['bigEndian'] = bigEndian
    # _________________________________
    byte_array = bytearray(0xfffe)
    next_packet = 0
    b_offset = 0
    packets = {}
    packet_objs = []
    i = 0
    for pos in pos_list:
        packet_bytes = read_packet(pos, param_map, session_id)
        obj = decode_obj(packet_bytes, bigEndian, linkType, nanosecond, )
        packet_objs.append(copy.deepcopy(obj))
        if not packet_bytes:
            continue
        packets[i] = packet_bytes
        while next_packet in packets:
            buffer = packets[next_packet]
            del packets[next_packet]
            next_packet = next_packet + 1
            if b_offset + len(buffer) > len(byte_array):
                res.extend(byte_array[:b_offset])
                b_offset = 0
                byte_array = bytearray(0xfffe)
            byte_array[b_offset:b_offset + len(buffer)] = buffer
            b_offset += len(buffer)
        i = i + 1
    os.close(fd)
    res.extend(byte_array[:b_offset])
    return res, packet_objs


def process_session_id_disk_simple(id, node, packet_pos, esdb, pcap_path_prefix):
    packetPos = packet_pos
    file = esdb.get_file_by_file_id(node=node, num=abs(packetPos[0]),
                                    prefix=None if pcap_path_prefix == "origin" else pcap_path_prefix)
    if file is None:
        return None, None
    fix_pos(packetPos, file['packetPosEncoding'])
    pos_list = group_numbers(packetPos)[0]
    pos_list.pop(0)
    return get_file_and_read_pos(id, file, pos_list)


def normalize_spaces_and_newlines(text):
    text = re.sub(r' +', ' ', text)
    # 将连续多个 \n 替换为一个 \n
    text = re.sub(r'\n{2,}', '\n', text)
    return text


def parse_body(data, skey='', session_id='none'):
    if data.find(b"\r\n\r\n") != -1:
        res = data.split(b"\r\n\r\n", 1)
        header = res[0]
        body = res[1]
    else:
        header = data
        body = b''
    chunked_pattern = pattern_chuncked.search(header)
    gzip_pattern = pattern_gzip.search(header)
    need_unzip = gzip_pattern and b'gzip' in gzip_pattern.group()
    is_err = False
    if chunked_pattern and b'chunked' in chunked_pattern.group():
        body, is_err = parse_chunked_body(body, need_un_gzip=need_unzip, session_id=session_id, skey=skey)
    elif need_unzip:
        try:
            body = gzip.decompress(body)
        except Exception as e:
            traceback.print_exc()
            print(f"解压失败:{skey} {session_id}")
            body = b''
            is_err = True
    return filter_visible_chars(header), filter_visible_chars(body), body, is_err


def reassemble_session_pcap(reassemble_tcp_res, skey, session_id='none'):
    my_map = None
    packet_list = []
    for packet in reassemble_tcp_res:
        header, body,body_bytes, is_err = parse_body(packet['data'], skey=skey, session_id=session_id)
        if packet['key'] == skey:
            if my_map is not None:
                packet_list.append(copy.deepcopy(my_map))
            my_map = {
                'key': packet['key'],
                'req_header': header,
                'req_body': body,
                'req_body_bytes': body_bytes,

                'req_time': packet['ts'],
                'req_size': len(packet['data']),
                'req_body_parse_err': is_err,
                'res_header': '',
                'res_body': '',
                'res_body_bytes': b'',
                'res_body_parse_err': False,
                'res_time': 0,
                'res_size': 0,
            }
        else:
            if my_map is not None:
                my_map['res_header'] = header
                my_map['res_body'] = body
                my_map['res_body_bytes'] = body_bytes
                my_map['res_time'] = packet['ts']
                my_map['res_size'] = len(packet['data'])
                my_map['res_body_parse_err'] = is_err
                packet_list.append(copy.deepcopy(my_map))
                my_map = None
    if my_map is not None:
        packet_list.append(copy.deepcopy(my_map))
    return packet_list


def reassemble_tcp_pcap(p):
    packets = [{'pkt': item} for item in p if TCP in item and Raw in item and IP in item]
    packets2 = []
    info = {}
    keys = []
    for index, packet in enumerate(packets):
        data = packet['pkt'][Raw].load
        flags = packet['pkt'][TCP].flags
        seq = packet['pkt'][TCP].seq
        if len(data) == 0 or 'R' in flags or 'S' in flags:
            continue
        key = f"{packet['pkt'][IP].src}:{packet['pkt'][IP].sport}"
        if key not in info.keys():
            info[key] = {
                "min": seq,
                "max": seq,
                "wrapseq": False,
                "wrapack": False,
            }
            keys.append(key)
        elif info[key]["min"] > seq:
            info[key]['min'] = seq
        elif info[key]["max"] < seq:
            info[key]['max'] = seq
        packets2.append(packet)
    if len(keys) == 1:
        key = f"{packets2[0]['pkt'][IP].dst}:{packets2[0]['pkt'][IP].dport}"
        ack = packets2[0]['pkt'][TCP].ack
        info[key] = {
            "min": ack,
            "max": ack,
            "wrapseq": False,
            "wrapack": False,
        }
        keys.append(key)
    if len(packets2) == 0:
        return []
    needwrap = False
    if info[keys[0]] and info[keys[0]]['max'] - info[keys[0]]['min'] > 0x7fffffff:
        info[keys[0]]['wrapseq'] = True
        info[keys[0]]['wrapack'] = True
        needwrap = True
    if info[keys[1]] and info[keys[1]]['max'] - info[keys[1]]['min'] > 0x7fffffff:
        info[keys[1]]['wrapseq'] = True
        info[keys[0]]['wrapack'] = True
        needwrap = True
    if needwrap:
        for packet in packets2:
            key = f"{packet['pkt'][IP].src}:{packet['pkt'][IP].sport}"
            if info[key]['wrapseq'] and packet['pkt'][TCP].seq < 0x7fffffff:
                packet['pkt'][TCP].seq += 0xffffffff
            if info[key]['wrapack'] and packet['pkt'][TCP].ack < 0x7fffffff:
                packet['pkt'][TCP].ack += 0xffffffff
    clientKey = f"{packets2[0]['pkt'][IP].src}:{packets2[0]['pkt'][IP].sport}"

    def compare_packets(a, b):
        a_seq = a['pkt'][TCP].seq
        b_seq = b['pkt'][TCP].seq
        a_ack = a['pkt'][TCP].ack
        b_ack = b['pkt'][TCP].ack
        a_data = a['pkt'][Raw].load
        b_data = b['pkt'][Raw].load
        a_ip = a['pkt'][IP].src
        a_port = a['pkt'][TCP].sport
        b_port = b['pkt'][TCP].sport
        b_ip = b['pkt'][IP].src
        if a_ip == b_ip and a_port == b_port:
            return a_seq - b_seq
        if clientKey == f"{a_ip}:{a_port}":
            return (a_seq + len(a_data) - 1) - b_ack
        return a_ack - (b_seq + len(b_data) - 1)

    packets2.sort(key=cmp_to_key(compare_packets))
    clientSeq = 0
    hostSeq = 0
    previous = 0
    results = []
    for i, item in enumerate(packets2):
        sip = item['pkt'][IP].src
        sport = item['pkt'][IP].sport
        seq = item['pkt'][TCP].seq
        data = item['pkt'][Raw].load
        pkey = f"{sip}:{sport}"
        seq_datalen = seq + len(data)
        if pkey == clientKey:
            if clientSeq >= seq_datalen:
                continue
            clientSeq = seq_datalen
        else:
            if hostSeq >= seq_datalen:
                continue
            hostSeq = seq_datalen
        if len(results) == 0 or pkey != results[len(results) - 1]['key']:
            previous = seq
            results.append({
                'key': pkey,
                'data': copy.deepcopy(data),
                'ts': float(item['pkt'].time),
                'pkt': item['pkt'],
            })
        elif seq - previous > 0xffff:
            results.append(
                {'key': '',
                 'data': b'',
                 'ts': float(item['pkt'].time),
                 'pkt': item['pkt'],
                 })
            previous = seq
            results.append({
                'key': pkey,
                'data': copy.deepcopy(data),
                'ts': float(item['pkt'].time),
                'pkt': item['pkt'],
            })
        else:
            previous = seq
            results[-1]['data'] += data
    return results


def reassemble_tcp(packets, skey, num_packets=1000):
    packets2 = []
    info = {}
    keys = []
    for index, packet in enumerate(packets):
        data = packet['tcp']['data']
        rstflag = packet['tcp']['rstflag']
        synflag = packet['tcp']['synflag']
        seq = packet['tcp']['seq']
        if len(data) == 0 or rstflag == 1 or synflag == 1:
            continue
        key = f"{packet['ip']['addr1']}:{packet['tcp']['sport']}"
        print(key)
        if key not in info.keys():
            info[key] = {
                "min": seq,
                "max": seq,
                "wrapseq": False,
                "wrapack": False,
            }
            keys.append(key)
        elif info[key]["min"] > seq:
            info[key]['min'] = seq
        elif info[key]["max"] < seq:
            info[key]['max'] = seq
        packets2.append(packet)
    if len(keys) == 1:
        key = f"{packets[0]['ip']['addr2']}:{packets[0]['tcp']['dport']}"
        info[key] = {
            "min": packets[0]['tcp']['ack'],
            "max": packets[0]['tcp']['ack'],
            "wrapseq": False,
            "wrapack": False,
        }
        keys.append(key)
    packets = packets2
    if len(packets) == 0:
        return []
    needwrap = False
    if info[keys[0]] and info[keys[0]]['max'] - info[keys[0]]['min'] > 0x7fffffff:
        info[keys[0]]['wrapseq'] = True
        info[keys[0]]['wrapack'] = True
        needwrap = True
    if info[keys[1]] and info[keys[1]]['max'] - info[keys[1]]['min'] > 0x7fffffff:
        info[keys[1]]['wrapseq'] = True
        info[keys[0]]['wrapack'] = True
        needwrap = True
    if needwrap:
        for packet in packets:
            key = f"{packet['ip']['addr1']}:{packet['tcp']['sport']}"
            if info[key]['wrapseq'] and packet['tcp']['seq'] < 0x7fffffff:
                packet['tcp']['seq'] += 0xffffffff
            if info[key]['wrapack'] and packet['tcp']['ack'] < 0x7fffffff:
                packet['tcp']['ack'] += 0xffffffff
    clientKey = f"{packets[0]['ip']['addr1']}:{packets[0]['tcp']['sport']}"

    def compare_packets(a, b):
        if a['ip']['addr1'] == b['ip']['addr1'] and a['tcp']['sport'] == b['tcp']['sport']:
            return a['tcp']['seq'] - b['tcp']['seq']

        if clientKey == f"{a['ip']['addr1']}:{a['tcp']['sport']}":
            return (a['tcp']['seq'] + len(a['tcp']['data']) - 1) - b['tcp']['ack']

        return a['tcp']['ack'] - (b['tcp']['seq'] + len(b['tcp']['data']) - 1)

    packets.sort(key=cmp_to_key(compare_packets))
    del packets[num_packets:]
    #Now divide up conversation
    clientSeq = 0
    hostSeq = 0
    start = 0
    previous = 0
    results = []
    for i, item in enumerate(packets):
        pkey = f"{item['ip']['addr1']}:{item['tcp']['sport']}"
        seq_datalen = item['tcp']['seq'] + len(item['tcp']['data'])
        if pkey == clientKey:
            if clientSeq >= seq_datalen:
                continue
            clientSeq = seq_datalen
        else:
            if hostSeq >= seq_datalen:
                continue
            hostSeq = seq_datalen
        if len(results) == 0 or pkey != results[len(results) - 1]['key']:
            previous = start = item['tcp']['seq']
            results.append({
                'key': pkey,
                'data': copy.deepcopy(item['tcp']['data']),
                'ts': item['pcap']['ts_sec'] * 1000 + round(item['pcap']['ts_usec'] / 1000)
            })
            print("first")
        elif item['tcp']['seq'] - previous > 0xffff:
            results.append(
                {'key': '',
                 'data': b'',
                 'ts': item['pcap']['ts_sec'] * 1000 + round(item['pcap']['ts_usec'] / 1000)
                 })
            previous = start = item['tcp']['seq']
            results.append({
                'key': pkey,
                'data': copy.deepcopy(item['tcp']['data']),
                'ts': item['pcap']['ts_sec'] * 1000 + round(item['pcap']['ts_usec'] / 1000)
            })
        else:
            previous = item['tcp']['seq']
            results[-1]['data'] = results[-1]['data'] + item['tcp']['data']
    if skey != results[0]['key']:
        results.insert(0, {'data': b'', 'key': skey})
    return results
