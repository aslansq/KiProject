import os
import jinja2
from kiconst import KiConst

class KiPrl:
        def __init__(self, projectName):
                self.projectName = projectName

        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["xproject.name"], self.projectName)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(projectName=self.projectName)
                with open(outFilePath, 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))
