import sys
import argparse
import formatParser
from formatParser import *
import pydump
import pycall

help_main = '''
pyss7: Dumpea y agrupa por llamadas un trace ss7 generado por el comando ss7trace

Uso:
pyss7 -i archivo -f formato -o salida -f1 filtro1 -f2 filtro2
'''

help_input = '''
archivo: Nombre del archivo de entrada, en caso de que el archivo sea .out se asume que es un dump y solo se agrupa por llamadas, en caso se ser stdin o nada se toma la entrada estandar (opcional)
'''

help_format = '''
formato: Formato de la salida indicado por una serie de caracteres (opcional)
    A continuacion se muestra el significado de cada caracter o conjunto de caracteres empezando por el 0 PRIMER CARACTER
    
    formato[0] Tipo de formato de salida (requerido)
        1: Formato con una linea por mensaje
        2: Idem v1 + parseo de mensajes
        3: Formato solo con mensajes parseados
        4: Idem v3 con formato compacto
        5: Formato con informacion basica de llamada 
        6: Formato con informacion basica de llamada formato tabla
        
        por defect se usa la opcion 3
    
    formato[1] Formato de los numeros de cic (opcional)
        h: Numero de cic en hexadecimal
        d: Numero de cic en decimal

        por defecto se usa la opcion d

    formato[2] Impresion de numero de linea (opcional)
        y: Imprimir numero de linea
        n: No imprimir numero de linea

        por defecto se usa la opcion n

    formato[3] Generacion de agrupacion de llamadas (opcional)
        y: Generar agrupacion de llamadas
        n: No generar agrupacion de llamadas

        por defecto se usa la opcion n

    formato[4:7] Desplazamiento horario (ejemplo -03) (opcional)
        por defecto se usa la opcion +00        

    formato[7] Uso de colores en salida por pantalla (opcional)
        y: Usar colores
        n: No usar colores
        
        por defecto se usa la opcion y        
    
    formato[8:10] Tamanio de archivo maximo, superado este se genera un nuevo archivo (opcional)

    formato[10:12] Cantidad maxima de archivos, superado este se pisa el primer archivo (opcional)   
'''
help_output = '''
salida: Tipo salida (opcional)

    Tipos de salida
        1: Salida por pantalla
        2: Salida por archivo
        3: Salida por pantalla y archivo
        
    por defecto se usa la opcion 1
'''

help_filter1 = '''
filtro1: Filtro de mensajes para dumpeo por pantalla (opcional)
'''
help_filter2 = '''    
filtro2: Filtro de mensajes para agrupacion de call por pantalla (opcional)
'''

help_example = '''
Ejemplo
    pyss7 -i trace.txt -f 3 -o 3

    Dumpea el archivo trace.txt con el formato 3 y envia su salida tanto a pantalla como a archivo         
'''

help = help_main + '\n' + help_input + '\n' + help_format + '\n' + help_output + '\n' + help_filter1 + '\n' + help_filter2 + '\n' + help_example

format = None

def getFormat(parameter):
    return formatParser.getFormat(format, parameter)

isFileSS7Trace = True   

parser = argparse.ArgumentParser(description='Dumpea y agrupa por llamadas un trace ss7 generado por el comando ss7trace')
#parser = argparse.ArgumentParser(usage=help)    
parser.add_argument('--input', '-i', default='stdin', help='Nombre del archivo de entrada')
parser.add_argument('--format', '-f', default='', help='Formato de la salida indicado por una serie de caracteres')
parser.add_argument('--output', '-o', default='1', help='Tipo salida')
parser.add_argument('--filter1', '-f1', help='Filtro de mensajes para dumpeo por pantalla')    
parser.add_argument('--filter2', '-f2', help='Filtro de mensajes para agrupacion de call por pantalla')    
parser.add_argument('--extended_help', '-eh', nargs='?', const='1', default=None, help='Mostar ayuda extendida')    
argParsed = parser.parse_args() 

#print str(argParsed)   

fileNameI = argParsed.input
format = argParsed.format
outputType = argParsed.output
filter1 = argParsed.filter1
filter2 = argParsed.filter2
extendedHelp = argParsed.extended_help

if extendedHelp:
    print help
    sys.exit(0)

format = checkFormat(format)

if format == '':
    print help
    sys.exit(0)

if fileNameI[-4:] == '.out':
    isFileSS7Trace = False
    
#Dumpeo el archivo, en caso de que no sea un fileSS7Trace solo se imprimira por pantalla
if isFileSS7Trace or (not isFileSS7Trace and getFormat(CALLS) == 'n' and outputType in ('1')):
    pydump.pydump(format, fileNameI, outputType, filter1)

if isFileSS7Trace:
    fileNameI = fileNameI + '.out'
    
if ((isFileSS7Trace and outputType in ('2', '3')) or not isFileSS7Trace) and getFormat(CALLS) == 'y':
    #Llamada a pycall
    pycall.pycall(format, fileNameI, outputType, filter2)

