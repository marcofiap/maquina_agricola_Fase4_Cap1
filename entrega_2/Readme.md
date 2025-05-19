# Entrega 2 – Banco de Dados com Python e Oracle  
### Projeto Fase 3 – FarmTech Solutions | FIAP

Esta entrega tem como foco o armazenamento dos dados coletados pela máquina agrícola inteligente em um banco de dados Oracle. Através de um script em Python, é possível realizar todas as operações CRUD (Create, Read, Update, Delete), simulando a persistência dos dados recebidos do ESP32.

---

## Grupo 58 - FIAP

**Integrantes:**
- Felipe Sabino da Silva  
- Juan Felipe Voltolini  
- Luiz Henrique Ribeiro de Oliveira  
- Marco Aurélio Eberhardt Assimpção  
- Paulo Henrique Senise  

**Professores:**  
- Tutor: Leonardo Ruiz Orabona  
- Coordenador: André Godoi

---

## Objetivo

Desenvolver um script em Python que:
- Armazene dados coletados de sensores simulados (via ESP32) em um banco Oracle
- Execute operações completas de inserção, listagem, atualização e exclusão
- Realize consulta com filtro por umidade (acima/abaixo de um valor)

---

## Estrutura da Tabela Oracle

```sql
CREATE TABLE leituras_sensores (
    timestamp       VARCHAR2(50) PRIMARY KEY,
    umidade         NUMBER(5,2),
    temperatura     NUMBER(5,2),
    ph              NUMBER(4,2),
    fosforo         VARCHAR2(10),
    potassio        VARCHAR2(10),
    bomba_dagua     VARCHAR2(10)
);
```

---

## Justificativa da Estrutura

A estrutura da tabela representa diretamente os sensores conectados ao ESP32:

| Campo         | Origem simulada        |
|---------------|------------------------|
| umidade       | Sensor DHT22           |
| temperatura   | Sensor DHT22           |
| ph            | Sensor LDR (simulado)  |
| fósforo       | Botão (booleano)       |
| potássio      | Botão (booleano)       |
| bomba_dagua   | Estado do relé (LED)   |

O campo `timestamp` é a **chave primária**, garantindo unicidade e rastreabilidade das leituras no tempo.

---
## Imagem da Tabela Oracle no Banco de Dados
- Dados coletados e inseridos conforme estrutura MER da Fase 2

  ![BancoDeDadosLeituraSensor](https://github.com/user-attachments/assets/6795aeb3-fa9b-4b57-92b4-9d5178d2099f)
 
## Tecnologias Utilizadas

- Python 3.10+
- Oracle Database XE
- Biblioteca `oracledb` (cliente Python)
- Terminal ou console interativo

---

## Arquivo principal

- [`crud_simulador_oracle.py`]

Este script contém o menu interativo e as funções para manipulação dos dados no banco.

---

## Funcionalidades CRUD

| Operação | Descrição |
|----------|-----------|
| **Create** | Inserção de uma nova leitura no banco |
| **Read**   | Listagem completa de todas as leituras |
| **Read (filtro)** | Consulta de leituras com umidade acima ou abaixo de um valor |
| **Update** | Atualização de uma leitura específica com base no timestamp |
| **Delete** | Remoção de uma leitura ou de todos os registros |

---

## Como Executar

1. Certifique-se que o Oracle DB esteja ativo.
2. Instale a biblioteca necessária:

```bash
pip install oracledb
```

3. Atualize as credenciais no script:
```python
DB_USER = "system"
DB_PASSWORD = "sua_senha"
DB_DSN = "localhost:1521/xe"
```

4. Execute:
```bash
python crud_simulador_oracle.py
```

---

## Exemplo de Execução (Menu)

```text
================ MENU CRUD - BANCO ORACLE ================
1 - Inserir nova leitura manualmente
2 - Listar todas as leituras enviadas pelo ESP32
3 - Atualizar uma leitura manualmente
4 - Remover uma leitura do banco de dados
5 - Excluir todos os dados do banco de dados
6 - Consultar leituras por umidade (acima/abaixo)
0 - Sair
===========================================================
```

---

## Observações

- Todos os dados inseridos manualmente são validados (faixa de pH, umidade, etc.)
- O campo `timestamp` deve ser único
- O script é modular e pronto para integrar com leitura real via API/ESP32 no futuro

---

## Status da Entrega

- Estrutura do banco implementada  
- CRUD funcional  
- Consulta por umidade adicionada  
- Validações básicas implementadas  
- Pronto para integração com outros módulos

---


---

## Relacionamento com o MER da Fase 2

A estrutura da tabela `LEITURAS_SENSORES` foi inspirada na entidade `LeituraSensor` do Modelo Entidade-Relacionamento (MER) da Fase 2, com os seguintes mapeamentos:

| Campo no MER         | Campo no Banco (Entrega 2)   | Observações                     |
|----------------------|------------------------------|----------------------------------|
| DataHoraLeitura      | timestamp                    | ✔️ Chave primária local           |
| ValorUmidade         | umidade                      | ✔️ Valor numérico direto          |
| ValorpH              | ph                           | ✔️ Simulado via sensor LDR        |
| ValorFosforo         | fosforo                      | ⚠️ Presente/ausente (booleano)    |
| ValorPotassio        | potassio                     | ⚠️ Presente/ausente (booleano)    |
| ID_Leitura           | —                            | 🔴 Não implementado               |
| ID_Sensor            | —                            | 🔴 Não implementado               |
| ID_Plantio           | —                            | 🔴 Não implementado               |

> **Nota:** Esta entrega tem foco em simular e armazenar dados sensoriais em uma estrutura funcional e simples. A normalização completa e a integração com outras entidades do MER (como `Plantio`, `Sensor`, `Talhão`) podem ser incorporadas em uma versão futura, com maior granularidade de dados e controle relacional.
