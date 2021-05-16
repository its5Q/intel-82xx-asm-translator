# Made by https://github.com/its5Q and https://github.com/Monika0000

import sys
import re

command_counter = 0
labels = []

operations = {
                'mov': '01{ri}{rj}',# Копирование значения из регистра rj в ri
                'mvi': '00{ri}110 {b2}', # Копирование значения регистра в аккумулятор
                'add': '10000{ri}', # Прибавление значения регистра к аккумулятору
                'sub': '10010{ri}', # Вычитание значения регистра от аккумулятора
                'hlt': '01110110',  # Остановка выполнения
                'inr': '00{ri}100', # Инкремент регистра
                'dcr': '00{ri}101', # Декремент регистра
                'sma': '00101111',  # Инверсия значения аккумулятора
                
                'nop': '00000000',
                
                'ana': '10100{ri}',
                'ora': '10110{ri}',

                'lda': '00111010 {b3} {b2}',  # Запись значений из ячейки в аккумулятор
                'sta': '00110010 {b3} {b2}',  # Запись значений аккумулятора в ячейку
                'lxi': '00{ri}001 {b3} {b2}', # загрузка пары регистров. ri <= b3, ri+1 <= b2
                'rlc': '00000111', # сдвиг влево
                'rrc': '00001111', # сдвиг вправо
                
                'jmp': '11000011 {label} 00',
                'jpo': '11100010 {label}', # прыжок если нечтное 
                'jpz': '11000010 {label}', # прыжок если не ноль
                'jpe': '11101010 {label}', # прыжок если четное
                'jm':  '11111010 {label}', # прыжок если минус
                'jp':  '11110010 {label}', # прыжок если плюс
            }

registers = {
                'a': '111', # Аккумулятор
                'b': '000',
                'c': '001',
                'd': '010',
                'e': '011',
                'h': '100',
                'l': '101',
                'm': '110'
            }

#op_regex = re.compile(r'^([a-zA-Z]{2,4}) ?([a-eA-EhHlL]?[0-9a-fA-F]{0,2})?\,? ?([a-eA-EhHlL]?[0-9a-fA-F]{0,2})')
op_regex = re.compile(r'^([a-zA-Z]{2,4}) ?([a-zA-ZhHlL]?[0-9a-xA-X]{0,2})?\,? ?([a-eA-EhHlL]?[0-9a-fA-F]{0,2})?([0-9a-fA-F]{0,2})')

def get_label_code(label_name):
    for label in labels:
        if label[0] == label_name:
            return label[1]

def link_code(preCompiled):
    for line in preCompiled:
        for i in range(0, len(line)):
            if line[i] == 'label:': 
                hex_label = get_label_code(line[i + 1])
                
                #print('[', hex_label , ']')
                #print('[', format(hex_label, '04x') , ']')
                
                b3 = str(format(hex_label, '04x'))[2:]
                b2 = str(format(hex_label, '04x'))[:2]
                
                line[i]     = b3
                line[i + 1] = b2
            else:
                line[i] = format(int(line[i], 2), '02x')

    return preCompiled

def op_to_binary(op: str):
    # Дефолтные значения аргументов
    ri = '111'
    rj = '111'
    b2 = 0
    b3 = 0

    parsed_op = op_regex.match(op)

    command = parsed_op.group(1)
    arg1    = parsed_op.group(2)
    arg2    = parsed_op.group(3)
    arg3    = parsed_op.group(4)

    binary_command  = operations.get(command)
    
    if command[0] == 'j':
        print('Jump to: ' + arg1)
        binary_command = binary_command.replace('{label}', 'label: ' + arg1)
        pass
    
    if not binary_command:
        print(f'{op} not implemented')
        return ''
    
    if not arg3:
        ri = registers.get(arg1, '')     
        rj = registers.get(arg2, '')

        if not ri:
            try:
                b2 = int(arg1, 16)
            except Exception:
                pass
            
            try:
                b3 = int(arg2, 16)
            except Exception:
                pass
        elif not rj:
            try:
                b2 = int(arg2, 16)
            except Exception:
                pass
        
        binary_command = binary_command.replace('{ri}', ri).replace('{rj}', rj).replace('{b2}', format(b2, '08b')).replace('{b3}', format(b3, '08b'))
    else:
        ri = registers.get(arg1, '')
        b3 = int(arg2, 16)
        b2 = int(arg3, 16)
        
        binary_command = binary_command.replace('{ri}', ri).replace('{b2}', format(b2, '08b')).replace('{b3}', format(b3, '08b'))

    return binary_command


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Invalid usage!\nUsage: python {sys.argv[0]} <input file> <output file>")
        sys.exit()
    
    input_path  = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, 'r', errors='ignore') as ifile:
        input_lines = [line.strip().lower() for line in ifile]
    
    counter = 0
    
    with open(output_path, 'w', errors='ignore') as ofile:
        preCompiledCode = []
        
        for line in input_lines:
            if not line or line.startswith('#'):
                continue
            
            labelPos = line.find(':')
            if labelPos != -1:
                label = [line[:labelPos], command_counter]
                
                if len(label[0]) > 2:
                    print('Label is very large!');
                    
                labels.append(label)
                print('Label: ', label)
                line = line[labelPos + 2:]
                pass
            
            op_binary = op_to_binary(line)
            
            #if op_binary:
            #    counter += 1
            #    print(op_binary)
            #    print(counter, end = '.\t')
            #    for byte in op_binary.split(' '):
            #        command_counter += 1
            #        _hex = format(int(byte, 2), '02x')
            #        print(_hex.upper(), end = ' ')
            #        ofile.write(_hex + ' ')
            #    print()
            #    ofile.write('\n')
            
            if op_binary:
                operation = []
                for byte in op_binary.split(' '):                    
                    command_counter += 1
                    operation.append(byte)
                    print(byte, end = ' ')
                print()
                preCompiledCode.append(operation)
            pass
        
        print('\nPrecompiled code:', preCompiledCode)
        
        linked_code = link_code(preCompiledCode)
        
        print('\nLinked code:', linked_code, '\n')
        
        for i in range(0, len(linked_code)):
            print(i, end = '. '); 
            for j in range(0, len(linked_code[i])):
                _hex = linked_code[i][j].upper()
                print(_hex, end = ' ') 
                ofile.write(_hex + ' ')
            print()
            ofile.write('\n')
        
        
