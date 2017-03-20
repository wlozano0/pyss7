TYPE = 0
CIC = 1
LINE_N = 2
CALLS = 3
TIME_SHIFT = 4
COLOR = 5
FILE_MAX_LEN = 6
FILE_MAX_N = 7

FORMAT_DEFAULT = '3dnn+00y0000'
    
def getFormat(format, parameter):
    try:
        if parameter == TYPE:
            return format[0]
        elif parameter == CIC:
            return format[1]
        elif parameter == LINE_N:
            return format[2]
        elif parameter == CALLS:
            return format[3]
        elif parameter == TIME_SHIFT:
            return format[4:7]
        elif parameter == COLOR:
            return format[7]
        elif parameter == FILE_MAX_LEN:
            return format[8:10]
        elif parameter == FILE_MAX_N:
            return format[10:12]
        return ''
    except:
        return ''    
    
def checkFormat(format):
    format = format.lower()
    
    if len(format) == 0:
        format += FORMAT_DEFAULT[0]
    if len(format) == 1:
        format += FORMAT_DEFAULT[1]
    if len(format) == 2:
        format += FORMAT_DEFAULT[2]            
    if len(format) == 3:
        format += FORMAT_DEFAULT[3]                
    if len(format) >= 4 and len(format) <= 6:
        format = format[0:4] + FORMAT_DEFAULT[4:7]                
    if len(format) == 7:
        format += FORMAT_DEFAULT[7]    
    if len(format) >= 8 and len(format) <= 9:
        format = format[0:8] + FORMAT_DEFAULT[8:10]
    if len(format) >= 10 and len(format) <= 11:
        format = format[0:10] + FORMAT_DEFAULT[10:12]           
            
    if getFormat(format, FILE_MAX_LEN) != '00':
        #format[3] = 'n'
        format = format[0:3] + 'n' + format[4:]        

    if getFormat(format, TYPE) not in ('1', '2', '3', '4', '5', '6'):
        print 'Error en parametro 1, formato de salida, caracter 0'
        format = ''

    if getFormat(format, CIC) not in ('d', 'h'):
        print 'Error en parametro 1, formato de salida, caracter 1'
        format = ''    

    if getFormat(format, LINE_N) not in ('y', 'n'):
        print 'Error en parametro 1, formato de salida, caracter 2'
        format = ''    

    if getFormat(format, CALLS) not in ('y', 'n'):
        print 'Error en parametro 1, formato de salida, caracter 3'
        format = ''    

    if getFormat(format, COLOR) not in ('y', 'n'):
        print 'Error en parametro 1, formato de salida, caracter 7'
        format = '' 

    return format
