FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    nmap nikto dirb gobuster \
    sqlmap hydra john \
    curl wget net-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install flask requests --break-system-packages

COPY server.py .

EXPOSE 5000

CMD ["python3", "server.py", "--ip", "0.0.0.0", "--port", "5000"]
