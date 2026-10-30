# -*- coding: utf-8 -*-
"""
君と紡ぐ三叉路 BL版・HARD MODE
実行: python crossroad_bl_yume.py

・20話すべてに専用の会話／リアクションを用意
・悠真／蒼の性格差を反映
・連続選択による好感度／信頼度の変動
・各話の任務とTRUE END判定
・セーブ／ロード対応
"""

import json
import os
import random
import time

SAVE = "crossroad_bl_save.json"
NAMES = ["悠真", "蒼"]
MAX_AFF = 20
MAX_TRUST = 10

# 悠真：落ち着いていて面倒見がよく、少し不器用。
# 蒼：明るく距離が近い。冗談好きだが、時々本音を隠す。
MEMES = [
    "やりますねぇ！", "いいゾ〜これ", "おっ、そうだな", "114514",
    "ファッ！？", "あっ、そっかぁ", "これもうわかんねぇな",
    "ぬわああああん疲れたもおおおん", "しょうがないさ",
    "まずうちさぁ……", "お前のことが好きだったんだよ！",
    "見たけりゃ見せてやるよ（思い出のアルバム）",
    "ダイナモ感覚！ダイナモ感覚！", "ﾎﾟｯﾁｬﾏ…",
    "なんだこれは……たまげたなぁ"
]

# title, description, 悠真の会話, 蒼の会話,
# 悠真を選んだ時の反応, 蒼を選んだ時の反応,
# 任務説明, 任務達成条件
SCENES = [
    {
        "title": "放課後の教室",
        "desc": "夕日が差し込む教室。帰ろうとした君を、二人がほぼ同時に呼び止めた。",
        "y": "悠真「まだ残ってたんだ。……よかったら、この問題を一緒に見てくれないか？」",
        "a": "蒼「おーい！帰るなら一緒に帰ろうぜ。今日は寄り道する気分なんだよね」",
        "yr": "悠真「ありがとう。君が隣にいると、なぜか集中できるんだ」",
        "ar": "蒼「やった！帰り道ゲット。今日は絶対退屈させないからな！」",
        "mission": "二人の話を最後まで聞く",
        "mission_hint": "選択前に表示された二人の会話を読んでから選択する（自動達成）"
    },
    {
        "title": "購買部の攻防",
        "desc": "最後の焼きそばパンに、悠真と蒼の手が同時に伸びた。",
        "y": "悠真「君が食べたいなら譲るよ。昼を抜くのはよくないから」",
        "a": "蒼「うわ、ラスト一個！なあ、半分こしない？その方が平和じゃん」",
        "yr": "悠真「本当にいいの？……じゃあ、半分だけもらおうかな」",
        "ar": "蒼「ナイス判断！半分こって、なんか仲良しっぽくていいよな」",
        "mission": "分け合う気持ちを大切にする",
        "mission_hint": "蒼を選ぶと達成"
    },
    {
        "title": "雨宿り",
        "desc": "突然の雨。駅前の屋根の下で、三人は雨が止むのを待つことになった。",
        "y": "悠真「寒くない？これ、使って。……僕は大丈夫だから」",
        "a": "蒼「雨やばっ！こういう時って、雨の音を聞いてると眠くならない？」",
        "yr": "悠真「遠慮しなくていいよ。君が風邪をひいたら困る」",
        "ar": "蒼「わかる？この雨音、なんか落ち着くよな。もう少しここにいようぜ」",
        "mission": "相手を気遣う言葉を返す",
        "mission_hint": "悠真を選ぶと達成"
    },
    {
        "title": "文化祭の準備",
        "desc": "文化祭の担当決め。二人とも、なぜか君と同じ班を希望している。",
        "y": "悠真「作業の段取りは考えてある。君がよければ一緒に看板を作りたい」",
        "a": "蒼「飾り付け担当は楽しそうじゃん！君となら絶対いい感じになるって」",
        "yr": "悠真「助かったよ。君のアイデア、僕にはない発想だった」",
        "ar": "蒼「センスいいじゃん！これ、完成したら一番目立つぞ！」",
        "mission": "文化祭の準備に協力する",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "帰り道の約束",
        "desc": "夕焼けの帰り道。二人から週末の予定を聞かれた。",
        "y": "悠真「図書館に行く予定なんだ。……もし暇なら、一緒に来ない？」",
        "a": "蒼「週末ヒマ？街に新しい店できたらしいし、見に行こうぜ！」",
        "yr": "悠真「約束、覚えておくね。楽しみにしてる」",
        "ar": "蒼「決まり！じゃあ当日、寝坊すんなよー！」",
        "mission": "週末の約束を忘れない",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "試験前夜",
        "desc": "試験前夜。勉強通話のはずが、気づけば雑談ばかりになっていた。",
        "y": "悠真「ここは公式を覚えるより、仕組みを理解した方がいい。焦らなくて大丈夫」",
        "a": "蒼「勉強ってさ、誰かとやると意外とはかどるよな。……まあ今は休憩中だけど！」",
        "yr": "悠真「うん、その調子。君が頑張っているのを見ると僕も頑張れる」",
        "ar": "蒼「よし、次の問題！間違えても笑わないから安心しろって！」",
        "mission": "勉強を投げ出さずに続ける",
        "mission_hint": "悠真を選ぶと達成"
    },
    {
        "title": "小さなすれ違い",
        "desc": "君が片方と長く話していたせいか、もう一人の様子が少しおかしい。",
        "y": "悠真「別に怒ってないよ。ただ……少しだけ、寂しかったのかもしれない」",
        "a": "蒼「いや、全然気にしてないって！……って言ったら嘘になるかも」",
        "yr": "悠真「話してくれてありがとう。ちゃんと言葉にしてよかった」",
        "ar": "蒼「そっか。じゃあ次は俺とも話してくれよ。約束な！」",
        "mission": "相手の本音を受け止める",
        "mission_hint": "悠真を選ぶと達成"
    },
    {
        "title": "夜のメッセージ",
        "desc": "寝る前、二人からほぼ同時にメッセージが届いた。",
        "y": "悠真『今日はありがとう。君と話せて、少し気持ちが軽くなったよ』",
        "a": "蒼『起きてる？今日の話の続きしたい！あと面白い動画見つけたｗ』",
        "yr": "悠真「返信ありがとう。……おやすみ。また明日」",
        "ar": "蒼「返信きた！よっしゃ。じゃあ明日、続きな！」",
        "mission": "どちらかにきちんと返事をする",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "休日の待ち合わせ",
        "desc": "休日の待ち合わせ場所。二人とも、君より少し早く到着していた。",
        "y": "悠真「待たせてない？今日は君の行きたい場所を優先しよう」",
        "a": "蒼「おっ、来た来た！早く行こうぜ。今日は予定を詰め込んでるからな！」",
        "yr": "悠真「君が楽しそうでよかった。僕も来てよかったよ」",
        "ar": "蒼「やっぱ一緒に出かけると楽しいな！次も誘っていい？」",
        "mission": "待ち合わせに遅れず合流する",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "三人で見た景色",
        "desc": "展望台から街の明かりを眺める。二人は君の感想を待っている。",
        "y": "悠真「ここから見ると、いつもの街も違って見えるね」",
        "a": "蒼「うわ、めっちゃきれい！写真撮ろうぜ。三人で写るやつ！」",
        "yr": "悠真「この景色を、君と見られてよかった」",
        "ar": "蒼「はい、撮れた！これ、絶対消さないで保存しとけよ！」",
        "mission": "三人の思い出を残す",
        "mission_hint": "蒼を選ぶと達成"
    },
    {
        "title": "忘れ物",
        "desc": "教室に忘れ物をした君。悠真と蒼が一緒に探してくれた。",
        "y": "悠真「焦らなくていいよ。最後に使った場所から順番に探そう」",
        "a": "蒼「ロッカー見た？俺、そっち探す！君は机の周り頼む！」",
        "yr": "悠真「見つかってよかった。大事なものなら、なおさらね」",
        "ar": "蒼「発見！ほら、あったじゃん。俺たちの連携、完璧だったな！」",
        "mission": "二人と協力して探す",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "放課後の寄り道",
        "desc": "帰り道、二人が別々の店を提案してきた。",
        "y": "悠真「静かな喫茶店を見つけたんだ。落ち着いて話せると思う」",
        "a": "蒼「新しいゲームショップ見つけた！ちょっとだけ寄っていこうぜ！」",
        "yr": "悠真「こういう時間も悪くないね。また一緒に来よう」",
        "ar": "蒼「見て見て、これ面白そう！今度一緒に遊ぼうぜ！」",
        "mission": "相手のおすすめを楽しむ",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "体育祭",
        "desc": "体育祭の応援席。二人とも、君に見ていてほしいらしい。",
        "y": "悠真「勝てるかはわからないけど、最後まで走るよ。見ていてくれる？」",
        "a": "蒼「俺の出番、ちゃんと見てろよ！かっこいいとこ見せるから！」",
        "yr": "悠真「声、聞こえたよ。応援してくれてありがとう」",
        "ar": "蒼「応援ありがとな！おかげでいつもより走れた気がする！」",
        "mission": "最後まで応援する",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "秘密の相談",
        "desc": "放課後、二人のうち一人が君にだけ悩みを打ち明けた。",
        "y": "悠真「しっかりしているように見られるけど、僕だって迷うことはあるんだ」",
        "a": "蒼「いつもふざけてるけどさ、たまには真面目な話も聞いてほしいんだ」",
        "yr": "悠真「否定せずに聞いてくれてありがとう。少し楽になった」",
        "ar": "蒼「聞いてくれてありがとな。君には変に格好つけなくていい気がする」",
        "mission": "秘密を他人に話さない",
        "mission_hint": "悠真を選ぶと達成"
    },
    {
        "title": "帰りの電車",
        "desc": "帰りの電車が混んでいて、三人は並んで立つことになった。",
        "y": "悠真「揺れるから気をつけて。つり革、こっち使っていいよ」",
        "a": "蒼「人多いなー。はぐれないように、ここにいろよ！」",
        "yr": "悠真「もうすぐ着くね。もう少しだけ、このまま話していよう」",
        "ar": "蒼「次の駅か。早いなー。もう一駅くらい乗ってたい気分！」",
        "mission": "混雑の中でも気遣いを忘れない",
        "mission_hint": "悠真を選ぶと達成"
    },
    {
        "title": "誕生日の計画",
        "desc": "もうすぐ君の誕生日。二人はサプライズを考えているらしい。",
        "y": "悠真「派手なことは苦手だけど、君が喜ぶものを考えているんだ」",
        "a": "蒼「サプライズは任せろ！……あ、今のでバレた？いや、まだ何も言ってない！」",
        "yr": "悠真「当日まで楽しみにしていて。きっと気に入ってもらえると思う」",
        "ar": "蒼「しまった、口が滑った！でも期待してていいからな！」",
        "mission": "サプライズを楽しみに待つ",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "夜の通話",
        "desc": "寝る前の短い通話。何気ない会話が、いつまでも続いていく。",
        "y": "悠真「声を聞くと安心する。……もう少しだけ話していてもいい？」",
        "a": "蒼「眠くない？俺はまだ平気！……たぶん。いや、ちょっと眠いかも」",
        "yr": "悠真「おやすみ。明日も君に会えるのを楽しみにしているよ」",
        "ar": "蒼「寝落ちする前に言っとく。今日も話せてよかった！」",
        "mission": "相手におやすみを伝える",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "最後の文化祭",
        "desc": "文化祭の終わり。片付けを終えた二人が、君を校庭へ呼び出した。",
        "y": "悠真「この文化祭、君と一緒だったから特別だった。忘れたくないな」",
        "a": "蒼「終わっちゃうの寂しいな。でも、思い出はこれからも増やせるよな！」",
        "yr": "悠真「これからも、隣で同じ景色を見ていたい」",
        "ar": "蒼「次のイベントも三人で来ようぜ。約束な！」",
        "mission": "これからの約束をする",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "卒業アルバム",
        "desc": "卒業アルバムの最後のページ。二人が君のページにメッセージを書こうとしている。",
        "y": "悠真「何を書けば伝わるかな。ありきたりな言葉じゃ足りない気がする」",
        "a": "蒼「長文でも落書きでもいい？俺らしいメッセージにしたいんだよな」",
        "yr": "悠真「君と過ごした日々は、これからも大切にするよ」",
        "ar": "蒼「見返したとき笑えるように、全力で書いといた！大事にしろよ！」",
        "mission": "二人との思い出を振り返る",
        "mission_hint": "どちらを選んでも達成"
    },
    {
        "title": "三叉路",
        "desc": "卒業の日。校門の前の三叉路で、二人は君の返事を静かに待っている。",
        "y": "悠真「答えを急がせたくない。でも、僕の気持ちは伝えておきたい」",
        "a": "蒼「最後くらい、ちゃんと言う。君と過ごした時間、俺にとって特別だった」",
        "yr": "悠真「ありがとう。これから先も、君の隣にいられたらうれしい」",
        "ar": "蒼「よし！その返事、ずっと大事にする。これからもよろしくな！」",
        "mission": "自分の気持ちに正直になる",
        "mission_hint": "どちらを選んでも達成"
    },
]

def fresh_state():
    return {
        "chapter": 0,
        "aff": {"悠真": 0, "蒼": 0},
        "trust": {"悠真": 5, "蒼": 5},
        "last": None,
        "streak": 0,
        "missions": [],
        "history": []
    }

def load_state():
    if not os.path.exists(SAVE):
        return fresh_state()
    try:
        with open(SAVE, "r", encoding="utf-8") as f:
            data = json.load(f)
        state = fresh_state()
        state.update(data)
        for key in ("aff", "trust"):
            state[key] = {n: int(data.get(key, {}).get(n, state[key][n])) for n in NAMES}
        state["chapter"] = max(0, min(len(SCENES), int(state.get("chapter", 0))))
        return state
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        print("セーブデータを読み込めません。新しいデータで開始します。")
        return fresh_state()

def save_state(state):
    with open(SAVE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def clamp(value, low, high):
    return max(low, min(high, value))

def hearts(value, maximum):
    return "♥" * value + "♡" * (maximum - value)

def status(state):
    print("\n┏━━━━━━━━━━ 好感度・信頼度 ━━━━━━━━━━┓")
    for name in NAMES:
        print(f"┃ {name:<3} 好感度 {hearts(state['aff'][name], MAX_AFF)} {state['aff'][name]:>2}/{MAX_AFF}")
        print(f"┃     信頼度 {hearts(state['trust'][name], MAX_TRUST)} {state['trust'][name]:>2}/{MAX_TRUST}")
    print(f"┃ 任務達成：{len(state['missions'])}/{len(SCENES)}")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

def pick(options):
    while True:
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        answer = input("> ").strip()
        if answer in ("1", "2"):
            return int(answer) - 1
        print("1か2で選んでね。")

def show_gauge(state):
    total = state["aff"]["悠真"] + state["aff"]["蒼"]
    trust = state["trust"]["悠真"] + state["trust"]["蒼"]
    aff_percent = int(total / (MAX_AFF * 2) * 100)
    trust_percent = int(trust / (MAX_TRUST * 2) * 100)
    print(f"\n絆ゲージ   [{'■' * (aff_percent // 5)}{'·' * (20 - aff_percent // 5)}] {aff_percent}%")
    print(f"信頼ゲージ [{'■' * (trust_percent // 5)}{'·' * (20 - trust_percent // 5)}] {trust_percent}%")

def update_relationship(state, target):
    other = "蒼" if target == "悠真" else "悠真"
    if state["last"] == target:
        state["streak"] += 1
    else:
        state["streak"] = 1

    # 選んだ相手の好感度は上がるが、連続しすぎると信頼が揺らぐ。
    state["aff"][target] = clamp(state["aff"][target] + 2, 0, MAX_AFF)
    state["aff"][other] = clamp(state["aff"][other] - 1, 0, MAX_AFF)

    if state["streak"] >= 2:
        state["aff"][other] = clamp(state["aff"][other] - 1, 0, MAX_AFF)
        state["trust"][other] = clamp(state["trust"][other] - 1, 0, MAX_TRUST)
        print(f"\n【HARD】{other}は少し寂しそうだ……好感度 -1／信頼度 -1")

    if state["streak"] >= 3:
        state["trust"][target] = clamp(state["trust"][target] - 1, 0, MAX_TRUST)
        print(f"【HARD】{target}は「自分だけを見てほしいわけじゃない」と感じている。信頼度 -1")

    # 何度も同じ相手を選ぶほど、関係のバランスが難しくなる。
    if state["streak"] >= 4:
        state["aff"][target] = clamp(state["aff"][target] - 1, 0, MAX_AFF)
        print(f"【HARD】{target}との間にも小さなすれ違いが生まれた。好感度 -1")

    state["last"] = target

def mission_success(state, index, choice):
    # ミッションの達成条件は各話の内容に対応。
    # "自動達成"／"どちらでも" は両方、名前指定はその人物を選ぶと達成。
    hint = SCENES[index]["mission_hint"]
    if "自動達成" in hint or "どちらを選んでも" in hint or "どちらでも" in hint:
        return True
    if "悠真" in hint:
        return choice == 0
    if "蒼" in hint:
        return choice == 1
    return True

def countdown():
    print("\n―― 卒業まで、あと少し。――")
    for number in (3, 2, 1):
        print(f"              {number} ...")
        time.sleep(0.25)
    print("                 START")

def finale_song():
    # ユーザー提供の歌詞をベースに、非同意の性的暴力を肯定する表現は
    # 入れず、パロディ調のフィナーレコールに調整しています。
    lyrics = [
        "田所浩二！田所浩二！",
        "",
        "王道を征く常夏のおっさん",
        "ネットの頂点に降り立つメシア",
        "喘ぎ声で命救うビースト",
        "彼こそが我らのイエスキリスト",
        "争い絶えぬ汚れきった世界",
        "救うために修行する女神",
        "人権侵害すべて許す包容",
        "いいよ！こいよ！ 我ら包む抱擁",
        "",
        "さあ今このアイスティーを飲み干そう",
        "そして天は鳴き大地は震える",
        "聖なる伝説を受け入れ",
        "アセンションの時 彼の語録を聞け",
        "",
        "お前やりますねぇスギ",
        "田所浩二！田所浩二！",
        "お前やりますねぇスギ",
        "田所浩二！"
    ]
    print("\n" + "♪ " + " ♪ ".join(lyrics) + " ♪")

def ending(state):
    countdown()
    status(state)
    show_gauge(state)

    y, a = state["aff"]["悠真"], state["aff"]["蒼"]
    yt, at = state["trust"]["悠真"], state["trust"]["蒼"]
    missions = len(state["missions"])

    print("\n" + "═" * 48)
    print("              FINAL JUDGEMENT")
    print("═" * 48)
    time.sleep(0.3)

    if y >= 13 and a >= 13 and yt >= 7 and at >= 7 and missions >= 16:
        title = "三人の約束 TRUE END"
        lines = [
            "二人の気持ちから逃げず、どちらか一方だけに頼ることもしなかった。",
            "悠真「これからも、三人で一緒に歩いていこう」",
            "蒼「それが一番だよな！これからもよろしく！」",
            "君たちは、それぞれの想いを胸に新しい道へ進んでいく。"
        ]
        rank = "S — TRUE ROUTE"
    elif y >= 12 and yt >= 5:
        title = "悠真エンド"
        lines = [
            "悠真は少し照れながら、君の手を取った。",
            "悠真「不器用な僕だけど、これからも隣にいさせてほしい」",
            "静かな約束が、二人の新しい始まりになった。"
        ]
        rank = "A — YUMA ROUTE"
    elif a >= 12 and at >= 5:
        title = "蒼エンド"
        lines = [
            "蒼はいつもの笑顔で君の前に立った。",
            "蒼「これからも一緒に笑っていようぜ。約束だからな！」",
            "賑やかな未来へ、二人は並んで歩き出した。"
        ]
        rank = "A — AO ROUTE"
    elif y >= 8 and a >= 8 and yt >= 4 and at >= 4:
        title = "特別な未決着エンド"
        lines = [
            "二人とも大切で、今はまだ答えをひとつに決められない。",
            "悠真「答えを急がなくていい。僕たちは待っているから」",
            "蒼「その間も三人で楽しく過ごそうぜ！」",
            "三叉路の先には、まだ選んでいない未来が広がっている。"
        ]
        rank = "B — SPECIAL ROUTE"
    else:
        title = "未決着エンド"
        lines = [
            "伝えきれなかった言葉が、胸の奥に残っている。",
            "それでも、物語がここで終わるわけではない。",
            "次に会うときは、もう少し素直になれるかもしれない。"
        ]
        rank = "C — ANOTHER ROUTE"

    print("\n" + "★" * 48)
    print(f"          【 {title} 】")
    print(f"              {rank}")
    print("★" * 48)
    for line in lines:
        print(line)
        time.sleep(0.2)

    print("\n―― 最終判定 ――")
    print(f"好感度：悠真 {y}/{MAX_AFF} ／ 蒼 {a}/{MAX_AFF}")
    print(f"信頼度：悠真 {yt}/{MAX_TRUST} ／ 蒼 {at}/{MAX_TRUST}")
    print(f"任務達成：{missions}/{len(SCENES)}")
    if title == "三人の約束 TRUE END":
        print("条件達成！二人との信頼と絆が、最高の未来につながった！")
    else:
        print("TRUE END条件：両者好感度13以上・両者信頼度7以上・任務16個以上")
    finale_song()

def play():
    print("=" * 48)
    print("       君と紡ぐ三叉路 BL版・HARD MODE")
    print("=" * 48)
    state = load_state()

    if state["chapter"] > 0:
        print(f"\n第{state['chapter'] + 1}話から再開できます。")
        if pick(["続きから", "最初から"]) == 1:
            state = fresh_state()
            save_state(state)

    for i in range(state["chapter"], len(SCENES)):
        scene = SCENES[i]
        print("\n" + "━" * 48)
        print(f"第{i + 1:02d}話：{scene['title']}")
        print("━" * 48)
        print(scene["desc"])
        print(f"\n【悠真】{scene['y']}")
        print(f"【蒼】{scene['a']}")

        if random.random() < 0.35:
            print("\n【謎の語録タイム】" + random.choice(MEMES))

        print(f"\n【今回の任務】{scene['mission']}")
        print("達成ヒント：" + scene["mission_hint"])
        print("\n誰と過ごす？")
        choice = pick([f"悠真：{scene['title']}の時間を一緒に過ごす",
                       f"蒼：{scene['title']}の時間を一緒に過ごす"])
        target = NAMES[choice]

        print("\n" + (scene["yr"] if choice == 0 else scene["ar"]))
        update_relationship(state, target)

        if mission_success(state, i, choice):
            if i not in state["missions"]:
                state["missions"].append(i)
                state["trust"][target] = clamp(state["trust"][target] + 1, 0, MAX_TRUST)
            print(f"\n【任務達成】{scene['mission']}  信頼度 +1")
        else:
            print("\n【任務失敗】今回は任務を達成できなかった……")

        # 専用リアクションは各話固有。共通セリフの使い回しはしない。
        print(f"\n【HARD判定】{target}を選択")
        status(state)
        show_gauge(state)

        state["history"].append({"chapter": i + 1, "choice": target})
        state["chapter"] = i + 1
        save_state(state)

        if i < len(SCENES) - 1:
            input("\nEnterで次の話へ...")

    ending(state)
    if os.path.exists(SAVE):
        os.remove(SAVE)
    input("\nEnterで終了...")

if __name__ == "__main__":
    play()
