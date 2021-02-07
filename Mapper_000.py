import Mapper

class Mapper_000(Mapper.Mapper):
    def cpuMapRead(self, addr):
        if addr >= 0x8000 and addr <= 0xFFFF:
            #print ("  (MAPPER) returning %04X" % (addr & (0x7FFF if self.prgBanks > 1 else 0x3FFF)))
            return addr & (0x7FFF if self.prgBanks > 1 else 0x3FFF)
        return None

    def cpuMapWrite(self, addr):
        if addr >= 0x8000 and addr <= 0xFFFF:
            return addr & (0x7FFF if self.prgBanks > 1 else 0x3FFF)
        return None

    def ppuMapRead(self, addr):
        if addr >= 0x0000 and addr <= 0x1FFF:
            return addr
        return None

    def ppuMapWrite(self, addr):
        if addr >= 0x0000 and addr <= 0x1FFF:
            if self.chrBanks == 0:
                return addr
        return None
