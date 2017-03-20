# coding: latin-1
import sys
import time
import re
import formatParser
from formatParser import *

LINE_NUM_PTR = 0 
LINE_NUM_LEN = 6
TIME_PTR = 0 + LINE_NUM_LEN
TIME_LEN = 10
DIRECTION_PTR = 18 + LINE_NUM_LEN
DIRECTION_LEN = 3
HEADER_PTR = 22 + LINE_NUM_LEN
HEADER_LEN = 15
POINT_CODE_PTR = HEADER_PTR
POINT_CODE_LEN = 10
CIC_PTR = 33 + LINE_NUM_LEN
CIC_LEN = 4
TYPE_PTR = CIC_PTR + CIC_LEN
TYPE_LEN = 2 
PARAMS_PTR = TYPE_PTR + TYPE_LEN
TYPE_PTR2 = CIC_PTR + CIC_LEN + 2
TYPE_LEN2 = 4
PARAMS_PTR2 = TYPE_PTR2 + TYPE_LEN2 
REL_CAUSE_PTR = 48 + LINE_NUM_LEN

TYPE_DICT = {'01':'IAM', '02':'SAM', '03':'INR', '04':'INF', '05':'COT', '06':'ACM', \
'07':'CON', '08':'FWD', '09':'ANM', '0C':'REL', '0D':'SUS', '0E':'RES', '10':'RLC', \
'11':'CCR', '12':'RSC', '13':'BLO', '14':'UBL', '15':'BLA', '16':'UBA', '17':'GRS', \
'18':'CGB', '19':'CGU', '1A':'CGBA', '1B':'CGUA', '29':'GRA', '2A':'CQM', '2B':'CQR', \
'2C':'CPG', '2F':'CFN', '30':'CRG'}

GROUP_MESSAGES = ('GRS', 'CGB', 'CGU', 'CGBA', 'CGUA', 'GRA')

STATISTICS_KEYS = [\
'entrantes concretadas', 'entrantes no concretadas', 'salientes concretadas', \
'salientes no concretadas', 'liberacion normal', 'liberacion ocupado', \
'liberacion no contesta',  'liberacion otras', 'no liberadas', 'liberacion sin rel', 'liberacion forzada']

format = FORMAT_DEFAULT
outputType = '1'
fileO = None
filter2 = None

linesI = None
processedMessages = None
statistics = None

def getFormat(parameter):
    return formatParser.getFormat(format, parameter)

#Funcion para loguear
#toStdout = 1: siempre, 2: nunca si hay filtro, 3: depende de filtro
def log(line, toStdout = 1):
    if outputType in ('1', '3') and (toStdout == 1 or (toStdout == 2 and not filter) or (toStdout == 3 and (not filter2 or re.search(filter2, line)))):
        print line

    if outputType in ('2', '3'):
        if fileO:
            fileO.write(line + '\n')
        
#Funcion para obtener una linea de la lista de lineas, devuelve None en caso de
#que no exista dicha linea
def getLine(lines, i):
    line = None
    try:
        line = lines[i]
        line = line[0:-1]
    except:
        pass
        
    return line

#Obtiene el nro de linea
def getLineNum(line):
    return line[LINE_NUM_PTR : LINE_NUM_PTR + LINE_NUM_LEN]

#Obtiene el campo tiempo del trace
def getTime(line):
    return line[TIME_PTR : TIME_PTR + TIME_LEN]
    
#Obtiene la direccion del mensaje
def getDirection(line):
    return line[DIRECTION_PTR : DIRECTION_PTR + DIRECTION_LEN]

#Obtiene el header de mensaje (punto de codigo y cic)
def getHeader(line):
    return line[HEADER_PTR : HEADER_PTR + HEADER_LEN]

def getPointCode(line):
    return line[POINT_CODE_PTR : POINT_CODE_PTR + POINT_CODE_LEN].strip()

#Obtiene el cic del mensaje
def getCircuit(line):
    return line[CIC_PTR : CIC_PTR + CIC_LEN]    

#Obtiene el valor del cic
def getCircuitVal(cic):
    if getFormat(CIC) == 'h':
        return int(cic[0:2], 16) + int(cic[3:4], 16) *  256
    elif getFormat(CIC) == 'd':
        return int(cic)
    
#Obtiene el tipo de mensaje
def getType(line):
    typeStr = ''
    if getFormat(TYPE) in ('1', '2'):
        type = line[TYPE_PTR : TYPE_PTR + TYPE_LEN]
        try:
            typeStr = TYPE_DICT[type]
        except:
            pass
    elif getFormat(TYPE) in ('3', '4', '5', '6'):
        typeStr = line[TYPE_PTR2 : TYPE_PTR2+TYPE_LEN2].strip()
    else:
        log('Error, format type no soportada')
     
    return typeStr      

#Obtiene los parametros del mensaje
def getParams(line):
    parmas = ''
    if getFormat(TYPE) in ('1', '2'): 
        params = line[PARAMS_PTR : ].strip()
    if getFormat(TYPE) in ('3', '4', '5', '6'):
        params = line[PARAMS_PTR2 : ].strip()
    else:
        log('Error, format type no soportada')
        
    return params

#Obtiene la causa de liberacion
def getReleaseCause(line):
    return line[REL_CAUSE_PTR : ]

#Obtiene un timet a partir de un string time
def getTimeT(time1):
    date = time.strftime('%Y-%m-%d', time.localtime())
    timet1 = 0
    try:
        timet1 = time.mktime(time.strptime(date + ' ' + time1[0:-2], '%Y-%m-%d %H:%M:%S'))
    except:
        pass
    
    return timet1

#Obtiene un string time a partir de un timet, si timet es negativo devuelve '' 
def checkTimeNeg(timet):
    timetStr = ''
    if timet >= 0:
        timetStr = str(timet)
        
    return timetStr

def isValidIam(line):
    if  re.search('ani.* nat\: [03]', line):
        return True
    else:
        return False
    
def logTopHeading():
    str1 = ''
    if getFormat(TYPE) in ('6'): 
        str1 += 'Lin'
        str1 += (' '* (LINE_NUM_LEN - len(str1)))         
        str1 += 'Hora       Dir Pto-Cod     Cic Dnis           N Ani        N Cont Lib Dir Causa'

    if str1 != '':
        log(str1)
        
#Loguea el encabezado de la llamada
def getLogHeading(line):
    str1 = ''

    if getFormat(TYPE) in ('1', '2'):        
        str1 += 'Lin'
        str1 += (' '* (LINE_NUM_LEN - len(str1)))         
        str1 += 'Hora       Prot   Dir Pto-Cod    Mensaje'
    if getFormat(TYPE) in ('3'):        
        str1 += 'Lin'
        str1 += (' '* (LINE_NUM_LEN - len(str1)))         
        str1 += 'Hora       Prot   Dir Pto-Cod     Cic  Mensaje'
    elif getFormat(TYPE) in ('4'): 
        #str1 = 'Circuito: ' + getHeader(line) + ' (' + str(getCircuitVal(getCircuit(line))) + ' dec)\n' + str1
        str1 = 'Circuito: ' + getHeader(line) + '\n' + str1        
        str2 = 'Lin'
        str2 += (' '* (LINE_NUM_LEN - len(str2))) 
        str2 += 'Hora       Dir  Tip Parametros'
        str1 += str2
    elif getFormat(TYPE) in ('5'):
        str1 += 'Lin'
        str1 += (' '* (LINE_NUM_LEN - len(str1)))         
        str1 += 'Hora       Dir Pto-Cod     Cic Parametros'
  
        
    return str1

def getLogLine(line):
    str1 = ''
    if getFormat(TYPE) in ('1', '2', '3'):
        str1 = line
    elif getFormat(TYPE) in ('4'):
        str1 = getLineNum(line) + getTime(line) + ' ' + getDirection(line) + ' ' + ' ' + getType(line) + ' ' + getParams(line)            
    elif getFormat(TYPE) in ('5') and getType(line) == 'IAM':
        #str1 = getLineNum(line) + getTime(line) + ' ' + getDirection(line) + ' ' + getHeader(line) + ' (' + str(getCircuitVal(getCircuit(line))) + ' dec) '  + getParams(line)
        str1 = getLineNum(line) + getTime(line) + ' ' + getDirection(line) + ' ' + getHeader(line) + ' ' + getParams(line)        
    elif getFormat(TYPE) in ('6') and getType(line) == 'IAM':
        params = getParams(line)
        re1 = re.findall(': ([0-9A-F]*)', params)
      
        DNIS_LEN = 15   
        NAT_LEN = 2
        ANI_LEN = 11
        LEN = DNIS_LEN
        
        try:
            str1 = re1[0]
            str1 = str1 + (' ' * (LEN - len(str1)))
            LEN = DNIS_LEN + NAT_LEN
            str1 = str1 + re1[1]
            str1 = str1 + (' ' * (LEN - len(str1)))
            LEN = DNIS_LEN + NAT_LEN + ANI_LEN
            str1 = str1 + re1[2]
            str1 = str1 + (' ' * (LEN - len(str1)))
            str1 = str1 + re1[3]
        
            str1 = getLineNum(line) +  getTime(line) + ' ' + getDirection(line) + ' ' + getHeader(line) + ' ' + str1
        except:
            str1 = ''
                
    return str1
    
def appendLog(call, log):
    if log != '':
        if call['log'] != '' and log != '\n': 
            call['log'] += '\n'
        call['log'] += log
    
    return call
    
#Inicializa un diccionario para almacenar los datos de una llamada
def newCall():
    call = {}
    call['pointCode'] = ''
    call['cic'] = ''    
    call['iam'] = '0'
    call['iamDirOut'] = '0'
    call['anm'] = '0'
    call['rel'] = '0'
    call['relDirOut'] = '0'
    call['cause'] = ''
    call['timeIAM'] = ''
    call['timeANM'] = ''
    call['timeREL'] = '' 
    call['log'] = ''   

    return call

def updateCall(call, line):
    if (call['pointCode'] == getPointCode(line) and call['cic'] == getCircuit(line)) or (call['pointCode'] == '' and call['cic'] == ''): 
        if call['iam'] == '0' and getType(line) == 'IAM' and isValidIam(line):
            #Grabo que ya hubo un iam
            call['iam'] = '1'
            #Almaceno la hora del IAM
            call['timeIAM'] = getTime(line)
          
            call['pointCode'] = getPointCode(line)
            call['cic'] = getCircuit(line)        
          
            if getDirection(line) == '-->':
                call['iamDirOut'] = '1'
    
            call = appendLog(call, getLogHeading(line))    
            call = appendLog(call, getLogLine(line))
        elif call['iam'] == '1' and getType(line) == 'IAM':
            call['rel'] = '3'
            log('Alerta, esta llamada no se libera correctamente, aparece un IAM sin un RLC previo')
        else:
            call = appendLog(call, getLogLine(line))      
       
            #En funcion del tipo de mensaje actualizo los datos de la llamada
            if getType(line) == 'CON':
                call['anm'] = '1'
                call['timeANM'] = getTime(line)
            if getType(line) == 'ANM':
                call['anm'] = '1'
                call['timeANM'] = getTime(line)
            elif getType(line) == 'REL':
                call['rel'] = '1'
                call['cause'] = getReleaseCause(line) 
                call['timeREL'] = getTime(line)                           
                if getDirection(line) == '-->':
                    call['relDirOut'] = '1'
            if getType(line) == 'RLC': 
                if call['rel'] == '0':
                    call['rel'] = '2'
                    call['timeREL'] = getTime(line)                           
                    if getDirection(line) == '-->':
                        call['relDirOut'] = '1'
                    log('Alerta, esta llamada no se libera correctamente, aparece un RLC sin REL previo')
    
    return call
    
#Actualiza una llamada a partir de un mensaje de grupo
def updateCallGroupMessage(call, line):
    if call['pointCode'] == getPointCode(line) and getType(line) in GROUP_MESSAGES and getFormat(TYPE) in ('4', '5', '6'):

        cicVal = getCircuitVal(call['cic'])
             
        pointCodeM = getPointCode(line)
        cicM = getCircuit(line)
        cicValM = getCircuitVal(cicM)
        params = getParams(line)
        re1 = re.findall(': ([0-9A-F]*)', params)
        groupVal = int(re1[0])
        
        if cicVal >= cicValM and cicVal <= cicValM + groupVal:                   
            call = appendLog(call, getLogLine(line))
            
    return call
                   
#Analiza una llamada
def analyzeCall(call):
    analysis = ''
    if call['iamDirOut'] == '0':
        analysis += 'Saliente'
    else:
        analysis += 'Entrante'

    if call['anm'] == '0':
        analysis += ' NO concretada'
    else:
        analysis += ' concretada'    
        
    if call['rel'] == '0':
        analysis += ' NO liberada'
    elif call['rel'] == '1':
        analysis += ' liberacion'
    elif call['rel'] == '2':
        analysis += ' liberacion completa'
    elif call['rel'] == '3':
        analysis += ' liberacion FORZADA'

    if call['rel'] == '1' or call['rel'] == '2' or call['rel'] == '3':
        if call['relDirOut'] == '0':
            analysis += ' saliente'
        else:
            analysis += ' entrante'
       
        if getFormat(TYPE) in ('5'):
            analysis += ' causa: ' + call['cause']
    
    timetIAM = getTimeT(call['timeIAM'])
    timetANM = getTimeT(call['timeANM'])
    timetREL = getTimeT(call['timeREL'])

    if call['anm'] == '1':
        analysis += ' IAM-ANM: ' + checkTimeNeg(timetANM-timetIAM) + ' ANM-REL: ' +  checkTimeNeg(timetREL-timetANM)
    else:                  
        analysis += ' IAM-REL: ' + checkTimeNeg(timetREL-timetIAM)

    #En funcion de la getFormat(TYPE) logueo
    if getFormat(TYPE) in ('1', '2', '3', '4'):
        call = appendLog(call, '\n')
        call = appendLog(call, 'Analisis: ' + analysis + '\n')   
        call = appendLog(call, '-'*100)   
    elif getFormat(TYPE) in ('5'):
        call = appendLog(call, analysis)
        call = appendLog(call, '\n')
    elif getFormat(TYPE) in ('6'):
        cause = call['cause']
        causeVal = cause[0:cause.find(' ')]
        cause = (' ' * (3 - len(causeVal))) + cause
        #call['log'] += '    ' + str(call['anm']) + '   ' + str(call['rel']) + '   ' + str(call['relDirOut']) + ' ' + cause
        if call['relDirOut'] == '0':
            relDir = '<--'
        else:
            relDir = '-->'
        call['log'] += '    ' + str(call['anm']) + '   ' + str(call['rel']) + ' ' + str(relDir) + ' ' + cause
        
    return call
 
def logCall(call):
    log(call['log'], 3)
        
#Loguea los mensajes huerfanos, no pertenecientes a ninguna llamada
def logOrphanMessages(lines, processedMessages):
    if getFormat(TYPE) in ('1', '2', '3', '4'): 
        log('', 2)
        str1 = 'Messages huerfanos\n'
        str1 += ('¯' * (len(str1)-1))
        log(str1, 2)  
        log('Mensajes total:       ' + str(len(lines)), 2)
        log('Mensajes procesados:  ' + str(len(processedMessages)), 2)
        log('Mensajes huerfanos:   ' + str(len(lines) - len(processedMessages)), 2)
        log('')
            
        #j = 0:
        #while j < len(lines): 
        #   try:
        #        temp = processedMessages.index(j)
        #    except Exception, e:
        #       log(getLine(lines, j))
        #    
        #       j += 1
        
        processedMessages.sort()

        #log('processedMessages: ' + str(processedMessages))
        
        lastLineNum = -1
        for i in processedMessages:
            #log('lastLineNum: ' + str(lastLineNum) + ' i: ' + str(i))
            
            if i > lastLineNum + 1 :
                for j in range(lastLineNum + 1, i):
                     log(getLine(lines, j), 2)
            lastLineNum = i

        for j in range(lastLineNum + 1, len(lines)):
             log(getLine(lines, j), 2)           

        log('-'*100, 2)
        log('', 2)

#Inicializa un diccionario para alacenar las estadisticas
def newStatistics():
    statistics = {}
    statistics['salientes concretadas'] = 0
    statistics['salientes no concretadas'] = 0
    statistics['entrantes concretadas'] = 0
    statistics['entrantes no concretadas'] = 0
    statistics['no liberadas'] = 0
    statistics['liberacion normal'] = 0
    statistics['liberacion ocupado'] = 0
    statistics['liberacion no contesta'] = 0
    statistics['liberacion otras'] = 0
    statistics['liberacion sin rel'] = 0
    statistics['liberacion forzada'] = 0    

    return statistics
    
#Actualiza las estadisticas con los datos de una llamada
def updateStatistics(statistics, call):
    if call['iamDirOut'] == '0':
        if call['anm'] == '0':
            statistics['entrantes no concretadas'] += 1
        else:            
            statistics['entrantes concretadas'] += 1
    else:
        if call['anm'] == '0':
            statistics['salientes no concretadas'] += 1
        else:            
            statistics['salientes concretadas'] += 1

    if call['rel'] == '0':
            statistics['no liberadas'] += 1
    elif call['rel'] == '1':
        if call['cause'][0:2] == '16':
            statistics['liberacion normal'] += 1
        elif call['cause'][0:2] == '17':
            statistics['liberacion ocupado'] += 1    
        elif call['cause'][0:2] == '18':
            statistics['liberacion no contesta'] += 1   
        else:
            statistics['liberacion otras'] += 1
    elif call['rel'] == '2':
        statistics['liberacion sin rel'] += 1
    elif call['rel'] == '3':
        statistics['liberacion forzada'] += 1


#Loguea las estadisticas
def logStatistics(statistics):
    log('', 2)
    str1 = 'Estadisticas de llamadas\n'
    #str1 += ('-' * (len(str1)-1)) + '\n'
    str1 += ('¯' * (len(str1)-1))
    log(str1, 2)
    
    for i in STATISTICS_KEYS:
        log(i.capitalize() + ': ' + (' '* (25 - len(i))) + str(statistics[i]), 2) 
  

def processLine(lineI, i):
    global linesI
    global processedMessages
    global statistics

    #Inicializo un diccionario para almacenar datos sobre la llamada
    call = newCall()
        
    #Busco el comienzo de una llamada
    if getType(lineI) == 'IAM' and isValidIam(lineI):
        #Agrego esta posicion a la lista de mensajes procesados
        processedMessages.append(i)
        #Actualizo la llamada
        call = updateCall(call, lineI)
        
        #A partir de aqui busco todos los mensajes de la misma llamada, es decir
        #todos aquellos mensajes con mismo header
        #Para esto, inicializo otra variable con la posicion del proximo mensaje 
        #a analizar, mientras guardo i para luego buscar una nueva llamada 
        j = i + 1
        lineI = getLine(linesI, j)

        #Busco todos los mensajes de dicha llamada
        processCall = True
        while processCall and lineI:
            if getPointCode(lineI) == call['pointCode']:
                if getType(lineI) in GROUP_MESSAGES:
                    call = updateCallGroupMessage(call, lineI)
                elif getCircuit(lineI) == call['cic']:
                    #Si no es un IAM analizo la llamada
                    if getType(lineI) != 'IAM':
                        #Agrego esta posicion a la lista de mensajes procesados
                        processedMessages.append(j)                       
                        call = updateCall(call, lineI)            
                        if getType(lineI) == 'RLC':
                            #Si es getFormat(TYPE) == 2 proceso una linea mas que tiene que ser el mensaje parseado
                            if getFormat(TYPE) in ('2'):
                                j = j + 1
                                lineI = getLine(linesI, j)
                                call = updateCall(call, lineI)
                            processCall = False                            
                    #Si es un IAM termino el procesamiento de la llamada anterior y
                    #salgo
                    else:
                        call = updateCall(call, lineI)
                        processCall = False
                        
            j = j + 1
            lineI = getLine(linesI, j)

        #Realizo el analisis de la llamada y logueo
        call = analyzeCall(call)
        #Logueo lo referente a la llamada
        logCall(call)
        #Actualizo las estadisticas con los datos de la llamada
        updateStatistics(statistics, call)

    
###############################################################################
#                               Main
###############################################################################
def pycall(format_, fileNameI, outputType_ = None, filter2_ = None):
    print 'PyCall: Call group of SS7 trace'
    
    #Declaro algunas variables de uso global
    global format
    global outputType
    global fileO
    global filter2
    
    global linesI
    global processedMessages
    global statistics

    fileI = None

    if format_:
        format = format_
        
    if outputType_:
        outputType = outputType_      
        
    if filter2_:
        filter2 = filter2_   
        
    print 'PyCall format: ' + format + ' fileNameI: ' + fileNameI +  ' outputType: ' + outputType
    
    #Abro el archivo de input y en caso de salida a archivo abro el de output
    fileI = open(fileNameI, 'r')
    if outputType in ('2', '3'):  
        fileNameO = fileNameI + '.call'        
        fileO = open(fileNameO, 'w')
    
    #Leo las lineas del archivo de input y las guardo en una lista para analizarlas
    linesI = fileI.readlines()
    linesI = linesI[1:]

    #Inicializo el contador de linea y obtengo una linea para analizar
    i = 0   
    lineI = getLine(linesI, i)
     
    #Inicializo una lista para guardar las posiciones de los mensajes procesados,
    #las posiciones que no esten en esta lista seran mensajes huerfanos 
    processedMessages = []
    #Inicializo un diccionario con las estadisticas
    statistics = newStatistics()

    logTopHeading()
    
    while lineI:
       
        processLine(lineI, i)
                    
        #Busco la siguiente linea para analizar                              
        i = i + 1
        lineI = getLine(linesI, i)
   
    #Logueo el reporte de mensajes huerfanos
    logOrphanMessages(linesI, processedMessages)

    #Logueo el reporte de estadisticas
    logStatistics(statistics)

    #Cierro los archivos abiertos
    if fileI:
        fileI.close()
    if fileO:
        fileO.close()
