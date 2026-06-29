import csv
import random
import re
import tkinter as tk
from tkinter import messagebox


class QuizApp:

    def __init__(self, root, csv_file):
        self.root = root
        self.root.title("2300語マスター！例文穴埋め4択クイズ")
        self.root.geometry("700x500")  # 例文が見やすいように少し横幅を広げました

        # データの読み込み
        self.quiz_data = self.load_csv(csv_file)
        self.current_question = None

        # 画面のパーツ
        # ① 例文を表示するラベル（問題文）
        self.sentence_label = tk.Label(
            root,
            text="",
            font=("Arial", 16, "bold"),
            fg="#333333",
            wraplength=650,
            justify="center",
        )
        self.sentence_label.pack(pady=20)

        # ② ヒント（意味）を表示するラベル
        self.meaning_label = tk.Label(
            root, text="", font=("MS Gothic", 12), fg="#666666"
        )
        self.meaning_label.pack(pady=5)

        self.buttons = []
        for i in range(4):
            btn = tk.Button(
                root,
                text="",
                font=("Arial", 13),
                width=50,
                height=2,
                bg="#f0f0f0",
                command=lambda idx=i: self.check_answer(idx),
            )
            btn.pack(pady=8)
            self.buttons.append(btn)

        self.next_question()

    def load_csv(self, filename):
        data = []
        with open(filename, "r", encoding="shift-jis", errors="ignore") as f:
            reader = csv.reader(f)
            for row in reader:
                # 単語、意味、例文、和訳が揃っている行だけを対象にする
                if len(row) >= 4:
                    data.append({
                        "word": row[0].strip(),
                        "meaning": row[1].strip(),
                        "sentence": row[2].strip(),
                        "translation": row[3].strip(),
                    })
        return data

    def make_blank_sentence(self, sentence, word):
        """例文の中の単語を ( ) に置き換える処理（大文字小文字や過去形・複数形にも対応）"""
        # 単語の頭文字3文字くらいを基準に、例文の中からそれっぽい部分を ( ) に置換する
        # （例：agreed や agrees も ( ) になるように、少し柔軟に探します）
        base_word = word.lower()
        if len(base_word) > 3:
            search_word = base_word[:3]
        else:
            search_word = base_word

        pattern = re.compile(rf"\b{search_word}[a-zA-Z]*\b", re.IGNORECASE)

        # もし例文の中にうまく見つからなければ、単純置換
        if pattern.search(sentence):
            return pattern.sub("(   )", sentence)
        else:
            # 完全に一致するものがない場合の保険（過去形などで形が変わりすぎている場合）
            return f"{sentence}\n\n【ヒントの単語】: {word[0]}..."

    def next_question(self):
        if not self.quiz_data:
            messagebox.showinfo("終了", "データがありません")
            return

        # 正解のデータをランダムに1つ選ぶ
        self.current_question = random.choice(self.quiz_data)
        correct_word = self.current_question["word"]

        # 例文を ( ) に加工
        blank_sentence = self.make_blank_sentence(
            self.current_question["sentence"], correct_word
        )

        # 不正解の選択肢（ほかの英単語）を3つランダムに選ぶ
        wrong_choices = [
            item["word"]
            for item in self.quiz_data
            if item["word"].lower() != correct_word.lower()
        ]
        selected_wrongs = random.sample(
            wrong_choices, min(3, len(wrong_choices))
        )

        # 4つの選択肢（英単語）を混ぜる
        self.choices = selected_wrongs + [correct_word]
        random.shuffle(self.choices)

        # 画面の表示を更新
        self.sentence_label.config(text=blank_sentence)
        self.meaning_label.config(
            text=f"日本語訳：{self.current_question['translation']} （意味：{self.current_question['meaning']}）"
        )

        for i, choice in enumerate(self.choices):
            self.buttons[i].config(text=f"{i+1}.  {choice}", bg="#f0f0f0")

    def check_answer(self, idx):
        selected = self.choices[idx]
        correct = self.current_question["word"]

        if selected.lower() == correct.lower():
            messagebox.showinfo(
                "正解！",
                f"素晴らしい！正解です！\n\n【元の例文】\n{self.current_question['sentence']}",
            )
            self.next_question()
        else:
            messagebox.showerror(
                "不正解...",
                f"残念！\n正解は「{correct}」でした。\n\n【元の例文】\n{self.current_question['sentence']}",
            )


# アプリの起動
if __name__ == "__main__":
    import os

    root = tk.Tk()

    # ★ここをあなたの実際のCSVファイル名（ファイル名だけ）に書き換える★
    # 例: "word.csv" や "LEAP_list.csv" など
    target_csv_name = "quiz_data.csv"

    # プログラムがある場所（フォルダ）を自動で取得して合体させる
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_filename = os.path.join(current_dir, target_csv_name)

    app = QuizApp(root, csv_filename)
    root.mainloop()