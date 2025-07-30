from .C_M import CM
from .CRC import CRC_Fix
from .Scan import Scan_Apk
from .Anti_Splits import Anti_Split
from .Files_Check import FileCheck
from .Argparse import ArgumentParser
from .RK_Pairip import RK_Techno_IND
from .Flutter_SO import Version, E_V_C
from .Instruction_Credit import instruction
from .Extract import Extract_Smali, Logs_Injected
from .Smali_Patch import Smali_Patch, Check_CoreX, Hook_Core
from .Fix_Dex import Scan_Application, Smali_Patcher, Replace_Strings
from .Decompile_Compile import Decompile_Apk, Recompile_Apk, FixSigBlock
from .Manifest_Patch import Patch_Manifest, Replace_Application, Encode_Manifest
from .Other_Patch import Application_Name, Translate_Smali_Name, Merge_Smali_Folders, UnMerge

if __name__ == '__main__': RK_Techno_IND()
