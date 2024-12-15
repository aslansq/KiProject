thisPath=$(realpath "$0")
thisDirPath=$(dirname "$thisPath")

py=python
python3 --help > /dev/null 2>&1
if [ $? == 0 ]
then
    py=python3
fi

rm -rf $thisDirPath/dev
mkdir $thisDirPath/dev
$py $thisDirPath/replace.py $thisDirPath/v8 $thisDirPath/dev