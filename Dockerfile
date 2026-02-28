FROM python:3.9-slim

RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HF_HOME=/home/user/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/user/app/.cache/huggingface \
    TORCH_HOME=/home/user/app/.cache/torch

WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

USER user
COPY --chown=user . .

RUN mkdir -p .cache/huggingface .cache/torch/hub

# Pre-download the breed model at build time so cold starts are fast
RUN python -c "\
from transformers import AutoImageProcessor, AutoModelForImageClassification; \
m = 'raffaelsiregar/dog-breeds-classification'; \
AutoImageProcessor.from_pretrained(m); \
AutoModelForImageClassification.from_pretrained(m)"

EXPOSE 7860

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "--timeout", "120", "app:app"]
