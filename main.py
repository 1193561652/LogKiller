import os
import sys
import re
import json
import zipfile
from shutil import copyfile

class FileIndex :
    def __init__(self, _line, _fileName):
        self.line = _line
        self.fileName = _fileName
    def getLine(self):
        return self.line
    def getFileName(self):
        return self.fileName
    def compare(fileIndex1, fileIndex2):
        if fileIndex1.getFileName() == fileIndex2.getFileName():
            if fileIndex1.getLine() > fileIndex2.getLine():
                return 1
            elif fileIndex1.getLine() == fileIndex2.getLine():
                return 0
            else:
                return -1
        elif fileIndex1.getFileName() > fileIndex2.getFileName():
            return 1
        else:
            return -1


class LogLine :
    def __init__(self, _logLine, _logType, _fileIndex):
        self.logLine = _logLine
        self.logType = _logType
        self.fileIndex = _fileIndex

    def printMessage(self):
        print(self.fileIndex.fileName, self.fileIndex.line)
        print(self.logLine)

    def getFileIndex(self):
        return self.fileIndex
    def getLine(self):
        return self.logLine

class UpdateStatusLogLine(LogLine) :
    def __init__(self, _logLine, _logType, _fileIndex):
        LogLine.__init__(self, _logLine, _logType, _fileIndex)
        self.analysisJson()

    def analysisJson(self):
        tup = re.search("\{[\w|\W]+\}", self.logLine).span()
        jsonStr = self.logLine[tup[0]:tup[1]]
        data = json.loads(jsonStr)
        self.updateStatus = "NULL"
        if data.get("body") != None:
            if data.get("body").get("package") != None:
                if data.get("body").get("package").get("status") != None :
                    self.updateStatus = data.get("body").get("package").get("status")
                if data.get("body").get("package").get("version") != None :
                    self.tagVersion = data.get("body").get("package").get("version")

    def printMessage(self):
        LogLine.printMessage(self)
        print(self.updateStatus)

    def getUpdateStatus(self):
        return self.updateStatus
    def getTagVersion(self):
        return self.tagVersion

#[uds_com_mgr.cpp:ComMgr_SendDataFromCAN:296] [UDS Data]:3600FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
#ComMgr_SendDataFromCAN:[0-9]+\] \[UDS Data\]:[0-9]+
#CANSEND

#[uds_com_mgr.cpp:ComMgr_SendDataFromCAN:303] [UDS REPRO] CAN Data Send Success.
#CAN Data Send Success.
#CANSENDSUCC

#[uds_com_mgr.cpp:ComMgr_CanRecvTask:626] [UDS Data]:7600
#ComMgr_CanRecvTask:[0-9]+\] \[UDS Data\]:[0-9]+
#CANWAIT

#[uds_seq_mgr.cpp:UdsSeq_RecvResponse:370] [UDS Data]:7600
#UdsSeq_RecvResponse:[0-9]+\] \[UDS Data\]:[0-9]+
#RECVRESPONSE

#[uds_repro.cpp:udsRepro_processUdsState:252] [UDS REPRO] Notify State: Finish Reprogram
#Finish Reprogram
#FINISH

#[uds_repro.cpp:udsRepro_processUdsState:252] [UDS REPRO] Notify State: Negative Response Error
#Negative Response Error
#NORESPONSE

#[uds_repro.cpp:udsRepro_processUdsState:255] 3016:2985018448 [UDS REPRO] Notify State: No Response Error
#No Response Error
#NORESPONSE

#[uds_com_mgr.cpp:ComMgr_SendDataFromEthernet:330] 123:456 [UDS Data]
#DOIPSEND

#start to init doip
#DOIPSTART

#doip  init
#DOIPINIT

#[uds_case_mgr.cpp:CaseMgr_GetCaseFromCaseVector:188] [UDS Data]:7101020300
#CaseMgr_GetCaseFromCaseVector:[0-9]+\] [0-9:\s]*\[UDS Data]:[0-9]+
#GETCASE



class UDSLogLine(LogLine) :
    #self.udsLogType = "NULL"
    def __init__(self, _logLine, _logType, _fileIndex):
        LogLine.__init__(self, _logLine, _logType, _fileIndex)
        self.udsLogType = "NULL"
        self.value = "NULL"
        if re.search("ComMgr_SendDataFromCAN:[0-9]+\] [0-9:\s]*\[UDS Data\]:[0-9]+", self.logLine) != None :
            searchObj = re.search("ComMgr_SendDataFromCAN:[0-9]+\] [0-9:\s]*\[UDS Data\]:(\w{4})\w*", self.logLine)
            self.value = searchObj.group(1)
            if self.value == "3E80":
                self.udsLogType = "CANSEND3E80"
            else:
                self.udsLogType = "CANSEND"
        elif re.search("ComMgr_SendDataFromEthernet:[0-9]+\] [0-9:\s]*\[UDS Data\]:[0-9]+", self.logLine) != None :
            searchObj = re.search("ComMgr_SendDataFromEthernet:[0-9]+\] [0-9:\s]*\[UDS Data\]:(\w{4})\w*", self.logLine)
            if searchObj != None:
                self.value = searchObj.group(1)
            self.udsLogType = "CANSEND"
        elif re.search("CAN Data Send Success.", self.logLine) != None :
            self.udsLogType = "CANSENDSUCC"
        elif re.search("ComMgr_CanRecvTask:[0-9]+\] [0-9:\s]*\[UDS Data\]:[0-9]+", self.logLine) != None :
            self.udsLogType = "CANWAIT"
        elif re.search("UdsSeq_RecvResponse:[0-9]+\] [0-9:\s]*\[UDS Data\]:[0-9]+", self.logLine) != None :
            self.udsLogType = "RECVRESPONSE"
        elif re.search("CaseMgr_GetCaseFromCaseVector:[0-9]+\] [0-9:\s]*\[UDS Data]:[0-9]+", self.logLine) != None :
            self.udsLogType = "GETCASE"
        elif re.search("Finish Reprogram", self.logLine) != None :
            self.udsLogType = "FINISH"
        elif re.search("No Response Error", self.logLine) != None :
            self.udsLogType = "NORESPONSE"
        elif re.search("Negative Response Error", self.logLine) != None :
            self.udsLogType = "NORESPONSE"
        elif re.search("start to init doip", self.logLine) != None :
            self.udsLogType = "DOIPSTART"
        elif re.search("doip  init", self.logLine) != None :
            self.udsLogType = "DOIPINIT"


    def printMessage(self):
        LogLine.printMessage(self)
        print(self.udsLogType)
    
    def getUdsType(self):
        return self.udsLogType

    def getValue(self):
        return self.value


    
class UpdateContext:
    def __init__(self):
        self.updateList = []
        self.udslineLists = []
        self.updateVersion = "NULL"

    def appendUpdateLine(self, updateLine):
        self.updateList.append(updateLine)

    def isFinish(self):
        if self.updateList[len(self.updateList)-1].getUpdateStatus() == "INSTALL_FAILED":
            return True
        return False
    def isBegin(self):
        if self.updateList[len(self.updateList)-1].getUpdateStatus() == "INSTALL_IN_PROGRESS":
            return True
        return False

    def isEmpty(self):
        if len(self.updateList) == 0:
            return True
        return False

    def printMessage(self):
        print("===========================begin============================")
        for updateLine in self.updateList :
            updateLine.printMessage()
        print("============================end=============================")
        print("")

    def getBegin(self):
        return self.updateList[0]
    def getEnd(self):
        return self.updateList[len(self.updateList)-1]

    def saveLog(self, logFiles, saveFile):
        save = open(saveFile, "w+")
        save.write(self.getBegin().getLine())
        for fullName in logFiles:
            tempIndex = FileIndex(99999999, fullName)
            retb = FileIndex.compare(tempIndex, self.getBegin().getFileIndex())
            tempIndex = FileIndex(0, fullName)
            rete = FileIndex.compare(tempIndex, self.getEnd().getFileIndex())
            if retb >= 0 and rete <= 0:
                file = open(fullName, errors="ignore")
                count = 0
                for line in file:
                    tempIndex = FileIndex(count, fullName)
                    retb = FileIndex.compare(tempIndex, self.getBegin().getFileIndex())
                    rete = FileIndex.compare(tempIndex, self.getEnd().getFileIndex())
                    if retb >= 0 and rete <= 0:
                        if re.search("UDS", line) != None :
                            udsline = UDSLogLine(line, "UDS", FileIndex(count, fullName))
                            if udsline.getUdsType() != "NULL":
                                self.udslineLists.append(udsline)
                                save.write(line)
                        elif re.search("saadapter.c:ota_get_version", line) != None or re.search("read_version.c:tbox_read_did", line) != None:
                            save.write(line)
                        elif re.search("readback the version: \w+", line) != None:
                            self.updateVersion = re.search("readback the version: (\w+)", line).group(1)
                            save.write(line)
                    count = count + 1
                file.close()
        save.write(self.getEnd().getLine())

        save.write("\n\n\n\n\n")
        save.write("/*******************\n")

        if self.getEnd().getUpdateStatus() == "INSTALL_FAILED":
            save.write("update failed\n")
        elif self.getEnd().getUpdateStatus() == "INSTALL_COMPLETED":
            save.write("update completed\n")
        else:
            save.write("update status error{}\n".format(self.getEnd().getUpdateStatus()))

        save.write("tagVersion:{}\n".format(self.getEnd().getTagVersion()))
        save.write("updateVersion:{}\n".format(self.updateVersion))
        if self.updateVersion == "NULL":
            save.write("can not read version\n")
        elif self.updateVersion != self.getEnd().getTagVersion():
            save.write("version not match\n")
        else:
            save.write("version is match\n")

        #uds = self.analyseUDS()
        save.write("\n")
        #save.write(uds)
        save.write("*******************/\n")
        save.close()

    def analyseUDS(self):
        result = ""
        endIndex = len(self.udslineLists) - 1
        udsLine = None
        while endIndex >= 0:
            udsLine = self.udslineLists[endIndex]
            if udsLine.getUdsType() == "NORESPONSE" or udsLine.getUdsType() == "FINISH":
                break
            endIndex = endIndex - 1
        if endIndex < 0 or endIndex >= len(self.udslineLists):
            result = result + "No Find End Status\n"
            return result
        elif udsLine.getUdsType() == "FINISH":
            result = result + "UDS is succ\n"
            return result
        
        lastSendIndex = endIndex - 1
        while lastSendIndex >= 0:
            udsLine = self.udslineLists[lastSendIndex]
            if udsLine.getUdsType() == "CANSEND":
                break
            lastSendIndex = lastSendIndex - 1
        
        if lastSendIndex < 0 or lastSendIndex >= len(self.udslineLists):
            result = result + "No Find Last Send\n"
            return result

        lastSendStatus = lastSendIndex + 1
        while lastSendStatus < len(self.udslineLists):
            udsLine = self.udslineLists[lastSendStatus]
            if udsLine.getUdsType() == "CANSENDSUCC":
                break
            lastSendStatus = lastSendStatus + 1
        if lastSendStatus < 0 or lastSendStatus >= len(self.udslineLists):
            result = result + "No Find Last Send Status\n"
            return result
        
        if self.udslineLists[lastSendStatus].getUdsType() == "CANSENDSUCC":
            result = result + "Send " + self.udslineLists[lastSendIndex].getValue() + " SUCC\n"
        else:
            result = result + "Send " + self.udslineLists[lastSendIndex].getValue() + " FAILD\n"
        
        respIndex = lastSendStatus + 1
        while respIndex < len(self.udslineLists):
            udsLine = self.udslineLists[respIndex]
            if udsLine.getUdsType() == "RECVRESPONSE":
                pass


        return result



def unZip(file_name):  
    """unzip zip file"""  
    zip_file = zipfile.ZipFile(file_name)
    for names in zip_file.namelist():  
        zip_file.extract(names, os.path.dirname(file_name))
    zip_file.close()



def reorganizeLog(rootPath, rotationPath):
    logFiles = []
    index = 0
    for root,dirs,files in os.walk(rotationPath):
        for file in files:
            if re.match("ecu-updateagent-[0-9]+\.zip$", file) != None :
                fullZipName = os.path.join(root, file)
                unZip(fullZipName)
                index = int(file[len("ecu-updateagent-"):len("ecu-updateagent-")+8])
                logFullName = os.path.join(root, "ecu-updateagent-{0:0>8d}.log".format(index))
                logFiles.append(logFullName)
    index = index + 1
    destinationFile = os.path.join(rotationPath, "ecu-updateagent-{0:0>8d}.log".format(index))
    copyfile(os.path.join(rootPath, "ecu-updateagent.log"), destinationFile)
    logFiles.append(destinationFile)
    return logFiles

def analysisUpdateStatusLine(logLists):
    updateList = []
    for fullName in logLists:
        count = 0
        file = open(fullName, errors="ignore")
        line = ""
        for line in file:
            count = count + 1
            #print(line)
            if re.search("xl4.update-status", line) != None :
                logline = UpdateStatusLogLine(line, "xl4.update-status", FileIndex(count, fullName))
                if logline.getUpdateStatus() != "NULL" :
                    updateList.append(logline)
        file.close()
    return updateList

def analysisUpdateProcess(updateList):
    updateContextLists = []
    updateContext = UpdateContext()
    for updateLine in updateList :
        if updateLine.getUpdateStatus() == "INSTALL_FAILED":
            updateContext.appendUpdateLine(updateLine)
            updateContextLists.append(updateContext)
            updateContext = UpdateContext()
        elif updateLine.getUpdateStatus() == "INSTALL_IN_PROGRESS":
            if updateContext.isEmpty() == False :
                updateContext = UpdateContext()
            updateContext.appendUpdateLine(updateLine)
        else:
            updateContext.appendUpdateLine(updateLine)

    if updateContext.isEmpty() == False and updateContext.isBegin() == True:
        updateContextLists.append(updateContext)
    
    return updateContextLists


def saveUpdateLog(currUpdateContext, saveFileName, logFiles, mode = "UDS"):
    saveFile = open(saveFileName, "w+")
    for fullName in logFiles:
        if fullName >=  currUpdateContext.getBegin().getFileIndex().getFileName() and fullName <= currUpdateContext.getEnd().getFileIndex().getFileName() :
            #print(fullName)
            count = 0
            file = open(fullName) 
            for line in file:
                count = count + 1
                inRang = True
                if fullName == currUpdateContext.getBegin().getFileIndex().getFileName() and count < currUpdateContext.getBegin().getFileIndex().getLine() :
                    inRang = False
                elif fullName == currUpdateContext.getEnd().getFileIndex().getFileName() and count > currUpdateContext.getEnd().getFileIndex().getLine() :
                    inRang = False
                
                if inRang :
                    if re.search("UDS", line) != None :
                        udsline = UDSLogLine(line, "UDS", FileIndex(count, fullName))
                        if udsline.getUdsType() != "NULL" :
                            saveFile.write(line)
            file.close()
    saveFile.close()




if __name__ == "__main__":
    
    rootPath = sys.argv[1]
    workCount = int(sys.argv[2])
    rotationPath = os.path.join(rootPath, "rotation")

    print("start unip zip find")
    logLists = reorganizeLog(rootPath, rotationPath)
    print("start get update status")
    updateStatusLists = analysisUpdateStatusLine(logLists)
    print("start analysis update process")
    updateContextLists = analysisUpdateProcess(updateStatusLists)
    print("analysis update process end count", len(updateContextLists))

    index = len(updateContextLists) - workCount
    while index < len(updateContextLists) and index >= 0:
        saveFile = os.path.join(rootPath, "{0:d}.log".format(index))
        updateContextLists[index].saveLog(logLists, saveFile)
        #saveUpdateLog(updateContextLists[index], saveFile, logLists)
        index = index + 1
        
