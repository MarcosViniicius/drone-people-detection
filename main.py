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


def display_menu():
    """Exibe opções de menu para o usuário e retorna a escolha"""
    print("\nOpções de Menu:")
    print("1. Iniciar processamento de Livestream | Não implementado")
    print("2. Iniciar processamento de vídeos | Implementado")
    print("3. Iniciar processamento de imagens | Não implementado")
    print("4. Sair")
    
    while True:
        choice = input("\nEscolha uma opção (1-4): ").strip()
        if choice in ('1', '2', '3', '4'):
            return choice
        print("Opção inválida. Por favor, escolha uma opção válida (1-4).")


def process_livestream(processor):
    """Processamento de livestream"""
    print("\nIniciando processamento de Livestream...")
    # Implementar lógica específica para livestream
    processor.process_livestream()


def process_videos(processor):
    """Processamento de vídeos"""
    print("\nIniciando processamento de vídeos...")
    processor.process_all()


def process_images(processor):
    """Processamento de imagens"""
    print("\nIniciando processamento de imagens...")
    # Implementar lógica específica para imagens
    processor.process_images()


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
        
        # Loop principal do menu
        while True:
            choice = display_menu()
            
            if choice == '1':
                process_livestream(processor)
            elif choice == '2':
                process_videos(processor)
            elif choice == '3':
                process_images(processor)
            else:  # Opção 4 (Sair)
                print("\nSaindo da aplicação...")
                break
                
    except FileNotFoundError as e:
        print(f"\n✗ Erro: {e}")
        print("Certifique-se de que o arquivo config.json existe.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n✗ Erro de configuração: {e}")
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