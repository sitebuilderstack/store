#!/usr/bin/env python3
"""Pull theme files to a local directory via the Admin GraphQL API.
Usage: theme_pull.py <themeId> <destDir> [filenameGlob ...]"""
import sys, os, base64, fnmatch, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from shopify_api import gql

def list_files(tid):
    q="""query($id:ID!,$after:String){theme(id:$id){name role files(first:250,after:$after){
         pageInfo{hasNextPage endCursor} nodes{filename size contentType}}}}"""
    after=None; out=[]
    while True:
        d=gql(q,{"id":tid,"after":after}); t=d['theme']; out+=t['files']['nodes']
        if not t['files']['pageInfo']['hasNextPage']: break
        after=t['files']['pageInfo']['endCursor']
    return t['name'], t['role'], out

def read_files(tid, names):
    q="""query($id:ID!,$names:[String!]!){theme(id:$id){files(first:50,filenames:$names){
         nodes{filename body{ ... on OnlineStoreThemeFileBodyText{content}
                              ... on OnlineStoreThemeFileBodyBase64{contentBase64}
                              ... on OnlineStoreThemeFileBodyUrl{url} }}}}}"""
    out={}
    for i in range(0,len(names),20):
        chunk=names[i:i+20]
        d=gql(q,{"id":tid,"names":chunk})
        for n in d['theme']['files']['nodes']:
            b=n['body'] or {}
            if 'content' in b: out[n['filename']]=('text',b['content'])
            elif 'contentBase64' in b: out[n['filename']]=('b64',b['contentBase64'])
            elif 'url' in b: out[n['filename']]=('url',b['url'])
    return out

if __name__=="__main__":
    tid=sys.argv[1]; dest=sys.argv[2]; globs=sys.argv[3:] or ['*']
    if not tid.startswith('gid://'): tid=f"gid://shopify/OnlineStoreTheme/{tid}"
    name,role,files=list_files(tid)
    want=[f['filename'] for f in files if any(fnmatch.fnmatch(f['filename'],g) for g in globs)]
    print(f"theme={name} role={role} matched {len(want)}/{len(files)} files -> {dest}")
    bodies=read_files(tid,want)
    for fn,(kind,val) in bodies.items():
        p=os.path.join(dest,fn); os.makedirs(os.path.dirname(p),exist_ok=True)
        if kind=='text': open(p,'w',encoding='utf8').write(val)
        elif kind=='b64': open(p,'wb').write(base64.b64decode(val))
        else: open(p+'.url','w').write(val)
    print(f"wrote {len(bodies)} files")
