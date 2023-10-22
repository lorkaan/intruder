
def run(attack_type, target, post_flag=False, **args):
    if post_flag:
        injector = attack_type(target, post_flag)
    else:
        injector = attack_type(target)
    return injector.run(args, args.delimiter)