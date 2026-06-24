import os, time, json
import redis, psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

r = redis.Redis(host=os.environ.get('REDIS_HOST','redis'), port=6379, decode_responses=True)

def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST','db'),
        dbname=os.environ.get('POSTGRES_DB','filadb'),
        user=os.environ.get('POSTGRES_USER','postgres'),
        password=os.environ.get('POSTGRES_PASSWORD','postgres')
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            servico VARCHAR(100) NOT NULL,
            senha VARCHAR(10) NOT NULL,
            chegada TIMESTAMP DEFAULT NOW(),
            chamado_em TIMESTAMP
        );
        CREATE SEQUENCE IF NOT EXISTS senha_seq START 1;
    """)
    conn.commit(); cur.close(); conn.close()

def gerar_senha():
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT nextval('senha_seq')")
    num = cur.fetchone()[0]; cur.close(); conn.close()
    return f"A{num:03d}"

@app.route('/queue', methods=['POST'])
def enfileirar():
    data = request.get_json() or {}
    nome = data.get('nome','').strip()
    servico = data.get('servico','geral').strip()
    
    # 1. Pegamos a prioridade do JSON (se não mandarem nada, vira 'normal')
    prioridade = data.get('prioridade', 'normal').strip().lower()
    
    if not nome:
        return jsonify({'error': 'nome obrigatorio'}), 400
        
    senha = gerar_senha()
    
    # 2. Colocamos a prioridade dentro do payload para o worker saber também
    payload = json.dumps({'nome': nome, 'servico': servico, 'senha': senha, 'prioridade': prioridade})
    
    # 3. Decidimos em qual fila o cliente vai entrar
    if prioridade == 'urgente':
        tamanho = r.rpush('fila:urgente', payload)  # Vai para a fila VIP
        nome_fila = 'fila:urgente'
    else:
        tamanho = r.rpush('fila:atendimento', payload) # Vai para a fila normal
        nome_fila = 'fila:atendimento'
        
    return jsonify({
        'senha': senha, 
        'posicao': tamanho, 
        'servico': servico, 
        'prioridade': prioridade,
        'fila': nome_fila
    })

#@app.route('/queue', methods=['POST'])
#def enfileirar():
#    data = request.get_json() or {}
#    nome = data.get('nome','').strip()
#    servico = data.get('servico','geral').strip()
#    if not nome:
#        return jsonify({'error': 'nome obrigatorio'}), 400
#    senha = gerar_senha()
#    payload = json.dumps({'nome': nome, 'servico': servico, 'senha': senha})
#    tamanho = r.rpush('fila:atendimento', payload)
#    return jsonify({'senha': senha, 'posicao': tamanho, 'servico': servico})

@app.route('/position/<nome>')
def posicao(nome):
    # 1. Pegamos todos os itens que estão guardados na fila do Redis
    fila = r.lrange('fila:atendimento', 0, -1)
    
    # 2. Varremos a fila item por item (i é o índice, item é o texto JSON)
    for i, item in enumerate(fila):
        # Transformamos o texto JSON de volta em um dicionário Python
        entry = json.loads(item)
        
        # 3. Comparamos o nome da fila com o nome que o usuário buscou (tudo em minúsculo)
        if entry['nome'].lower() == nome.lower():
            # ACHOU! Retornamos a posição (índice + 1) e incluímos o 'servico' que pegamos do Redis
            return jsonify({
                'nome': nome, 
                'posicao': i + 1,
                'servico': entry.get('servico', 'geral') # <-- ADAPTADO: Incluindo o serviço aqui!
            })
            
    # 4. Se o loop terminar e não encontrar ninguém, avisa que não achou (Erro 404)
    return jsonify({'nome': nome, 'posicao': None, 'msg': 'nao encontrado'}), 404
    
#@app.route('/position/<nome>')
#def posicao(nome):
#    # retorna posicao do nome na fila (0 = proximo)
#    fila = r.lrange('fila:atendimento', 0, -1)
#    for i, item in enumerate(fila):
#        entry = json.loads(item)
#        if entry['nome'].lower() == nome.lower():
#            return jsonify({'nome': nome, 'posicao': i+1})
#    return jsonify({'nome': nome, 'posicao': None, 'msg': 'nao encontrado'}), 404

@app.route('/health')
def health():
    return 'ok'

if __name__ == '__main__':
    time.sleep(4)
    init_db()
    app.run(host='0.0.0.0', port=5000)