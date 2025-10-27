
# Servidor NGINX-RTMP para Streaming e Análise de Vídeo com YOLO

Este projeto cria um servidor de streaming RTMP/HLS otimizado para análise de vídeo em tempo real com modelos de IA (ex: YOLO).

## 1. Pré-requisitos

### Windows
Instale o Docker Desktop:
[https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)

### Linux
Siga o guia oficial:
[https://docs.docker.com/desktop/setup/install/linux/](https://docs.docker.com/desktop/setup/install/linux/)

---

## 2. Iniciar o servidor

Navegue até a pasta do projeto `nginx-rtmp-stream` e execute:

```bash
docker compose up -d
````

Verifique se o NGINX está rodando corretamente:

```bash
docker compose logs nginx
```

---

## 3. Transmitir vídeo (RTMP)

Use um dispositivo ou software de streaming (ex: OBS) para enviar vídeo para:

```
rtmp://localhost:1935/live
```

---

## 4. Visualizar a transmissão (HLS)

Abra no navegador ou em players como VLC:

```
http://localhost:8081/live/.m3u8
```

---

## 5. Observações Técnicas

* **Baixa latência**: fragmentos HLS curtos (2s) e sincronização do stream permitem que a IA capture todos os frames sem perda.
* **Estabilidade**: múltiplas conexões simultâneas são suportadas, ideal para análise em tempo real.
* **Eficiência de recursos**: Docker limita CPU/memória para não interferir na execução da IA.
* **Segurança**: acesso fora da pasta `/live` é bloqueado, e headers HTTP otimizados para CORS e cache.

---

## 6. Estrutura de Pastas

```
nginx-rtmp-stream/
├─ docker-compose.yml
├─ nginx.conf
└─ stream/          # onde os vídeos HLS serão gerados
```

---

## 7. Recomendações

* Utilize resoluções compatíveis com a capacidade do seu servidor para evitar perda de frames.
* Para múltiplas câmeras ou streams simultâneos, cada aplicação RTMP pode ter sua própria pasta HLS.
* O servidor pode ser monitorado em tempo real via:

```bash
docker compose logs -f nginx
```
