import sys
import re
import ctypes
import formatParser
from formatParser import *

# See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
# for information on Windows APIs.
STD_INPUT_HANDLE        = -10
STD_OUTPUT_HANDLE       = -11
STD_ERROR_HANDLE        = -12

FOREGROUND_BLUE         = 0x01 # text color contains blue.
FOREGROUND_GREEN        = 0x02 # text color contains green.
FOREGROUND_RED          = 0x04 # text color contains red.
FOREGROUND_WHITE        = 0x07 # text color contains white.
FOREGROUND_INTENSITY    = 0x08 # text color is intensified.
BACKGROUND_BLUE         = 0x10 # background color contains blue.
BACKGROUND_GREEN        = 0x20 # background color contains green.
BACKGROUND_RED          = 0x40 # background color contains red.
BACKGROUND_INTENSITY    = 0x80 # background color is intensified.

LINE_NUM_LEN = 6

HEADER_PTR = 0
HEADER_LEN = 33
CIC_PTR = 0
CIC_LEN = 4
TYPE_PTR = CIC_PTR + CIC_LEN
TYPE_LEN = 2
PARAMS_PTR = TYPE_PTR + TYPE_LEN  
PTR_LEN = 2
PARAM_NAME_LEN = 2
PARAM_LEN_LEN = 2  

CIC_PTR2 = 33 + LINE_NUM_LEN
CIC_LEN2 = 4    

MAX_CHUNK_LEN = 32
        
TYPE_DICT = {'01':'IAM', '02':'SAM', '03':'INR', '04':'INF', '05':'COT', '06':'ACM', \
'07':'CON', '08':'FWD', '09':'ANM', '0C':'REL', '0D':'SUS', '0E':'RES', '10':'RLC', \
'11':'CCR', '12':'RSC', '13':'BLO', '14':'UBL', '15':'BLA', '16':'UBA', '17':'GRS', \
'18':'CGB', '19':'CGU', '1A':'CGBA', '1B':'CGUA', '29':'GRA', '2A':'CQM', '2B':'CQR', \
'2C':'CPG', '2F':'CFN', '30':'CRG'}

CAU_DICT = {'1':'Nro no asignado', '2':'Ruta no disponible', '3':'Ruta no disponible', \
'4':'Envio de tono especial', '5':'Error de marcacion de prefijo', \
'16':'Normal', '17':'Ocupado', '18':'No contesta', '19':'No hay respuesta', \
'21':'Rechazada', '22':'Numero cambiado', '27':'Fuera de servicio', \
'28':'Direccion incompleta', '29':'Facilidad rechazada', '31':'Normal sin especificar', \
'34':'No hay circuitos', '38':'Red fuera de servicio', '41':'Fallo temporal de la red', \
'42':'Congestion del equipo', '44':'Canal solicitado no disponible', \
'47':'Recursos no disponibles', '50':'Facilidad no suscripta', '55':'Prohibicion de llamada', \
'57':'Capacidad portadora no autorizada', '58':'Capacidad portadora no disponible',
'63':'Servicio no disponible', '65':'Capacidad portadora no implementada', \
'69':'Facilidad no implementada', '70':'Capacidad portadora restringida', \
'79':'Servicio no implementado', '87':'Usuario no miembro', '88':'Destino incompatible', \
'91':'Selecccion de red invalida', '95':'Mensaje no valido', '97':'Tipo de mensaje no existente', \
'99':'Parametro no existente', '102':'Vencimiento de temporizador', '103':'Parametro no existente', \
'111':'Error de protocolo', '127':'Interfuncionamiento'} 

format = FORMAT_DEFAULT
outputType = '1'
fileNameI = None
fileI2 = None
fileO = None
fileN = 0
filter1 = None

def getFormat(parameter):
    return formatParser.getFormat(format, parameter)

def setColor(color, handle=None):

    if handle == None:
        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    """(color) -> BOOL
    
    Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    """
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

def has1(str1, str2):
    if str1.find(str2) != -1:
        return True
    else:
        return False

def has(str1, str2):
    if re.search(str2, str1):
        return True
    else:
        return False

#Funcion para loguear
def log(line, cic = -1):
    global fileI2
    global fileO
    global fileN

    #Por defecto todas las lineas matchean
    match = True
    #Si hay filtro y es una linea de dump aplicar el filtro para ver si matchea o no
    if filter1 and cic != -1:        
        match = False
        if eval(filter1):
            match = True

    #Si se debe imprimir imprimo
    if outputType in ('1', '3') and match:
        if getFormat(COLOR) == 'y':
            if re.search('IAM', line):
                setColor(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
            elif re.search('ACM|ANM', line):
                setColor(FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_INTENSITY)
            elif re.search('REL|RLC', line):
                setColor(FOREGROUND_GREEN | FOREGROUND_RED | FOREGROUND_INTENSITY)
            elif re.search('RSC|BLO|UBL|BLA|UBA', line):
                setColor(FOREGROUND_BLUE | FOREGROUND_RED | FOREGROUND_INTENSITY)                
            elif re.search('GRS|CGB|CGU|CGBA|CGUA|GRA', line):
                setColor(FOREGROUND_RED  | FOREGROUND_INTENSITY)
            else:
                setColor(FOREGROUND_WHITE)
                    
        print line
            
        if getFormat(COLOR) == 'y':
            setColor(FOREGROUND_WHITE)

    if outputType in ('2', '3') and fileO:

        fileO.write(line + '\n')
        if getFormat(FILE_MAX_LEN) != '00' and fileO.tell() > int(getFormat(FILE_MAX_LEN)) * 1024 * 1024:
            fileN += 1
            if getFormat(FILE_MAX_N) != '00' and fileN > int(getFormat(FILE_MAX_N)):
                fileN = 0

            if fileI2:
                fileI2.close()
                fileNameI2 = fileNameI + '_' + ('0' * (2 - len(str(fileN)))) + str(fileN) 
                fileI2 = open(fileNameI2, 'w')                 

            if fileO:
                fileO.close()
                fileNameO = fileNameI + '_' + ('0' * (2 - len(str(fileN)))) + str(fileN) + '.out'
                fileO = open(fileNameO, 'w') 
                    
#Loguea el encabezado de la llamada
def getLogTopHeading():
    str1 = ''
  
    if getFormat(TYPE) in ('1', '2'):
        str1 += 'Lin'
        str1 += (' '* (LINE_NUM_LEN - len(str1)))         
        str1 += 'Hora       Prot   Dir Pto-Cod    Mensaje'
    elif getFormat(TYPE) in ('3', '4', '5', '6'):
        str1 += 'Lin'
        str1 += (' '* (LINE_NUM_LEN - len(str1)))         
        str1 += 'Hora       Prot   Dir Pto-Cod     Cic  Mensaje'            
    return str1

#Funcion para obtener la direccion del mensaje
def getDirection(line):
    return line[DIRECTION_PTR : DIRECTION_PTR + DIRECTION_LEN]

#Funcion para obtener el comando del mensaje
def getType(message):
    type = message[TYPE_PTR:TYPE_PTR + TYPE_LEN]
    
    return type

#Funcion para devolver un string con el nombre del comando
def getTypeDesc(type):

    typeDesc = ''
    try:
        typeDesc = TYPE_DICT[type]
    except:
        pass
            
    return typeDesc 

#Funcion para realizar un ajuste por zona horaria
def adjustShiftTime(header):
    shiftTime = int(getFormat(TIME_SHIFT))
    if shiftTime != 0:
        hour = header[0:header.find(':')]
        hour = int(hour) + shiftTime
        if hour < 0:
            hour += 24 
        elif hour > 23:
            hour -= 24
        
        hour = str(hour)
        hour = ('0'*(2-len(hour))) + hour
        header = hour + header[header.find(':'):]
    
    return header 
    
#Funcion para dar vuelta los bytes de dnis y ani del mensaje IAM
def swapBytes(param):
    i = 0
    result = ''
    while i < len(param):
        try:
            result = result + param[i+1] + param[i]
            i = i + 2
        except:
            fileO.write('Exception: param: ' + str(param) + ' len: ' + str(len(param)) + ' i: ' + str(i) + '\n') 
            i = len(param) + 1
    return result
            
#Funcion para parsear el IAM
#Las posiciones y longitudes estan en caracteres (NO en Bytes)
def parseIAM(message):
    parsedMessage = ''
    if getTypeDesc(getType(message)) == 'IAM':
        
        cic = int(message[0:2], 16) + int(message[3:4], 16) *  256
        
        #Parametro CPN - LDO
        #Para buscar el parametro CPN - LDO en un IAM debo buscar su puntero, ya 
        #que es un parametro obligatorio variable
        #El puntero en cuestion se encuentra despues de los parametros obligatorios
        #de longitud fija nat, adl, cat y rmt cuyas longitudes en caracteres son
        # 2, 4, 2, 2 respectivamente.
        #Con este puntero busco el inicio del parametro, al ser un parametro variable
        #los primeros dos caracteres son la logitud del mismo, y a partir del proximo
        #caracter se encuentra el parametro propiamente dicho        
        
        #Posicion del puntero al parametro
        posPtr = PARAMS_PTR + 2 + 4 + 2 + 2
        #Puntero al parametro
        paramPtr = int(message[posPtr : posPtr + PTR_LEN], 16) * 2
        if paramPtr != 4:
            log('Alerta, puntero al parametro cldPtyNum no es 2') 
        #Posicion del parametro a analizar
        posParam = posPtr + paramPtr
        #Logitud del parametro
        lenParam = int(message[posParam : posParam + PARAM_LEN_LEN], 16) * 2      
        #Parametro
        param = message[posParam + PARAM_LEN_LEN : posParam + PARAM_LEN_LEN + lenParam]
        natDnis = str(int(param[0 : 2], 16) & 127)   
        dnis = swapBytes(param[4:len(param)])
        
        #log('cldPtyNum: ' + param + ' dnis: ' + dnis)

        #Parametro CGN - LTE 
        #Para buscar el parametro CGN - LTE en un IAM debo analizar los parametros
        #variables buscando el nombre del parametro en cuestion.
        #Para tal fin ubico el primer parametro opcional, para lo cual sumo a la 
        #posicion del puntero de la parte facultativa el valor de dicho puntero.
        #A partir de alli leo los dos primeros caracteres que son el nombre del
        #parametro y los dos siguientes que son la longitud hasta encontrar el
        #parametro deseado
        
        #El IAM tiene solo un parametro obligatorio variable, por lo que el proximo
        #puntero es el puntero a la parte facultativa
        #Posicion del puntero al parametro
        posPtr = posPtr + PTR_LEN
        #Puntero al parametro
        paramPtr = int(message[posPtr : posPtr + PTR_LEN], 16) * 2
        #Posicion del parametro a analizar
        posParam = posPtr + paramPtr
        #Nombre del parametro a analizar
        nameParam = ''
        #Busqueda del parametro CGN - LTE = '0A'
        while nameParam != '0A' and nameParam != '00':
            #Si no es la primera iteracion calcular la posicion del parametro
            if nameParam != '':
                #Se calcula la posicion del parametro a analizar
                posParam = posParam + PARAM_NAME_LEN + PARAM_LEN_LEN + lenParam 
            #Nombre del parametro, si es '00' no hay mas parametros
            nameParam = message[posParam : posParam + PARAM_NAME_LEN]
            if nameParam != '00':
                #Logitud del parametro
                lenParam = int(message[posParam  + PARAM_NAME_LEN : posParam + PARAM_NAME_LEN + PARAM_LEN_LEN], 16) * 2
                #Parametro a analizar
                param = message[posParam + PARAM_NAME_LEN + PARAM_LEN_LEN : posParam + PARAM_NAME_LEN + PARAM_LEN_LEN + lenParam]
                paramTotalLenFix = 0
        
        #Si no se encontro el parametro reportar error
        if nameParam != '0A':
            log('Alerta, parametro clgPtyNum no encontrado')
                                
        natAni = str(int(param[0 : 2], 16) & 127)   
        ani = swapBytes(param[4:len(param)])
        
        #log('clgPtyNum: ' + param + ' ani: ' + ani, ouputFile)
        
        #parsedMessage = 'circ: ' + str(cic) + ' dnis: ' + dnis + ' nat: ' + natDnis + ' ani: ' + ani + ' nat: ' + natAni
        parsedMessage = 'dnis: ' + dnis + ' nat: ' + natDnis + ' ani: ' + ani + ' nat: ' + natAni

        '''
        DNIS_LEN = 21   
        NAT_LEN = 7
        LEN = DNIS_LEN
        ANI_LEN = 15
        
        parsedMessage = 'dnis: ' + dnis
        parsedMessage = parsedMessage + (' ' * (LEN - len(parsedMessage)))
        LEN = DNIS_LEN + NAT_LEN
        parsedMessage = parsedMessage + 'nat: ' + natDnis
        parsedMessage = parsedMessage + (' ' * (LEN - len(parsedMessage)))
        LEN = DNIS_LEN + NAT_LEN + ANI_LEN
        parsedMessage = parsedMessage + 'ani: ' + ani
        parsedMessage = parsedMessage + (' ' * (LEN - len(parsedMessage)))
        parsedMessage = parsedMessage + ' nat: ' + natAni
        '''
        
    return parsedMessage

#Funcion para parsear el ACM
#Las posiciones y longitudes estan en caracteres (NO en Bytes)
def parseACM(message):
    parsedMessage = ''
    if getTypeDesc(getType(message)) == 'ACM':
       
        #Parametro BCI - ATR
        posParam = PARAMS_PTR
        param = message[posParam : posParam + 4]
        chrgInd = str(int(param[0 : 2], 16) & 3)
        cadPtyCatInd = str(int(param[0 : 2], 16) & 48)
                       
        parsedMessage = 'chrInd: ' + chrgInd + ' cadPtyCatInd: ' + cadPtyCatInd
        
    return parsedMessage

#Funcion para parsear el REL
#Las posiciones y longitudes estan en caracteres (NO en Bytes)
def parseREL(message):
    parsedMessage = ''
    if getTypeDesc(getType(message)) == 'REL':
        
        #Parametro CAU - CAU
        posPtr = PARAMS_PTR
        paramPtr = int(message[posPtr : posPtr + PTR_LEN], 16) * 2
        if paramPtr != 4:
            log('Alerta, el puntero al parametro cau no es 2') 
        posParam = posPtr + paramPtr
        lenParam = int(message[posParam : posParam + PARAM_LEN_LEN], 16) * 2                   
        param = message[posParam + PARAM_LEN_LEN : posParam + PARAM_LEN_LEN + lenParam]
        #Parche para release con len = 3 bytes (6 caracteres), es correcto?
        if lenParam == 4:
            cauVal = str(int(param[2 : 4], 16) & 127)
        else: #Par
            cauVal = str(int(param[4 : 6], 16) & 127)           

        cauValStr = ''
        try:
            cauValStr = CAU_DICT[cauVal]
        except:
            pass
                       
        parsedMessage = 'cau: ' + cauVal + ' (' + cauValStr + ')'
        
    return parsedMessage

#Funcion para parsear el GR
#Las posiciones y longitudes estan en caracteres (NO en Bytes)
def parseGR(message):
    parsedMessage = ''
          
    if getTypeDesc(getType(message)) in ('GRS', 'GRA'):          
        #pointCodeM = getHeader(message)[0:-4].strip()
        #cicM = int(getHeader(message)[-4:-2], 16) + int(getHeader(message)[-1:], 16) *  256
            
        cic = int(message[0:2], 16) + int(message[3:4], 16) *  256
        posPtr = PARAMS_PTR
        paramPtr = int(message[posPtr : posPtr + PTR_LEN], 16) * 2
        posParam = posPtr + paramPtr
        lenParam = int(message[posParam : posParam + PARAM_LEN_LEN], 16) * 2                   
        param = message[posParam + PARAM_LEN_LEN : posParam + PARAM_LEN_LEN + lenParam]
        group = param[0:2]
        groupVal = int(group, 16)
        
        parsedMessage = 'range: ' + str(groupVal) 

    return parsedMessage

#Funcion para parsear el GB
#Las posiciones y longitudes estan en caracteres (NO en Bytes)
def parseGB(message):
    parsedMessage = ''
          
    if getTypeDesc(getType(message)) in ('CGB', 'CGU', 'CGBA', 'CGUA'):          
        #pointCodeM = getHeader(message)[0:-4].strip()
        #cicM = int(getHeader(message)[-4:-2], 16) + int(getHeader(message)[-1:], 16) *  256
            
        cic = int(message[0:2], 16) + int(message[3:4], 16) *  256
        posPtr = PARAMS_PTR + 2
        paramPtr = int(message[posPtr : posPtr + PTR_LEN], 16) * 2
        posParam = posPtr + paramPtr
        lenParam = int(message[posParam : posParam + PARAM_LEN_LEN], 16) * 2                   
        param = message[posParam + PARAM_LEN_LEN : posParam + PARAM_LEN_LEN + lenParam]
        group = param[0:2]
        groupVal = int(group, 16)
        
        parsedMessage = 'range: ' + str(groupVal) 

    return parsedMessage

#Funcion para expandir un filtro y que pueda ser evaluado con eval()
def expandFilter(filter1):
    if filter1:
        '''
        filter1 = filter1.replace('!', ' not ')
        filter1 = filter1.replace('&', ' and ')
        filter1 = filter1.replace('|', ' or ')
        '''
        filter1 = filter1.replace('has(', ' has(line, ')

        #log('Expanded filter: ' + filter1)
    
    return filter1

def processLine(lineI, header, message, i):
    lineI = lineI.strip()
    messageEnd = False
    #Si es un header lo proceso
    if re.search('<--', lineI) or re.search('-->',lineI):           
        #print 'HEADER: ' + lineI

        #Saco el ultimo caracter de header '\n'
        header = lineI[0:-1]
        header = adjustShiftTime(header)
        #Compelto el header con ' ' para que el mensaje empiece siempre en la misma posicion
        header = header + (' '*(HEADER_LEN-len(header))) 
        #Inicio el mensaje
        message = ''
    #Si es parte de un mensaje lo apendo a lo que ya tenia 
    elif re.search('[0-9A-F][0-9A-F] +', lineI):
        #print 'COMMAND: ' + lineI
    
        #Tomo la parte valida del mensaje 48 caracteres y le quito los ' '
        messageChunk = lineI[0:48].replace(' ', '')              
        message = message + messageChunk

        #Si el chunk de mensaje es menor al tamanio maximo de chunk el mensaje esta completo
        if len(messageChunk) < MAX_CHUNK_LEN:
            messageEnd = True
        
    elif lineI == '' and message != '':
        #print 'LINE END: ' + lineI
        #Obtengo el comando
        
        messageEnd = True     
          
    else:
        #print 'ELSE: *' + lineI + '*'
        pass
        
    if messageEnd and message != '':
        type = getType(message)

        messageParsed = '' 
        #Parseo el mensaje
        if getTypeDesc(type) == 'IAM': 
            messageParsed = parseIAM(message)
        if getTypeDesc(type) == 'ACM':
            messageParsed = parseACM(message)
        elif getTypeDesc(type) == 'REL':
            messageParsed = parseREL(message)
        elif getTypeDesc(type) in ('GRS', 'GRA'): 
            messageParsed = parseGR(message)
        elif getTypeDesc(type) in ('CGB', 'CGU', 'CGBA', 'CGUA'): 
            messageParsed = parseGB(message)
        
        if header != '':
            lineN = ''
            #Si de debe imprimir el numero de linea lo agrego, sino pongo espacios en blanco
            if getFormat(LINE_N) == 'y':
                leni = len(str(i))
                lineN = str(i) + (' '*(LINE_NUM_LEN-leni))
            else:
                lineN = (' '*(LINE_NUM_LEN))            
            #Calculo el numero de cic tanto en hexa como en decimal
            cicHexa = message[CIC_PTR:CIC_LEN]
            cicDecimal = str(int(cicHexa[2:4]+cicHexa[0:2], 16))
            cicDecimal = (' '*(4-len(cicDecimal))) + cicDecimal
            cic = cicDecimal              
            if getFormat(CIC) == 'h':
                cic = cicHexa
            if getFormat(TYPE) in ('1'):
                log(lineN + header + message, cicDecimal)
            elif getFormat(TYPE) in ('2'):
                log(lineN + header + message, cicDecimal)
                #log(lineN + header + message[0:4] + ': ' + getTypeDesc(type) + ' ' + messageParsed, int(cicDecimal))                
                log(lineN + header + cic + ': ' + getTypeDesc(type) + ' ' + messageParsed, int(cicDecimal))
            elif getFormat(TYPE) in ('3', '4', '5', '6'):
                #log(lineN + header + message[0:4] + ': ' + getTypeDesc(type) + ' ' + messageParsed, int(cicDecimal))
                log(lineN + header + cic + ': ' + getTypeDesc(type) + ' ' + messageParsed, int(cicDecimal))
            i += 1    
            header = ''
            message = ''
    
    return header, message

###############################################################################
#                               Main
###############################################################################
def pydump(format_, fileNameI_, outputType_ = None, filter1_ = None):
    print 'PyDump: Dump SS7 trace'

    global format   
    global outputType
    global fileNameI
    global fileI2
    global fileO
    global fileN
    global filter1

    fileI = None
    fileI2 = None

    if format_:
        format = format_
        
    if fileNameI_:
        fileNameI = fileNameI_
        
    if outputType_:
        outputType = outputType_
        
    if filter1_:
        filter1 = expandFilter(filter1_)

    print 'PyDump format: ' + format + ' fileNameI: ' + fileNameI +  ' outputType: ' + outputType
    
    if fileNameI == 'stdin':
        fileI = sys.stdin
        if outputType in ('2', '3'): 
            if getFormat(FILE_MAX_LEN) == '00':
                fileNameI2 = fileNameI
            else:
                fileNameI2 = fileNameI + '_00'
            fileI2 = open(fileNameI2, 'w')
    else:
        fileI = open(fileNameI, 'r')

    isFileSS7Trace = True
    try:
        if fileNameI[-3:] == 'out':
            isFileSS7Trace = False    
    except:
        pass
        
    if isFileSS7Trace:
        if outputType in ('2', '3'):  
            if getFormat(FILE_MAX_LEN) == '00':
                fileNameO = fileNameI + '.out'
            else:
                fileNameO = fileNameI + '_00.out'
            
            fileO = open(fileNameO, 'w')
        
    if isFileSS7Trace:
        log(getLogTopHeading())    
    
    i=0
    lineI = fileI.readline()
    if fileI2:
        fileI2.write(lineI)
    header = ''
    message = ''
    lastLine = False
    while lineI:
        #En caso de ser un archivo filSS7Trace proceso la linea, en cado contrario logueo solamente
        if isFileSS7Trace:
            header, message = processLine(lineI, header, message, i)
        elif not lastLine:
            cic = -1
            try:
                cic = int(lineI[CIC_PTR2 : CIC_PTR2 + CIC_LEN2])
            except:
                pass
            log(lineI.strip(), cic)
        
        #Si no es la ultima linea leo una nueva linea para procesarla
        #en caso de que la lectura devuelva vacio, genero una ultima iteracion para imprimir lo que habia
        if not lastLine:
            lineI = fileI.readline()
            if fileI2:
                fileI2.write(lineI)            
            if not lineI:
                lineI = '\n'
                lastLine = True      
        else:
            lineI = None

    #Cierro los archivos abiertos
    if fileI:                
        fileI.close()
    if fileI2:
        fileI2.close()
    if fileO:
        fileO.close()

