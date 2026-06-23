import streamlit as st

st.title("クイズ")

st.write("問題：日本の首都はどこ？")#表示される問題

answer=st.radio("選択肢を選んでね：",["大阪","東京","京都"])#ラジオボタン、[]内は選択肢


if st.button("回答する"):#ボタン押される
    if answer=="東京":
        st.success("正解！")#緑色の成功ボックスを表示
    else:
        st.error("残念！はずれ！")#赤色のエラーボックスを表示