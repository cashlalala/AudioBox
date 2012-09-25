
set PATH=%PATH%;C:\python\python25

E:

cd E:\pyinstaller-2.0

python pyinstaller.py --paths="C:\Users\cash_chang\Documents\Visual Studio 2010\Projects\DLL Test\AudioBox\koanSDK";"C:\Users\cash_chang\Documents\Visual Studio 2010\Projects\DLL Test\Debug";"C:\Users\cash_chang\Documents\Visual Studio 2010\Projects\DLL Test\AudioBox" --onefile -o "C:\Users\cash_chang\Desktop\Ouput" "C:\Users\cash_chang\Documents\Visual Studio 2010\Projects\DLL Test\AudioBox\AudioBox.py"