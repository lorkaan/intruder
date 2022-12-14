from kaan_http_target import Target
from kaan_file_handler import MultiFileHandler, SingleFileHandler, NamedMultiFileHandler, FileHandlerNotReady

class HttpInjection:
    # Already a BatteringRamInjection

    _target_type = Target

    _wordlist_file_reader = MultiFileHandler

    @classmethod
    def _default_process_response(cls, response): # Need a better thing than this
        if(len(response.text) > 0):
            return True
        else:
            return False

    def __init__(self, target_url, post_flag=False, **post_kwargs):
        """ 
        
        @param kwargs => A dictionary for the POST parameters
        """
        self.target = self.__class__._target_type(target_url, **post_kwargs)
        self.post_flag = post_flag

    def get_param_list(self):
        return list(self.target.get_parameters.keys())

    def _send_request(self, process_response, **inject_kwargs):
        if self.post_flag:
            resp = self.target.post(**inject_kwargs)
        else:
            resp = self.target.get(**inject_kwargs)
        try:
            return self._handle_response(resp, process_response)
        except Exception as e:
            print(e)
            return None

    @classmethod
    def _check_status_code(cls, code):
        return code >= 200 and code < 300

    def _handle_response(self, response, process_repsonse):
        if self.__class__._check_status_code(response.status_code):
            # in the 200 range, so good
            if not callable(process_repsonse):
                process_response = self.__class__._default_process_response
            return process_response(response)
        else:
            raise Exception("Bad Status Code")

    def run(self):
        pass

class SniperInjection(HttpInjection):

    _wordlist_file_reader = SingleFileHandler

    def run(self, keyword, filename, delimiter=None, process_response_func=None):
        reader = self.__class__._wordlist_file_reader(filename)
        params = {}
        found_flag = False
        while not found_flag:
            # Repeatedly read from chunks from reader and for c in chunk send_request with keyword=c
            try:
                chunk_map = reader.read(delimiter=None)
                for chunk in chunk_map:
                    params[keyword] = chunk
                    found_flag = self._send_request(process_response_func, **params)
                    if found_flag:
                        break
            except FileHandlerNotReady:
                break
        if found_flag:
            return params
        else:
            return {}

class BatteringRamInjection(HttpInjection):
    pass

class PitchforkInjection(HttpInjection):
    pass

class ClusterBombInjection(HttpInjection):
    
    _wordlist_file_reader = NamedMultiFileHandler

    """
        Recursively read though all the lists bit by bit trying to hold as least as possible in memory

        Note:
            Recursion works like a chain, signaling the previous file in the least to read one more
    """
    def _recurse_read(self, params, index, reader, keys, filenames, delimiter=None, process_response_func=None):
        if len(keys) != len(filenames):
            raise TypeError("Lists are not aligned   keys: {0} filenames: {1}".format(len(keys), len(filenames)))
        if index < 0 or index >= len(keys):
            raise IndexError("Index is out of range: {0} {1}".format(index, len(keys)))
        found_flag = False
        if index == (len(keys)-1):
            while not found_flag:
                try:
                    chunk_map = reader.read_filename(filenames[index], delimiter=delimiter)
                    for chunk in chunk_map:
                        params[keys[index]] = chunk
                        found_flag = self._send_request(process_response_func, **params)
                        if found_flag:
                            return found_flag, params
                        else:
                            continue
                except FileHandlerNotReady:
                    #import pdb; pdb.set_trace()
                    reader.reset_filename(filenames[index])
                    return False, {}
        else:
            while not found_flag:
                try:
                    chunk_map = reader.read_filename(filenames[index], delimiter=delimiter)
                    for chunk in chunk_map:
                        params[keys[index]] = chunk
                        found_flag, params = self._recurse_read(params, index+1, reader, keys, filenames, delimiter, process_response_func)
                        if found_flag:
                            return found_flag, params
                        else:
                            continue
                except FileHandlerNotReady:
                    reader.reset_filename(filenames[index])
                    return False, {}
        

    def run(self, keyword_filename_dict, delimiter=None, process_response_func=None):
        found_flag = False
        filenames = []
        keys = []
        for key, filename in keyword_filename_dict.items():
            filenames.append(filename)
            keys.append(key)
        reader = self.__class__._wordlist_file_reader(filenames)
        found_flag, params = self._recurse_read(self.target.get_parameters, 0, reader, keys, filenames)
        if found_flag:
            return params
        else:
            return {}
            
        