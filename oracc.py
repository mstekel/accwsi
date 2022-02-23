import glob
import json
import re
from zipfile import ZipFile
from jsonpath_ng.ext import parse


class oracc_corpus:
    def should_skip(self, lemma):
        if 'f' in lemma and 'lang' in lemma['f'] and not 'akk' in lemma['f']['lang']:
            return True
        valid_pos = ['AJ', 'AV', 'CN', 'DN', 'GN', 'MN', 'N', 'PN', 'TN', 'V']
        if 'f' in lemma and 'pos' in lemma['f'] and lemma['f']['pos'] in valid_pos:
            return False
        return True

    """An iterator that yields sentences (lists of str)."""

    def __iter__(self):
        for file_path in glob.glob(r'oracc_json\*.zip'):
            archive = ZipFile(file_path, 'r')
            catalogue_paths = [name for name in archive.namelist() if re.findall('catalogue\.json', name)]
            if len(catalogue_paths) > 0:
                catalogue = json.loads(archive.read(catalogue_paths[0]))
            else:
                catalogue = None
            files = [name for name in archive.namelist() if re.findall('corpusjson/.+\.json', name)]
            for file in files:
                try:
                    data = json.loads(archive.read(file))
                except ValueError as e:
                    print(e)
                    pass
                textid = data['textid']
                genre = 'UNKNOWN'
                if not catalogue is None and textid in catalogue['members']:
                    text_in_catalogue = catalogue['members'][textid]
                    if 'language' in text_in_catalogue and 'Akkadian' not in text_in_catalogue['language']:
                        continue
                    if 'genre' in text_in_catalogue:
                        genre = text_in_catalogue['genre']
                sentence_match = parse('$..cdl[?(@.type=="sentence")]').find(data)
                for s in sentence_match:
                    parts = []
                    discont_count = 0
                    orig_sentence = []
                    context = []
                    clean_sentence = []
                    sense = []
                    if not 'cdl' in s.value:
                        continue
                    sentence_cdl = s.value['cdl']
                    lemma_match = parse('`this`[?(@.node=="l")]').find(sentence_cdl)
                    for l in lemma_match:
                        if 'lang' in l.value['f'] and not 'akk' in l.value['f']['lang']:
                            continue
                        self.add_normal(l, orig_sentence)
                        self.add_sense(l, sense)

                        if not self.should_skip(l.value):
                            self.add_normal(l, context)
                            self.add_lemmatized(l, clean_sentence)
                        else:
                            discont_count += 1
                            if discont_count >= 8:
                                parts += [(textid, orig_sentence, context, clean_sentence, sense, genre)]
                                discont_count = 0
                                orig_sentence = []
                                context = []
                                sense = []
                                clean_sentence = []
                    if discont_count < 8:
                        parts += [(textid, orig_sentence, context, clean_sentence, sense, genre)]

                    for textid, orig_sentence, context, clean_sentence, sense, genre in parts:
                        if len(clean_sentence) > 1:
                            yield textid, ' '.join(orig_sentence), ' '.join(context), \
                                  ' '.join(clean_sentence), ' '.join(sense), genre

    def add_lemmatized(self, lemma, sentence):
        if 'cf' in lemma.value['f']:
            sentence.append(lemma.value['f']['cf'])
        elif 'norm' in lemma.value['f']:
            sentence.append(lemma.value['f']['norm'])
        elif 'form' in lemma.value['f']:
            sentence.append(lemma.value['f']['form'])

    def add_normal(self, lemma, sentence):
        if 'norm' in lemma.value['f']:
            sentence.append(lemma.value['f']['norm'])
        elif 'cf' in lemma.value['f']:
            sentence.append(lemma.value['f']['cf'])
        elif 'form' in lemma.value['f']:
            sentence.append(lemma.value['f']['form'])

    def add_sense(self, lemma, sentence):
        if 'sense' in lemma.value['f']:
            sentence.append(lemma.value['f']['sense'])


config = {
    'corpus': 'oracc',
    'corpus_ctor': oracc_corpus,
    'term': 'galû',
    'word2vec_args': {
        'min_count': 1,
        'window': 2,
        'size': 300,
        'workers': 1,
    }
}
