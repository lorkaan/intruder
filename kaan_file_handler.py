from kaan_lfr import LargeFileReader, TooSmallReadSizeError

class FileHandlerException(Exception):
    pass

class FileHandlerNotReady(Exception):
    pass

class MultiFileHandler(object):

    _default_file_handler_class = LargeFileReader # This needs to be made into a better system

    def __init__(self, file_names, num_handlers=1, file_handler_class = None):
        self.handlers = []
        self.buffer_sizes = []
        if file_handler_class == None: # More strict type checking
                file_handler_class = self.__class__._default_file_handler_class
        if isinstance(file_names, str) and num_handlers > 0:
            for i in range(num_handlers):
                self.handlers.append(file_handler_class(file_names))  
        elif isinstance(file_names, list):
            for file_name in file_names:
                self.handlers.append(file_handler_class(file_names))
            num_handlers = len(file_names)
        else:
            raise FileHandlerException("Input is not in expected format")
        if len(self.handlers) != num_handlers or not all(file_handler_class.is_valid, self.handlers):
            raise FileHandlerException("There exists an issue with the file handles")
        for i in range(num_handlers):
            self.buffer_sizes.append(self.handlers[i].get_default_chunk_size())

    """
    Read from specific file handler.

    """
    def read_from_handler(self, handler_index=0, delimiter=None):
        read_complete - False
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
                    
        
