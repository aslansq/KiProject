from kiconst import KiConst
import jinja2
import os
# minimal dummy class just to be able to generate
class KiSchEditPrj:
        def __init__(self):
                self.prj = None

        def parse(self, prj):
                self.prj = prj
        
        def gen(self, templateFilePath, outFolderPath):
                templateFileName = os.path.basename(templateFilePath)
                templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(templateFilePath))
                templateEnv = jinja2.Environment(loader=templateLoader)
                template = templateEnv.get_template(templateFileName)

                # change the filename to library name
                self.outFileName = templateFileName.replace(KiConst.invertedUniqDict["project.name"], self.prj.name)

                outFilePath = os.path.join(outFolderPath, self.outFileName)
                renderedText = template.render(project=self.prj)
                with open(os.path.join(outFolderPath, outFilePath), 'w') as f:
                        f.write(renderedText)
                print("Gen: " + str(outFilePath))
