import os
from os.path import expanduser

class PanExporter:
    def __init__(self, pandataset, filelocation=None):
        self.module_dir = os.path.dirname(os.path.dirname(__file__))
        self.pandataset=pandataset
        if filelocation == None:
            self.filelocation =os.path.join(expanduser("~"),'pangaeapy_export')
            try:
                os.makedirs(self.filelocation)
            except FileExistsError:
                pass
        else:
            self.filelocation = filelocation
        self.file = None
        self.logging = self.pandataset.logging
        #print(self.logging)

    #check if export is possible
    def verify(self):
        return True

    #create the export file (as IO object if possible)
    def create(self):
        return True

    #save the file  at self.filelocation
    def save(self):
        return True

    #return a string representation of the export file
    def __str__(self):
        return ''