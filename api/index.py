from typing import Literal
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from koi10 import SCENES, NAMES, MAX_AFF, MAX_TRUST, MEMES, fresh_state, clamp, mission_success, update_relationship

app = FastAPI(title="君と紡ぐ三叉路 API", version="1.0.0")

class ChoiceInput(BaseModel):
    chapter: int = Field(ge=0, lt=len(SCENES))
    choice: Literal[0, 1]
    state: dict

@app.get("/game")
def game_info():
    return {"title": "君と紡ぐ三叉路 BL版・HARD MODE", "chapters": len(SCENES)}

@app.get("/scene/{chapter}")
def get_scene(chapter: int):
    if chapter < 0 or chapter >= len(SCENES):
        raise HTTPException(status_code=404, detail="この話は見つかりません")
    scene = SCENES[chapter]
    return {
        "chapter": chapter,
        "title": scene["title"],
        "desc": scene["desc"],
        "y": scene["y"],
        "a": scene["a"],
        "mission": scene["mission"],
        "mission_hint": scene["mission_hint"],
        "meme": random.choice(MEMES) if random.random() < 0.35 else None,
    }

@app.post("/choose")
def choose(data: ChoiceInput):
    state = fresh_state()
    incoming = data.state or {}
    for key in ("chapter", "last", "streak", "missions", "history"):
        if key in incoming:
            state[key] = incoming[key]
    for key in ("aff", "trust"):
        values = incoming.get(key, {})
        state[key] = {name: clamp(int(values.get(name, state[key][name])), 0,
                                  MAX_AFF if key == "aff" else MAX_TRUST)
                      for name in NAMES}
    state["chapter"] = max(0, min(len(SCENES), int(state["chapter"])))
    if state["chapter"] != data.chapter:
        raise HTTPException(status_code=409, detail="セーブデータと話数が一致しません。画面を再読み込みしてください。")

    target = NAMES[data.choice]
    other = NAMES[1 - data.choice]
    scene = SCENES[data.chapter]
    update_relationship(state, target)
    completed = mission_success(state, data.chapter, data.choice)
    if completed and data.chapter not in state["missions"]:
        state["missions"].append(data.chapter)
        state["trust"][target] = clamp(state["trust"][target] + 1, 0, MAX_TRUST)

    state["history"].append({"chapter": data.chapter + 1, "choice": target})
    state["chapter"] = data.chapter + 1
    state["missions"] = state["missions"][-len(SCENES):]

    result = {
        "state": state,
        "target": target,
        "reaction": scene["yr"] if data.choice == 0 else scene["ar"],
        "mission_completed": completed,
        "hard_note": None,
    }
    if state["streak"] >= 2:
        result["hard_note"] = f"{other}は少し寂しそうだ……"
    if state["chapter"] == len(SCENES):
        y, a = state["aff"]["悠真"], state["aff"]["蒼"]
        yt, at = state["trust"]["悠真"], state["trust"]["蒼"]
        missions = len(state["missions"])
        if y >= 13 and a >= 13 and yt >= 7 and at >= 7 and missions >= 16:
            ending = ("三人の約束 TRUE END", "S — TRUE ROUTE",
                      "二人の気持ちを大切にしながら歩んだ、三人の新しい未来。")
        elif y >= 12 and yt >= 5:
            ending = ("悠真エンド", "A — YUMA ROUTE",
                      "悠真「不器用な僕だけど、これからも隣にいさせてほしい」")
        elif a >= 12 and at >= 5:
            ending = ("蒼エンド", "A — AO ROUTE",
                      "蒼「これからも一緒に笑っていようぜ。約束だからな！」")
        elif y >= 8 and a >= 8 and yt >= 4 and at >= 4:
            ending = ("特別な未決着エンド", "B — SPECIAL ROUTE",
                      "今はまだ答えをひとつに決められない。三叉路の先には、まだ未来が広がっている。")
        else:
            ending = ("未決着エンド", "C — ANOTHER ROUTE",
                      "伝えきれなかった言葉が残っている。それでも物語がここで終わるわけではない。")
        result["ending"] = {"title": ending[0], "rank": ending[1], "text": ending[2]}
    return result
