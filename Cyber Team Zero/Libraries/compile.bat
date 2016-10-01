@ECHO OFF
setlocal enabledelayedexpansion
set JAVAC=javac

echo [Checking Path Variable]

javac.exe -classpath "%CLASS_PATH%" "%SOURCE_FILE%" -d "%OUTPUT_FOLDER%"
rem VEGETA!! WHAT DOES THE SCOUTER SAY ABOUT HIS ERROR LEVEL
if !ERRORLEVEL!==9009 goto :SearchJava
if !ERRORLEVEL!==0 goto :CompileSuccess
goto :CompileError


:SearchJava
set ERRORLEVEL=
FOR /f "tokens=*" %%i in ('DIR /a:d /b "C:\Program Files\Java\jdk*"') DO (

echo Checking "C:/Program Files/Java/%%i/bin/javac.exe"
"C:/Program Files/Java/%%i/bin/javac.exe" -classpath "%CLASS_PATH%" "%SOURCE_FILE%" -d "%OUTPUT_FOLDER%"
if !ERRORLEVEL!==0 goto :CompileSuccess
if not !ERRORLEVEL!==9009 goto :CompileError
rem (else continue looking)

)

rem At this point we've tried every location and failed. If javac was found it would have exited or went to :CompileError by now

echo ========================================= 1>&2
echo COMPILATION FAILED >&2
echo The JDK could not be found on your system 1>&2
echo ========================================= 1>&2

EXIT /B 2

:CompileError

EXIT /B 1

:CompileSuccess

echo ==================================
echo COMPILATION WAS SUCCESSFUL
echo ==================================
EXIT /B 0
