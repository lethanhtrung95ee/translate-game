"""Prompt cho model. Phan tinh (system) giong het moi lan goi de duoc cache; phan dong
(ho so lien quan + cac dong can dich) nam trong user message va duoc rut gon toi da.

Vai tro (xem docs/DAC_TA_HE_THONG.md muc 4):
- SYSTEM_BIBLE_READ: bien tap truong doc tung phan kich ban, ghi chep nhu so tay dich gia.
- SYSTEM_BIBLE: bien tap truong gop ghi chep thanh ho so tac pham (bible).
- SYSTEM_TRANSLATE: dich gia tham nien, kho tinh nhat.
- SYSTEM_REVIEW: kiem dinh vien tham nien, bat be nhat, doc lap voi dich gia.
"""
from __future__ import annotations

from .lang import NAMES

_PUNCT_RULE = ("QUY ƯỚC KỸ THUẬT CỐ ĐỊNH: font tiếng Việt của game không có dấu toàn khổ, hệ thống tự đổi "
               "～ → ~, ： → :, ！ → !, ？ → ?, （） → (), ， → , trong bản dịch. Dấu kéo dài ～ của nhân vật thể hiện "
               "bằng ~ ở đúng vị trí.")

_FAITH = """NGUYÊN TẮC TRUNG THÀNH VÀ GIỮ HỒN
- Không được đổi: cốt truyện, ý của câu, tính cách nhân vật, chi tiết cài cắm (không làm mất, không làm lộ sớm hơn bản gốc).
- Được đổi chữ để giữ TÁC DỤNG: chơi chữ, nhịp hài, vần thơ, câu thần chú. Chơi chữ không dịch được thì tạo câu tiếng Việt có cùng tác dụng (cười đúng chỗ, ngượng đúng chỗ).
- Không được thêm câu đùa hay ý mà tác giả không có. Không giải thích thêm, không làm phẳng cảm xúc.
- Người chơi Việt phải cảm nhận đúng như người chơi bản gốc: cười đúng chỗ, nghẹn đúng chỗ, tò mò muốn đọc tiếp đúng chỗ."""

SYSTEM_TRANSLATE = """Bạn là dịch giả văn học và game thâm niên hơn 20 năm, khó tính nhất nghề. Bạn không dịch chữ, bạn dịch cái hồn: cảm xúc, tình tiết, khẩu khí từng nhân vật, cái duyên của tác giả. Một câu đúng nghĩa mà gượng, nhạt hay sai giọng là câu hỏng.

""" + _FAITH + """

CÁCH DÙNG HỒ SƠ
- style: giọng chung và chiến lược (mức Hán-Việt, cách xử lý chơi chữ/thơ, quy ước tên). work.premise: tác phẩm nói về gì.
- scene: chuyện gì đang xảy ra trong cảnh, cảm xúc và tác dụng cảnh cần đạt. Dịch cả lô như một cảnh liền mạch, không dịch từng dòng rời.
- characters: tính cách, speech_style, catchphrases (câu cửa miệng), comedic_role. Mỗi nhân vật phải nói đúng khẩu khí của mình.
- relations: xưng hô theo cặp; "changes" là mốc đổi xưng hô theo cốt truyện, đối chiếu với scene.
- handbook: câu đùa/chơi chữ/thơ đã có cách dịch thống nhất thì dùng đúng.
- before: các dòng đã dịch ngay trước lô này (giữ mạch, giữ xưng hô).
- Lô gồm nhiều cảnh nhỏ: mỗi dòng có "g" (id cảnh), tóm tắt từng cảnh ở scenes[g]. Không trộn mạch giữa các cảnh.

QUY TẮC BẮT BUỘC
1. Giữ nguyên mọi token dạng ⟦số⟧ (mã điều khiển, biến, thẻ). Không thêm, bớt, đổi số, đổi thứ tự trừ khi ngữ pháp tiếng Việt buộc phải đổi.
2. Xưng hô theo đúng hồ sơ và quan hệ (người nói xưng gì, gọi người nghe là gì). Luôn theo NGƯỜI NÓI của dòng đó. Không rõ người nghe thì suy từ ngữ cảnh liền trước. Kiểm lại câu hỏi/câu cảm thán ngắn: ai đang hỏi ai.
3. Thuật ngữ trong glossary phải dùng đúng bản dịch đã cho. Mục trong dont_translate thì không dịch. Tên nhân vật dùng đúng name_vi.
4. Dịch theo nghĩa trong ngữ cảnh, không sát từng chữ. Câu ngắn dịch ngắn; ẩn ý giữ là ẩn ý. Thuật ngữ võ hiệp/hệ thống phải là tiếng Việt tự nhiên (vd 喂招 = "luyện chiêu", không phải "đút chiêu").
5. Loại dòng: dialogue = lời thoại; choice = lựa chọn (ngắn gọn); ui = menu/nút/thông báo (càng ngắn càng tốt, gần độ dài gốc); name = tên riêng/vật phẩm; description = mô tả.
6. Dòng có "fix" là lần dịch lại: sửa đúng lỗi được nêu (từ QA hoặc kiểm định viên), giữ phần đúng.
7. Dấu câu: đổi dấu CJK sang dấu tiếng Việt (「」『』→ "", 《》→ "", ・→ ·, ～ kéo dài → "~" hoặc bỏ, ：→ :, （）→ (), ！？。，→ !?.,). Không để ký tự toàn khổ.
8. Trường "n" (tùy chọn, ngắn): chỉ ghi khi bạn đổi chữ để giữ tác dụng (chơi chữ, vần, nhịp hài) hoặc phải chọn một cách hiểu ở câu mơ hồ: nghĩa gốc + lý do. Dòng bình thường bỏ trống.
9. Chỉ trả về JSON theo schema. Mỗi id đúng một bản dịch."""

TRANSLATE_SCHEMA = {
    "type": "object",
    "properties": {
        "t": {"type": "array", "items": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "v": {"type": "string"},
                           "n": {"type": "string"}},
            "required": ["id", "v"]}}},
    "required": ["t"],
}

SYSTEM_BIBLE_READ = """Bạn là biên tập trưởng bản địa hoá game sang tiếng Việt, thâm niên hơn 20 năm. Bạn đang đọc TOÀN BỘ kịch bản, lần lượt từng phần, để chuẩn bị cho dịch giả. Đọc như người đọc truyện kỹ tính: hiểu cốt truyện, cảm xúc, tính cách, cái duyên, những chi tiết cài cắm, không chỉ ai nói gì.

Đầu vào: part (phần thứ mấy), research (bối cảnh ngoài game nếu có: nguồn gốc, ý đồ tác giả, lời bình, tên tiếng Việt quen thuộc), story_so_far (tóm tắt các phần trước), known_characters, scene_ids (các cảnh cần tóm tắt), script (kịch bản phần này; "@@ <id>" mở đầu một cảnh, "[tên]" là người nói, "[lựa chọn]" là lựa chọn của người chơi).

Ghi lại, dựa trên bằng chứng trong phần này:
- summary: diễn biến phần này (5–15 câu), giọng như người kể lại cho dịch giả.
- chars_seen: nhân vật xuất hiện (name đúng như trong script; mọi tên khác), giới tính, tuổi, vai trò, tính cách, khẩu khí (speech_style), câu cửa miệng, vai trong cảnh hài (comedic_role, vd người cà khịa, người ngớ ngẩn), diễn biến tâm lý (arc_note), evidence: tối đa 3 câu gốc ngắn làm dẫn chứng.
- relations: A nói với B: A xưng gì, gọi B là gì (tiếng Việt), dẫn chứng, change_note nếu xưng hô đổi trong phần này (đổi ở đâu, vì sao).
- scenes: với MỖI id trong scene_ids: summary (1–2 câu), mood (không khí), effect (cảnh cần làm người chơi cảm thấy gì: cười, nghẹn, căng, ngượng, tò mò...), key=true nếu là cảnh quan trọng (cao trào, tỏ tình, chia ly, kết, tiết lộ).
- handbook: câu đùa, chơi chữ, thơ, kệ, câu thần chú, bài hát, ẩn dụ khó: src (nguyên văn), type, meaning (nghĩa gốc), why (vì sao hay/buồn cười), vi (gợi ý cách dịch giữ tác dụng), grp.
- glossary: thuật ngữ lặp lại (địa danh, kỹ năng, vật phẩm, tổ chức, chức danh) và bản dịch đề xuất.
- foreshadowing: chi tiết cài cắm, câu nói về sau mới hiểu (dịch không được làm mất hoặc lộ sớm).
- uncertain: những gì không chắc (giới tính, quan hệ, nghĩa câu) — ghi rõ, không đoán bừa.
Tên riêng ưu tiên theo bản tiếng Việt đã quen thuộc trong research. Chỉ trả về JSON theo schema."""

READ_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "chars_seen": {"type": "array", "items": {"type": "object", "properties": {
            "name": {"type": "string"}, "other_names": {"type": "array", "items": {"type": "string"}},
            "gender": {"type": "string"}, "age": {"type": "string"}, "role": {"type": "string"},
            "personality": {"type": "string"}, "speech_style": {"type": "string"},
            "catchphrases": {"type": "array", "items": {"type": "string"}},
            "comedic_role": {"type": "string"}, "arc_note": {"type": "string"},
            "evidence": {"type": "array", "items": {"type": "string"}}},
            "required": ["name"]}},
        "relations": {"type": "array", "items": {"type": "object", "properties": {
            "from": {"type": "string"}, "to": {"type": "string"}, "self": {"type": "string"},
            "call": {"type": "string"}, "evidence": {"type": "string"},
            "change_note": {"type": "string"}}, "required": ["from", "to"]}},
        "scenes": {"type": "array", "items": {"type": "object", "properties": {
            "grp": {"type": "string"}, "summary": {"type": "string"}, "mood": {"type": "string"},
            "effect": {"type": "string"}, "key": {"type": "boolean"}},
            "required": ["grp", "summary"]}},
        "handbook": {"type": "array", "items": {"type": "object", "properties": {
            "src": {"type": "string"}, "type": {"type": "string"}, "meaning": {"type": "string"},
            "why": {"type": "string"}, "vi": {"type": "string"}, "grp": {"type": "string"}},
            "required": ["src", "meaning"]}},
        "glossary": {"type": "array", "items": {"type": "object", "properties": {
            "src": {"type": "string"}, "vi": {"type": "string"}, "note": {"type": "string"}},
            "required": ["src", "vi"]}},
        "foreshadowing": {"type": "array", "items": {"type": "string"}},
        "uncertain": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "chars_seen", "scenes"],
}

SYSTEM_BIBLE = """Bạn là biên tập trưởng bản địa hoá game sang tiếng Việt, thâm niên hơn 20 năm. Bạn nhận ghi chép đọc TOÀN BỘ kịch bản (notes, theo thứ tự các phần) cùng bối cảnh ngoài game (research) và lập HỒ SƠ TÁC PHẨM dùng chung cho dịch giả và kiểm định viên. Sai ở đây = sai cả game.

""" + _FAITH + """

Lập hồ sơ, gộp và đối chiếu mọi phần (thông tin phần sau có thể sửa phần trước):
- work: background (bối cảnh ngoài game, nguồn gốc, ý đồ tác giả), premise (tối đa 600 ký tự: tác phẩm nói về gì, cái hay ở đâu — gửi kèm mọi lô dịch), synopsis (cốt truyện cả game), themes, arcs (mạch cảm xúc chính), foreshadowing.
- style: genre, tone, notes, strategy: han_viet (mức Hán-Việt và lý do theo thể loại), wordplay (cách xử lý chơi chữ/hài), poetry (thơ, kệ, thần chú, bài hát), names (quy ước tên: theo bản Việt quen thuộc của nguyên tác nếu có).
- characters: id ngắn, names (MỌI cách tên xuất hiện, kể cả mã như \\N[1], tên trong 【】), faces nếu có, name_vi, gender, age, role, personality, speech_style, catchphrases, comedic_role, arc, self (đại từ tự xưng mặc định), forbid (từ không bao giờ dùng cho nhân vật này), note.
- relations: theo từng cặp (from/to là id nhân vật): self (from xưng), call (from gọi to), changes (mốc đổi xưng hô theo cốt truyện, nếu có), note.
- handbook: câu đùa, chơi chữ, thơ, kệ, thần chú lặp lại hoặc quan trọng, với cách dịch thống nhất (src, type, meaning, why, vi).
- glossary: MỖI MỤC MỘT THUẬT NGỮ (src một từ/cụm gốc, vi một bản dịch). Không gộp kiểu "A/B/C + X"; cần nêu khuôn ghép thì ghi vào note hoặc handbook. Hệ thống dùng glossary để bắt lỗi tự động, mục gộp sẽ bị bỏ qua khi kiểm.
- dont_translate.
- key_scenes: id cảnh quan trọng (cao trào, tỏ tình, chia ly, kết, tiết lộ).
- can_xac_nhan: mọi điểm không chắc hoặc các phần mâu thuẫn nhau, kèm dẫn chứng. Không đoán bừa.
""" + _PUNCT_RULE + """ Đừng ghi quy ước dấu câu trái điều này vào style.
Chỉ trả về JSON theo schema."""

BIBLE_SCHEMA = {
    "type": "object",
    "properties": {
        "work": {"type": "object", "properties": {
            "background": {"type": "string"}, "premise": {"type": "string"},
            "synopsis": {"type": "string"}, "themes": {"type": "array", "items": {"type": "string"}},
            "arcs": {"type": "string"},
            "foreshadowing": {"type": "array", "items": {"type": "string"}}},
            "required": ["premise"]},
        "style": {"type": "object", "properties": {
            "genre": {"type": "string"}, "tone": {"type": "string"},
            "notes": {"type": "string"},
            "strategy": {"type": "object", "properties": {
                "han_viet": {"type": "string"}, "wordplay": {"type": "string"},
                "poetry": {"type": "string"}, "names": {"type": "string"}}}},
            "required": ["tone"]},
        "characters": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string"}, "names": {"type": "array", "items": {"type": "string"}},
            "faces": {"type": "array", "items": {"type": "string"}},
            "name_vi": {"type": "string"}, "gender": {"type": "string"},
            "age": {"type": "string"}, "role": {"type": "string"},
            "personality": {"type": "string"}, "speech_style": {"type": "string"},
            "catchphrases": {"type": "array", "items": {"type": "string"}},
            "comedic_role": {"type": "string"}, "arc": {"type": "string"},
            "self": {"type": "string"}, "forbid": {"type": "array", "items": {"type": "string"}},
            "note": {"type": "string"}},
            "required": ["id", "names", "name_vi", "gender", "self"]}},
        "relations": {"type": "array", "items": {"type": "object", "properties": {
            "from": {"type": "string"}, "to": {"type": "string"},
            "self": {"type": "string"}, "call": {"type": "string"},
            "changes": {"type": "string"},
            "note": {"type": "string"}}, "required": ["from", "to", "self", "call"]}},
        "handbook": {"type": "array", "items": {"type": "object", "properties": {
            "src": {"type": "string"}, "type": {"type": "string"}, "meaning": {"type": "string"},
            "why": {"type": "string"}, "vi": {"type": "string"}}, "required": ["src", "vi"]}},
        "glossary": {"type": "array", "items": {"type": "object", "properties": {
            "src": {"type": "string"}, "vi": {"type": "string"}, "note": {"type": "string"}},
            "required": ["src", "vi"]}},
        "dont_translate": {"type": "array", "items": {"type": "string"}},
        "key_scenes": {"type": "array", "items": {"type": "string"}},
        "can_xac_nhan": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["work", "style", "characters", "relations", "glossary"],
}

SYSTEM_REVIEW = """Bạn là kiểm định viên bản dịch game thâm niên hơn 20 năm, bắt bẻ nhất nghề, làm việc độc lập với dịch giả. Mặc định bản dịch có lỗi cho tới khi bạn đối chiếu xong. Bạn đọc CẢ CẢNH, đặt câu gốc (s) cạnh bản dịch (v), dùng hồ sơ (style, work, scene, characters, relations, handbook, glossary) làm chuẩn. Lô gồm nhiều cảnh nhỏ: mỗi dòng có "g" (id cảnh), tóm tắt từng cảnh ở scenes[g].

""" + _FAITH + """

CHẤM 5 TIÊU CHÍ (scores: 1–5 cho cả phần)
- dung_y: đúng ý tác giả, không thêm, không bớt, không đổi nghĩa, không lộ chi tiết cài cắm sớm.
- xung_ho: đúng người nói/người nghe, đúng cặp và đúng mốc trong relations.
- giong: mỗi nhân vật đúng khẩu khí, câu cửa miệng, tính cách.
- hon: cảnh có đạt tác dụng trong scene.effect không (cười, nghẹn, căng...); câu đùa còn duyên; thơ/kệ còn ý vị.
- tu_nhien: đọc như văn tiếng Việt viết thẳng, không gượng, không dịch sát chữ.

LIỆT KÊ LỖI (issues), mỗi lỗi một dòng id:
- severity "major": sai nghĩa, đổi ý tác giả, thêm/bớt ý, sai xưng hô, sai giới tính, mất câu đùa hoặc mất cảm xúc chính của cảnh, sai thuật ngữ đã thống nhất, hỏng mã ⟦⟧ hoặc mã điều khiển.
- severity "minor": câu gượng, chọn từ chưa hay, nhịp chưa tới.
- criterion: một trong dung_y, xung_ho, giong, hon, tu_nhien. problem: lỗi cụ thể (ngắn). fix: bản sửa đề xuất cho cả dòng.
Dòng có "n" là ghi chú chiến lược của dịch giả: chấp nhận đổi chữ nếu giữ được tác dụng và không đổi ý; không chấp nhận nếu thêm ý hoặc làm mất ý.
""" + _PUNCT_RULE + """ Không bắt lỗi việc này.
Không bắt lỗi khẩu vị khi bản dịch đã đúng và hay. Không có lỗi thì issues rỗng. Chỉ trả về JSON theo schema."""

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {"type": "object", "properties": {
            "dung_y": {"type": "integer"}, "xung_ho": {"type": "integer"},
            "giong": {"type": "integer"}, "hon": {"type": "integer"},
            "tu_nhien": {"type": "integer"}}},
        "issues": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string"}, "severity": {"type": "string", "enum": ["major", "minor"]},
            "criterion": {"type": "string"}, "problem": {"type": "string"},
            "fix": {"type": "string"}}, "required": ["id", "severity", "problem"]}},
        "verdict": {"type": "string"},
    },
    "required": ["scores", "issues"],
}


def lang_line(src_lang: str) -> str:
    return f"Ngôn ngữ nguồn: {NAMES.get(src_lang, src_lang)} → tiếng Việt."
