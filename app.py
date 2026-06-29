import csv
import os
import random
import re
import streamlit as st

# ページの設定（スマホでも見やすいようにタイトルなどを設定）
st.set_page_config(page_title="2300語マスター！例文穴埋めクイズ", page_icon="📝")


# CSVデータを読み込む関数（キャッシュ機能をつけて動きを速くします）
@st.cache_data
def load_csv():
    # プログラムと同じフォルダにあるCSVファイルを探す
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # ★あなたの実際のCSVファイル名に書き換えてください★
    csv_filename = os.path.join(current_dir, "quiz_data.csv")

    data = []
    if os.path.exists(csv_filename):
        with open(
            csv_filename, "r", encoding="shift_jis", errors="ignore"
        ) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    data.append({
                        "word": row[0].strip(),
                        "meaning": row[1].strip(),
                        "sentence": row[2].strip(),
                        "translation": row[3].strip(),
                    })
    return data


def make_blank_sentence(sentence, word):
    """例文の中の単語を ( ) に置き換える処理"""
    base_word = word.lower()
    search_word = base_word[:3] if len(base_word) > 3 else base_word
    pattern = re.compile(rf"\b{search_word}[a-zA-Z]*\b", re.IGNORECASE)
    if pattern.search(sentence):
        return pattern.sub("(   )", sentence)
    return f"{sentence}\n\n（ヒント: {word[0]}...）"


# データの準備
quiz_data = load_csv()

if not quiz_data:
    st.error(
        "CSVファイルが見つからないか、データが空っぽです。ファイル名を確認してください。"
    )
else:
    st.title("📝 2300語マスター！例文穴埋めクイズ")
    st.write("友達と一緒に英単語を極めよう！")
    st.divider()

    # アプリ内で「現在の問題」を記憶するための仕組み（セッション状態）
    if "current_q"  not in st.session_state:

        # 新しい問題をセット
        q = random.choice(quiz_data)
        correct_word = q["word"]
        wrong_choices = [
            item["word"]
            for item in quiz_data
            if item["word"].lower() != correct_word.lower()
        ]
        selected_wrongs = random.sample(
            wrong_choices, min(3, len(wrong_choices))
        )
        choices = selected_wrongs + [correct_word]
        random.shuffle(choices)

        st.session_state.current_q = q
        st.session_state.choices = choices
        st.session_state.answered = False
        st.session_state.selected_answer = None

    # 現在の問題データを取得
    q = st.session_state.current_q
    choices = st.session_state.choices

    # 問題の表示
    blank_sentence = make_blank_sentence(q["sentence"], q["word"])
    st.subheader("【問題】 空欄に入る単語はどれ？")
    st.info(blank_sentence)
    st.write(f"💡 日本語訳：{q['translation']}")

    st.write("---")

    # 4択ボタンの配置
    for i, choice in enumerate(choices):
        if st.button(f"{i+1}. {choice}", key=f"btn_{choice}", use_container_width=True):
            st.session_state.answered = True
            st.session_state.selected_answer = choice

    # 答え合わせの表示
    if st.session_state.answered:
        selected = st.session_state.selected_answer
        correct = q["word"]

        if selected.lower() == correct.lower():
            st.success(f"🎉 正解！ すばらしい！")
        else:
            st.error(f"❌ 残念... 正解は 「{correct}」 でした。")

        st.warning(f"📚 【元の例文】\n{q['sentence']}\n（意味：{q['meaning']}）")

        # 次の問題へ進むボタン
        if st.button("次の問題へ ➡️", type="primary"):
            del st.session_state.current_q  # データをクリアして次へ
            st.rerun()
