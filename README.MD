# 🎯 Detecção de Pessoas em Vídeos de Drone

Sistema de detecção e rastreamento de pessoas em filmagens aéreas usando YOLOv8 e OpenCV.

## 📋 Sobre o Projeto

Aplicação de visão computacional para identificar e contar pessoas em vídeos capturados por drones. O sistema utiliza o modelo YOLOv8 para detecção em tempo real, oferecendo alta precisão e velocidade de processamento.

### 🔧 Tecnologias Utilizadas

- **Python 3.x**
- **OpenCV** - Processamento de imagens e vídeos
- **Ultralytics YOLOv8** - Detecção de objetos em tempo real
- **NumPy** - Operações numéricas

## 🚀 Instalação

```
# Clone o repositório
git clone <seu-repositorio>

# Instale as dependências
pip install opencv-python ultralytics numpy
ou
pip install -r requirements.txt
```

## 💻 Como Usar

1. Execute o script principal:
```
python index.py
```

2. Na primeira execução, o código automaticamente:
   - Baixa o modelo YOLO configurado no código
   - Cria as pastas `input/` e `output/`

3. Adicione seu vídeo na pasta `input/`

4. Os resultados processados serão salvos em `output/`

## 📚 Sobre o YOLO

YOLO (You Only Look Once) é um modelo de detecção de objetos desenvolvido por Joseph Redmon e Ali Farhadi em 2015. Reconhecido por sua velocidade e precisão em detecção em tempo real.

[Saiba mais sobre os modelos YOLO](https://docs.ultralytics.com/pt/#yolo-a-brief-history)

## 📝 Estrutura do Projeto

```
├── index.py          # Script principal
├── input/            # Vídeos para análise
├── output/           # Resultados processados
└── README.md
```

## 📄 Licença

Este projeto está sob a licença MIT.
