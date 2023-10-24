import requests
from functools import partial

from kaan_lfr import LargeFileReader, TupleFileReader, TooSmallReadSizeError
from kaan_http_target import Target

# CLI Implementation
import argparse

inject_type_keys = ['Sniper', 'Battering Ram', 'Pitchfork', 'Cluster Bomb']

class HttpInject:
    """
        Super class for implementing the child classes of attacks
            Sniper
            Battering Ram
            Pitchfork
            Cluster Bomb
    """

    @classmethod
    def _default_process_response(cls, response):
        if(len(response.text) > 0):
            return True
        else:
            return False

    def _valid_chunk(self, chunk):
        return isinstance(chunk, str)

    _wordlist_file_reader = LargeFileReader

    _target_type = Target


    def __init__(self, target_url, post_flag=False, **post_kwargs):
        """ 
        
        @param kwargs => A dictionary for the POST parameters
        """
        self.target = self.__class__._target_type(target_url, **post_kwargs)
        self.post_flag = post_flag

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

    def _attack(self, chunk):
        return None
    
    def run(self, filepath, delimiter=None):
        """
            Run the specified attack using a wordlist
        """
        reader = self.__class__._wordlist_file_reader(filepath)
        if self.__class__._wordlist_file_reader.is_valid(reader):
            cur_size = self.__class__._wordlist_file_reader.get_default_chunk_size()
            while reader.is_ready():
                try:
                    chunk_map = reader.read_chunk(cur_size, delimiter)
                except TooSmallReadSizeError:
                    cur_size = self.__class__._wordlist_file_reader._increase_chunk_size(cur_size)
                    continue
                for chunk in chunk_map:
                    if self._valid_chunk(chunk) and self._attack(chunk): # Looking for a chunk that gives a positive result from the given function
                        return chunk
                    else:
                        continue
            return None
        else:
            raise IOError("Can not read from {0}".format(filepath))

class KeywordInject(HttpInject):
    """ There is a better way to do this than using Keyword and MultiKeyword """

    @classmethod
    def _valid_keywords(cls, keyword):
        if isinstance(keyword, list) and len(keyword) > 0:
            for k in keyword:
                if isinstance(k, str):
                    continue
                else:
                    return False
            return True
        else:
            return False

    def __init__(self, keyword, target_url, post_flag=False, **post_kwargs):
        print(keyword)
        if not self.__class__._valid_keywords(keyword):
            raise TypeError("keyword param needs to be a string")
        self.keyword = keyword
        super().__init__(target_url=target_url, post_flag=post_flag, **post_kwargs)


class MultiPayloadInject(KeywordInject):

    def _attack(self, chunk):
        tmp_params = {}
        if len(chunk) == len(self.keyword):
            for i in range(len(chunk)):
                tmp_params[self.keyword[i]] = chunk[i]
            return self._send_request(None, **tmp_params)
        else:
            return False

class SniperInject(KeywordInject):

    def _attack(self, chunk):
        if len(self.keyword) > 0:
            tmp_params = {}
            tmp_params[self.keyword[0]] = chunk
            return self._send_request(None, **tmp_params)
        else:
            raise TypeError("SniperInject requires a parameter to work on")

class BatteringRamInject(KeywordInject):

    def _attack(self, chunk):
        tmp_params = {}
        for k in self.keyword:
            tmp_params[k] = chunk
        return self._send_request(None, **tmp_params)

class PitchforkInject(MultiPayloadInject):

    _wordlist_file_reader = TupleFileReader

    def _valid_chunk(self, chunk):
        return isinstance(chunk, tuple) and len(chunk) == len(self.keyword)


class ClusterBombInject(MultiPayloadInject):
    """ This is not implemented yet 
    
    Need a way to iterate though every permutation 
    held in a large file. Might have to actually store 
    the contents
    """

    _wordlist_file_reader = TupleFileReader


#------- This is the main function that runs everything ------

inject_type = [SniperInject, BatteringRamInject, PitchforkInject, ClusterBombInject]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('type', type=int)
    parser.add_argument('--wordlists', '-w', nargs="+")
    parser.add_argument('--delimiter', '-d')
    parser.add_argument('--position', '-p', nargs='+')
    parser.add_argument('--target', '-t')
    args = parser.parse_args()

    attack_type = None
    if args.type >= 0 and args.type < len(inject_type):
        if args.type == 3:
            raise NotImplementedError("Cluster Bomb not supported")
        attack_type = inject_type[args.type]
    else:
        raise TypeError("Can not determine which attack type to use")

    for item in args.wordlists:
        # These is a better way to do this
        injector = attack_type(args.position, args.target)
        results = injector.run(item, args.delimiter)
        print(f"Results are: {results}")


if __name__ == '__main__':
    main()