from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Mock Interviewer</title>
    <style>
        body{
            font-family:Arial;
            background:#111827;
            color:white;
            padding:40px;
            max-width:900px;
            margin:auto;
        }

        textarea{
            width:100%;
            height:150px;
            padding:10px;
            margin-top:10px;
        }

        button{
            padding:12px 20px;
            background:#2563eb;
            color:white;
            border:none;
            cursor:pointer;
            margin-top:10px;
        }

        .card{
            background:#1f2937;
            padding:20px;
            border-radius:10px;
            margin-bottom:20px;
        }
    </style>
</head>
<body>

<h1>AI Interviewer</h1>

<div class="card">
<h3 id="question">{{question}}</h3>
</div>

<textarea id="answer" placeholder="Type your answer here"></textarea>

<br>

<button onclick="submitAnswer()">Submit Answer</button>

<div class="card" id="result" style="display:none;">
    <h3>Feedback</h3>
    <p id="feedback"></p>

    <h3>Score</h3>
    <p id="score"></p>
</div>

<script>

async function submitAnswer(){

    const answer = document.getElementById("answer").value;

    const response = await fetch("/evaluate",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            answer:answer
        })
    });

    const data = await response.json();

    document.getElementById("feedback").innerText=data.feedback;
    document.getElementById("score").innerText=data.score+"/10";
    document.getElementById("question").innerText=data.next_question;

    document.getElementById("result").style.display="block";
    document.getElementById("answer").value="";
}

</script>

</body>
</html>
"""

current_question = "Tell me about yourself."

@app.route("/")
def home():
    return render_template_string(
        HTML,
        question=current_question
    )

@app.route("/evaluate", methods=["POST"])
def evaluate():

    global current_question

    answer = request.json["answer"]

    prompt = f"""
You are an expert technical interviewer.

Current Question:
{current_question}

Candidate Answer:
{answer}

Return ONLY JSON:

{{
"score":8,
"feedback":"Detailed feedback",
"next_question":"Adaptive next question"
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    import json

    result = json.loads(response.output_text)

    current_question = result["next_question"]

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)