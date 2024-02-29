Word Pattern
Find All Numbers Disappeared in an Array
Intersection of Two Linked Lists
class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        words = s.split(" ")
        if len(pattern) != len(words):
            return False
        
        CharToWord = {}
        WordToChar = {}

        for c, w in zip(pattern,words):
            if c in CharToWord and CharToWord[c] != w:
                return False
            if w in WordToChar and WordToChar[w] != c:
                return False
            CharToWord[c] = w
            WordToChar[w] = c

        return True

