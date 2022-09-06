from multiprocessing import current_process
from sqlite3 import ProgrammingError
from tkinter import font
import pygame
import gpu
import random


NUM_REGISTERS = 10
START_ADDRESS = 0x200
keys = {
    0x0: pygame.K_x,
    0x1: pygame.K_1,
    0x2: pygame.K_2,
    0x3: pygame.K_3,
    0x4: pygame.K_q,
    0x5: pygame.K_w,
    0x6: pygame.K_e,
    0x7: pygame.K_a,
    0x8: pygame.K_s,
    0x9: pygame.K_d,
    0xA: pygame.K_z,
    0xB: pygame.K_c,
    0xC: pygame.K_4,
    0xD: pygame.K_r,
    0xE: pygame.K_f,
    0xF: pygame.K_v
}

fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

class chip8_cpu(object):
    def __init__(self):
        self.timers = {
            'delay': 0,
            'sound': 0
        }
        
        self.V = [0o0]*16            #CPU registers
        self.I = 0x0                 #index register
        self.program_counter = START_ADDRESS     #program counter
        self.stack = [0x0]*16        #the stack, baby!
        self.stack_depth = 0         #current stack depth
        self.keypad = [0]*16         #state of each usable key
        self.curr_operand = 0x0000   #current operand to be used
        self.memory = [0]*4096
        i = 0
        for byte in fonts:
            self.memory[i] = byte
            i+=1

    def init_rom(self, rom):
        for i in range(len(rom)):
            self.memory[START_ADDRESS + i] = rom[i]

    def fetch_opcode(self):
        
        return self.memory[self.program_counter]
         
    def execute_opcode(self, opcode, chip8_gpu):
        self.curr_operand = opcode

        print(hex(opcode))
        print(hex(opcode & 0xF000))
        print(hex((opcode & 0xF000) >> 12))
        if((opcode & 0xF000)>> 12 == 0x0):
            print('got here2')
            if(opcode == 0x00E0):
                print("executing clear screen")
                self.cls(chip8_gpu)
            elif(opcode == 0x00EE):
                print("executing return")
                self.return_subroutine()

        elif((opcode & 0xF000) >> 12 == 0x1):
            print("executing jp")
            self.jp()

        elif((opcode & 0xF000) >> 12 == 0x2):
            print("executing call")
            self.call()

        elif((opcode & 0xF000) >> 12 == 0x3):
            print("executing se_vx_byte")
            self.SE_VX_byte()

        elif((opcode & 0xF000) >> 12 == 0x4):
            print("executing sne_vx_byte")
            self.SNE_VX_byte()

        elif((opcode & 0xF000) >> 12 == 0x5):
            print("executing se_vx_vy")
            self.SE_VX_VY()

        elif((opcode & 0xF000) >> 12 == 0x6):
            print("executing ld_vx_byte")
            self.LD_VX_byte()

        elif((opcode & 0xF000)>> 12 == 0x7):
            print("executing add_vx_byte")
            self.ADD_VX_byte()

        elif((opcode & 0xF000)>> 12 == 0x8):
            if((opcode & 0x000F) == 0x0):
                print("executing ld_vx_vy")
                self.LD_VX_VY()
            elif((opcode & 0x000F) == 0x1):
                print("executing or_vx_vy")
                self.OR_VX_VY()
            elif((opcode & 0x000F) == 0x2):
                print("executing and_vx_vy")
                self.AND_VX_VY()
            elif((opcode & 0x000F) == 0x3):
                print("executing xor_vx_vy")
                self.XOR_VX_VY()
            elif((opcode & 0x000F) == 0x4):
                print("executing add with carry")
                self.ADDwCARRY_VX_VY()
            elif((((opcode & 0x000F))) == 0x5):
                print("executing sub_vx_vy")
                self.SUB_VX_VY()
            elif(((opcode & 0x000F)) == 0x6):
                print("executing shr_vx")
                self.SHR_VX()
            elif(((opcode & 0x000F)) == 0x7):
                print("executing sub_vy_vx")
                self.SUB_VY_VX()
            elif(((opcode & 0x000F)) == 0xE):
                print("executing shl_vx")
                self.SHL_VX()

        elif((opcode & 0xF000)>> 12 == 0x9):
            print("executing sne_vx_vy")
            self.SNE_VX_VY()

        elif((opcode & 0xF000)>> 12 == 0xA):
            print("executing ld_i_addr")
            self.LD_I_ADDR()

        elif((opcode & 0xF000)>> 12 == 0xB):
            print("executing jp_v0_addr")
            self.JP_V0_ADDR()

        elif((opcode & 0xF000)>> 12 == 0xC):
            print("executing rnd_vx_byte")
            self.RND_VX_BYTE()

        elif((opcode & 0xF000)>> 12 == 0xD):
            print("executing drw_vx_vy")
            self.DRW_VX_VY(chip8_gpu)

        elif((opcode & 0xF000)>> 12 == 0xE):
            if(opcode & 0x00FF == 0x9E):
                print("executing skp_vx")
                self.SKP_VX()
            elif(opcode & 0x00FF == 0xA1):
                print("executing sknp_vx")
                self.SKNP_VX()
        elif((opcode & 0xF000)>> 12 == 0xF):
            if((opcode & 0x00FF) == 0x07):
                print("executing ld_vx_dt")
                self.LD_VX_DT()
            elif((opcode & 0x00FF) == 0x0A):
                print("executing ld_vx_k")
                self.LD_VX_K()
            elif((opcode & 0x00FF) == 0x15):
                print("executing ld_dt_vx")
                self.LD_DT_VX()
            elif((opcode & 0x00FF) == 0x18):
                print("executing st_vx")
                self.LD_ST_VX()
            elif((opcode & 0x00FF) == 0x1E):
                print("executing add_i_vx")
                self.ADD_I_VX()
            elif((opcode & 0x00FF) == 0x29):
                print("executing ld_f_vx")
                self.LD_F_VX()
            elif((opcode & 0x00FF) == 0x55):
                print("executing ld_i_vx")
                self.LD_I_VX()
            elif((opcode & 0x00FF) == 0x65):
                print("executing ld_vx_i")
                self.LD_VX_I()

    def inc_pc(self):
        self.program_counter += 1

    def get_delay_timer(self):
        return self.timers['delay']
    
    def inc_delay_timer(self):
        self.timers['delay']+= 1

    def dec_delay_timer(self):
        self.timers['delay']-= 1

    def get_sound_timer(self):
        return self.timers['sound']
    
    def inc_sound_timer(self):
        self.timers['sound']+= 1

    def dec_sound_timer(self):
        self.timers['sound']-= 1
    
    # CLEAR SCREEN
    def cls(self, chip8_gpu):
        chip8_gpu.clear()

    # RETURN TO LATER
    def return_subroutine(self):
        self.program_counter = self.stack_depth
        self.stack_depth -= 1

    # JUMP TO LOCATION 
    def jp(self):
        self.program_counter = self.curr_operand & 0x0FFF

    # 2nnn - CALL addr
    # Call subroutine at nnn.
    def call(self):
        self.stack_depth += 1
        self.stack[self.stack_depth] = self.program_counter
        program_counter = 0xFFF

    # 3xkk - SE Vx, byte
    # Skip next instruction if Vx == kk
    def SE_VX_byte(self):
        if(self.V[(self.curr_operand & 0x0F00) >> 8] == self.curr_operand & 0x00FF):
            self.program_counter += 2
    
    # 4xkk - SE Vx, byte
    # Skip next instruction if Vx != kk
    def SNE_VX_byte(self):
        if(self.V[(self.curr_operand & 0x0F00) >> 8] != self.curr_operand & 0x00FF):
            self.program_counter += 2
    
    # 5xy0 - SE Vx, Vy
    # Skip next instruction if Vx = Vy
    def SE_VX_VY(self):
        if(self.V[(self.curr_operand & 0x0F00) >> 8] == self.V[self.curr_operand & 0x00F0 << 4]):
            self.program_counter += 2

    # 6xkk - LD Vx, byte
    # Set Vx = kk
    def LD_VX_byte(self):
        self.V[(self.curr_operand & 0x0F00) >> 8] = self.curr_operand & 0x00FF

    # 7xkk - ADD Vx, byte
    # Set Vx = Vx + kk
    def ADD_VX_byte(self):
        self.V[(self.curr_operand & 0x0F00) >> 8] = self.V[self.curr_operand & 0x0F00 >> 8] + self.curr_operand & 0x00FF

    # 8xy0 - LD Vx, Vy
    # Set Vx = Vy
    def LD_VX_VY(self):
        self.V[(self.cur_operand & 0x0F00) >> 8] = self.V[(self.curr_operand & 0x00F0) << 4]

    # 8xy1 - OR Vx, Vy
    # Set Vx = Vx OR Vy
    def OR_VX_VY(self):
        self.V[(self.cur_operand & 0x0F00) >> 8] = self.V[(self.curr_operand & 0x00F0) << 4] | self.V[(self.cur_operand & 0x0F00) >> 8]
    
    # 8xy2 - AND Vx, Vy
    # Set Vx = Vx AND Vy
    def AND_VX_VY(self):
        self.V[self.cur_operand & 0x0F00 >> 8] = self.V[(self.curr_operand & 0x00F0) << 4] & self.V[(self.cur_operand & 0x0F00) >> 8]
    
    # 8xy3 - AND Vx, Vy
    # Set Vx = Vx XOR Vy
    def XOR_VX_VY(self):
        self.V[(self.cur_operand & 0x0F00) >> 8] = self.V[(self.curr_operand & 0x00F0) << 4] ^ self.V[(self.cur_operand & 0x0F00) >> 8]

    # 8xy4 - ADD Vx, Vy
    # Set Vx = Vx + Vy if result > 255 then VF is set to carry
    def ADDwCARRY_VX_VY(self):
        result = self.V[(self.cur_operand & 0x0F00) >> 8] + self.V[(self.cur_operand & 0x00F0) >> 4]
        if result > 0xFF:
            self.V[(self.cur_operand & 0x0F00) >> 8] = 0xFF
            self.V[15] = result - 0xFF
        else:
            self.V[self.cur_operand & 0x0F00 >> 8] = result
    
    # 8xy5 - SUB Vx, Vy
    # Set Vx = Vx - Vy if Vx > Vy then VF is set to 1, otherwise VF is set to 0
    def SUB_VX_VY(self):
        if self.V[(self.cur_operand & 0x0F00) >> 8] > self.V[(self.cur_operand & 0x00F0) >> 4]:
            self.V[15] = 0x001
        else:
            self.V[15] = 0x000
        self.V[(self.cur_operand & 0x0F00) >> 8] = self.V[(self.cur_operand & 0x0F00) >> 8] - self.V[(self.cur_operand & 0x00F0) >> 4]

    # 8xy6 - SHR Vx, Vy
    # Set Vx = Vx/2 if least sig bit is 1 then VF is set to 1, otherwise VF is set to 0
    def SHR_VX(self):
        if self.V[(self.cur_operand & 0x0100) >> 8] == 0x001:
            self.V[15] = 0x001
        else:
            self.V[15] = 0x000
        self.V[self.cur_operand & 0x0F00 >> 8] = self.V[self.cur_operand & 0x0F00 >> 8] >> 1

    # 8xy7 - SUB Vy, Vx
    # Set Vx = Vy - Vx if Vy > Vx then VF is set to 1, otherwise VF is set to 0
    def SUB_VY_VX(self):
        if self.V[self.cur_operand & 0x0F00 >> 8] < self.V[self.cur_operand & 0x00F0 >> 4]:
            self.V[15] = 0x001
        else:
            self.V[15] = 0x000
        self.V[self.cur_operand & 0x0F00 >> 8] = self.V[self.cur_operand & 0x00F0 >> 4] - self.V[self.cur_operand & 0x0F00 >> 8]

    # 8xyE - SHL Vx, Vy
    # Set Vx = Vx*2 if most sig bit is 1 then VF is set to 1, otherwise VF is set to 0
    def SHL_VX(self):
        if self.V[self.cur_operand & 0x800 >> 8] == 0x001:
            self.V[15] = 0x001
        else:
            self.V[15] = 0x000
        self.V[self.cur_operand & 0x0F00 >> 8] = self.V[self.cur_operand & 0x0F00 >> 8] << 1

    # 9xy0 - SNE Vx, Vy
    # Skip next instruction if Vx != Vy
    def SNE_VX_VY(self):
        if self.V[self.cur_operand & 0x0F00 >> 8] != self.V[self.cur_operand & 0x00F0 >> 4]:
            self.program_counter += 2

    # Annn - LD I, addr
    # Set I = nnn.
    def LD_I_ADDR(self):
        self.I = self.curr_operand & 0x0FFF

    # Bnnn - JP V0, addr
    # Jump to location nnn + V0.
    def JP_V0_ADDR(self):
        self.program_counter = self.curr_operand & 0x0FFF + self.V[0]

    # Cxkk - RND Vx, byte
    # Set Vx = random byte AND kk.
    def RND_VX_BYTE(self):
        self.V[self.curr_operand & 0x0F00 >> 8] = hex(random.randbytes(1)) & 0x00FF & self.curr_operand


    # Dxyn - DRW Vx, Vy, nibble
    # Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
    def DRW_VX_VY(self, chip8_gpu):    
        i = 0x0
        VF_flag = 0
        while i < self.curr_operand & 0x000F:
            VF_flag += chip8_gpu.display_byte(self.curr_operand & 0x0F00, self.curr_operand & 0x00F0 +i, self.V[self.curr_operand & 0x000F + i])
            i += 0x1
        self.V[0xF] = VF_flag > 0

    # Ex9E - SKP Vx
    # Skip next instruction if key with the value of Vx is pressed.
    def SKP_VX(self):
        keyStates = pygame.key.get_pressed()
        if keyStates[keys[0x0F00 >> 8]]:
            self.program_counter += 2
    
    # ExA1 - SKNP Vx
    # Skip next instruction if key with the value of Vx is not pressed.
    def SKNP_VX(self):
        keyStates = pygame.key.get_pressed()
        if keyStates[keys[0x0F00 >> 8]]:
            self.program_counter += 2
    
    # Fx07 - LD Vx, DT
    # Set Vx = delay timer value
    def LD_VX_DT(self):
        self.V[self.curr_operand & 0x0F00 >> 8] = self.timers['delay']

    # Fx0A - LD Vx, K
    # Wait for a key press, store the value of the key in Vx
    def LD_VX_K(self):
        counter = 0
        while counter == 0:
            keyStates = pygame.key.get_pressed()
            for key in keys:
                if keyStates[keys[key]] == 1:
                    counter += 1
                    self.V[self.curr_operand & 0x0F00 >> 8] = key
        
    # Fx15 - LD DT, Vx
    # Set delay timer value = Vx
    def LD_DT_VX(self):
        self.timers['delay'] = self.V[self.curr_operand & 0x0F00 >> 8] 

    # Fx18 - LD ST, Vx
    # Set sound timer value = Vx
    def LD_ST_VX(self):
        self.timers['sound'] = self.V[self.curr_operand & 0x0F00 >> 8] 

    # Fx1E - ADD I, Vx
    # Set I = I + Vx
    def ADD_I_VX(self):
        self.I = self.V[self.curr_operand & 0x0F00 >> 8] + self.I

    # Fx29 - LD F, Vx
    # Set I = location of sprite for digit Vx
    def LD_F_VX(self):
        self.I = self.V[self.curr_operand & 0x0F00 >> 8] * 0x5
    
    # Fx33 - LD B, Vx
    # Store BCD represenation of Vx in memory locations I, I+1, and I+2
    def LD_B_VX(self):
        self.I = self.V[self.curr_operand & 0x0F00 >> 8] * 0x5
        #pulls out and stores the Base-10 hundreds place of Vx
        self.V[self.I] = int(((self.curr_operand & 0x0F00 >> 8) - (self.curr_operand & 0x0F00 >> 8) % 0x64)/0x64)
        #pulls out and stores the Base-10 tens place of Vx
        self.V[self.I + 0x1] = int(((self.curr_operand & 0x0F00 >> 8) - (self.curr_operand & 0x0F00 >> 8) % 0xA)/0xA)
        #pulls out and stores the Base-10 ones place of Vx
        self.V[self.I + 0x2] = int((self.curr_operand & 0x0F00 >> 8) % 0xA)
    
    # Fx55 - LD [I], Vx
    # Stores registers V0 through Vx in memory starting at location I
    def LD_I_VX(self):
        for i in range(self.curr_operand & 0x0F00 >> 8):
            self.memory[self.I + i] = self.V[i]
    
    # Fx65 - LD Vx, [I]
    # Read memory starting at location I into registers V0 through Vx
    def LD_VX_I(self):
        for i in range(self.curr_operand & 0x0F00 >> 8):
            self.V[i] = self.memory[self.I + i]