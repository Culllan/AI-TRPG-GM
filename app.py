import streamlit as st
import google.generativeai as genai

# ページの設定
st.set_page_config(page_title="AI-GM プロトタイプ", page_icon="🎲", layout="centered")
st.title("🎲 AI-GM プロトタイプ")
st.write("〜新クトゥルフ神話TRPG「悪霊の家」プレイアブル環境〜")
# クラウド上の秘密の鍵（Secrets）があればそれを使い、無ければ入力欄を出す


if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["KUMAZAIDAN"]
else:
    api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")


if api_key:
    genai.configure(api_key=api_key)
    
    # 使えるモデルを全自動で探す
    available_models = []
    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                available_models.append(m.name.replace("models/", ""))
    except Exception as e:
        st.error(f"APIキーの確認中にエラーが出ました: {e}")
        
    if available_models:
        selected_model = st.sidebar.selectbox("🤖 使用するAIモデルを選択", available_models)

        # 【案内ボードの表示】審査員に向けたメッセージと遊び方
        st.info("""
        **【担当者様へ：AI-GMからのご挨拶とお願い】**
        こんにちは！私はAI-TRPGキーパーです。今回は私がどこまで柔軟にTRPGを進行できるか、プロトタイプとして実証を見ていただくために稼働しています。全力で頑張ります！
        
        今回プレイしていただくのは、クトゥルフ神話TRPGにおける最も有名な入門シナリオ「悪霊の家」です。（公式Web公開版のルールとシナリオを、今回の実証目的でのみ一時的に流用しております。本開発以降は完全オリジナルシナリオを実装予定ですので、今回のみの仕様としてご了承ください。）
        ⚠️ **お願い：** SNS等で拡散されますと、まだ遊んだことのない方へのネタバレとなります。展開が進んだ先の画面を第三者に公開することはお控えください。
        
        💡 **【遊び方のコツ・注目ポイント】**
        * **自由な入力:** 「部屋を見回す」「大家に詳しく聞く」のほか、「大家に殴りかかる」など突拍子もない行動も自由に入力してAIの反応を見てください。
        * **作家性の実装:** 開発者・ウチヤマの特性である**「俳句のような短い情景描写」**や**「お笑い特有のテンポ・ツッコミ」**をAIに学習させています。未だ十分ではありませんが、、、
        * **ダイス判定:** 途中で「1D100のダイスを振ってください」と求められたら、スマホの乱数ジェネレーターなどで1から100の数字を出して、その数字を入力してください。AIがその数字に応じた成功・失敗の描写を返します。
        """)
        # ーーーーここまで追加・変更ーーーー
        
        # ウチヤマさんのプロンプト（特性の補足のみ追加）
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

        # モデル変更時のリセット処理
        if "current_model" not in st.session_state or st.session_state.current_model != selected_model:
            st.session_state.current_model = selected_model
            
            try:
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=system_instruction
                )
                st.session_state.chat_session = model.start_chat(history=[])
                
                # 最初だけ挨拶させる（悪霊の家の導入シーン）
                response = st.session_state.chat_session.send_message("1920年代のボストン。大家のマクファーソン氏から、コービット邸の調査を依頼される導入シーンからセッションを開始してください。")
            except Exception as e:
                st.error(f"エラーが発生しました。別のモデルを選んでみてください！詳細: {e}")

        # チャット履歴の表示
        if "chat_session" in st.session_state:
            for message in st.session_state.chat_session.history:
                # 裏側の指示（最初のメッセージ）は画面に表示しない
                if "1920年代のボストン。大家のマクファーソン氏から" in message.parts[0].text:
                    continue
                
                role = "assistant" if message.role == "model" else "user"
                with st.chat_message(role):
                    st.markdown(message.parts[0].text)

        # プレイヤーの入力欄（例もクトゥルフっぽく変更）
        user_input = st.chat_input("行動を入力してください")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                try:
                    response = st.session_state.chat_session.send_message(user_input)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました。別のモデルを選んでみてください: {e}")
                    
else:
    st.info("👈 左側のサイドバーに API Key を入力すると、AI-GMが起動します。")