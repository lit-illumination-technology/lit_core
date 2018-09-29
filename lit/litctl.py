#! /usr/bin/python3
import argparse
import lit

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send a command to the L.I.T. daemon')
    parser.add_argument('effect', type=str, 
                                help='name of the effect')
    parser.add_argument('--speed', '-s', dest='speed', type=float, 
                                help='speed of the effect (if applicable)')
    parser.add_argument('--color', '-c', dest='color', metavar=('RED', 'GREEN', 'BLUE'), type=int, nargs=3,
                                help='rgb color')

    args = parser.parse_args()
    resp = lit.start(effect=args.effect, args={'speed': args.speed, 'color': args.color})
    print(resp['result'])
    exit(resp['rc'])
