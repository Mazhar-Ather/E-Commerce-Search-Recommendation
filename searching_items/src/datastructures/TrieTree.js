// datastructures/TrieTree.js

class TrieNode {
    constructor() {
        this.children = {};
        this.isEndOfWord = false;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
        this.wordCount = 0;
    }

    // Insert a word into the trie
    insert(word) {
        if (!word || typeof word !== 'string') return;
        
        let node = this.root;
        const cleanWord = word.toLowerCase().trim();
        
        for (let char of cleanWord) {
            if (!node.children[char]) {
                node.children[char] = new TrieNode();
            }
            node = node.children[char];
        }
        
        if (!node.isEndOfWord) {
            node.isEndOfWord = true;
            this.wordCount++;
        }
    }

    // Search for a word in the trie
    search(word) {
        let node = this.root;
        
        for (let char of word.toLowerCase()) {
            if (!node.children[char]) {
                return false;
            }
            node = node.children[char];
        }
        
        return node.isEndOfWord;
    }

    // Get suggestions for a prefix
    getSuggestions(prefix, limit = 10) {
        if (!prefix || typeof prefix !== 'string') return [];
        
        let node = this.root;
        const suggestions = [];
        
        // Navigate to the last node of the prefix
        for (let char of prefix.toLowerCase()) {
            if (!node.children[char]) {
                return suggestions; // No words with this prefix
            }
            node = node.children[char];
        }
        
        // Collect all words starting with this prefix
        this._collectAllWords(node, prefix, suggestions, limit);
        
        return suggestions;
    }

    // Helper method to collect words recursively
    _collectAllWords(node, currentWord, suggestions, limit) {
        if (suggestions.length >= limit) return;
        
        if (node.isEndOfWord) {
            suggestions.push(currentWord);
        }
        
        // Sort keys for alphabetical order
        const sortedChars = Object.keys(node.children).sort();
        
        for (let char of sortedChars) {
            if (suggestions.length >= limit) break;
            this._collectAllWords(node.children[char], currentWord + char, suggestions, limit);
        }
    }

    // Get all words in the trie (for debugging)
    getAllWords() {
        const words = [];
        this._collectAllWords(this.root, "", words, Infinity);
        return words;
    }

    // Get count of words in the trie
    count() {
        return this.wordCount;
    }

    // Clear the trie
    clear() {
        this.root = new TrieNode();
        this.wordCount = 0;
    }

    // Load multiple words at once
    loadWords(wordArray) {
        if (!Array.isArray(wordArray)) return;
        
        wordArray.forEach(word => {
            if (word && typeof word === 'string') {
                this.insert(word);
            }
        });
    }
}

export default Trie;