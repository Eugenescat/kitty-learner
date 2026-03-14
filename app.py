#!/usr/bin/env python3
"""
Passive Learner - Web Application

Flask-based web app for transforming PDFs into RedNote-style feeds.
"""

import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

import database  # PostgreSQL storage with JSON fallback
from pipeline.graph import run_pipeline
from pipeline.state import build_initial_state

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Initialize database
database.init_db()


@app.route('/')
def index():
    """Main page with feed."""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and start processing."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())[:8]
    filepath = app.config['UPLOAD_FOLDER'] / f"{file_id}_{filename}"
    file.save(filepath)
    
    # Get title from form or filename
    title = request.form.get('title', filename.rsplit('.', 1)[0])
    
    return jsonify({
        "success": True,
        "file_id": file_id,
        "filename": filename,
        "title": title,
        "message": "File uploaded successfully. Starting processing...",
    })


@app.route('/api/process/<file_id>', methods=['POST'])
def process_pdf(file_id):
    """Process uploaded PDF and generate feed."""
    # Find the uploaded file
    upload_folder = app.config['UPLOAD_FOLDER']
    matching_files = list(upload_folder.glob(f"{file_id}_*.pdf"))
    
    if not matching_files:
        return jsonify({"error": "File not found"}), 404
    
    filepath = matching_files[0]
    payload = request.get_json(silent=True) or {}
    title = payload.get('title', filepath.stem.split('_', 1)[-1])
    
    try:
        state = build_initial_state(
            file_id=file_id,
            title=title,
            pdf_path=str(filepath),
        )
        result = run_pipeline(state)

        if result.get("errors"):
            raise RuntimeError(result["errors"][-1])
        
        return jsonify({
            "success": True,
            "file_id": file_id,
            "title": result.get("title", title),
            "summary": result.get("paper_summary", ""),
            "topic_count": result.get("topic_count", 0),
            "post_count": result.get("post_count", 0),
        })
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/feed/<file_id>')
def get_feed(file_id):
    """Get generated feed data from database."""
    feed_data = database.load_feed_with_fallback(file_id)
    
    if not feed_data:
        return jsonify({"error": "Feed not found. Please process the PDF first."}), 404
    
    return jsonify(feed_data)


@app.route('/api/feeds')
def list_feeds():
    """List all saved feeds from database."""
    feeds = database.list_feeds_with_fallback()
    return jsonify({"feeds": feeds})


@app.route('/api/demo')
def get_demo_feed():
    """Return demo feed data for preview."""
    demo_posts = [
        {
            "id": 0,
            "agent": {"nickname": "曲奇脆脆猪", "name": "AI专业本科生", "avatar_emoji": "🐷"},
            "topic": {
                "topic_id": 1,
                "title": "🎰 什么是多臂老虎机问题？赌场里的AI入门课",
                "core_idea": "探索与利用的权衡是强化学习的核心问题",
                "why_it_matters": "这是理解所有RL算法的基础",
                "controversy_level": "low",
                "source_section": "2.1",
                "difficulty": 3,
            },
            "content": "让我来拆解一下这个概念！想象你在赌场面对一排老虎机，每台机器的中奖概率都不一样，但你不知道哪台最好。你要怎么玩才能赚最多？这就是经典的「探索vs利用」困境：是继续试新机器（探索），还是一直玩目前看起来最好的那台（利用）？",
            "likes": 156,
            "replies": [
                {"agent": {"nickname": "海参难吃", "avatar_emoji": "🌊"}, "content": "所以这个问题在现实中有什么用呀？感觉就是个数学游戏...", "likes": 23},
                {"agent": {"nickname": "鸡肋哥", "avatar_emoji": "👨‍💻"}, "content": "推荐系统、A/B测试、广告投放全都是这个问题的变种！", "likes": 45},
            ],
        },
        {
            "id": 1,
            "agent": {"nickname": "吃西瓜的狐狸", "name": "互联网产品经理", "avatar_emoji": "🦊"},
            "topic": {
                "topic_id": 2,
                "title": "ε-greedy 真的是最优解吗？🤔",
                "core_idea": "简单但不一定最优的探索策略",
                "why_it_matters": "理解算法的局限性很重要",
                "controversy_level": "high",
                "source_section": "2.2",
                "difficulty": 6,
            },
            "content": "等等，这里有问题！ε-greedy 说「大部分时间选最好的，偶尔随机探索」，但这个 ε 到底设多少合适？而且随着时间推移，我们对各个选项已经很了解了，为什么还要保持同样的探索率？这不是在浪费机会吗？",
            "likes": 89,
            "replies": [],
        },
        {
            "id": 2,
            "agent": {"nickname": "小六AIGC", "name": "科技自媒体编辑", "avatar_emoji": "✨"},
            "topic": {
                "topic_id": 3,
                "title": "UCB算法：「乐观面对不确定性」是什么鬼？",
                "core_idea": "用置信上界来平衡探索和利用",
                "why_it_matters": "这是一个优雅的数学解法",
                "controversy_level": "medium",
                "source_section": "2.7",
                "difficulty": 5,
            },
            "content": "这个类比绝了！UCB 的核心思想就像相亲：对于没怎么了解的人，你会「乐观地假设」ta可能很优秀，所以值得多约几次。对于已经很了解的人，你心里已经有数了。UCB就是用数学公式量化了这种「给新选项更多机会」的直觉 ✨",
            "likes": 203,
            "replies": [
                {"agent": {"nickname": "卡刃大师", "avatar_emoji": "🎓"}, "content": "这让我想到了 Thompson Sampling，也是用「不确定性」来指导探索...", "likes": 31},
            ],
        },
        {
            "id": 3,
            "agent": {"nickname": "鸡肋哥", "name": "资深开发工程师", "avatar_emoji": "👨‍💻"},
            "topic": {
                "topic_id": 4,
                "title": "Regret：衡量你「后悔程度」的指标 📊",
                "core_idea": "Regret是评估bandit算法的标准指标",
                "why_it_matters": "工程落地需要量化指标",
                "controversy_level": "low",
                "source_section": "2.4",
                "difficulty": 4,
            },
            "content": "在实际项目里，我们怎么知道算法好不好？用 Regret！它计算的是：如果你一开始就知道最优选项，能赚多少钱，减去你实际赚的钱。这个差值就是你的「后悔值」。好的算法应该让 Regret 增长得越来越慢。",
            "likes": 127,
            "replies": [],
        },
        {
            "id": 4,
            "agent": {"nickname": "海参难吃", "name": "想进入AI行业的文科生", "avatar_emoji": "🌊"},
            "topic": {
                "topic_id": 5,
                "title": "非平稳问题：当最优解会变的时候怎么办？😱",
                "core_idea": "现实世界中环境往往是变化的",
                "why_it_matters": "这才是实际应用的难点",
                "controversy_level": "high",
                "source_section": "2.5",
                "difficulty": 7,
            },
            "content": "小白问一下... 前面讲的都假设每台老虎机的中奖率是固定的，但现实中这个假设成立吗？比如用户口味会变、季节会变、竞争对手也在变... 那之前学的方法还能用吗？感觉这才是真正难的地方！",
            "likes": 245,
            "replies": [
                {"agent": {"nickname": "吃西瓜的狐狸", "avatar_emoji": "🦊"}, "content": "问到点上了！这就是为什么要用「指数加权平均」而不是简单平均", "likes": 56},
            ],
        },
        {
            "id": 5,
            "agent": {"nickname": "卡刃大师", "name": "第五年博士生", "avatar_emoji": "🎓"},
            "topic": {
                "topic_id": 6,
                "title": "Gradient Bandit：用梯度下降做选择？🧮",
                "core_idea": "把bandit问题转化为优化问题",
                "why_it_matters": "这是通往Policy Gradient的桥梁",
                "controversy_level": "medium",
                "source_section": "2.8",
                "difficulty": 8,
            },
            "content": "从更大的视角来看，Gradient Bandit 其实是把 Bandit 问题转化成了一个优化问题。每个动作有一个「偏好值」，用 softmax 转成概率，然后用梯度上升来更新偏好。这个思路和后面要学的 Policy Gradient 是一脉相承的！",
            "likes": 98,
            "replies": [],
        },
    ]
    
    return jsonify({
        "title": "RL Chapter 2 - Multi-armed Bandits",
        "summary": "这一章讲的是如何在「探索未知」和「利用已知」之间做权衡",
        "posts": demo_posts,
    })


if __name__ == '__main__':
    print("🚀 Starting Passive Learner Web App...")
    print("📍 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
