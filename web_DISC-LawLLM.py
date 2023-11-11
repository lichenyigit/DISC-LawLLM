import json
import torch
import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig


st.set_page_config(page_title="法小贤")
st.title("法小贤")


@st.cache_resource
def init_model():
    model_path = "ShengbinYue/DISC-LawLLM"
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True
    )
    model.generation_config = GenerationConfig.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, use_fast=False, trust_remote_code=True
    )
    return model, tokenizer


def clear_chat_history():
    del st.session_state.messages


def init_chat_history():
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("您好,我是法小贤,您的法律助手。由专业研发团队开发,可以为您提供法律咨询服务。💖")

    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = "🙋‍♂️" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    else:
        st.session_state.messages = []

    return st.session_state.messages


def main():
    model, tokenizer = init_model()
    messages = init_chat_history()
    if prompt := st.chat_input("Shift + Enter 换行，Enter 发送"):
        with st.chat_message("user", avatar="🙋‍♂️"):
            st.markdown(prompt)
        messages.append({"role": "user", "content": prompt})
        print(f"[user] {prompt}", flush=True)
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            for response in model.chat(tokenizer, messages, stream=True):
                placeholder.markdown(response)
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
        messages.append({"role": "assistant", "content": response})
        print(json.dumps(messages, ensure_ascii=False), flush=True)

        st.button("清空对话", on_click=clear_chat_history)


if __name__ == "__main__":
    main()
