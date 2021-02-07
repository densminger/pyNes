class Mapper:
    def __init__(self, prgBanks, chrBanks):
        self.prgBanks = prgBanks
        self.chrBanks = chrBanks
        pass

    def cpuMapRead(self, addr):
        raise NotImplementedError()

    def cpuMapWrite(self, addr):
        raise NotImplementedError()

    def ppuMapRead(self, addr):
        raise NotImplementedError()

    def ppuMapWrite(self, addr):
        raise NotImplementedError()
