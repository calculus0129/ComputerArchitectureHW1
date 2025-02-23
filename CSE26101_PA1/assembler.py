import sys
import os
from enum import Enum
from tempfile import TemporaryFile
import re
import ctypes

################################################
# For debug option. If you want to debug, set 1
# If not, set 0.
################################################

DEBUG = 1

MAX_SYMBOL_TABLE_SIZE = 1024
MEM_TEXT_START = 0x00400000
MEM_DATA_START = 0x10000000
BYTES_PER_WORD = 4

################################################
# Additional Components
################################################

class bcolors:
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'


start = '[' + bcolors.BLUE + 'START' + bcolors.ENDC + ']  '
done = '[' + bcolors.YELLOW + 'DONE' + bcolors.ENDC + ']   '
success = '[' + bcolors.GREEN + 'SUCCESS' + bcolors.ENDC + ']'
error = '[' + bcolors.RED + 'ERROR' + bcolors.ENDC + ']  '

pType = [start, done, success, error]


def log(printType, content):
    print(pType[printType] + content)


################################################
# Structure Declaration
################################################

class inst_t:
    def __init__(self, name, op, type, funct):
        self.name = name
        self.op = op
        self.type = type
        self.funct = funct


class symbol_t:
    def __init__(self):
        self.name = 0
        self.address = 0


class la_struct:
    def __init__(self, op, rt, imm):
        self.op = op
        self.rt = rt
        self.imm = imm

class section(Enum):
    DATA = 0
    TEXT = 1
    MAX_SIZE = 2


################################################
# Global Variable Declaration
################################################

ADD = inst_t("add", "000000", 'R', "100000")
ADDI = inst_t("addi", "001000", 'I', "")
ADDIU = inst_t("addiu", "001001", "I", "")  # 0
ADDU = inst_t("addu",    "000000", 'R', "100001")  # 1
AND = inst_t("and",     "000000", 'R', "100100")
ANDI = inst_t("andi",    "001100", 'I', "")
BEQ = inst_t("beq",     "000100", 'I', "")
BNE = inst_t("bne",     "000101", 'I', "")
J = inst_t("j",       "000010", 'J', "")
JAL = inst_t("jal",     "000011", 'J', "")
JR = inst_t("jr",      "000000", 'R', "001000")
LUI = inst_t("lui",     "001111", 'I', "")
LW = inst_t("lw",      "100011", 'I', "")
NOR = inst_t("nor",     "000000", 'R', "100111")
OR = inst_t("or",      "000000", 'R', "100101")
ORI = inst_t("ori",     "001101", 'I', "")
SLT = inst_t("slt", "000000", 'R', "101010")
SLTI = inst_t("slti", "001010", 'I', "")
SLTIU = inst_t("sltiu",    "001011", 'I', "")
SLTU = inst_t("sltu",    "000000", 'R', "101011")
SLL = inst_t("sll",     "000000", 'R', "000000")
SRL = inst_t("srl",     "000000", 'R', "000010")
SW = inst_t("sw",      "101011", 'I', "")
SUB = inst_t("sub", "000000", 'R', "100010")
SUBU = inst_t("subu",    "000000", 'R', "100011")

inst_list = [ADD,  ADDI, ADDIU, ADDU, AND,
             ANDI, BEQ,  BNE,   J,    JAL, 
             JR,   LUI,   LW,   NOR,
             OR,   ORI,  SLT,   SLTI, SLTIU,  
             SLTU, SLL,  SRL,   SW, 
             SUB,  SUBU, ]

symbol_struct = symbol_t()
#SYMBOL_TABLE = [symbol_struct] * MAX_SYMBOL_TABLE_SIZE
SYMBOL_TABLE = {}

symbol_table_cur_index = 0

data_section_size = 0
text_section_size = 0


################################################
# Function Declaration
################################################

def change_file_ext(fin_name):
    fname_list = fin_name.split('.')
    fname_list[-1] = 'o'
    fout_name = ('.').join(fname_list)
    return fout_name


def symbol_table_add_entry(name, address):
    global SYMBOL_TABLE
    global symbol_table_cur_index

    SYMBOL_TABLE[name] = address
    symbol_table_cur_index += 1
    if DEBUG:
        log(1, f"{name}: 0x" + hex(address)[2:].zfill(8))


def convert_label(label):
    address = 0
    for i in range(symbol_table_cur_index):
        if label == SYMBOL_TABLE[i].name:
            address = SYMBOL_TABLE[i].address
            break
    return address


def num_to_bits(num, len):
    bit = bin(num & (2**len-1))[2:].zfill(len)
    return bit

def num_to_hex(num, len=8):
    ret = '0x'+hex(num & ((1<<len*4)-1))[2:].zfill(len)
    return ret

def someint(numstr):
    try:
        return int(numstr)
    except ValueError:
        return int(numstr, 16)
        #assert(int('0x821', 16) == 0x821)

#################################################
# # # # # # # # # # # # # # # # # # # # # # # # #
#                                               #
# Please Do not change the above if possible    #
# The TA's are not resposinble for failures     #
# due to changes in the above                   #
#                                               #
# # # # # # # # # # # # # # # # # # # # # # # # #
#################################################

def make_symbol_table(input):
    size_bit = 0
    address = 0
    wordcnt, txtcnt = 0, 0
    x = 4
    x += 3 << 1
    assert(x == 10)

    cur_section = section.MAX_SIZE.value

    # Read .data section
    lines = input.readlines()
    # MYCODE
    global BYTES_PER_WORD
    # /MYCODE
    while len(lines) > 0:
        line = lines.pop(0)
        line = line.strip()
        _line = line
        token_line = _line.strip('\n\t').split()
        temp = token_line[0]

        if temp == ".data":
            '''
            blank
            '''
            cur_section = section.DATA.value
            global data_seg
            data_seg = TemporaryFile('w+')
            continue

        if temp == '.text':
            '''
            blank
            '''
            cur_section = section.TEXT.value
            global text_seg
            text_seg = TemporaryFile('w+')
            continue

        if cur_section == section.DATA.value:
            # MYCODE
            global data_section_size
            data_section_size+=BYTES_PER_WORD
            # /MYCODE
            '''
            blank
            '''
            if temp[-1] == ':':
                #symbol = symbol_t()
                #symbol.name = temp[:-1]
                #symbol.address = ctypes.c_uint(address).value
                symbol_table_add_entry(temp[:-1], wordcnt+MEM_DATA_START)#symbol)

            word = line.find(".word")

            if word != -1:
                data_seg.write("%s\n" % line[word:])
                wordcnt += BYTES_PER_WORD

        elif cur_section == section.TEXT.value:
            '''
            blank
            '''
            if temp[-1] == ":":
                #symbol = symbol_t()
                #symbol.name = temp[:-1]
                #symbol.address = ctypes.c_uint(address).value
                symbol_table_add_entry(temp[:-1], txtcnt+MEM_TEXT_START)
                continue # This would assert that F: 222 would not occur.
            is1 = True
            if temp == 'la':
                reg = token_line[1].strip().split(',')[0]
                name = line.split(',')[-1].strip() # name of variable
                addr = hex(SYMBOL_TABLE[name])[2:].zfill(8) #'0x'+hex(SYMBOL_TABLE[line.split(',')[-1].strip()])[2:].zfill(8)
                text_seg.write(f'lui {reg}, 0x{addr[:4]}')
                if DEBUG:
                    log(0, 'al! => '+name+': '+addr) # Good! array2 0x1000000c
                    log(0, f'lui {reg}, 0x{addr[:4]}')
                is1 = addr[4:] == '0000'
                if not is1:
                    text_seg.write(f'\nori {reg}, {reg}, 0x{addr[4:]}')
                    log(0, f'ori {reg}, {reg}, 0x{addr[4:]}')
                line=''
            elif temp in ['pop', 'push', 'blt']:
                is1 = False
                line = ''
                if temp == 'blt':
                    args = list(map(lambda csw: csw.strip(), ''.join(token_line[1:]).split(',')))
                    text_seg.write(f'slt $1, {args[0]}, {args[1]}\nbne $1, $0, {args[2]}')
                    if DEBUG:
                        log(0, f'blt! => args: {args}')
                        log(0, f'slt $1, {args[0]}, {args[1]}\nbne $1, $0, {args[2]}')
                else:
                    reg = token_line[1]
                    if temp == 'push':
                        text_seg.write(f'addi $29, $29, -4\nsw {reg}, 0($29)')
                        if DEBUG:
                            log(0, 'push! => rs: '+reg)
                            log(0, f'addi $29, $29, -4\nsw {reg}, 0($29)')
                    else: # 'pop'
                        text_seg.write(f'lw {reg}, 0($29)\naddi $29, $29, 4')
                        if DEBUG:
                            log(0, 'pop! => rs: '+reg)
                            log(0, f'lw {reg}, 0($29)\naddi $29, $29, 4')
            elif temp == 'move':
                line = f'addi {"".join(token_line[1:])}, 0'
                if DEBUG:
                    log(0, f"move! => args: {''.join(token_line[1:])}\n{line}")
            # MYCODE
            global text_section_size
            text_section_size+=BYTES_PER_WORD << (0 if is1 else 1)
            text_seg.write(line+'\n')
            txtcnt += BYTES_PER_WORD << (0 if is1 else 1)
            # /MYCODE
            
        address += BYTES_PER_WORD

#def branch_or_num_to_addr(s):
#    if()

def record_text_section(fout):
    # print text section
    cur_addr = MEM_TEXT_START
    text_seg.seek(0)

    lines = text_seg.readlines()
    
    # MYCODE
    global inst_list
    mips_table = {
        'add':0, 'addi':1, 'addiu':2, 'addu':3, 'and' : 4,
        'andi': 5, 'beq': 6, 'bne' : 7, 'j' : 8, 'jal': 9,
        'jr' : 10, 'lui' : 11, 'lw' : 12, 'nor': 13, 'or' : 14,
        'ori': 15, 'slt' : 16, 'slti' : 17, 'sltiu' : 18, 'sltu' : 19,
        'sll' : 20, 'srl' : 21, 'sw' : 22, 'sub' : 23, 'subu' : 24
    }

    # /MYCODE
    if DEBUG == 1:
        for i in SYMBOL_TABLE:
            log(0, f"name: {i},\taddr: {num_to_hex(SYMBOL_TABLE[i])}")
    for line in lines:
        line = line.strip() # strip the \n at the end of the line.
        inst_type, rs, rt, rd, imm, shamt = '0', 0, 0, 0, 0, 0
        
        # MYCODE
        token_line = line.split()
        op = token_line[0]
        args = list(map(lambda word: word.strip(), ''.join(token_line[1:]).strip().split(','))) # .strip('$')
        # /MYCODE
        '''
        blank: Find the instruction type that matches the line
        '''
        if DEBUG==1: print(line, op, args)

        if token_line[0] in mips_table: # MYCODE + standard MIPS instruction
            inst_obj = inst_list[mips_table[token_line[0]]]
            inst_type = inst_obj.type
            if inst_type == 'R': # finished: 23/10/03
                args = list(map(lambda word: int(word.strip('$')), args)) #assert('5'.strip('$') == '5') # working assertion
                if len(args) == 1: # 'jr'
                    rs = args[0]
                else:
                    rd = args[0]
                    if op in ['sll', 'srl']:
                        rt = args[1]
                        shamt = args[2]
                    else:
                        rs = args[1]
                        rt = args[2]
                '''
                blank
                '''
                if DEBUG:
                    log(1, f"0x" + hex(cur_addr)[2:].zfill(
                        8) + f": op: {inst_obj.op} rs:${rs} rt:${rt} rd:${rd} shamt:{shamt} funct:{inst_obj.funct}")
                fout.write(f'{inst_obj.op}{num_to_bits(rs, 5)}{num_to_bits(rt, 5)}{num_to_bits(rd, 5)}{num_to_bits(shamt, 5)}{inst_obj.funct}')
            if inst_type == 'I':
                if op in ['addi', 'addiu', 'andi', 'ori', 'slti', 'sltiu']:
                    args = list(map(lambda word: someint(word.strip('$')), args))
                    rt = args[0]
                    rs = args[1]
                    imm = args[2]
                elif op in ['beq', 'bne']:
                    branch = args[2]
                    args = list(map(lambda word: someint(word.strip('$')), args[:2]))
                    rt, rs = args[0], args[1]
                    try:
                        imm = someint(branch)
                    except ValueError:
                        imm = SYMBOL_TABLE[branch]-(cur_addr+BYTES_PER_WORD) >> 2 # as words
                elif op in ['lw', 'sw']:
                    rt = args[0] = int(args[0].strip('$'))
                    args[1] = args[1].split('(')
                    imm = someint(args[1][0])
                    rs = int(args[1][1][1:-1]) #assert([4, 5, 6][1:-1] == [5]) # works
                else: # lui
                    args = list(map(lambda word: someint(word.strip('$')), args))
                    rt = args[0]
                    imm = args[1]
                '''
                blank
                '''

                if DEBUG:
                    log(1, f"0x" + hex(cur_addr)
                        [2:].zfill(8) + f": op:{inst_obj.op} rs:${rs} rt:${rt} imm:{num_to_hex(imm, 4)}")
                fout.write(f'{inst_obj.op}{num_to_bits(rs, 5)}{num_to_bits(rt, 5)}{num_to_bits(imm, 16)}')
            if inst_type == 'J':
                '''
                blank
                '''
                try:
                    addr = someint(args[0])
                except ValueError:
                    addr = SYMBOL_TABLE[args[0]] >> 2
                #addr = (cur_addr & (0b1111<<28)) | ((addr<<2) & ((1<<28)-1))
                if DEBUG:
                    log(1, f"0x" + hex(cur_addr)
                        [2:].zfill(8) + f" op:{inst_obj.op} addr:{num_to_hex(addr, 8)}")
                fout.write(f'{inst_obj.op}{num_to_bits(addr, 26)}')
        '''else: # MYCODE + pseudoinstruction (except for la.)
            if op == 'move':
                args = list(map(lambda word: int(word.strip('$')), args))
                fout.write(f"001000{num_to_bits(args[1], 5)}{num_to_bits(args[0], 5)}0000000000000000")
            elif op == "":'''
        
        fout.write("\n")
        cur_addr += BYTES_PER_WORD


def record_data_section(fout):
    cur_addr = MEM_DATA_START
    data_seg.seek(0)

    lines = data_seg.readlines()
    
    for line in lines:
        '''
        blank
        '''
        line = line.strip()
        token_line = line.strip('\n\t').split()
        data = token_line[-1]
        data = int(data, 0)
        fout.write("%s\n" % num_to_bits(data, 32))

        if DEBUG:
            log(1, f"0x" + hex(cur_addr)[2:].zfill(8) + f": {line}")

        cur_addr += BYTES_PER_WORD


def make_binary_file(fout):
    if DEBUG:
        # print assembly code of text section
        text_seg.seek(0)
        lines = text_seg.readlines()
        for line in lines:
            line = line.strip()

    if DEBUG:
        log(1,
            f"text size: {text_section_size}, data size: {data_section_size}")

    # print text_size, data_size
    '''
    blank: Print text section size and data section size
    '''
    fout.write("%s\n" % num_to_bits(int(text_section_size),32))
    fout.write("%s\n" % num_to_bits(int(data_section_size),32))

    record_text_section(fout)
    record_data_section(fout)

#################################################
# # # # # # # # # # # # # # # # # # # # # # # # #
#                                               #
# Please Do not change the below if possible    #
# The TA's are not resposinble for failures     #
# due to changes in the below code.             #
#                                               #
# # # # # # # # # # # # # # # # # # # # # # # # #
#################################################

################################################
# Function: main
#
# Parameters:
#   argc: the number of argument
#   argv[]: the array of a string argument
#
# Return:
#   return success exit value
#
# Info:
#   The typical main function in Python language.
#   It reads system arguments from terminal (or commands)
#   and parse an assembly file(*.s)
#   Then, it converts a certain instruction into
#   object code which is basically binary code
################################################


if __name__ == '__main__':
    argc = len(sys.argv)
    log(1, f"Arguments count: {argc}")

    if argc != 2:
        log(3, f"Usage   : {sys.argv[0]} <*.s>")
        log(3, f"Example : {sys.argv[0]} sample_input/example.s")
        exit(1)

    input_filename = sys.argv[1]
    input_filePath = os.path.join(os.curdir, input_filename)

    if os.path.exists(input_filePath) == False:
        log(3,
            f"No input file {input_filename} exists. Please check the file name and path.")
        exit(1)

    f_in = open(input_filePath, 'r')

    if f_in == None:
        log(3,
            f"Input file {input_filename} is not opened. Please check the file")
        exit(1)

    output_filename = change_file_ext(sys.argv[1])
    output_filePath = os.path.join(os.curdir, output_filename)

    if os.path.exists(output_filePath) == True:
        log(0, f"Output file {output_filename} exists. Remake the file")
        os.remove(output_filePath)
    else:
        log(0, f"Output file {output_filename} does not exist. Make the file")

    f_out = open(output_filePath, 'w')
    if f_out == None:
        log(3,
            f"Output file {output_filename} is not opened. Please check the file")
        exit(1)

    ################################################
    # Let's compelte the below functions!
    #
    #   make_symbol_table(input)
    #   make_binary_file(output)
    ################################################

    make_symbol_table(f_in)
    make_binary_file(f_out)

    f_in.close()
    f_out.close()
