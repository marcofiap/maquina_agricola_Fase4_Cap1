#!/usr/bin/env python3
"""
Script para executar o dashboard Streamlit FarmTech Solutions
Automatiza a configuração e execução
"""

import subprocess
import sys
import os
import requests
import time

def verificar_servidor_flask():
    """Verifica se o servidor Flask está rodando"""
    try:
        print("🔍 Verificando servidor Flask...")
        response = requests.get("http://127.0.0.1:8000/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor Flask está rodando!")
            print(f"📊 Status: {data.get('status', 'N/A')}")
            print(f"💾 Banco: {data.get('banco', 'N/A')} ({data.get('total_registros', 0)} registros)")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Servidor Flask não está rodando!")
        print("💡 Execute primeiro: cd Servidor_Local && python serve.py")
        return False
    except requests.exceptions.Timeout:
        print("⏱️ Timeout ao conectar com servidor Flask!")
        print("⚠️ Servidor pode estar sobrecarregado")
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar servidor: {e}")
        return False

def instalar_dependencias():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências do Streamlit...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def executar_streamlit():
    """Executa o dashboard Streamlit"""
    print("🚀 Iniciando dashboard Streamlit...")
    print("🌐 O dashboard será aberto automaticamente no navegador")
    print("📱 URL: http://localhost:8501")
    print("⚠️ Para parar: Ctrl+C no terminal")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard_streamlit.py",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar Streamlit: {e}")

def main():
    print("🌱 FARMTECH SOLUTIONS - DASHBOARD STREAMLIT")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("dashboard_streamlit.py"):
        print("❌ Arquivo dashboard_streamlit.py não encontrado!")
        print("💡 Execute este script na pasta 'dashboard/'")
        return
    
    # Verificar Flask
    if not verificar_servidor_flask():
        resposta = input("\n❓ Deseja continuar mesmo assim? (s/N): ").lower().strip()
        if resposta != 's':
            return
    
    # Instalar dependências
    if not instalar_dependencias():
        return
    
    # Executar Streamlit
    executar_streamlit()

if __name__ == "__main__":
    main() 