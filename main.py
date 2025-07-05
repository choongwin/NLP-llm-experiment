import json,os,csv
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from openai import OpenAI

client = OpenAI(
    api_key="sk-e81350e27cd44a0786b1252bd9744512",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_embedding(embedding_name):
    # 根据embedding名称去加载embedding模型
    if embedding_name == "bge":
        model_name = "BAAI/bge-large-zh-v1.5"
        model_kwargs = {'device': 'cpu'}
        return HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs={'normalize_embeddings': True}
        )
        
def get_db(data_path, db_path, flag):
    with open(data_path,'r',encoding='utf-8') as f:
        data = json.load(f)
    
    if flag == 'articles':
        chunks = [v for k, v in data.items()]
    else:
        chunks = [k for k, v in data.items()]
    

    documents = [Document(page_content=c) for c in chunks]
    embeddings = get_embedding(embedding_name="bge")
    
    db = FAISS.from_documents(documents, embeddings)
    os.makedirs(db_path, exist_ok=True)
    db.save_local(db_path)

    
def load_vector_db(db_path, embedding_name="bge"):
    embeddings = get_embedding(embedding_name)
    db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    return db

def create_db():
    articles_db = get_db(
        data_path="articles.json",
        db_path="articles_db",
        flag='articles'
    )
    
    charges_db = get_db(
        data_path="charges.json",
        db_path="charges_db",
        flag='charges'
    )

def predict_charges(fact, defendants,top_k=3):
    
    articles_db = load_vector_db(db_path="articles_db")
    similar_articles = articles_db.similarity_search(fact, k=top_k)
    law_context = "\n".join([f"• {doc.page_content}" for doc in similar_articles])

    charges_db = load_vector_db("new_charges_db", embedding_name="bge")
    similar_charges = charges_db.similarity_search(fact, k=top_k)
    charges_name = "\n".join([f"• {doc.page_content}" for doc in similar_charges])

    prompt = f"""你是一名资深刑事法官，请根据案件事实和相关法律条文，严格按以下要求分析并输出结果：

【案件事实】
{fact}

【罪名】
{charges_name}

【相关法律条文】
{law_context}

* 每个人的罪名有可能都完全不一样，同一个人也可能同时有多个罪状

【任务要求】
1. 从【罪名】里预测和选择每个被告人的罪名
2. 使用分号(;)分隔不同被告人的罪名
3. 同一被告人的多个罪名用逗号(,)分隔
4. 必须严格依据【罪名】，不得虚构罪名,不可能会出现“无罪”

【被告人列表】
{"; ".join(defendants)}

请直接输出罪名预测结果，不要包含任何解释。输出格式为JSON
{"被告人": [""],"罪行": [""],"刑期(月)": []}"""
    
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": "你是一个法律罪名预测专家"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    return response.choices[0].message.content.strip()
    
    
if __name__ == "__main__":
    # create_db()
    
    data = []
    with open('test.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line)) 
    
    case = []
    for i in range(len(data)):
        fact = data[i]['fact']
        defendants = data[i]['defendants']
        charges = predict_charges(fact, defendants)
        case[i] = charges
        
   # 把 case [] 写进 jsonl
    
