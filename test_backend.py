"""
Script para testar se o backend está funcionando corretamente
"""
import requests
import json

BACKEND_URL = "https://crew-ai-agent-for-copywriting.onrender.com"

def test_health():
    """Testa o endpoint de health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check OK!")
            print(f"   Resposta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

def test_copywriting():
    """Testa o endpoint de copywriting"""
    print("\n🔍 Testando endpoint de copywriting...")
    payload = {
        "topic": "Curso de Python",
        "target_audience": "Iniciantes em programação",
        "platform": "Instagram",
        "tone": "Profissional",
        "url": "Nenhuma URL fornecida. Use seu conhecimento geral."
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/copywriting",
            json=payload,
            timeout=60  # 1 minuto para teste rápido
        )
        
        if response.status_code == 200:
            print("✅ Copywriting endpoint OK!")
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Result length: {len(result.get('result', ''))} caracteres")
            return True
        else:
            print(f"❌ Copywriting falhou: {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False

if __name__ == "__main__":
    print(f"🌐 Testando backend em: {BACKEND_URL}\n")
    
    health_ok = test_health()
    
    if health_ok:
        print("\n⚠️  Teste de copywriting pode demorar (timeout de 60s)...")
        print("   Você pode cancelar com Ctrl+C se necessário.\n")
        try:
            copy_ok = test_copywriting()
        except KeyboardInterrupt:
            print("\n⚠️  Teste cancelado pelo usuário")
            copy_ok = False
    else:
        copy_ok = False
    
    print("\n" + "="*50)
    if health_ok and copy_ok:
        print("✅ Todos os testes passaram!")
    elif health_ok:
        print("⚠️  Health check OK, mas copywriting falhou ou foi cancelado")
    else:
        print("❌ Backend não está respondendo corretamente")
    print("="*50)

