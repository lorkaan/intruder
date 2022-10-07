import requests

#------- Classes for doing automted HTTP Requests against a target URL ---------

class Target:
        """
            This represents a target and the number of parameters, or positions, that need to be automated.
        
            Needs to be implemented
        """

        _query_str_seperator = "?"

        _parameter_seperator = "&"

        _key_value_separate = "="


        def __init__(self, url, **kwargs):
            tmp = url.split(self.__class__._query_str_seperator)
            self.page = tmp[0]
            self.get_parameters = {}
            self.post_parameters = {}
            if len(tmp) > 1:
                for kv_pair in tmp[1].split(self.__class__._parameter_seperator):
                    kv_params = kv.pair.split(self.__class__._key_value_separate)
                    if len(kv_params) >= 2:
                        self.get_parameters[kv_params[0]] = kv_params[1]
                    else:
                        continue
            for k, v in kwargs.items():
                self.post_parameters[k] = v

        def has_parameter(self, name, get_only=True):
            if get_only:
                return True if self.get_parameters.get(name, None) else False
            else:
                return True if self.get_parameters.get(name, None) or self.post_parameters.get(name, None) else False


        @classmethod
        def _current_params(cls, inital_dict, **kwargs):
            tmp_dict = inital_dict.copy()
            tmp_dict.update(kwargs)
            return tmp_dict

        def get(self, **kwargs):
            payload = self.__class__._current_params(self.get_parameters, **kwargs)
            return requests.get(current_url, params=payload)

        def post(self, get_kwargs={}, **kwargs):
            payload = self.__class__._current_params(self.get_parameters, **get_kwargs)
            post_payload = self.__class__._current_params(self.post_parameters, **kwargs)
            return requests.post(current_url, params=payload, data=post_payload)    


