"""
Keyboard Predictor web page (Gradio). Step 8 of the activity.
Keep this file in the same folder as predictor_starter.py and the books folder.
Run:  python predictor_app.py   then open http://127.0.0.1:7860
Do not use launch(share=True): it makes a public link to your computer.
"""
import gradio as gr
import predictor_starter as kb

MODELS = {author: kb.build_model(kb.load_words(path)) for author, path in kb.BOOKS.items()}


def predict(text, author):
    # Gradio calls this function every time the text or the book changes.
    model = MODELS[author]
    words = text.lower().split()
    if text.endswith(" ") or not words:
        # A finished word: PREDICT the next word.
        return dict(kb.suggest(model, words, k=5))

    # Still typing: COMPLETE the word. Keep only the suggestions that
    # start with the letters typed so far ("wat" -> watson).
    prefix, context = words[-1], words[:-1]
    options = kb.suggest(model, context, k=500)
    matches = [(w, p) for w, p in options if w.startswith(prefix)]
    if not matches:   # nothing fits this context, so try every word in the book
        matches = [(w, p) for w, p in kb.top_k(model["unigrams"], 5000) if w.startswith(prefix)]
    return dict(matches[:5])


def write(text, author, mode):
    # Gradio calls this function when you press the button.
    start = text.strip() or "the"
    return kb.generate(MODELS[author], start, length=25, mode=mode.lower())


with gr.Blocks(title="Keyboard Predictor") as demo:
    gr.Markdown("# Keyboard Predictor\nStart typing. The bars show what the book thinks comes next.")
    author = gr.Radio(["alice", "sherlock"], value="alice", label="Learn from which book?")
    text = gr.Textbox(label="Type here: end with a space to predict the next word, or stop mid-word to complete it", value="the ")
    bars = gr.Label(label="Next word probabilities", num_top_classes=5)

    with gr.Row():
        mode = gr.Radio(["Greedy", "Random"], value="Greedy", label="Writing style")
        go = gr.Button("Let the book keep writing")
    story = gr.Textbox(label="What the book wrote", lines=3)

    text.change(predict, [text, author], bars)
    author.change(predict, [text, author], bars)
    go.click(write, [text, author, mode], story)
    demo.load(predict, [text, author], bars)

if __name__ == "__main__":
    demo.launch()
