thisPath=$(realpath "$0")
req=$1
thisDirPath=$(dirname "$thisPath")
prjDirPath=$thisDirPath/..

rm -rf $thisDirPath/log
rm -rf $thisDirPath/out

gen()
{
    example=$1
    customArg=$2
    mkdir -p $thisDirPath/out/$example
    mkdir -p $thisDirPath/log
    cmd="
python $prjDirPath/kicli.py
        --csvFilePath $thisDirPath/${example}.csv
        --outFolderPath $thisDirPath/out/${example}
        --logFolderPath $thisDirPath/log
        --pageWidth 384
        --pageHeight 216
        $customArg
    "
    echo "$cmd"

    python $prjDirPath/kicli.py \
           --csvFilePath $thisDirPath/${example}.csv \
           --outFolderPath $thisDirPath/out/${example} \
           --logFolderPath $thisDirPath/log \
           --pageWidth 384 \
           --pageHeight 216 \
           $customArg
}

if [ ! -z "$req" ]
then
    gen $req
else
    gen microchip "--pinNumbers --fullProject"

    echo
    echo
    echo Showcase
    cd $thisDirPath
    python showcase.py
fi
