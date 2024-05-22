import pandas as pd
import argparse

def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,description='A script for generating a string of alleles that approximates an ST for rapid evaluation of candidate loci sets for an MGT level.')
    parser.add_argument("-l", "--locils", help="list of loci to build allele profile with, one per line",required=True)
    parser.add_argument("-a", "--alleleprofile", help="cgMLST allele profile exported from MGT site with the grapetree flag (negative alleles replaced with positive versions i.e.-2_1 -> 2)", required=True)
    parser.add_argument("-o", "--output",
                        help="path to output file", required=True)
    args = parser.parse_args()
    return args

def main():

    args = parseargs()
    inp = args.locils
    inp_geneids = open(inp).read().splitlines()
    name = inp.split("/")[-1].replace(".txt","")

    inap = pd.read_csv(args.alleleprofile,sep="\t",na_values=[0])

    outap = inap[['#Name']+inp_geneids]
    outap["combined_MGT2wip"] = inap[inp_geneids].apply(lambda row: ':'.join(row.values.astype(int).astype(str)), axis=1)
    outap.columns = ['Name'] + inp_geneids + [name]
    outap.to_csv(args.output,sep="\t",index=False)


if __name__ == '__main__':
    main()
