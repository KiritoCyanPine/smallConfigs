import concurrent.futures
import re
import color
import os


class ConfigManager:
    filePointer = 'str'

    def __init__(self, address_to_config):
        self.filePointer = address_to_config
        try:
            fp = open(self.filePointer, 'r')
            fp.close()
        except FileNotFoundError as e:
            fp = open(self.filePointer, 'w')
            print(color.blue("* ", e, f"\n\t*New file with name' {self.filePointer}' created..."))
            fp.close()

    def findMultiProp(self, keys):
        tempDict = {}
        for i in keys:
            tempDict[i] = self.findProp(i)
        return tempDict

    def findProp(self, key, logInsData=False):

        def read_specfic():
            fp = open(self.filePointer, 'r')
            readBuffer = fp.read()
            fp.close()
            readBuffer = readBuffer.split("\n")
            lenOfKey = len(key)
            if readBuffer == "":
                return None
            valueOfKey = None
            for i in readBuffer:
                if len(i.split()) != 0 and i.split()[0] == key:
                    valueOfKey = i[lenOfKey:]
                    break
            if valueOfKey is None and logInsData:
                print(color.yellow(f"no attribute named '{key}' exists in config..."))
                return None
            else:
                return valueOfKey

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(read_specfic)
            return_value = future.result()
            if return_value is None:
                return None
            # noinspection RegExpRedundantEscape
            try:
                lst = re.findall(r"{(.*?)}", return_value)[0].split()
            except IndexError:
                #  print("no notation")
                lst = ''
            try:
                if len(lst) == 0:
                    ans = return_value[return_value.index('=') + 2:]
                if len(lst) == 1:
                    if lst[0] == 'int':
                        ans = int(return_value[return_value.index('=') + 1:].strip(" "))
                    elif lst[0] == 'float':
                        ans = float(return_value[return_value.index('=') + 1:].strip(" "))
                    elif lst[0] == 'str':
                        ans = str(return_value[return_value.index('=') + 1:].strip(" "))
                    else:
                        ans = "value changed"
                if len(lst) == 3:
                    if lst[0] == 'int' and lst[2] == 'list':
                        ans = return_value[return_value.index('=') + 1:].strip(" ")
                        ans = [int(i) for i in ans.split()]
                    elif lst[0] == 'float' and lst[2] == 'list':
                        ans = return_value[return_value.index('=') + 1:].strip(" ")
                        ans = [float(i) for i in ans.split()]
                    elif lst[0] == 'str' and lst[2] == 'list':
                        ans = return_value[return_value.index('=') + 1:].strip(" ")
                        ans = [str(i) for i in ans.split()]
                    else:
                        ans = "value changed"
                if len(lst) == 4:
                    if lst[0] == 'int' and lst[2] == 'list' and '[' in lst[3] and ']' in lst[3]:
                        ans = return_value[return_value.index('=') + 1:].strip(" ")
                        inBrackets = lst[3].strip('[]')
                        ans = [int(i) for i in ans.split()]
                        ans = ans[:int(inBrackets)]
                    elif lst[0] == 'float' and lst[2] == 'list' and '[' in lst[3] and ']' in lst[3]:
                        ans = return_value[return_value.index('=') + 1:].strip(" ")
                        inBrackets = lst[3].strip('[]')
                        ans = [float(i) for i in ans.split()]
                        ans = ans[:int(inBrackets)]
                    elif lst[0] == 'str' and lst[2] == 'list' and '[' in lst[3] and ']' in lst[3]:
                        ans = return_value[return_value.index('=') + 1:].strip(" ")
                        inBrackets = lst[3].strip('[]')
                        ans = [str(i) for i in ans.split()]
                        ans = ans[:int(inBrackets)]
                    else:
                        ans = "value changed"
            except IOError:
                pass
            return ans

    def createProp(self, name, value, propType=None, isList=False, size=None, logInsData=False):
        def insert_new_data(newLine):
            fp = open(self.filePointer, 'r')
            fr = fp.read()
            fp.close()
            fp = open(self.filePointer, 'a')
            if fr != "":
                fp.writelines("\n" + newLine)
            else:
                fp.writelines(newLine)
            fp.close()
            return " value Inserted into the manager..."

        checkBeforeCreate = self.findProp(name, logInsData)
        if checkBeforeCreate is None:
            pushInString = f"{name} "
            if isList is False and type(value) == list:
                isList = True
                if propType is None:
                    propType = str(type(value[0]))[8:-2]
                else:
                    print(propType == str(type(value))[8:-2])

            if propType is None and type(value) == int:
                propType = "int"
            elif propType is None and type(value) == float:
                propType = "float"
            elif propType is None and type(value) == str:
                propType = "str"
            else:
                if type(value) == float and propType == "int":
                    propType = "float"
                    print(color.red(f"*converting the 'int' type to 'float' for saving loss of data..."))
                if type(value) == str and propType != str(type(value))[8:-2]:
                    if value.isnumeric():
                        pass
                    else:
                        propType = "str"
                    print("*the value Type and mentioned type do not match..")
                else:
                    if type(value) == list and propType != str(type(value[0]))[8:-2]:
                        if all(isinstance(x, int) for x in value):
                            propType = "int"
                            print(color.red("*the value Type and mentioned type do not match.. ",
                                            str(type(value[0]))[8:-2], "type Casting to ", propType))
                        elif all(isinstance(x, float) for x in value):
                            print(color.red("*the value Type and mentioned type do not match.. ",
                                            str(type(value[0]))[8:-2], "type Casting to ", propType))
                            propType = "float"
                        else:
                            propType = "str"
                            print(color.red("*the value Type and mentioned type do not match.. ",
                                            "changing to appropriate Type"))

            if propType == "int" or propType == "str" or propType == "float":
                pushInString += ("{ " + propType)
                if isList is not False:
                    pushInString += " : list "
                    if type(size) is int:
                        if len(value) > size:
                            size = len(value)
                            print("*the value size exceeds the Size mentioned using Automatic Sizing")
                        pushInString += ("[" + str(size) + "] } ")
                    else:
                        if size is not None:
                            print(color.blue("*the type of size should be 'int' ... ignoring size attribute..."))
                        pushInString += "} "
                else:
                    pushInString += " } "
            else:
                pass
            if propType == "float" and type(value) != list and type(value) == int:
                value = float(value)

            pushInString += ("= " + str(value).strip("[]").replace(",", "").replace("'", ""))
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(insert_new_data, pushInString)
                print(future.result())
            if logInsData:
                print("log:\n\t", pushInString)

        else:
            print(color.yellow(f"the attribute named '{name}' exists in config..."))

    def deleteProperty(self, name, showNewData=False, returnResult=False):
        def readWhole():
            fp = open(self.filePointer, 'r')
            readBuffer = fp.read()
            fp.close()
            readBuffer = readBuffer.split("\n")
            return readBuffer

        def writeWhole(newData):
            fp = open(self.filePointer, 'w')
            fp.write(newData)
            fp.close()

        buffer = self.findProp(name)
        if buffer is not None:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(readWhole)
                OUT = future.result()
            NewBuffer = ""
            for i in OUT:
                if i != "" and i.split()[0] == name:
                    continue
                NewBuffer = NewBuffer + i + "\n"
            NewBuffer = re.sub(r"\n+", "\n", NewBuffer)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(writeWhole, NewBuffer)
            if showNewData:
                print(re.sub(r"\n+", "\n", NewBuffer))
            if returnResult:
                return NewBuffer
        else:
            print(color.red(f"*no attribute named '{name}' exists in config..."))
            return None

    def modifyContent(self, name, value):

        def get_list_of_prop():
            fp = open(self.filePointer, 'r')
            readBuffer = fp.read()
            fp.close()
            readBuffer = readBuffer.split("\n")
            valueOfKey = None
            checkProp = {}
            for i in readBuffer:
                if i.split()[0] == name:
                    valueOfKey = i[len(name):]
                    checkProp["index"] = readBuffer.index(i)
                    break
            try:
                lst = re.findall(r"{(.*?)}", valueOfKey)[0].split()
            except IndexError:
                lst = ""
            if "int" in lst or "float" in lst or "str" in lst or "bool" in lst:
                checkProp["propType"] = lst[0]
                del lst[0]
                if ":" in lst:
                    del lst[0]
                    if "list" in lst:
                        checkProp["isList"] = True
                        del lst[0]
                        if len(lst) != 0:
                            checkProp["size"] = int(lst[0].strip("[]"))
                            del lst
                        else:
                            checkProp["size"] = None
                    else:
                        checkProp["isList"] = False
                else:
                    checkProp["isList"] = False
                    checkProp["size"] = None
            else:
                checkProp["propType"] = "str"
                checkProp["isList"] = False
                checkProp["size"] = None
            checkProp["value"] = valueOfKey[valueOfKey.index("=")+2:]
            checkProp["header"] = name+valueOfKey[:valueOfKey.index("=")+2]
            return checkProp

        def writeWhole(replacingData, index):
            fp = open(self.filePointer, 'r')
            readBuffer = fp.read()
            fp.close()
            readBuffer = readBuffer.split("\n")
            readBuffer[index] = replacingData
            buff = "\n".join(readBuffer)
            fp = open(self.filePointer, 'w')
            fp.write(buff)
            fp.close()
            print("#applied changes")
        try:
            buffer = self.findProp(name)
        except IndexError:
            buffer = None
        if buffer is None:
            print(color.yellow(f"*property with the name '{name}' does not exist..."))
            return None
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(get_list_of_prop)
            prop = future.result()
        if buffer is None:
            print(color.red(f"no attribute named '{name}' exists in config..."))
            return 0
        if type(value) != list and type(buffer) != list and type(value) == type(buffer):
            replacingStr = str(value).strip("[]").replace(",", "").replace("'", "")
        elif type(value) == list and type(buffer) == list:
            if type(buffer[0]) == type(value[0]):
                replacingStr = str(value).strip("[]").replace(",", "").replace("'", "")
            elif type(buffer[0]) == str and (type(value[0]) == int or type(value[0]) == float):
                replacingStr = str(value).strip("[]").replace(",", "").replace("'", "")
            else:
                print(color.red("*Cannot insert type ", type(value[0]),
                                " into buffer of type ", type(buffer[0]), "..."))
                print(color.red("*rejecting changes"))
                return None
        elif type(buffer) == str and (type(value) == float or type(value) == int or type(value) == str):
            replacingStr = str(value).strip("[]").replace(",", "").replace("'", "")
        else:
            print(color.red("*the modifying value has a type too 'distinct' for typecasting... \nrejecting changes "))
            return None
        if prop["size"] is not None and len(replacingStr.split()) < prop["size"]:
            print(color.red("*the modifying length is less than the configured size... \n",
                            "\t\tCheck the input before entering..."))
            return None
        newData = prop["header"]+replacingStr
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(writeWhole, newData, prop["index"])

    def commit(self):
        import shutil
        import time
        import hashlib
        appdir = os.getenv('APPDATA')
        saveDir = ""
        try:
            saveDir = appdir+"\\Python\\share\\ConfigManager"
            os.mkdir(saveDir)
        except FileExistsError:
            pass
        seconds = int(round(time.time()))
        local_time = "["+str(time.ctime(seconds)).replace(":", ".")+"] "
        commitFile = local_time+self.filePointer

        listOfCommits = [i for i in os.listdir(saveDir) if self.filePointer in i]
        sha1 = hashlib.sha1(open(self.filePointer).read().encode()).hexdigest()
        for i in listOfCommits:
            if hashlib.sha1(open(saveDir + "\\" + i).read().encode()).hexdigest() == sha1:
                os.remove(saveDir + "\\" + i)
                print(color.blue(f"*file with similar SHA stamp found...\n\t\t "
                                 f"removing previous file to '{commitFile}'..."))
        shutil.copyfile(self.filePointer, saveDir + "\\" + commitFile)
        print(color.blue(f"*file committed to '{commitFile}'..."))

    @staticmethod
    def openCommitFiesPath():
        import subprocess
        FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        appdir = os.getenv('APPDATA')
        saveDir = appdir + "\\Python\\share\\ConfigManager"
        FolderPath = os.path.join(appdir, saveDir)
        subprocess.run([FILEBROWSER_PATH, FolderPath])
        print(color.blue("Opening Commit files Directory \n\t\t"), FolderPath, " \t\t")
