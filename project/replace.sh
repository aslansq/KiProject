thisPath=$(realpath "$0")
thisDirPath=$(dirname "$thisPath")

rm -rf $thisDirPath/dev
mkdir $thisDirPath/dev
python $thisDirPath/replace.py $thisDirPath/v8 $thisDirPath/dev