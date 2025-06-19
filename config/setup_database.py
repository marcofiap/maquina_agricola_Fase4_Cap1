#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar banco de dados PostgreSQL
com tabelas para dados meteorológicos e integração ML
"""

import psycopg2
from database_config import DatabaseConfig, SCHEMA_SQL

def conectar_banco():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            database=DatabaseConfig.DATABASE,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def executar_schema():
    """Executa o schema SQL para criar todas as tabelas"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(SCHEMA_SQL)
            conn.commit()
            print("✅ Schema executado com sucesso!")
            print("✅ Tabelas criadas:")
            print("   - leituras_sensores")
            print("   - dados_meteorologicos") 
            print("   - leituras_integradas")
            print("   - view_ml_completa")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erro ao executar schema: {e}")
            conn.rollback()
            conn.close()
            return False
    return False

def verificar_tabelas():
    """Verifica se as tabelas foram criadas"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Lista todas as tabelas do schema
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{DatabaseConfig.SCHEMA}'
                ORDER BY table_name
            """)
            
            tabelas = cursor.fetchall()
            
            print(f"\n📊 Tabelas no schema '{DatabaseConfig.SCHEMA}':")
            for tabela in tabelas:
                print(f"   ✅ {tabela[0]}")
            
            # Verifica a view
            cursor.execute(f"""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = '{DatabaseConfig.SCHEMA}'
                ORDER BY table_name
            """)
            
            views = cursor.fetchall()
            
            if views:
                print(f"\n📈 Views no schema '{DatabaseConfig.SCHEMA}':")
                for view in views:
                    print(f"   ✅ {view[0]}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar tabelas: {e}")
            conn.close()
            return False
    return False

def popular_dados_exemplo():
    """Popula o banco com alguns dados de exemplo"""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Insere alguns dados meteorológicos de exemplo
            dados_met_exemplo = [
                (25.5, 72.0, 1013.25, 8.5, 'NE', 'Parcialmente nublado', 15.0, 0.0, 7.2, 25.0),
                (28.2, 68.0, 1015.80, 12.1, 'E', 'Ensolarado', 5.0, 0.0, 9.8, 30.0),
                (22.8, 85.0, 1008.90, 15.2, 'SW', 'Nublado', 75.0, 2.5, 3.5, 12.0)
            ]
            
            for dados in dados_met_exemplo:
                cursor.execute(f"""
                    INSERT INTO {DatabaseConfig.SCHEMA}.dados_meteorologicos 
                    (temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento,
                     direcao_vento, condicao_clima, probabilidade_chuva, quantidade_chuva,
                     indice_uv, visibilidade)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, dados)
            
            # Insere alguns dados integrados de exemplo
            dados_int_exemplo = [
                (45.2, 24.8, 6.8, True, True, False, 25.5, 72.0, 1013.25, 8.5, 'Parcialmente nublado', 15.0, 0.0, 0.7, 22.0, 5.2),
                (38.5, 27.1, 6.5, True, False, True, 28.2, 68.0, 1015.80, 12.1, 'Ensolarado', 5.0, 0.0, 1.1, 18.0, 6.8),
                (62.8, 23.2, 7.1, False, True, False, 22.8, 85.0, 1008.90, 15.2, 'Nublado', 75.0, 2.5, -0.4, 35.0, 4.1)
            ]
            
            for dados in dados_int_exemplo:
                cursor.execute(f"""
                    INSERT INTO {DatabaseConfig.SCHEMA}.leituras_integradas 
                    (umidade_solo, temperatura_solo, ph_solo, fosforo, potassio, bomba_dagua,
                     temperatura_externa, umidade_ar, pressao_atmosferica, velocidade_vento,
                     condicao_clima, probabilidade_chuva, quantidade_chuva,
                     diferenca_temperatura, deficit_umidade, fator_evapotranspiracao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, dados)
            
            conn.commit()
            print("\n✅ Dados de exemplo inseridos:")
            print("   - 3 registros meteorológicos")
            print("   - 3 registros integrados")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao popular dados: {e}")
            conn.rollback()
            conn.close()
            return False
    return False

def main():
    """Função principal"""
    print("🗃️ Configurando banco de dados FarmTech Solutions...")
    print(f"🏗️ Host: {DatabaseConfig.HOST}")
    print(f"💾 Database: {DatabaseConfig.DATABASE}")
    print(f"📊 Schema: {DatabaseConfig.SCHEMA}")
    print("-" * 50)
    
    # 1. Executa schema
    print("1️⃣ Executando schema SQL...")
    if executar_schema():
        print("✅ Schema executado com sucesso!")
    else:
        print("❌ Falha ao executar schema")
        return
    
    # 2. Verifica tabelas
    print("\n2️⃣ Verificando tabelas criadas...")
    if verificar_tabelas():
        print("✅ Tabelas verificadas!")
    else:
        print("❌ Falha ao verificar tabelas")
        return
    
    # 3. Popula dados de exemplo
    print("\n3️⃣ Inserindo dados de exemplo...")
    if popular_dados_exemplo():
        print("✅ Dados de exemplo inseridos!")
    else:
        print("❌ Falha ao inserir dados")
        return
    
    print("\n🎉 Configuração concluída com sucesso!")
    print("\n🚀 Próximos passos:")
    print("   1. Execute o dashboard: streamlit run dashboard/dashboard_streamlit.py")
    print("   2. Acesse a página '🧠 Machine Learning'")
    print("   3. Treine os modelos com dados meteorológicos!")

if __name__ == "__main__":
    main() 