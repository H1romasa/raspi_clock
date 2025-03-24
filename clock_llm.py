# APIを使用した軽量な実装例
import requests
import json

class LLMAssistant:
    def __init__(self, api_key):
        self.api_key = api_key
        # OpenAI APIを使用する場合
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def ask(self, question, max_tokens=300):
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"エラー: {response.status_code} - {response.text}"
        except Exception as e:
            return f"リクエスト中にエラーが発生しました: {str(e)}"


# ローカルで軽量LLMを実行する場合（llama.cpp使用例）
from llama_cpp import Llama

class LocalLLM:
    def __init__(self, model_path):
        # 量子化されたモデルを使用（例：7B、4bitで量子化）
        self.model = Llama(
            model_path=model_path,
            n_ctx=2048,       # コンテキスト長
            n_threads=4       # 使用スレッド数
        )
    
    def ask(self, question, max_tokens=300):
        try:
            response = self.model(
                prompt=f"質問: {question}\n回答: ",
                max_tokens=max_tokens,
                temperature=0.7,
                stop=["質問:"]
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            return f"モデル実行中にエラー: {str(e)}"


# メインアプリケーションに統合する例
def add_llm_to_app(app, use_local=False):
    # LLMフレームの作成
    llm_frame = tk.Frame(app.root, bg="black")
    llm_frame.pack(fill=tk.BOTH, pady=10)
    
    # 入力欄
    question_entry = tk.Entry(llm_frame, font=("Arial", 14), width=50)
    question_entry.pack(side=tk.LEFT, padx=5)
    
    # 回答表示エリア
    answer_text = tk.Text(app.root, font=("Arial", 12), bg="#222", fg="white", height=6)
    answer_text.pack(fill=tk.X, padx=10, pady=5)
    
    # LLMインスタンスの初期化
    if use_local:
        # ローカルモデルのパス（例：Raspberry Piに対応した量子化モデル）
        model_path = "/home/pi/models/ggml-model-q4_0.bin"
        llm = LocalLLM(model_path)
    else:
        # APIキー（実際のキーに置き換えてください）
        api_key = "あなたのAPIキー"
        llm = LLMAssistant(api_key)
    
    # 質問送信関数
    def send_question():
        question = question_entry.get()
        if question.strip():
            # 処理中メッセージ
            answer_text.delete(1.0, tk.END)
            answer_text.insert(tk.END, "考え中...")
            answer_text.update()
            
            # 別スレッドで処理（UIをブロックしないため）
            def process_question():
                response = llm.ask(question)
                # UIスレッドで回答を表示
                app.root.after(0, lambda: update_answer(response))
            
            threading.Thread(target=process_question, daemon=True).start()
            
            # 入力欄をクリア
            question_entry.delete(0, tk.END)
    
    def update_answer(text):
        answer_text.delete(1.0, tk.END)
        answer_text.insert(tk.END, text)
    
    # 送信ボタン
    send_button = tk.Button(llm_frame, text="質問する", command=send_question)
    send_button.pack(side=tk.LEFT, padx=5)