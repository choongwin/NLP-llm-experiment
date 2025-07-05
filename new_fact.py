import json

max_lines = 10000
all = []
with open('train.jsonl', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= max_lines:
            break
        all.append(json.loads(line))
    all.append(json.loads(line))


charges = []
with open('charges.json', 'r', encoding='utf-8') as a:
    charges = json.load(a)
charges_dict = {}

for charge, label in charges.items():
    charges_dict[charge] = label

    

charges_collector = []
charge_set = set()
for element in all:
    e = []
    for judgement in element['outcomes']:
        for standard_accusation in judgement['judgment']:
            e.append(standard_accusation['standard_accusation'])

    acc_set = list(set(e))
    for crime in acc_set:
        charges_collector.append([charges_dict[crime]])
        charge_set.add(charges_dict[crime])
        
charge_set = list(charge_set)
print(len(charge_set))

sort_charge = sorted(charge_set)
new_label = {}
for i,label in enumerate(sort_charge):
    new_label[label] = i
    
fact = []
with open('new_fact.json', 'r', encoding='utf-8') as f:
    fact = json.load(f)
    
combined_data = []
for i in range(len(fact)):
    combined_data.append({
        "fact": fact[i],
        "label": new_label[charges_collector[i][0]]
    })

with open('final_output.json', 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=4)

for c in charges_collector:
    if len(c) > 2:
        print(c)

              
                

        



