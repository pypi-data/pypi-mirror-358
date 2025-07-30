import configparser

class ConfigManager(configparser.ConfigParser):
    def __init__(self, file_addr, *args, **kwargs):
        self.__file_addr = file_addr
        super().__init__(*args, **kwargs)
    
    
    def set(self, section, option, value = None, save: bool = False):
        super().set(section, option, value)
        if save:
            self.update()
            
    def update(self)-> None:
        with open(self.__file_addr, "w") as file:
            self.write(file)

    def read(self, encoding = None):
        filenames = self.__file_addr
        return super().read(filenames, encoding)