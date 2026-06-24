# Sistema de Fila de Atendimento - Arquitetura de Microsserviços

Este repositório contém a evolução estrutural e a automação de implantação de uma aplicação de gerenciamento de filas de atendimento baseada em microsserviços. A solução foi migrada para um ambiente orquestrado nativo em Kubernetes, utilizando ferramentas modernas de Infraestrutura como Código (IaC), Observabilidade e Integração Contínua (CI/CD).

## 🛠️ Componentes do Ecossistema
* **Frontend (Dashboard):** Aplicação Node.js para visualização e acompanhamento das filas em tempo real.
* **Backend (API):** Microsserviço em Python/Flask responsável pelo recebimento e roteamento de requisições.
* **Worker:** Consumidor assíncrono encarregado de processar as mensagens da fila em background.
* **Bancos de Dados:** Cache/Mensageria com Redis e camada de persistência relacional com PostgreSQL.

## 🚀 Tecnologias de DevOps Implementadas

1. **Orquestração de Containers:** Cluster local Kubernetes provisionado através do **K3d/K3s**.
2. **Infraestrutura como Código (IaC):** Provisionamento declarativo, idempotente e automatizado do cluster utilizando **Terraform**.
3. **Observabilidade:** Monitoramento ativo do cluster estruturado com **Prometheus** (coleta de métricas) e **Grafana** (visualização de dashboards).
4. **Integração Contínua (CI/CD):** Pipeline automatizado via **GitHub Actions** (`ci.yml`) encarregado de realizar testes de sintaxe no Terraform e validações estruturais estritas nos manifestos do Kubernetes (`kubectl dry-run`) a cada commit efetuado na branch principal.

## 📁 Organização do Repositório
* `/.github/workflows/`: Definição do fluxo automatizado de CI/CD.
* `/terraform/`: Scripts de provisionamento da infraestrutura local (`main.tf`).
* `/k8s/`: Manifestos declarativos do Kubernetes (Deployments, Services, Secrets, PVCs).
* `/k8s/monitoring/`: Configurações de implantação do Prometheus e Grafana.
* `/api/`, `/dashboard/`, `/worker/`: Código-fonte das regras de negócio do sistema.