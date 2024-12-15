thisPath=$(realpath "$0")
req=$1
thisDirPath=$(dirname "$thisPath")
prjDirPath=$thisDirPath/..

# if everything is okay; dont tell anything to user
$prjDirPath/configure.sh 1>/dev/null

if [ $? != 0 ]
then
    exit 1
fi

rm -rf $thisDirPath/log
rm -rf $thisDirPath/out

gen()
{
    example=$1
    customArg=$2
    mkdir -p $thisDirPath/out/$example
    mkdir -p $thisDirPath/log
    cmd="
kicli \\
    --csvFilePath $thisDirPath/${example}.csv \\
    --outFolderPath $thisDirPath/out/${example} \\
    --logFolderPath $thisDirPath/log \\
    --pageWidth 384 \\
    --pageHeight 216 \\
    $customArg
    "
    echo "$cmd"

    kicli \
        --csvFilePath $thisDirPath/${example}.csv \
        --outFolderPath $thisDirPath/out/${example} \
        --logFolderPath $thisDirPath/log \
        --pageWidth 384 \
        --pageHeight 216 \
        $customArg
    if [ $? != 0 ]
    then
        exit 1
    fi
}

genPython()
{
    example=$1
    echo
    echo python $example.py
    echo
    cd $thisDirPath
    mkdir -p out/$example
    mkdir -p log
    python $example.py
    if [ $? != 0 ]
    then
        exit 1
    fi
}

if [ ! -z "$req" ]
then
    gen $req
else
    gen microchip "--pinNumbers"

    genPython showcase

    genPython simple
fi
