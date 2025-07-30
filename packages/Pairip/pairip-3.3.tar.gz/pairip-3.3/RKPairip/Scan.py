from .C_M import CM;  C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

G2 = "\n" * 2

def Scan_Apk(apk_path):
    print(f"\n{C.r}{'_' * 61}\n")
    App_Name = False; isPairip = False; Package_Name = ''
    
    # Extract Package Name
    if C.os.name == 'posix':
        result = C.subprocess.run(['aapt', 'dump', 'badging', apk_path], capture_output=True, text=True)
        pkg_name = C.re.search(r"package: name='([^']+)'", result.stdout)
        if pkg_name:
            Package_Name = pkg_name[1]
            print(f"\n{C.lb}[ {C.c}Package Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{Package_Name}{C.pr}' {C.g} ✔\n")

        # Match Application Name
        result = C.subprocess.run(['aapt', 'dump', 'xmltree', apk_path, 'AndroidManifest.xml'], capture_output=True, text=True)
        app_name = C.re.search(r'A: android:name\(.*\)="com\.pairip\.application\.Application"', result.stdout)
        if app_name:
            print(f"\n{C.lb}[ {C.c}Application Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}com.pairip.application.Application{C.pr}' {C.g} ✔\n")
            App_Name = True

    #  Extract Package Name with APKEditor
    if not Package_Name:
        cmd = ["java", "-jar", F.APKEditor_Path, "info", "-package", "-i", apk_path]
        result = C.subprocess.run(cmd, capture_output=True, text=True)
        Package_Name = result.stdout.split('"')[1]
        print(f"\n{C.lb}[ {C.c}Package Name {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}{Package_Name}{C.pr}'{C.g}  ✔\n")

    # Check for APK protections
    Detect_Protection = []
    with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
        for item in zip_ref.infolist():
            if item.filename.startswith('lib/'):
                if item.filename.endswith('libpairipcore.so'):
                    print(f"\n{C.lb}[ {C.c}Pairip Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}Google加固{C.pr}' {C.g} ✔")
                    isPairip = True
                    break
        
    if not App_Name and not isPairip: exit(f"{C.rd} Your APK Has No Pairip Protection ✘\n")

    def Check_Lib():
        isUnity, isFlutter, dex_files = [], [], []

        with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
            for item in zip_ref.infolist():
                if item.filename.startswith('lib/'):
                    if item.filename.endswith('libunity.so'):
                        isUnity.append(item.filename)
                    if item.filename.endswith('libflutter.so'):
                        isFlutter.append(item.filename)
                elif item.filename.startswith("classes") and item.filename.endswith('.dex'):
                    dex_files.append(item.filename)

            Methods = Fields = 0

            if dex_files:
                try:
                    data = zip_ref.open(dex_files[-1], 'r').read()
                    Methods = int.from_bytes(data[88:91], "little")
                    Fields = int.from_bytes(data[80:83], "little")
                except (OSError, ValueError, KeyError, C.zipfile.BadZipFile) as e:
                    print(f"{G2}{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}{e}, Skipping Methods & Fields Count.")

        if isUnity:
            print(f"{G2}{C.lb}[ {C.c}Unity Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}libunity.so{C.pr}' {C.g} ✔{G2}{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}This is a Unity app. Completely removing Pairip may not be possible unless you can bypass the libpairipcore.so check from Unity libraries.")
        if isFlutter:
            print(f"{G2}{C.lb}[ {C.c}Flutter Protection {C.lb}] {C.rkj}➸❥ {C.pr}'{C.g}libflutter.so{C.pr}' {C.g} ✔\n\n\n{C.lb}[ {C.y}WARN ! {C.lb}] {C.rd}This is a Flutter app. It may not run directly after removing pairip, unless you can bypass the libpairipcore.so check from Flutter libraries.")
        if Methods and Fields:
            print(f"{G2}{C.lb}[{C.y} Last Dex Total {C.lb}] {C.c}Methods: {C.rkj}{Methods} {C.g}➸❥ {C.c}Field: {C.rkj}{Fields}  {C.g}✔")
        else:
            pass

    Check_Lib()
    return Package_Name