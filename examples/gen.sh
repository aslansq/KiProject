thisPath=$(realpath "$0")
req=$1
thisDirPath=$(dirname "$thisPath")
prjDirPath=$thisDirPath/..

gen()
{
    example=$1
    customArg=$2
    mkdir -p $thisDirPath/out/${example%.csv}
    mkdir -p $thisDirPath/log
    cmd="
python $prjDirPath/kicli.py
        --csvFilePath $thisDirPath/$example
        --outFolderPath $thisDirPath/out/${example%.csv}
        --logFolderPath $thisDirPath/log
        --pageWidth 384
        --pageHeight 216
        $customArg
    "
    echo "$cmd"

    python $prjDirPath/kicli.py \
           --csvFilePath $thisDirPath/$example \
           --outFolderPath $thisDirPath/out/${example%.csv} \
           --logFolderPath $thisDirPath/log \
           --pageWidth 384 \
           --pageHeight 216 \
           $customArg
}

if [ ! -z "$req" ]
then
    gen $req
else
    gen in.csv
    gen one.csv
    gen two.csv --pinNumbers

    echo
    echo
    echo Showcase
    cd $thisDirPath
    python showcase.py
fi
