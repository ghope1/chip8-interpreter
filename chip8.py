from fileinput import filename
import pygame
import string
import codecs
from gpu import chip8_gpu
from cpu import chip8_cpu

filename = "IBMLogo.ch8"

opcode = 0              #current opcode being decoded


def import_rom(filename):
    rom_source = open(filename, 'r')
    rom = rom_source.read()
    
    rom = rom.split()
    
    for i in range(len(rom)):
        rom[i] = int(rom[i], 16)
        
    rom_source.close()
    print(rom)
    return rom

def emulateCycle(screen, cpu):
    opcode = cpu.fetch_opcode()
    print("Recieved Opcode", hex(opcode))
    cpu.execute_opcode(opcode, screen)
    cpu.inc_pc()
    screen.update()

def emulateChip8():
    screen = chip8_gpu()
    cpu = chip8_cpu()
    rom = import_rom(filename)
    cpu.init_rom(rom)
    
    screen.init_display()
    pygame.init()
    
    while 1:
        emulateCycle(screen, cpu)

    return 0

emulateChip8()
