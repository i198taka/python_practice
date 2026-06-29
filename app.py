import csv
import os
import random
import re
import streamlit as st

st.set_page_config(page_title="2300語マスター！例文穴埋めクイズ", page_icon="📝")


@st.cache_data
def load_csv():
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
    base_word = word.lower()
    search_word = base_word[:3] if len(base_word) > 3 else base_word
    pattern = re.compile(rf"\b{search_word}[a-zA-Z]*\b", re.IGNORECASE)
    if pattern.search(sentence):
        return pattern.sub("(   )", sentence)
    return f"{sentence}\n\n（ヒント: {word[0]}...）"


all_quiz_data = load_csv()

if not all_quiz_data:
    st.error(
        "CSVファイルが見つからないか、データが空っぽです。ファイル名を確認してください。"
    )
else:
    st.title("📝 2300語マスター！例文穴埋めクイズ")

    # --- 🛠️ ここから【範囲選択機能】の追加 ---
    st.sidebar.header("🎯 出題範囲の設定")
    total_words = len(all_quiz_data)

    # サイドバーにスライダーを表示
    start_num, end_num = st.sidebar.slider(
        "解く問題の範囲を選んでね：",
        min_value=1,
        max_value=total_words,
        value=(1, min(100, total_words)),  # 初期値は1〜100
    )

    # 選択された範囲のデータだけを切り出す（Pythonは0番目から数えるので -1 する）
    quiz_data = all_quiz_data[start_num - 1 : end_num]
    st.sidebar.write(f"現在の対象： {len(quiz_data)} 単語")
    # --- 🛠️ ここまで ---

    st.divider()

    # 範囲が変わったら問題をリセットするための仕組み
    if "current_range" not in st.session_state:
        st.session_state.current_range = (start_num, end_num)

    # ユーザーが範囲を変えたら、今の問題を強制クリアして新しい範囲から選ぶ
    if st.session_state.current_range != (start_num, end_num):
        st.session_state.current_range = (start_num, end_num)
        if "current_q" in st.session_state:
            del st.session_state.current_q

    # クイズの出題ロジック
    if "current_q" not in st.session_state:
        q = random.choice(quiz_data)
        correct_word = q["word"]
        wrong_choices = [
            item["word"]
            for item in all_quiz_data
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

    q = st.session_state.current_q
    choices = st.session_state.choices

    blank_sentence = make_blank_sentence(q["sentence"], q["word"])
    st.subheader(
        f"【問題】 空欄に入る単語はどれ？ ({start_num} 〜 {end_num}番 から出題中)"
    )
    st.info(blank_sentence)
    st.write(f"💡 日本語訳：{q['translation']}")

    st.write("---")

    for i, choice in enumerate(choices):
        if st.button(
            f"{i+1}. {choice}", key=f"btn_{choice}", use_container_width=True
        ):
            st.session_state.answered = True
            st.session_state.selected_answer = choice

    if st.session_state.answered:
        selected = st.session_state.selected_answer
        correct = q["word"]

        if selected.lower() == correct.lower():
            st.success(f"🎉 正解！ すばらしい！")
        else:
            st.error(f"❌ 残念... 正解は 「{correct}」 でした。")

        st.warning(f"📚 【元の例文】\n{q['sentence']}\n（意味：{q['meaning']}）")

        if st.button("次の問題へ ➡️", type="primary"):
            del st.session_state.current_q
            st.rerun()
