import argparse
from kaan_injection import SniperInjection, BatteringRamInjection, PitchforkInjection, ClusterBombInjection

inject_type = [SniperInjection, BatteringRamInjection, PitchforkInjection, ClusterBombInjection]

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
        attack_type = inject_type[args.type]
    else:
        raise TypeError("Can not determine which attack type to use")

    if attack_type == inject_type[0]:
        for item in args.wordlists:
            # These is a better way to do this
            injector = attack_type(args.target)
            results = injector.run(args.position[0], item, args.delimiter)
            print(f"Results are: {results}")
    else:
        wlists = args.wordlists
        injector = attack_type(args.target)
        param_keys = injector.get_param_list()
        key_filename = {}
        if len(wlists) != len(param_keys):
            raise TypeError("Wordlists are not aligned with param list: {0} <-> {1}".format(len(param_keys), len(wlists)))
        for i in range(len(param_keys)):
            key_filename[param_keys[i]] = wlists[i]
        results = injector.run(key_filename, args.delimiter)
        print(f"Results are: {results}")
        

if __name__ == '__main__':
    main()