import argparse

import fasttext

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--input', help='input training file')
    arg_parser.add_argument('-o', '--output', help='output file path')
    args = arg_parser.parse_args()

    model = fasttext.train_unsupervised(
            args.input,
            'cbow',
            minCount=3,
            lr=0.1,
            ws=5,
            epoch=5,
            dim=100,
            thread=24)

    model.save_model(args.output)
