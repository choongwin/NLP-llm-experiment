import json
from collections import defaultdict
import csv
import re

# 读取action json 的方法
actions = []
with open('','r',encoding='utf-8') as f:
    actions = json.load(f)

# 将所有的actions 放入一个list
action_lists = []
for action in actions:
    for act in action['actions']:
        action_lists.append(act)


word_counter = defaultdict(int) #计入每个action 被当成索引的频率
new_fact = [] 

def find_all_contexts_fast(fact, i):
    sentences = [s.strip() for s in re.split(r'[。]', fact) if s.strip()] #输入的fact 用“。”分开
    action_list = list(set(action_lists))
    relevant_sentences = []

    for sentence in sentences:
        found_actions = [action for action in action_list if action in sentence] 
        
        # 更新 word_counter
        for act in found_actions:
            word_counter[act] += 1

        # 如果句子包含关键字，加入 relevant_sentences
        if found_actions:
            relevant_sentences.append(sentence)

    # 判断是否有句子包含关键字
    if not relevant_sentences:
        new_fact.append(fact)  # 无关键字，保留原 fact
    else:
        # 将所有包含关键字的句子合并为一个字符串（用句号分隔）
        combined_sentences = '，'.join(relevant_sentences) + '。'  # 添加句号
        new_fact.append(combined_sentences)

max_lines = 10000
data = []
with open('train.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= max_lines:
            break
        data.append(json.loads(line))
    data.append(json.loads(line))


for i,case in enumerate(data):
    fact = case['fact']
    prompt = find_all_contexts_fast(fact,i) ## 生成new fact， new fact是全局变量

# 按照出现次数逆序排序
sorted_actions = sorted(word_counter.items(), key=lambda x: x[1], reverse=True)

# 在 csv 写入频率统计
with open("word_counts.csv", mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["动作", "出现次数"])
    for action, count in sorted_actions:
        writer.writerow([action, count])

# 在 json 写入 new fact 
with open('new_fact.json', 'w', encoding='utf-8') as f:
    json.dump(new_fact, f, ensure_ascii=False, indent=4)