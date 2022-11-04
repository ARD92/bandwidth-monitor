import os
import json
import argparse

def generate_xml(args):
    if (args.rpc_name == "bandwidth-account"):
        with open("/var/log/peak_{}_{}.json".format(args.year, args.month) as f:
            fdata = json.loads(f)
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
    for xml_val in rpc_output_xml:
        print(xml_val)

if __name__ == "__main__":
    main()
