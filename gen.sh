# clear old files
rm -rf ./out
mkdir -p ./out
# generate and collect examples
cd examples
#python custom.py > custom.csv
examples=$(find . -type f | grep '.csv')
cd ..
# collect templates
cd templates
templateFiles=$(find . -type f)
cd ..
# good luck
for templateFile in $templateFiles
do
    for example in $examples
    do
        mkdir -p ./out/${example%.csv}
        echo python kigen.py --csvFilePath ./examples/$example --outFolderPath ./out/${example%.csv} --logFolderPath ./log --templateFilePath ./templates/$templateFile
        python kigen.py --csvFilePath ./examples/$example --outFolderPath ./out/${example%.csv} --logFolderPath ./log --templateFilePath ./templates/$templateFile
    done
done
