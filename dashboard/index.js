const express = require('express');
const { Pool } = require('pg');
const redis = require('redis');

const app = express();
const pool = new Pool({
  host: process.env.DB_HOST || 'db',
  database: process.env.POSTGRES_DB || 'filadb',
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD || 'postgres',
});

const rc = redis.createClient({ socket: { host: process.env.REDIS_HOST || 'redis' } });
rc.connect().catch(console.error);

app.get('/', async (req, res) => {
  const senha = await rc.get('atual:senha') || '---';
  const nome  = await rc.get('atual:nome')  || '---';
  const { rows } = await pool.query(
    'SELECT senha, nome, servico, chamado_em FROM atendimentos ORDER BY chamado_em DESC LIMIT 20'
  );
  const linhas = rows.map(r =>
    `<tr><td>${r.senha}</td><td>${r.nome}</td><td>${r.servico}</td><td>${new Date(r.chamado_em).toLocaleTimeString('pt-BR')}</td></tr>`
  ).join('');
  res.send(`<!DOCTYPE html><html><head><meta charset="UTF-8">
  <meta http-equiv="refresh" content="3">
  <title>Painel de Atendimento</title>
  <style>body{font-family:sans-serif;padding:2rem}
  .senha{font-size:4rem;font-weight:bold;color:#1D9E75}
  table{border-collapse:collapse;width:100%;margin-top:2rem}
  th,td{padding:8px 12px;border:1px solid #ddd;text-align:left}
  th{background:#f5f5f5}</style></head>
  <body><h1>Painel de Atendimento</h1>
  <p>Chamando agora:</p><div class="senha">${senha}</div>
  <p>${nome}</p>
  <table><tr><th>Senha</th><th>Nome</th><th>Serviço</th><th>Horário</th></tr>${linhas}</table>
  </body></html>`);
});

app.listen(3000, () => console.log('Dashboard em :3000'));