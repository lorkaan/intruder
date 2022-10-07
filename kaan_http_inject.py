import requests
from functools import partial

from kaan_lfr import LargeFileReader
from kaan_http_target import Target

# CLI Implementation
import argparse

inject_type = ['Sniper', 'Battering Ram', 'Pitchfork', 'Cluster Bomb']


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
                    if self._attack(chunk): # Looking for a chunk that gives a positive result from the given function
                        return chunk
                    else:
                        continue
            return None
        else:
            raise IOError("Can not read from {0}".format(filepath))

class SniperInject(HttpInject):

    def __init__(self, keyword, target_url, post_flag=False, **post_kwargs):
        if not isinstance(keyword, str):
            raise TypeError("keyword param needs to be a string")
        self.keyword = keyword
        super().__init__(target_url=target_url, post_flag=post_flag, **post_kwargs)

    def _attack(self, chunk):
        tmp_params = {}
        tmp_params[self.keyword] = chunk
        return self._send_request(None, **tmp_params)

        

#------- Helper functions used to run the Objects in a Modular manner --------

def read_word_list(filepath, delimiter):
    """
        This utilizes the LargeFileReader class to
        read a word list from a file and apply the 
        desired functionality for each item in that list

        @param filepath This is the path to the word list file
    """
    reader = LargeFileReader(filepath)
    reader.get_chunks(print, delimiter)

#------- This is the main function that runs everything ------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('type', type=int)
    parser.add_argument('--wordlists', '-w', nargs="+")
    parser.add_argument('--delimiter', '-d')
    args = parser.parse_args()
    if args.type >= 0 and args.type < len(inject_type):
        print(inject_type[args.type])
    else:
        print("No type of that kind")
    print(args.wordlists)
    for item in args.wordlists:
        read_word_list(item, args.delimiter)

if __name__ == '__main__':
    main()