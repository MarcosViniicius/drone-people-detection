# Sistema de Detecção de Pessoas em Vídeos e Imagens

Sistema automatizado para detectar pessoas em vídeos e imagens usando YOLOv11, otimizado para filmagens de drones.

## 📋 Índice

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Estrutura de Diretórios](#estrutura-de-diretórios)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Parâmetros de Inferência](#parâmetros-de-inferência)
- [Exemplos de Configuração](#exemplos-de-configuração)

## ✨ Características

- Detecção de pessoas em vídeos e imagens
- **Processamento de livestreams em tempo real**
- **Suporte para streams RTMP e HLS**
- **Gravação opcional de streams processados**
- Geração de estatísticas detalhadas
- Anotações visuais com contadores
- Processamento em lote
- Configuração flexível via JSON
- Suporte a múltiplos formatos de vídeo e imagem

## 🔧 Requisitos

- Python 3.8+
- OpenCV
- Ultralytics YOLO
- PyTorch

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/drone-people-detection.git
cd drone-people-detection

# Instale as dependências
pip install -r requirements.txt
```

## 📁 Estrutura de Diretórios

```
drone-people-detection/
├── configs/
│   └── config.json          # Arquivo de configuração
┌── data/
│   ├── input/
│   │   ├── videos/         # Coloque vídeos aqui
│   │   └── images/         # Coloque imagens aqui
│   └── output/
│       ├── videos/         # Vídeos processados
│       │   ├── videos/     # Vídeos anotados
│       │   ├── lives/      # Streams processados
│       │   ├── live_recordings/  # Gravações de streams
│       │   └── stats/      # Estatísticas dos vídeos
│       └── images/         # Imagens processadas
├── nginx-rtmp-stream/       # Servidor RTMP/HLS local
│   └── stream/             # HLS streams gerados pelo nginx (não editar)
├── src/
│   ├── core/
│   ├── processors/
│   └── utils/
└── main.py                  # Script principal
```

## ⚙️ Configuração

O arquivo [`configs/config.json`](configs/config.json) controla todos os parâmetros do sistema.

### Estrutura Básica

```json
{
  "video_input_directory": "./data/input/videos",
  "video_output_directory": "./data/output/videos",
  "image_input_directory": "./data/input/images",
  "image_output_directory": "./data/output/images",
  "model": {
    "type": "YOLO",
    "weights": "yolo11m.pt"
  },
  "video_extensions": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
  "image_extensions": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"],
  "inference_parameters": {
    "conf": 0.1,
    "iou": 0.45,
    "classes": [0],
    "verbose": false
  },
  "video_dimensions": {
    "width": 1280,
    "height": 720
  },
  "image_dimensions": {
    "width": 800,
    "height": 600
  },
  "stream": {
    "local_rtmp_url": "rtmp://localhost:1935/live",
    "local_hls_url": "http://localhost:8081/live/.m3u8",
    "output_directory": "./data/output/videos/lives",
    "recording_directory": "./data/output/videos/live_recordings",
    "stats_directory": "./data/output/videos/stats",
    "dimensions": {
      "width": 1280,
      "height": 720
    }
  }
}
```

### Diretórios

- **video_input_directory**: Pasta onde os vídeos para processar devem ser colocados
- **video_output_directory**: Pasta onde os resultados dos vídeos serão salvos
- **image_input_directory**: Pasta onde as imagens para processar devem ser colocadas
- **image_output_directory**: Pasta onde os resultados das imagens serão salvos

### Modelo YOLO

```json
"model": {
  "type": "YOLO",
  "weights": "yolo11m.pt"
}
```

**Opções de pesos disponíveis:**
- `yolo11n.pt` - Nano (mais rápido, menos preciso)
- `yolo11s.pt` - Small (rápido)
- `yolo11m.pt` - Medium (balanceado) ⭐ **Recomendado**
- `yolo11l.pt` - Large (preciso)
- `yolo11x.pt` - Extra Large (mais preciso, mais lento)

### Extensões Suportadas

```json
"video_extensions": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
"image_extensions": [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
```

Adicione ou remova extensões conforme necessário.

### Dimensões de Processamento

```json
"video_dimensions": {
  "width": 1280,
  "height": 720
},
"image_dimensions": {
  "width": 800,
  "height": 600
}
```

- Valores maiores = mais precisão, processamento mais lento
- Valores menores = menos precisão, processamento mais rápido

## 🎯 Parâmetros de Inferência

Os parâmetros de inferência controlam como o modelo YOLO detecta objetos.

```json
"inference_parameters": {
  "conf": 0.1,
  "iou": 0.45,
  "classes": [0],
  "verbose": false
}
```

### 📊 conf (Confiança Mínima)

**O que faz:** Define a confiança mínima para uma detecção ser considerada válida.

- **Valor:** 0.0 a 1.0
- **Padrão:** 0.1 (10%)

**Quando ajustar:**
- ⬆️ **Aumentar** se há muitos falsos positivos (detecções incorretas)
- ⬇️ **Diminuir** se o sistema não está detectando pessoas visíveis

**Exemplos:**
```json
"conf": 0.1  // Detecta mais, pode ter falsos positivos
"conf": 0.5  // Detecção balanceada
"conf": 0.8  // Apenas detecções muito confiáveis
```

### 🔲 iou (Intersection over Union)

**O que faz:** Controla a supressão de caixas sobrepostas (Non-Maximum Suppression).

- **Valor:** 0.0 a 1.0
- **Padrão:** 0.45

**Quando ajustar:**
- ⬆️ **Aumentar** se há múltiplas caixas detectando a mesma pessoa
- ⬇️ **Diminuir** se pessoas próximas estão sendo ignoradas

**Exemplos:**
```json
"iou": 0.3   // Permite mais sobreposição (detecta pessoas próximas)
"iou": 0.45  // Balanceado (recomendado)
"iou": 0.7   // Remove mais sobreposições
```

### 🎯 classes

**O que faz:** Define quais objetos do dataset COCO detectar.

- **Valor:** Lista de IDs de classes
- **Padrão:** `[0]` (apenas pessoas)

**Classes COCO principais:**
```json
0  - pessoa
1  - bicicleta
2  - carro
3  - moto
5  - ônibus
7  - caminhão
16 - cachorro
17 - gato
```

**Exemplos:**
```json
"classes": [0]           // Apenas pessoas
"classes": [0, 2, 3]     // Pessoas, carros e motos
"classes": [0, 16, 17]   // Pessoas e animais
```

[Lista completa de classes COCO](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml)

### 📝 verbose

**O que faz:** Ativa logs detalhados do YOLO durante a inferência.

```json
"verbose": false  // Desativa logs (recomendado)
"verbose": true   // Ativa logs detalhados
```

## 🚁 Exemplos de Configuração

### Para Drones em Alta Altitude

Pessoas aparecem pequenas, necessita maior sensibilidade.

```json
"inference_parameters": {
  "conf": 0.3,
  "iou": 0.3,
  "classes": [0],
  "verbose": false
}
```

### Para Ambientes Lotados

Muitas pessoas juntas, necessita filtro mais rigoroso.

```json
"inference_parameters": {
  "conf": 0.5,
  "iou": 0.45,
  "classes": [0],
  "verbose": false
}
```

### Para Máxima Sensibilidade

Detectar todas as possíveis pessoas, mesmo com baixa confiança.

```json
"inference_parameters": {
  "conf": 0.1,
  "iou": 0.3,
  "classes": [0],
  "verbose": false
}
```

### Para Detecção de Múltiplos Objetos

Detectar pessoas, veículos e animais.

```json
"inference_parameters": {
  "conf": 0.4,
  "iou": 0.45,
  "classes": [0, 2, 3, 16, 17],
  "verbose": false
}
```

## � Processamento de Livestreams

O sistema suporta processamento de vídeo em tempo real de streams ao vivo.

### Configuração de Stream

```json
"stream": {
  "local_rtmp_url": "rtmp://localhost:1935/live",
  "local_hls_url": "http://localhost:8081/live/.m3u8",
  "hls_stream_directory": "./nginx-rtmp-stream/stream",
  "output_directory": "./data/output/videos/lives",
  "recording_directory": "./data/output/videos/live_recordings",
  "stats_directory": "./data/output/videos/stats",
  "dimensions": {
    "width": 1280,
    "height": 720
  }
}
```

**Importante:**
- `hls_stream_directory`: Diretório onde o servidor nginx-rtmp gera os arquivos HLS (.m3u8 e .ts)
- Esta pasta é gerenciada automaticamente pelo nginx e não deve ser editada manualmente
- Os streams processados e gravados são salvos em `recording_directory`

### Tipos de Stream Suportados

#### 1️⃣ Stream Interno (RTMP/HLS Local)

Utilize o servidor NGINX-RTMP incluído no projeto:

**Iniciar o servidor:**
```bash
cd nginx-rtmp-stream
docker compose up -d
```

**Transmitir para o servidor:**
- URL RTMP: `rtmp://localhost:1935/live`
- Use software como OBS Studio para transmitir

**Assistir o stream:**
- URL HLS: `http://localhost:8081/live/.m3u8`

#### 2️⃣ Stream Externo

Suporte para streams de qualquer fonte:
- **RTMP:** `rtmp://example.com/live/stream`
- **HLS:** `http://example.com/stream.m3u8`
- **HTTP:** `http://example.com/video.mp4`

### Recursos do Processamento de Stream

- ✅ Detecção em tempo real
- ✅ Visualização ao vivo com anotações
- ✅ Gravação opcional do stream processado
- ✅ Estatísticas em tempo real
- ✅ Controles interativos:
  - `Q` - Parar processamento
  - `S` - Alternar exibição de estatísticas

### Como Usar Livestreams

1. **No menu principal**, selecione opção `1` (Livestream processing)
2. **Escolha a fonte:**
   - Opção 1: Stream interno (RTMP/HLS local)
   - Opção 2: Stream externo (URL customizada)
3. **Decida se quer gravar** o stream processado
4. **Acompanhe o processamento** em tempo real
5. **Pressione Q** para finalizar
**⚠️ Importante para HLS interno:**
- Você precisa estar **transmitindo ativamente** para o servidor RTMP
- Use OBS Studio ou similar para transmitir para `rtmp://localhost:1935/live`
- Aguarde 5-10 segundos após iniciar a transmissão antes de processar HLS
- Ou use RTMP diretamente (sem espera necessária)
## �🚀 Como Usar

### 1. Preparar Arquivos

Coloque seus arquivos nas pastas apropriadas:
- Vídeos: `./data/input/videos/`
- Imagens: `./data/input/images/`

### 2. Configurar Parâmetros

Edite [`configs/config.json`](configs/config.json) conforme suas necessidades.

### 3. Executar Processamento

```bash
python main.py
```

### 4. Verificar Resultados

**Vídeos processados:**
- Vídeos anotados: `./data/output/videos/videos/`
- Estatísticas: `./data/output/videos/stats/`

**Imagens processadas:**
- Imagens anotadas: `./data/output/images/`

**Livestreams:**
- Gravações: `./data/output/videos/live_recordings/`
- Estatísticas: `./data/output/videos/stats/`

## 📊 Estatísticas Geradas

Para cada vídeo processado, é gerado um arquivo de estatísticas contendo:

- Total de frames processados
- Pessoas detectadas por frame (máximo e mínimo)
- Tempo total de processamento
- FPS de processamento
- Dimensões do vídeo

Exemplo de saída:
```
=== ESTATÍSTICAS DO VÍDEO ===
Vídeo: meu_video.mp4
Dimensões: 1280x720

Total de frames processados: 1500
Máximo de pessoas em um frame: 12
Mínimo de pessoas em um frame: 0
Tempo total de processamento: 45.3s
FPS de processamento: 33.1
```

## 🔍 Troubleshooting

### Muitos falsos positivos
- Aumente o valor de `conf` (ex: 0.5 ou 0.6)

### Pessoas não estão sendo detectadas
- Diminua o valor de `conf` (ex: 0.2 ou 0.3)
- Verifique se a classe `0` está em `classes`

### Múltiplas caixas na mesma pessoa
- Aumente o valor de `iou` (ex: 0.6 ou 0.7)

### Pessoas próximas sendo ignoradas
- Diminua o valor de `iou` (ex: 0.3 ou 0.35)

### Processamento muito lento
- Use um modelo mais leve (`yolo11n.pt` ou `yolo11s.pt`)
- Reduza as dimensões de processamento

### Processamento impreciso
- Use um modelo mais pesado (`yolo11l.pt` ou `yolo11x.pt`)
- Aumente as dimensões de processamento

### Stream não conecta (interno)
- Verifique se o servidor NGINX-RTMP está rodando: `docker compose ps`
- Reinicie o servidor: `cd nginx-rtmp-stream && docker compose restart`
- **IMPORTANTE**: Certifique-se de que você está **transmitindo ativamente** (OBS deve mostrar "Live")
- Para HLS: Aguarde 5-10 segundos após iniciar a transmissão para os arquivos serem gerados
- Verifique se arquivos HLS existem: `nginx-rtmp-stream/stream/live/index.m3u8`
- Se não houver transmissão ativa, o HLS não funcionará!

### Stream não conecta (externo)
- Verifique se a URL está correta
- Teste a URL em um player de vídeo (VLC, etc.)
- Verifique sua conexão de internet
- Alguns streams podem ter restrições geográficas

### Lag ou atraso no processamento de stream
- Reduza as dimensões de processamento em `stream.dimensions`
- Use um modelo mais leve (yolo11n.pt ou yolo11s.pt)
- Feche outros programas que consomem recursos

## 📝 Licença

Este projeto está sob a licença MIT.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.
