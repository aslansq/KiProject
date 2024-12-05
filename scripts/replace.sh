thisPath=$(realpath "$0")
thisDirPath=$(dirname "$thisPath")
prjDirPath=$thisDirPath/..
cd $prjDirPath
if [[ $? != 0 ]]
then
    echo cd to project directory failed
    exit 1
fi
rm -rf ./dev
mkdir ./dev
python $thisDirPath/replace.py