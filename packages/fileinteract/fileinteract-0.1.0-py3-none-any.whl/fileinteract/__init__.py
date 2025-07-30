import os
import shutil

def Exists(Path: str) -> bool:
    return os.path.exists(Path)

class File:
    def __init__(self, Path: str):
        self.Path = Path

        if not os.path.exists(self.Path):
            raise FileNotFoundError()

        self.Name      = os.path.basename(self.Path)
        self.Extension = os.path.splitext(self.Path)[1]

    def GetContent(self, Mode: str = "normal", Encoding: str = "utf-8") -> bytes | str:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        if Mode.lower() == "normal":
            Mode = "r"
        elif Mode.lower() == "binary":
            Mode = "rb"
        else:
            raise "Invalid argument : Mode arg must be 'normal" or 'binary'

        with open(self.Path, Mode, encoding=Encoding if Mode == "r" else None) as F:
            return F.read()
        
    def OverWrite(self, Content: str | bytes, Encoding: str = "utf-8") -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "wb" if str(type(Content)) == "<class 'bytes'>" else "w", encoding=Encoding if str(type(Content)) == "<class 'str'>" else None) as F:
            F.write(Content)
        
    def Write(self, Content: str | bytes, Encoding: str = "utf-8") -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "ab" if str(type(Content)) == "<class 'bytes'>" else "a", encoding=Encoding if str(type(Content)) == "<class 'str'>" else None) as F:
            F.write(Content)

    def Delete(self) -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        os.remove(self.Path)
    
    def Copy(self, DistPath: str) -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        shutil.copy(self.Path, DistPath)

    def ClearContent(self):
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "w", encoding='utf-8') as F:
            F.write('')

    def Move(self, DistPath: str) -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        shutil.copy(self.Path, DistPath)
        os.remove(self.Path)

    def GetContentLines(self, Encoding: str = 'utf-8') -> list[str]:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "r", encoding=Encoding) as F:
            return F.readlines()
        
    def GetLine(self, Index: int, Encoding: str = "utf-8") -> str | None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "r", encoding=Encoding) as F:
            ContentLines = F.readlines()

            try:
                return ContentLines[Index]
            except IndexError:
                return None
        
    def GetCharsCount(self, Encoding: str = "utf-8") -> int:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "r", encoding=Encoding) as F:
            return len(F.read())

    def GetLinesCount(self, Encoding: str = "utf-8") -> int:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "r", encoding=Encoding) as F:
            return len(F.readlines())
        
    def GetSize(self) -> int:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        return os.path.getsize(self.Path)

    def Rename(self, NewName: str) -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        os.rename(self.Path, os.path.join(self.Path.replace(self.Name, ""), NewName))

        self.Path      = self.Path.replace(self.Name, NewName)
        self.Name      = NewName
        self.Extension = os.path.splitext(self.Path)[1]

    def IsBinary(self) -> bool:
        if not Exists(self.Path):
            raise FileNotFoundError()

        with open(self.Path, "rb") as F:
            Chunk = F.read(1024) 

            if b'\x00' in Chunk:
                return True

            text_chars = bytes(range(32, 127)) + b'\n\r\t\b'
            NonStr = sum(Byte not in text_chars for Byte in Chunk)

            return NonStr / len(Chunk) > 0.30 if Chunk else False

    def InsertLine(self, Content: str, Index: int, Encoding: str = 'utf-8') -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        Lines = self.GetContentLines()

        try:
            Lines.insert(Index, Content)
        except IndexError:
            raise IndexError()
        
        with open(self.Path, "w", encoding=Encoding) as F:
            F.write(Lines)

    def Replace(self, WhatToReplace: str, ReplaceBy: str, Encoding: str) -> None:
        if not Exists(self.Path):
            raise FileNotFoundError()
    
        FContent = self.GetContent()

        with open(self.Path, "w", encoding=Encoding) as F:
            F.write(FContent.replace(WhatToReplace, ReplaceBy))
    
    def Contain(self, Search: str, Encoding: str = 'utf-8') -> bool:
        if not Exists(self.Path):
            raise FileNotFoundError()
        
        with open(self.Path, "r", encoding=Encoding) as F:
            return True if Search in F.read() else False
    
    def IsEmpty(self) -> bool:
        if not Exists(self.Path):
            raise FileNotFoundError()
    
        return False if len(self.GetSize()) > 0 else True