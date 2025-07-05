import jieba
import jieba.analyse
import json
import jieba.posseg as pseg
import re
from itertools import product

def load_charges(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_actions(charges):
    return ["".join(k[:-1].split("、")) for k in charges.keys()]

def process_brackets(text):
    bracket_pattern = re.compile(r"(.*)（(.*)）(.*)")
    match = bracket_pattern.search(text)
    if match:
        prefix = match.group(1)
        options = match.group(2)
        suffix = match.group(3)
        return [f"{prefix[:-1]}{option}{suffix}" for option in [options, prefix[-1]]]
    return [text] 

w  = []
def split_crime_phrases(phrase):
    parts = [p for p in phrase.split('、')]
    
    if len(parts) > 1:
        w.append(parts)
    

def prepare_phrase_components(charges):
    bracket_processed = []
    for charge in charges.keys():
        split_phrases = charge[:-1].split("、")
        processed = [process_brackets(phrase) for phrase in split_phrases]
        bracket_processed.append([p[0] for p in processed])
    
    unsplit_phrases = []
    for charge in charges.keys():
        split_result = split_crime_phrases(charge)
        # unsplit_phrases.append([p[:-1] for p in split_result])
    
    combined = []
    # for i in range(len(bracket_processed)):
    #     combined.append(bracket_processed[i] + unsplit_phrases[i])
    
    return combined

def extract_keywords(texts):
    return [[word for word, _ in jieba.analyse.extract_tags(text, topK=10, withWeight=True)] for text in texts]

pos_set = set()
def analyze_pos(keywords):
    pos_results = []
    for words in keywords:
        pos_dict = {}
        for word in words:
            pos = next(pseg.cut(word)).flag
            pos_set.add(pos)
            pos_dict.setdefault(pos, []).append(word)
        pos_results.append(pos_dict)
    return pos_results

def generate_phrases(pos_data, phrase_components):
    # mono_combinations = {
    #     ('j'),('nr'),('ns'),('nt'),('i'),('l'),('nz')
    # }
    
    bi_combinations = {
        ('a', 'n'), ('v', 'n'),
        ('b', 'n'), ('vn', 'n'), ('an', 'n')
    }
    
    all_phrases = []
    for i, pos_dict in enumerate(pos_data):
        current_phrases = []
        
        for pos1, pos2 in bi_combinations:
            if pos1 in pos_dict and pos2 in pos_dict:
                current_phrases.extend(f"{w1}{w2}" for w1, w2 in product(pos_dict[pos1], pos_dict[pos2]))
        
        current_phrases.extend(phrase_components[i])
        all_phrases.append(list(set(current_phrases)))

    return all_phrases

def all_combination(sentence):
    char_list = list(sentence)
    return char_list

def main():
    charges = load_charges('charges.json')
    actions = extract_actions(charges)
    phrase_components = prepare_phrase_components(charges)
    with open('test_1.json', 'w', encoding='utf-8') as f:
        json.dump(w, f, ensure_ascii=False, indent=2)
    keywords = extract_keywords(actions)
    pos_data = analyze_pos(keywords)
    result_phrases = generate_phrases(pos_data, phrase_components)
    check_list = ['a','v','b','d','r']
    result_phrase = []
    for i,result in enumerate(result_phrases):
        if len(result) == 1:
            if(len(result[0]) > 2):
                check = [(f"{result[0][0]}{result[0][1]}")]
                checkverb = analyze_pos(check)
                for ch in checkverb:
                    for k,v in ch.items():
                        if k in check_list:
                            char_to_remove = "".join(ve for ve in v)
                            result[0] = result[0].replace(char_to_remove, "")
                            actions[i] = result[0]
                            
            allcomb = all_combination(actions[i])
            allcombination = []
            for all in allcomb:
                allcombination.append(all)
        
            unique_combinations = list(set(allcombination))
            result_phrase.append(unique_combinations)
        else:
            result_phrase.append(result)

    
    with open('action_1.json', 'w', encoding='utf-8') as f:
        json.dump([
            {
                "actions": phrases,
                "label": i
            }
            for i, phrases in enumerate(result_phrase)
        ], f, ensure_ascii=False, indent=2)
  

if __name__ == "__main__":
    
    # main()
    
    import csv
    tfidf = []
    with open('word_counts_test.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if int(row[1]) < 10000:
                tfidf.append(row[0])
                
    no_meaning = ['r', 'uj', 'p', 'm', 'zg']
    pos = set()
    wordset = set()
    for i in tfidf:
        s = analyze_pos(i)

        for d in s:
            for key in d:
                if key in no_meaning:
                    try:
                        tfidf.remove(d[key][0])
                    except:
                        wordset.add(d[key][0])
  
    wordset_list =list(wordset)
    for w in tfidf:
        for sd in wordset_list:
            if sd in w:
                try:
                    tfidf.remove(w)
                except:
                    print(sd)
    
    with open('tfidff.json', 'w', encoding='utf-8') as f:
        json.dump(tfidf, f, ensure_ascii=False, indent=4)