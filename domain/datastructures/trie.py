class TrieNode:
    __slots__=("ch","end","kids")  # kids: dict[ch->TrieNode]
    def __init__(self, ch=""): self.ch=ch; self.end=[]; self.kids={}

class Trie:
    """Índice por prefijo para autocompletar nombres."""
    def __init__(self): self.root=TrieNode()

    def insert(self, word, ref=None):
        n=self.root
        for c in word.lower():
            if c not in n.kids: n.kids[c]=TrieNode(c)
            n=n.kids[c]
        n.end.append(ref or word)

    def search_prefix(self, pref):
        n=self.root
        for c in pref.lower():
            if c not in n.kids: return []
            n=n.kids[c]
        res=[]
        def dfs(x):
            res.extend(x.end)
            for k in x.kids.values(): dfs(k)
        dfs(n)
        return res
