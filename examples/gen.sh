thisPath=$(realpath "$0")
req=$1
thisDirPath=$(dirname "$thisPath")
prjDirPath=$thisDirPath/..

cd $prjDirPath
if [[ $? != 0 ]]
then
    echo cd to project directory failed
    exit 1
fi

# clear old files
rm -rf ./out
mkdir -p ./out
# clear old log files
rm -rf ./log
mkdir -p ./log

# generate and collect examples
cd examples
python custom.py > custom.csv
examples=$(find . -type f | grep '.csv')
cd ..

# if there is specific request do not generate everything
if [[ ! -z "${req}" ]]
then
    examples=${req}
fi

for example in $examples
do
    mkdir -p ./examples/out/${example%.csv}
    mkdir -p ./examples/log
    echo python kicli.py --csvFilePath ./examples/$example --outFolderPath ./examples/out/${example%.csv} --logFolderPath ./examples/log --pageWidth 384 --pageHeight 216
    python kicli.py --csvFilePath ./examples/$example --outFolderPath ./examples/out/${example%.csv} --logFolderPath ./examples/log --pageWidth 384 --pageHeight 216
done

