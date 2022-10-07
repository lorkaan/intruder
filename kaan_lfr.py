#------ These are the Classes for the Reading word lists -------

class TooSmallReadSizeError(Exception):
    """
        Class used to specify an exception that requires
        increasing the chunk size of the reading buffer
    """
    pass

class LargeFileReader:
    """
        This serves a lightweight interface for iteratively accessing
        data stored in large files.

        This is easier on the computer than storing all the lines in
        memory before handling them, so only a batch or chunk of the
        data file is processed at a time.
    """

    _default_read_size = 10

    _default_chunk_delimiter = '\n'

    @classmethod
    def is_valid(cls, obj):
        return (isintance(obj, cls) and obj.file != None)

    @classmethod
    def _process_chunk(cls, chunk):
        """ This processes a Chunk for things like
        handling the protocol for the file type

        Does not handle the actual use of each chunk, but
        rather turning the chunk storage into something useful
        for the given function to do something with the chunk
        """
        return chunk

    @classmethod
    def _default_process_result_item(cls, obj):
        """
        Default function for handling a chunk of information
        read from file.

        This is the function that activates if there is no
        function given to the system.
        """
        print(obj)

    @classmethod
    def _increase_chunk_size(cls, size):
        return size + 1

    @classmethod
    def get_default_chunk_size(cls):
        return cls._default_read_size

    def _reset_buffer(self):
        self.prev_buffer = None

    def _set_buffer(self, chunk):
        if self.prev_buffer == None:
            self.prev_buffer = chunk
        else:
            self.prev_buffer = self.prev_buffer + chunk

    def __init__(self, file_name):
        try:
            self.file = open(file_name, 'r')
            self.prev_buffer = None
        except IOError as e:
            print(e)
            self.file = None
        self.eof = False

    def reset_file(self, offset=0, from_where=0):
        if self.file == None:
            return
        self.file.seek(offset, from_where)
        self.eof = False

    def is_ready(self):
        return not self.eof

    def read_chunk(self, size, delimiter=None):
        if self.file == None or self.eof == True:
            return map(self.__class__._process_chunk, [])
        if size < 1:
            size = self.__class__._default_read_size
        if delimiter == None:
            delimiter = self.__class__._default_chunk_delimiter
        chunk_info = self.file.read(size)
        delimited_pieces = chunk_info.split(delimiter)
        if self.prev_buffer != None:
            if len(delimited_pieces) > 0:
                delimited_pieces[0] = self.prev_buffer + delimited_pieces[0]
            else:
                delimited_pieces.append(self.prev_buffer)
            self._reset_buffer()
        if len(chunk_info) < size:
            # EOF
            self.eof = True
            return map(self.__class__._process_chunk, delimited_pieces)
        if len(delimited_pieces) > 1:
            extra_piece = delimited_pieces.pop(-1) # in case the chunk does not catch the last one 
            # len(extra_piece) is the amount the seek pointer needs to go back by
            self._set_buffer(extra_piece)
            # Note: This returns a map class that has the qualities of an iterator
            return map(self.__class__._process_chunk, delimited_pieces)
        else:
            self._set_buffer(delimited_pieces[0])
            # Unable to pull a specific chunk with definite end (delimiter)
            raise TooSmallReadSizeError("There is no delimiter in the chunk")

    def get_chunks(self, process_result_item=None, delimiter=None):
        """
        @param {function} process_result_item   This is a function that does something useful with each chunk
        
        This is a good automated system, but for more advanced things, we need to 
        use read_chunk(), which this is a good example for.
        
        """
        if not callable(process_result_item):
            process_result_item = self.__class__._default_process_result_item
        cur_size = self.__class__.get_default_chunk_size()
        while self.is_ready() and self.file != None:
            try:
                chunk_map = self.read_chunk(cur_size, delimiter)
            except TooSmallReadSizeError:
                cur_size = self.__class__._increase_chunk_size(cur_size)
                continue
            for chunk in chunk_map:
                if process_result_item(chunk): # Looking for a chunk that gives a positive result from the given function
                    return chunk
                else:
                    continue
        return None

    def __del__(self): 
        if self.file != None:
            self.file.close()

