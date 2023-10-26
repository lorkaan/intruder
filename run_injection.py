import argparse
from kaan_injection import HttpInjection, SniperInjection, BatteringRamInjection, PitchforkInjection, ClusterBombInjection

inject_type = [SniperInjection, BatteringRamInjection, PitchforkInjection, ClusterBombInjection]

keyword_param = [str, None, None, None]


class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value

def setup_wordlists(wordlist_files):
    if isinstance(wordlist_files, list) and len(wordlist_files) > 0:
        if len(wordlist_files) == 1:
            return wordlist_files[0]
        else:
            return []
    else:
        raise TypeError("Expected a non-empty list, got {0}".format(type(wordlist_files)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('type', type=int)
    parser.add_argument('--wordlists', '-w', nargs="+")
    parser.add_argument('--delimiter', '-d')
    parser.add_argument('--get', '-g', nargs='*')
    parser.add_argument("--post", '-p', nargs='*', action=ParseKwargs)
    parser.add_argument('--target', '-t')
    args = parser.parse_args()

    attack_type = None
    if args.type >= 0 and args.type < len(inject_type):
        attack_type = inject_type[args.type]
        keyword_param_type = keyword_param[args.type]
    else:
        raise TypeError("Can not determine which attack type to use")
    
    wlists = setup_wordlists(args.wordlists)

    # Ingnore Post Flag for now
    if issubclass(attack_type, HttpInjection):
        attk = attack_type(args.target)
        if keyword_param_type == None:
            raise Exception("This attack type {0} has been disabled".format(args.type))
        else:
            for key in args.get:
                print(attk.run(key, wlists, args.delimiter))


    
        

if __name__ == '__main__':
    main()