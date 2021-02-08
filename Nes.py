import GameEngine
import Nes6502
import Bus
import Cartridge
import sys
import time
import pygame

class Nes(GameEngine.GameEngine):
    def user_init(self):
        self.fps = 30
        self.construct(780, 480, self.fps)
        self.nes = Bus.Bus()
        self.cpu = self.nes.cpu
        self.cpu.ConnectBus(self.nes)
        self.update_count = 0
        self.next_frame = 0
        self.frame_count = 0
        self.realtime = False
        self.set_font("PressStartK-EX89.ttf", 8)

        self.emulationRun = False
        self.residualTime = 0.0

        self.selectedPalette = 0

        self.cartridge = Cartridge.Cartridge('nestest.nes')
        self.nes.insertCartridge(self.cartridge)

        self.mapAsm = self.cpu.disassemble(0x0000, 0xFFFF)

        self.cpu.reset()

    def user_update(self, elapsed_time):
        self.screen.fill((0, 7, 122))

        completed_frame = False
        if self.emulationRun:
            if self.residualTime > 0.0:
                self.residualTime -= elapsed_time
            else:
                self.residualTime += (1.0/60.0) - elapsed_time
                self.nes.clock()
                while not self.nes.ppu.frame_complete:
                    self.nes.clock()
                self.nes.ppu.frame_complete = False
                completed_frame = True
        else:
            if self.keypressed == 'c':
                self.nes.clock()
                while self.cpu.cycles > 0:
                    self.nes.clock()
                self.nes.clock()
                while self.cpu.cycles == 0:
                    self.nes.clock()
            elif self.keypressed == 'f':
                self.nes.clock()
                while not self.nes.ppu.frame_complete:
                    self.nes.clock()
                self.nes.clock()
                while self.cpu.cycles == 0:
                    self.nes.clock()
                self.nes.ppu.frame_complete = False
        if self.keypressed == 'r':
            self.nes.reset()
        elif self.keypressed == 'space':
            self.emulationRun = not self.emulationRun
        elif self.keypressed == 'p':
            self.selectedPalette = (self.selectedPalette + 1) & 0x07
        elif self.keypressed == 'q':
            sys.exit(0)
        
        self.draw_cpu(516, 2)
        self.draw_code(516, 72, 26)

        swatch_size = 6
        for p in range(8):
            for s in range(4):
                self.screen.fill(self.nes.ppu.GetColorFromPaletteRam(p, s), pygame.Rect((516 + p * (swatch_size * 5) + s * swatch_size, 340), (swatch_size, swatch_size)))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect((516 + self.selectedPalette * (swatch_size * 5) - 1, 339),(swatch_size * 4, swatch_size+1)), width=1)
        self.screen.blit(self.nes.ppu.GetPatternTable(0, self.selectedPalette), (516, 348))
        self.screen.blit(self.nes.ppu.GetPatternTable(1, self.selectedPalette), (648, 348))
        self.screen.blit(pygame.transform.scale(self.nes.ppu.GetScreen(), (512, 480)), (0, 0))

        # hex = lambda x,y:'{word:0{padding}X}'.format(word=x if x >=0 else x+256, padding=y)
        # scr = pygame.Surface((256, 240))
        # pat = self.nes.ppu.GetPatternTable(1, self.selectedPalette)
        # for y in range(30):
        #     for x in range(32):
        #         # s = hex(self.nes.ppu.tblName[0][y * 32 + x], 2)
        #         # if s == "24": s = "  "
        #         # self.draw_string(x * 16, y * 16, s)
        #         tileid = self.nes.ppu.tblName[0][y * 32 + x]
        #         scr.blit(pat, (x * 8, y * 8), area=pygame.Rect(((tileid & 0x0F) << 3, ((tileid >> 4) & 0x0F) << 3), (8, 8)))
        # self.screen.blit(pygame.transform.scale(scr, (256*2, 240*2)), (0, 0))

        if not self.emulationRun or (self.emulationRun and completed_frame):
            pygame.display.update()

    def draw_cpu(self, x, y):
        hex = lambda x,y:'{word:0{padding}X}'.format(word=x if x >=0 else x+256, padding=y)

        self.draw_string(x , y , "STATUS:", self.COLOR_WHITE)
        self.draw_string(x  + 64, y, "N", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_N > 0 else self.COLOR_RED)
        self.draw_string(x  + 80, y , "V", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_V > 0 else self.COLOR_RED)
        self.draw_string(x  + 96, y , "-", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_U > 0 else self.COLOR_RED)
        self.draw_string(x  + 112, y , "B", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_B > 0 else self.COLOR_RED)
        self.draw_string(x  + 128, y , "D", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_D > 0 else self.COLOR_RED)
        self.draw_string(x  + 144, y , "I", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_I > 0 else self.COLOR_RED)
        self.draw_string(x  + 160, y , "Z", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_Z > 0 else self.COLOR_RED)
        self.draw_string(x  + 178, y , "C", self.COLOR_GREEN if self.nes.cpu.status & self.cpu.FLAGS6502_C > 0 else self.COLOR_RED)
        self.draw_string(x , y + 10, "PC: $" + hex(self.nes.cpu.pc, 4))
        self.draw_string(x , y + 20, "A: $" +  hex(self.nes.cpu.a, 2) + "  [" + str(self.nes.cpu.a) + "]");
        self.draw_string(x , y + 30, "X: $" +  hex(self.nes.cpu.x, 2) + "  [" + str(self.nes.cpu.x) + "]");
        self.draw_string(x , y + 40, "Y: $" +  hex(self.nes.cpu.y, 2) + "  [" + str(self.nes.cpu.y) + "]");
        self.draw_string(x , y + 50, "Stack P: $" + hex(self.nes.cpu.stkp, 4));

    def draw_code(self, x, y, lines):
        keys = list(self.mapAsm.keys())
        pc_i = keys.index(self.nes.cpu.pc)

        for i in range(lines):
            self.draw_string(x, i*10 + y, self.mapAsm[keys[int(pc_i+(i-lines/2))]], self.COLOR_CYAN if (i==lines/2) else self.COLOR_WHITE)


if __name__ == "__main__":
    nes = Nes()
    nes.run()


