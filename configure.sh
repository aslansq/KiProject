thisPath=$(realpath "$0")
thisDirPath=$(dirname "$thisPath")

echoerr() { echo "$@" 1>&2; }

ungracefulExit()
{
    echoerr
    echoerr ERROR!!
    exit 1
}

# is environment variable exist
if [ -z $KI_PROJECT_HOME ]
then
    echoerr ERROR: KI_PROJECT_HOME is not defined.
    echoerr Suggestion:
    echoerr "echo \"export KI_PROJECT_HOME=$thisDirPath\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: found KI_PROJECT_HOME environment variable.
fi

# is environment points to existing directory
if [ ! -d $KI_PROJECT_HOME ]
then
    echoerr ERROR: KI_PROJECT_HOME points to unexisting directory.
    echoerr Suggestion:
    echoerr "echo \"export KI_PROJECT_HOME=$thisDirPath\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: KI_PROJECT_HOME points to existing directory.
fi

# is python exist
python -c "" > /dev/null 2>&1
if [ $? != 0 ]
then
    echoerr ERROR: python does not exist.
    echoerr Suggestion
    echoerr "sudo apt update; sudo apt install python"
    ungracefulExit
else
    echo SUCCESS: found python.
fi

kicli --help > /dev/null 2>&1
if [ $? == 127 ]
then
    echoerr ERROR: kicli not found.
    echoerr Suggestion
    echoerr "echo \"export PATH=\\\$KI_PROJECT_HOME:\\\$PATH\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: found kicli.
fi

kicli --help > /dev/null 2>&1
if [ $? == 126 ]
then
    echoerr ERROR: kicli has NO execute permission.
    echoerr Suggestion
    echoerr "chmod +x $KI_PROJECT_HOME/kicli"
    ungracefulExit
else
    echo SUCCESS: kicli has execute permission.
fi

exitStr=$(kicli --help 2>&1)
if [ $? != 0 ]
then
    echoerr ERROR: unknown error
    echoerr "$exitStr"
    ungracefulExit
else
    echo SUCCESS: kicli is successfully runned
fi

pythonModuleCheck()
{
    # is module exist
    python -c "import $1" > /dev/null 2>&1
    if [ $? != 0 ]
    then
        echoerr ERROR: python could not find $1 module.
        ungracefulExit
    else
        echo SUCCESS: python found $1 module.
    fi
}

pythonModuleCheck jinja2
# most likely below module comes by default just checking
pythonModuleCheck copy
pythonModuleCheck csv
pythonModuleCheck uuid

python -  > /dev/null 2>&1 << EOF
import os
import sys
try:
        home = os.environ['KI_PROJECT_HOME']
        sys.path.append(home)
except Exception as e:
        raise Exception("KI_PROJECT_HOME environment variable is not found")
EOF

if [ $? != 0 ]
then
    echoerr ERROR: python can not find environment variable KI_PROJECT_HOME
    echoerr Suggestion:
    echoerr "echo \"export KI_PROJECT_HOME=$thisDirPath\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: python found environment variable KI_PROJECT_HOME.
fi

tempDir=$(mktemp -d)
cd $tempDir
python -c "import kiapi"  > /dev/null 2>&1
if [ $? != 0 ]
then
    echoerr ERROR: python can not find kiapi module
    echoerr Suggestion:
    echoerr "echo \"export PYTHONPATH=$thisDirPath:\\\$PYTHONPATH\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: python found kiapi module
fi
rm -r $tempDir
cd $thisDirPath

echo '```bash' > $thisDirPath/doc/kicli.md
echo '$ kicli --help' >> $thisDirPath/doc/kicli.md
kicli --help >> $thisDirPath/doc/kicli.md
echo '```  ' >> $thisDirPath/doc/kicli.md
echo '![PinStyles](./img/pinStyles.PNG "PinStyles")  ' >> $thisDirPath/doc/kicli.md
echo 'Figure 1. Avaliable pin styles  ' >> $thisDirPath/doc/kicli.md
echo '![ExpectedResult](./img/attiny3224kicliHelpExpected.PNG "ExpectedResult")  ' >> $thisDirPath/doc/kicli.md
echo 'Figure 2. Expected result of help documentation example.' >> $thisDirPath/doc/kicli.md

echo
echo SUCCESS!!