"""Minimal Merkle commitment/opening demo for oracle-style proof intuition."""
import hashlib

def H(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def leaf(x: bytes) -> bytes:
    return H(b"\x00" + x)

def node(a: bytes,b: bytes) -> bytes:
    return H(b"\x01" + a + b)

def build(values):
    if not values or len(values)&(len(values)-1):
        raise ValueError("use a non-empty power-of-two number of leaves")
    levels=[[leaf(v) for v in values]]
    while len(levels[-1])>1:
        cur=levels[-1]
        levels.append([node(cur[i],cur[i+1]) for i in range(0,len(cur),2)])
    return levels

def open_path(levels,index):
    path=[]; i=index
    for level in levels[:-1]:
        path.append((i&1, level[i^1]))
        i//=2
    return path

def verify(root,value,index,path):
    h=leaf(value); i=index
    for was_right,sibling in path:
        h=node(sibling,h) if was_right else node(h,sibling)
        i//=2
    return h==root

def self_test():
    vals=[f"v{i}".encode() for i in range(8)]
    tree=build(vals); root=tree[-1][0]
    p=open_path(tree,5)
    assert verify(root,vals[5],5,p)
    assert not verify(root,b"tampered",5,p)
    print("Merkle commitment/opening: PASS")

if __name__=="__main__": self_test()
