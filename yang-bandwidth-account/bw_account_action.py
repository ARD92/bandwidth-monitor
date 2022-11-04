import os
import json
import argparse

def generate_xml(args):
    if (args.rpc_name == "get-bandwidth-account"):
        print(args)
        with open("/var/log/peak_{}_{}.json".format(args.year, args.month)) as f:
            fdata = json.load(f)
            XML = '''
               <bw-account>
               <time>{0}</time>
               <peak-bps>{1}</peak-bps>
               </bw-account>
               '''.format(fdata["time"], fdata["BPS"])
            return XML

def main():
    parser = argparse.ArgumentParser(description='peak bw account script')
    parser.add_argument('--rpc_name', required=True)
    parser.add_argument('--year', required=True, default=None)
    parser.add_argument('--month', required=True, default=None)
    args = parser.parse_args()

    rpc_output_xml = generate_xml(args)
    print(rpc_output_xml)

if __name__ == "__main__":
    main()
