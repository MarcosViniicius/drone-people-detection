"""
Sistema de Detecção de Pessoas usando YOLO
Ponto de entrada principal da aplicação
"""
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config_loader import load_config, validate_config
from src.processors.video_processor import VideoProcessor


def print_header():
    """Imprime cabeçalho da aplicação"""
    print("=" * 60)
    print("SISTEMA DE DETECÇÃO DE PESSOAS - YOLO")
    print("=" * 60)
    print()


def main():
    """Função principal da aplicação"""
    print_header()
    
    try:
        # Carregar configurações
        print("Carregando configurações...")
        config = load_config("./configs/config.json")
        validate_config(config)
        print("✓ Configurações carregadas com sucesso\n")
        
        # Criar processador de vídeos
        processor = VideoProcessor(config)
        
        # Processar todos os vídeos
        processor.process_all()
        
    except FileNotFoundError as e:
        print(f"✗ Erro: {e}")
        print("Certifique-se de que o arquivo config.json existe.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"✗ Erro de configuração: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nProcessamento interrompido pelo usuário.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
