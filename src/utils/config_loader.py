"""
Módulo para carregar configurações do projeto
"""
import json
import os


def load_config(config_path="config.json"):
    """
    Carrega arquivo de configuração JSON
    
    Args:
        config_path (str): Caminho para o arquivo de configuração
        
    Returns:
        dict: Configurações carregadas
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
        json.JSONDecodeError: Se o JSON for inválido
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return config


def validate_config(config):
    """
    Valida se as configurações necessárias estão presentes
    
    Args:
        config (dict): Configurações a validar
        
    Returns:
        bool: True se válido
        
    Raises:
        ValueError: Se configuração obrigatória estiver faltando
    """
    required_keys = ["model", "video_input_directory", "video_output_directory", "video_extensions", "image_input_directory", "image_output_directory"]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Configuração obrigatória ausente: {key}")
    
    return True
