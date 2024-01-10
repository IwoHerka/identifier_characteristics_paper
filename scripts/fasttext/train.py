import fasttext

model = fasttext.train_unsupervised(
    'training_file.txt',
    'cbow',
    minCount=3,
    lr=0.1,
    ws=5,
    epoch=5,
    dim=100,
    thread=24
)

model.save_model('model.bin')
