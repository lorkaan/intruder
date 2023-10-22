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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('type', type=int)
    parser.add_argument('--wordlists', '-w', nargs="+")
    parser.add_argument('--delimiter', '-d')
    parser.add_argument('--get', '-g', nargs='*', action=ParseKwargs)
    parser.add_argument("--post", '-p', nargs='*', action=ParseKwargs)
    parser.add_argument('--target', '-t')
    args = parser.parse_args()

    attack_type = None
    if args.type >= 0 and args.type < len(inject_type):
        attack_type = inject_type[args.type]
        keyword_param_type = keyword_param[args.type]
    else:
        raise TypeError("Can not determine which attack type to use")

    if attack_type == ClusterBombInjection:
        pass    # To Do: got to get the wordlists in place

    # Ingnore Post Flag for now
    if isinstance(attack_type, HttpInjection):
        attk = attack_type(args.get)
        if keyword_param_type == None:
            raise Exception("This attack type {0} has been disabled".format(args.type))
        

    
        

if __name__ == '__main__':
    main()