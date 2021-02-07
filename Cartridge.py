import struct
from Mapper_000 import Mapper_000

# from ctypes import *
# class CARTHEADER(Structure):
#     _fields_ = [
#         ("name",            c_char*4),
#         ("prg_rom_chunks",  c_uint8),
#         ("chr_rom_chunks",  c_uint8),
#         ("mapper1",         c_uint8),
#         ("mapper2",         c_uint8),
#         ("prg_ram_size",    c_uint8),
#         ("tv_system_1",     c_uint8),
#         ("tv_system_2",     c_uint8),
#         ("unused",          c_char*5)
#     ]

class Cartridge:
    MIRROR_HORIZONTAL   = 0
    MIRROR_VERTICAL     = 1
    MIRROR_ONESCREEN_LO = 2
    MIRROR_ONESCREEN_HI = 3

    def __init__(self, filename):
        def readFile(filename):
            try:
                f = open(filename, 'rb')
            except:
                return
            headerData = f.read(16)
            header = struct.unpack('>4sBBBBBBB5s', headerData)

            if header[3] & 0x04 > 0:
                f.read(512)

            self.mapperID = ((header[4] >> 4) << 4) | (header[3] >> 4)
            self.mirror = self.MIRROR_VERTICAL if (header[3] & 0x01) > 0 else self.MIRROR_HORIZONTAL

            fileType = 1    # assume filetype 1 for now

            if fileType == 0:
                pass
            elif fileType == 1:
                self.prgBanks = header[1]
                self.prgMemory = list(f.read(self.prgBanks * 16384))
                self.chrBanks = header[2]
                self.chrMemory = list(f.read(self.chrBanks * 8192))
            elif fileType == 2:
                pass

            f.close()


        self.prgMemory = []
        self.chrMemory = []

        self.mapperID = 0
        self.prgBanks = 0
        self.chrBanks = 0

        readFile(filename)

        self.mapper = None
        if self.mapperID == 0:
            self.mapper = Mapper_000(self.prgBanks, self.chrBanks)

    def cpuRead(self, addr):
        mapped_addr = self.mapper.cpuMapRead(addr)
        if mapped_addr is not None:
            data = self.prgMemory[mapped_addr]
            return data
        return None

    def cpuWrite(self, addr, data):
        mapped_addr = self.mapper.cpuMapWrite(addr)
        if mapped_addr is not None:
            self.prgMemory[mapped_addr] = data
            return data
        return None

    def ppuRead(self, addr):
        mapped_addr = self.mapper.ppuMapRead(addr)
        if mapped_addr is not None:
            data = self.chrMemory[mapped_addr]
            return data
        return None

    def ppuWrite(self, addr, data):
        mapped_addr = self.mapper.ppuMapWrite(addr)
        if mapped_addr is not None:
            self.chrMemory[mapped_addr] = data
            return data
        return None
