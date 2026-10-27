"""Independent metric helpers and optional actual CLIPScore lab."""
def macro_f1(expected,predicted):
    labels=sorted(set(expected)|set(predicted)); scores=[]
    for label in labels:
        tp=sum(a==label and b==label for a,b in zip(expected,predicted))
        fp=sum(a!=label and b==label for a,b in zip(expected,predicted))
        fn=sum(a==label and b!=label for a,b in zip(expected,predicted))
        scores.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return sum(scores)/len(scores) if scores else 0

def clip_score(image,caption):
    import numpy as np
    from PIL import Image
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer('clip-ViT-B-32')
    with Image.open(image) as im: visual=model.encode(im.convert('RGB'))
    text=model.encode(caption)
    cosine=float(np.dot(visual,text)/(np.linalg.norm(visual)*np.linalg.norm(text)))
    # CLIPScore style rescaling; no reference caption, no safety/faithfulness guarantee.
    return {'cosine':cosine,'clipscore':2.5*max(0,cosine),'definition':'2.5 * max(0, image/text cosine); CLIP ViT-B/32'}

if __name__=='__main__':
    import argparse
    from .core import save
    p=argparse.ArgumentParser(); p.add_argument('image'); p.add_argument('caption');a=p.parse_args()
    print(save('clipscore.json',clip_score(a.image,a.caption)))
