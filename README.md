# raspi_clock

curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama.tgz\\

tar -xzf ollama.tgz\\

ls -l ./bin/ollama
chmod +x ./bin/ollama
\\

./bin/ollama serve
\\

./bin/ollama --version
\\

./bin/ollama run llama2
\\

echo "alias ollama='$HOME/bin/ollama'" >> ~/.bashrc
source ~/.bashrc
