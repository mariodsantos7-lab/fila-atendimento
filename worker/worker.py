import os, time, json
import redis, psycopg2

r = redis.Redis(host=os.environ.get('REDIS_HOST','redis'), port=6379, decode_responses=True)

def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST','db'),
        dbname=os.environ.get('POSTGRES_DB','filadb'),
        user=os.environ.get('POSTGRES_USER','postgres'),
        password=os.environ.get('POSTGRES_PASSWORD','postgres')
    )

print('Worker iniciado — aguardando atendimentos...')
while True:
    try:
        # ALTERADO: Agora passamos uma lista com as duas filas. 
        # O Redis vai olhar primeiro 'fila:urgente'. Se estiver vazia, ele olha 'fila:atendimento'.
        result = r.blpop(['fila:urgente', 'fila:atendimento'], timeout=0)
        
        if not result:
            continue
            
        # O result nos devolve uma tupla: (nome_da_fila_de_onde_tirou, payload_em_texto)
        fila_origem, raw = result
        data = json.loads(raw)
        
        conn = get_db(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO atendimentos (nome, servico, senha, chamado_em) VALUES (%s,%s,%s,NOW())",
            (data['nome'], data['servico'], data['senha'])
        )
        conn.commit(); cur.close(); conn.close()
        
        # atualiza a senha sendo chamada agora no Redis para o Dashboard mostrar
        r.set('atual:senha', data['senha'])
        r.set('atual:nome', data['nome'])
        
        # Adicionei a origem no print para você conseguir ver a mágica acontecendo nos logs!
        print(f"[{fila_origem}] Chamando: {data['senha']} — {data['nome']} ({data.get('prioridade', 'normal')})")
        
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(2)