import Cartridge

class Nes2C02:
    STATUS_SPROVERFLOW = (1 << 5)
    STATUS_SPRZERO     = (1 << 6)
    STATUS_VERTBLANK   = (1 << 7)

    MASK_GRAYSCALE     = (1 << 0)
    MASK_RENDER_BKGD_L = (1 << 1)
    MASK_RENDER_SPR_L  = (1 << 2)
    MASK_RENDER_BKGD   = (1 << 3)
    MASK_RENDER_SPR    = (1 << 4)
    MASK_ENHANCE_RED   = (1 << 5)
    MASK_ENHANCE_GREEN = (1 << 6)
    MASK_ENHANCE_BLUE  = (1 << 7)

    CONTROL_NAMETBL_X  = (1 << 0)
    CONTROL_NAMETBL_Y  = (1 << 1)
    CONTROL_INC_MODE   = (1 << 2)
    CONTROL_PATT_SPR   = (1 << 3)
    CONTROL_PATT_BKGD  = (1 << 4)
    CONTROL_SPR_SIZE   = (1 << 5)
    CONTROL_SLAVE_MODE = (1 << 6)   # unused
    CONTROL_ENABLE_NMI = (1 << 7)
    def __init__(self):
        self.cart = None

        # 2D array, tblName[2][1024]
        self.tblName = [[0 for i in range(1024)] for j in range(2)]
        self.tblPalette = [0 for i in range(32)]
        self.tblPattern = [[0 for i in range(4096)] for j in range(2)]

        self.status = 0x00
        self.mask = 0x00
        self.control = 0x00
        self.address_latch = 0
        self.ppu_data_buffer = 0
        self.ppu_address = 0x0000
        self.nmi = False

        # For visualizing the state of the ppu
        import pygame
        self.palScreen = [
            (84, 84, 84),       (0, 30, 116),       (8, 16, 144),       (48, 0, 136),       (68, 0, 100),       (92, 0, 48),        (84, 4, 0),         (60, 24, 0),        (32, 42, 0),        (8, 58, 0),         (0, 64, 0),         (0, 60, 0),         (0, 50, 60),        (0, 0, 0),          (0, 0, 0), (0, 0, 0), 
            (152, 150, 152),    (8, 76, 196),       (48, 50, 236),      (92, 30, 228),      (136, 20, 176),     (160, 20, 100),     (152, 34, 32),      (120, 60, 0),       (84, 90, 0),        (40, 114, 0),       (8, 124, 0),        (0, 118, 40),       (0, 102, 120),      (0, 0, 0),          (0, 0, 0), (0, 0, 0), 
            (236, 238, 236),    (76, 154, 236),     (120, 124, 236),    (176, 98, 236),     (228, 84, 236),     (236, 88, 180),     (236, 106, 100),    (212, 136, 32),     (160, 170, 0),      (116, 196, 0),      (76, 208, 32),      (56, 204, 108),     (56, 180, 204),     (60, 60, 60),       (0, 0, 0), (0, 0, 0), 
            (236, 238, 236),    (168, 204, 236),    (188, 188, 236),    (212, 178, 236),    (236, 174, 236),    (236, 174, 212),    (236, 180, 176),    (228, 196, 144),    (204, 210, 120),    (180, 222, 120),    (168, 226, 144),    (152, 226, 180),    (160, 214, 228),    (160, 162, 160),    (0, 0, 0), (0, 0, 0)
        ]
        self.sprScreen = pygame.Surface((256, 240))
        self.sprNameTable = [pygame.Surface((256, 240)), pygame.Surface((256, 240))]
        self.sprPatternTable = [pygame.Surface((128, 128)), pygame.Surface((128, 128))]
        self.frame_complete = False
        self.scanline = 0
        self.cycle = 0
    def GetScreen(self):
        return self.sprScreen
    def GetNameTable(self, i):
        return self.sprNameTable[i]
    def GetPatternTable(self, i, palette):
        for tileY in range(16):
            for tileX in range(16):
                offset = tileY * 256 + tileX * 16
                for row in range(8):
                    tile_lsb = self.ppuRead(i * 0x1000 + offset + row)
                    tile_msb = self.ppuRead(i * 0x1000 + offset + row + 8)
                    for col in range(8):
                        pixel = ((tile_msb & 0x01) << 1) | (tile_lsb & 0x01)
                        #pixel = (tile_lsb & 0x01) + (tile_msb & 0x01)
                        tile_lsb >>= 1
                        tile_msb >>= 1
                        self.sprPatternTable[i].set_at(
                            (tileX * 8 + (7 - col), tileY * 8 + row),
                            self.GetColorFromPaletteRam(palette, pixel)
                        )
        return self.sprPatternTable[i]
    def GetColorFromPaletteRam(self, palette, pixel):
        return self.palScreen[self.ppuRead(0x3F00 + (palette << 2) + pixel) & 0x3F]

    def cpuRead(self, addr, readonly=False):
        data = 0x00

        if readonly:
            if addr == 0x0000:      # control
                data = self.control
            elif addr == 0x0001:    # mask
                data = self.mask
            elif addr == 0x0002:    # status
                data = self.status
            elif addr == 0x0003:    # oam address
                pass
            elif addr == 0x0004:    # oam data
                pass
            elif addr == 0x0005:    # scroll
                pass
            elif addr == 0x0006:    # ppu address
                pass
            elif addr == 0x0007:    # ppu data
                pass
        else:
            if addr == 0x0000:      # control
                pass
            elif addr == 0x0001:    # mask
                pass
            elif addr == 0x0002:    # status
                # if (self.status & self.STATUS_VERTBLANK) > 0:
                #     print("  (PPU) reading status - vertblank true")
                data = (self.status & 0xE0) | (self.ppu_data_buffer & 0x1F)
                # if (data & self.STATUS_VERTBLANK) > 0:
                #     print("  (PPU) data has vertblank (0x%02X)" % (data))
                self.status &= ~self.STATUS_VERTBLANK
                self.address_latch = 0
            elif addr == 0x0003:    # oam address
                pass
            elif addr == 0x0004:    # oam data
                pass
            elif addr == 0x0005:    # scroll
                pass
            elif addr == 0x0006:    # ppu address
                pass
            elif addr == 0x0007:    # ppu data
                data = self.ppu_data_buffer
                self.ppu_data_buffer = self.ppuRead(self.ppu_address)

                if self.ppu_address > 0x3F00:
                    data = self.ppu_data_buffer

                self.ppu_address += 1
        # print("  (PPU) returning 0x%02X" % (data))
        return data

    def cpuWrite(self, addr, data):
        if addr == 0x0000:      # control
            self.control = data
        elif addr == 0x0001:    # mask
            self.mask = data
        elif addr == 0x0002:    # status
            pass
        elif addr == 0x0003:    # oam address
            pass
        elif addr == 0x0004:    # oam data
            pass
        elif addr == 0x0005:    # scroll
            pass
        elif addr == 0x0006:    # ppu address
            if self.address_latch == 0:
                self.ppu_address = (self.ppu_address & 0x00FF) | (data << 8)
                self.address_latch = 1
            else:
                self.ppu_address = (self.ppu_address & 0xFF00) | data
                self.address_latch = 0
        elif addr == 0x0007:    # ppu data
            self.ppuWrite(self.ppu_address, data)
            self.ppu_address += 1

    def ppuRead(self, addr, readonly=False):
        data = 0x00
        addr &= 0x3FFF

        cartData = self.cart.ppuRead(addr)
        if cartData:
            data = cartData
        elif addr >= 0x0000 and addr <= 0x1FFF:
            data = self.tblPattern[(addr & 0x1000) >> 12][addr & 0x0FFF]
        elif addr >= 0x2000 and addr <= 0x3EFF:
            pass
        elif addr >= 0x3F00 and addr <= 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010:
                addr = 0x0000
            elif addr == 0x0014:
                addr = 0x0004
            elif addr == 0x0018:
                addr = 0x0008
            elif addr == 0x001C:
                addr = 0x000C
            data = self.tblPalette[addr]
        
        return data

    def ppuWrite(self, addr, data):
        addr &= 0x3FFF

        if self.cart.ppuWrite(addr, data):
            pass
        elif addr >= 0x0000 and addr <= 0x1FFF:
            self.tblPattern[(addr & 0x1000) >> 12][addr & 0x0FFF] = data
        elif addr >= 0x2000 and addr <= 0x3EFF:
            pass
        elif addr >= 0x3F00 and addr <= 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010:
                addr = 0x0000
            elif addr == 0x0014:
                addr = 0x0004
            elif addr == 0x0018:
                addr = 0x0008
            elif addr == 0x001C:
                addr = 0x000C
            self.tblPalette[addr] = data

    def ConnectCartridge(self, cartridge):
        self.cart = cartridge

    def clock(self):
        if self.scanline == -1 and self.cycle == 1:
            self.status &= ~self.STATUS_VERTBLANK
        if self.scanline == 241 and self.cycle == 1:
            # print("Setting vertblank")
            self.status |= self.STATUS_VERTBLANK
            if self.control & self.CONTROL_ENABLE_NMI > 0:
                self.nmi = True
        import random
        self.sprScreen.set_at((self.cycle - 1, self.scanline), self.palScreen[0x3F] if random.randint(0, 1) == 0 else self.palScreen[0x30])
        self.cycle += 1
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline >= 261:
                self.scanline = -1
                self.frame_complete = True
