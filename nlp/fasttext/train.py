import fasttext
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, help="training file path")
    parser.add_argument("-o", required=True, help="output model file path")
    args = parser.parse_args()

    model = fasttext.train_unsupervised(
        args.i, "cbow", minCount=3, lr=0.1, ws=5, epoch=5, dim=100, thread=24
    )

    # model.save_model(args.o)
