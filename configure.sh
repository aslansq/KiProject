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
    echoerr "echo -e \"\\nexport KI_PROJECT_HOME=$thisDirPath\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: found KI_PROJECT_HOME environment variable.
fi

# does it point to current directory
if [ $KI_PROJECT_HOME != $thisDirPath ]
then
    echoerr ERROR: KI_PROJECT_HOME points to different location $KI_PROJECT_HOME
    echoerr Suggestion:
    echoerr "Please update KI_PROJECT_HOME and PYTHONPATH to $thisDirPath to use this version."
    ungracefulExit
else
    echo SUCCESS: KI_PROJECT_HOME points to this version
fi


# is environment points to existing directory
if [ ! -d $KI_PROJECT_HOME ]
then
    echoerr ERROR: KI_PROJECT_HOME points to unexisting directory.
    echoerr Suggestion:
    echoerr "echo -e \"\\nexport KI_PROJECT_HOME=$thisDirPath\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: KI_PROJECT_HOME points to existing directory.
fi

# is repo broken
if [ ! -f $KI_PROJECT_HOME/kicli ]
then
    echoerr ERROR: KI_PROJECT_HOME points to broken repo. Not found $KI_PROJECT_HOME/kicli
    echoerr Suggestion:
    echoerr "cd $thisDirPath; git status"
    ungracefulExit
else
    echo SUCCESS: kicli file found
fi

# is repo broken
if [ ! -f $KI_PROJECT_HOME/kiapi.py ]
then
    echoerr ERROR: KI_PROJECT_HOME points to broken repo. Not found $KI_PROJECT_HOME/kiapi.py
    echoerr Suggestion:
    echoerr "cd $thisDirPath; git status"
    ungracefulExit
else
    echo SUCCESS: kiapi.py file found
fi

py=python
python3 --help > /dev/null 2>&1
if [ $? == 0 ]
then
    py=python3
fi

# is $py exist
$py --help > /dev/null 2>&1
if [ $? != 0 ]
then
    echoerr ERROR: $py does not exist.
    echoerr Suggestion
    echoerr Windows
    echoerr Install python3 from https://www.python.org/downloads/
    echoerr GNU/Linux
    echoerr "sudo apt update; sudo apt install python3"
    ungracefulExit
else
    echo SUCCESS: found $py.
fi

moduleCheck()
{
    # is module exist
    $py -c "import $1" > /dev/null 2>&1
    if [ $? != 0 ]
    then
        echoerr ERROR: $py could not find $1 module.
        ungracefulExit
    else
        echo SUCCESS: $py found $1 module.
    fi
}

moduleCheck jinja2
# most likely below module comes by default just checking
moduleCheck copy
moduleCheck csv
moduleCheck uuid

$py -  > /dev/null 2>&1 << EOF
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
    echoerr ERROR: $py can not find environment variable KI_PROJECT_HOME
    echoerr Suggestion:
    echoerr "echo -e \"\\nexport KI_PROJECT_HOME=$thisDirPath\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: $py found environment variable KI_PROJECT_HOME.
fi

tempDir=$(mktemp -d)
cd $tempDir
$py -c "import kiapi"  > /dev/null 2>&1
if [ $? != 0 ]
then
    echoerr ERROR: $py can not find kiapi module
    echoerr Suggestion:
    echoerr Windows
    echoerr add to environment variable PYTHONPATH using gui, $thisDirPath
    echoerr GNU/Linux
    echoerr "echo -e \"\\nexport PYTHONPATH=$thisDirPath:\\\$PYTHONPATH\" >> ~/.bashrc"
    ungracefulExit
else
    echo SUCCESS: $py found kiapi module
fi
rm -r $tempDir
cd $thisDirPath

kicli --help > /dev/null 2>&1
if [ $? == 127 ]
then
    echoerr ERROR: kicli not found.
    echoerr Suggestion
    echoerr "echo -e \"\\nexport PATH=\\\$KI_PROJECT_HOME:\\\$PATH\" >> ~/.bashrc"
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