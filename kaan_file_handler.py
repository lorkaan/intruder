from kaan_lfr import LargeFileReader, TooSmallReadSizeError

class FileHandlerException(Exception):
    pass

class FileHandlerNotReady(Exception):
    pass

class MultiFileHandler(object):
    """
        A class for handling multiple reading from files 
    """

    _default_file_handler_class = LargeFileReader # This needs to be made into a better system

    def __init__(self, file_names, num_handlers=1, file_handler_class = None):
        self.handlers = []
        self.buffer_sizes = []
        if file_handler_class == None: # More strict type checking
                file_handler_class = self.__class__._default_file_handler_class
        if isinstance(file_names, str) and num_handlers > 0:
            for i in range(num_handlers):
                self.handlers.append(file_handler_class(file_names[i]))  
        elif isinstance(file_names, list):
            for file_name in file_names:
                self.handlers.append(file_handler_class(file_name))
            num_handlers = len(file_names)
        else:
            raise FileHandlerException("Input is not in expected format")
        if len(self.handlers) != num_handlers or not all(map(file_handler_class.is_valid, self.handlers)):
            raise FileHandlerException("There exists an issue with the file handles")
        for i in range(num_handlers):
            self.buffer_sizes.append(self.handlers[i].get_default_chunk_size())

    """
    Read from specific file handler.

    delimiter is in here as a parameter in case the delimiter is being specified by the read as
    an override

    """
    def read_from_handler(self, handler_index=0, delimiter=None):
        read_complete = False
        if handler_index >= 0 and handler_index < len(self.handlers):
            if self.handlers[handler_index].is_ready():
                while not read_complete:
                    try:
                        chunk_map = self.handlers[handler_index].read_chunk(self.buffer_sizes[handler_index], delimiter)
                        read_complete = True
                    except TooSmallReadSizeError:
                        self.buffer_sizes[handler_index] = self.handlers[handler_index]._increase_chunk_size(self.buffer_sizes[handler_index])
                return chunk_map
            else:
                raise FileHandlerNotReady("File is not ready to be read")
        else:
            raise IndexError("Given handler index is not in range")

    def reset_filename(self, handler_index):
        if handler_index >= 0 and handler_index < len(self.handlers):
            self.handlers[handler_index].reset_file()
        else:
            raise IndexError("Given handler index is not in range")

class SingleFileHandler(MultiFileHandler):
    """
        Convience class for handling a single file with the MultiFileHandler class
    """

    def __init__(self, file_name, file_handler_class = None):
        if not isinstance(file_name, str):
            raise TypeError("Expected a single file name to be passed")
        super().__init__(file_name, num_handlers=1, file_handler_class=file_handler_class)

    def read(self, delimiter=None):
        return super().read_from_handler(0, delimiter=delimiter)

                    
class NamedMultiFileHandler(MultiFileHandler):
    """
    Child class for the MultiFileHandler

    Adds an interface for handling files in the system by name rather by
    index with the MultiFileHandler does

    """

    def __init__(self, filenames=[], file_handler_class=None):
        if not isinstance(filenames, list) or len(filenames) <= 0:
            raise TypeError("Filenames must be a non-empty list of filenames")
        self.file_name_index = {}
        for i in range(len(filenames)):
            self.file_name_index[filenames[i]] = i
        super().__init__(filenames, file_handler_class=file_handler_class)

    def reset_filename(self, filename):
        file_index = self.file_name_index.get(filename, -1)
        try:
            super().reset_filename(file_index)
        except IndexError:
            raise KeyError("filename: {0} does not have an index".format(filename))

    def read_filename(self, filename, delimiter=None):
        file_index = self.file_name_index.get(filename, -1)
        try:
            return self.read_from_handler(file_index, delimiter=delimiter)
        except IndexError:
            raise KeyError("filename: {0} does not have an index".format(filename))