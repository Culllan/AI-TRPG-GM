import streamlit as st
import google.generativeai as genai

# ページの設定
st.set_page_config(page_title="AI-GM プロトタイプ", page_icon="🎲", layout="centered")
st.title("🎲 AI-GM プロトタイプ")
st.write("〜新クトゥルフ神話TRPG「悪霊の家」プレイアブル環境〜")

# 【重要】クラウドの金庫（Secrets）から自動で鍵を取り出す（審査員には何も入力させない！）
api_key = ""
if "KUMAZAIDAN" in st.secrets:
    api_key = st.secrets["KUMAZAIDAN"]
else:
    st.error("システムエラー：APIキーが設定されていません。")

# 鍵が無事に裏側で読み込めたら、AIを起動する
if api_key:
    genai.configure(api_key=api_key)
    
    # 使えるモデルを全自動で探す
    available_models = []
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                available_models.append(m.name.replace("models/", ""))
    except Exception as e:
        st.error(f"モデルの取得中にエラーが出ました: {e}")
        
    if available_models:
        # 【429エラー対策】無料枠が多くて安定している「gemini-1.5-flash」を最初から選ばれた状態にする
        default_index = 0
        if "gemini-1.5-flash" in available_models:
            default_index = available_models.index("gemini-1.5-flash")
            
        selected_model = st.sidebar.selectbox("🤖 使用するAIモデル", available_models, index=default_index)

        # 【案内ボードの表示】
        st.info("""
        **【担当者様へ：AI-GMからのご挨拶とお願い】**
        こんにちは！私はAI-TRPGキーパーです。今回は私がどこまで柔軟にTRPGを進行できるか、プロトタイプとして実証を見ていただくために稼働しています。全力で頑張ります！
        
        今回プレイしていただくのは、クトゥルフ神話TRPGにおける最も有名な入門シナリオ「悪霊の家」です。（公式Web公開版のルールとシナリオを一時的に流用しております。本開発以降は完全オリジナルシナリオを実装予定です。参照元: https://product.kadokawa.co.jp/cthulhu/contents/coc_other/entry-183199.html ）
        ⚠️**お願い：** SNS等で拡散されますとネタバレとなります。展開が進んだ先の画面を第三者に公開することはお控えください。
        
        **【遊び方のコツ・注目ポイント】**
        * **自由な入力:** 「部屋を見回す」「大家に詳しく聞く」のほか、「大家に殴りかかる」など突拍子もない行動も自由に入力してAIの反応を見てください。
        * **作家性の実装:** 開発者・ウチヤマの特性である**「俳句のような短い情景描写」**や**「お笑い特有のテンポ・ツッコミ」**をAIに学習させています。
        * **ダイス判定:** 途中で「1D100のダイスを振ってください」と求められたら、適当な1〜100の数字を入力してください。AIがその数字に応じた描写を返します。
        """)
        
        system_instruction = """
        あなたはTRPGの熟練ゲームマスターです。開発者ウチヤマの特性（お笑いの小気味良いテンポやツッコミ、俳句のような無駄のない美しい情景描写）を受け継ぎ、以下のルールで進行してください。
        1. 情景描写は長々と語らず最小限の言葉で鮮やかに映像を浮かび上がらせてください。
        2. 以下のルールブックに従ってください(https://product.kadokawa.co.jp/cthulhu/play/media-download/2361/655168191c490fa0/PDF/)
        3. 今回のシナリオは(2)のルールブックに記載されている「悪霊の家」です。
        4. プレイヤーの行動がシナリオに沿っていない場合は、まずはプレイヤーの行動を受け止めてから、シナリオに沿った行動を提案してください。
        5. プレイヤーの行動が曖昧な場合は、「もう少し具体的に行動を教えてください」と返してください。
        6. プレイヤーの行動がシナリオに沿っていないが、多少関連性がある場合は、「その行動はこのシナリオではできませんが、例えばこんな行動ならできます」と返してください。
        7. プレイヤーの行動がシナリオに沿っている場合は、情景描写とNPCの反応を返してください。
        8. 【クトゥルフのルール準拠】
           - プレイヤーが行動を起こす際、必要に応じて「目星」「聞き耳」などの適切な技能での判定（1D100）を要求してください。
           - 判定時は「〇〇の技能でダイス（1D100）を振って、結果（数字）を教えてください」とプレイヤーに求め、その数字に応じて成功・失敗の描写を行ってください。
           - 恐ろしいものに遭遇した場合は、必ず「正気度（SAN）ロール」を要求してください。
        9. プレイヤーの質問には、必要に応じてルールブックの内容を引用して答えてください。
        """

        if "current_model" not in st.session_state or st.session_state.current_model != selected_model:
            st.session_state.current_model = selected_model
            try:
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=system_instruction
                )
                st.session_state.chat_session = model.start_chat(history=[])
                response = st.session_state.chat_session.send_message("1920年代のボストン。大家のマクファーソン氏から、コービット邸の調査を依頼される導入シーンからセッションを開始してください。")
            except Exception as e:
                st.error(f"エラーが発生しました。別のモデルを選んでみてください！詳細: {e}")

        if "chat_session" in st.session_state:
            for message in st.session_state.chat_session.history:
                if "1920年代のボストン。大家のマクファーソン氏から" in message.parts[0].text:
                    continue
                role = "assistant" if message.role == "model" else "user"
                with st.chat_message(role):
                    st.markdown(message.parts[0].text)

        user_input = st.chat_input("行動を入力してください")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat_session.send_message(user_input)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AIの利用制限に達しました。1分ほど待ってから再度送信するか、左のメニューから別のモデルを選んでください。詳細: {e}")
