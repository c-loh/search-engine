# Posting class

class Posting:
    def __init__(self, docWordCount, url):
        self.freq = 0
        self.docWordCount = docWordCount
        self.bold_count = 0
        self.header_count = 0
        self.title_count = 0
        self.score = 0
        self.positions = []
        self.url = url

    def incr_freq(self):
        self.freq += 1
    
    def incr_bold(self):
        self.bold_count += 1
    
    def incr_header(self):
        self.header_count += 1
    
    def incr_title(self):
        self.title_count += 1

    def get_freq(self):
        return self.freq

    def get_bold(self):
        return self.bold_count

    def get_header(self):
        return self.header_count

    def get_title(self):
        return self.title_count

    def get_positions(self):
        return self.positions

    def compute_score(self):
        self.score = self.freq + (2*self.bold_count) + (3*self.header_count) + (4*self.title_count)
        return self.score
    
    def get_url(self):
        return self.url
        
# {token: {docid: posting, docid2: posting2, ...}, token2: {...}, ...}