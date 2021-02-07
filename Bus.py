import Nes6502
import Nes2C02
import Cartridge

class Bus:
    def __init__(self):
        self.cpu = Nes6502.Nes6502()
        self.ppu = Nes2C02.Nes2C02()
        #self.cpuRam = [0 for i in range(2048)]
        self.cpuRam = [0 for i in range(0xFFFF)]
        self.cart = None

        self.systemClockCounter = 0

        self.cpu.ConnectBus(self)

    def cpuWrite(self, addr, data):
        if self.cart.cpuWrite(addr, data):
            pass
        elif addr >= 0x0000 and addr <= 0x1FFF:
            self.cpuRam[addr & 0x07FF] = data
        elif addr >= 0x2000 and addr <= 0x3FFF:
            self.ppu.cpuWrite(addr & 0x0007, data)

    def cpuRead(self, addr, readonly=False):
        data = 0x00
        #print("reading from 0x%04X" % (addr))
        cartData = self.cart.cpuRead(addr)
        #print("  (CPU) cart handled)" if cartData is not None else "  (CPU) (cart did not handle)")
        if cartData:
            data = cartData
        elif addr >= 0x0000 and addr <= 0x1FFF:
            data = self.cpuRam[addr & 0x07FF]
        elif addr >= 0x2000 and addr <=0x3FFF:
            data = self.ppu.cpuRead(addr & 0x0007, readonly)
            # print("  (BUS) data is 0x%02X" % (data))
        #print("  (CPU) returning %02X" % data)
        return data

    def insertCartridge(self, cartridge):
        self.cart = cartridge
        self.ppu.ConnectCartridge(cartridge)

    def reset(self):
        self.cpu.reset()
        self.systemClockCounter = 0

    def clock(self):
        self.ppu.clock()
        if self.systemClockCounter % 3 == 0:
            self.cpu.clock()

        if self.ppu.nmi:
            self.ppu.nmi = False
            self.cpu.nmi()
        self.systemClockCounter += 1
