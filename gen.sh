rm -rf ./out
mkdir -p ./out
cd examples
python custom.py > custom.csv
cd ..
python kigen.py --csvFilePath ./examples/custom.csv --outFolderPath ./out --info
