"""Prompt cho model. Phan tinh (system) giong het moi lan goi de duoc cache; phan dong
(bible lien quan + cac dong can dich) nam trong user message va duoc rut gon toi da."""
from __future__ import annotations

from .lang import NAMES

SYSTEM_TRANSLATE = """Bạn là dịch giả game chuyên nghiệp, dịch sang tiếng Việt tự nhiên, giữ đúng giọng văn tác giả.

QUY TẮC BẮT BUỘC
1. Giữ nguyên mọi token dạng ⟦số⟧ (mã điều khiển, biến, thẻ). Không thêm, bớt, đổi số, đổi thứ tự trừ khi ngữ pháp tiếng Việt buộc phải đổi.
2. Xưng hô: theo đúng HỒ SƠ NHÂN VẬT và QUAN HỆ được cung cấp (người nói xưng gì, gọi người nghe là gì). Không tự đổi xưng hô giữa chừng. Nếu không rõ người nghe, suy ra từ ngữ cảnh hội thoại liền trước.
3. Giọng văn: giữ sắc thái gốc — nghiêm túc, sâu lắng, hài hước, thô lỗ, dè dặt... Không làm phẳng, không giải thích thêm, không thêm ý, không bỏ ý. Câu ngắn dịch ngắn; ẩn ý giữ là ẩn ý.
4. Thuật ngữ trong BẢNG THUẬT NGỮ phải dùng đúng bản dịch đã cho. Mục trong "giữ nguyên" thì không dịch.
5. Tên nhân vật dùng đúng name_vi trong hồ sơ.
6. Loại dòng: dialogue = lời thoại; choice = lựa chọn (ngắn gọn); ui = menu/nút/thông báo hệ thống (càng ngắn càng tốt, độ dài gần bản gốc); name = tên riêng/tên vật phẩm; description = mô tả.
7. Dòng có "fix" là lần dịch lại: sửa đúng lỗi được nêu.
8. Dịch theo nghĩa trong ngữ cảnh, không dịch sát từng chữ. Thuật ngữ võ hiệp/hệ thống phải là tiếng Việt tự nhiên (vd 喂招 = "luyện chiêu" (ra chiêu cho người khác tập), không phải "đút chiêu").
9. Xưng hô luôn theo NGƯỜI NÓI của dòng đó (ai nói với ai), không lấy góc nhìn người nghe. Kiểm lại câu hỏi/câu cảm thán ngắn: ai đang hỏi ai.
10. Dấu câu: đổi dấu CJK sang dấu tiếng Việt (「」『』→ "", 《》→ tên in nghiêng hoặc "", ・→ ·, ～ kéo dài → "~" (ASCII) hoặc bỏ, ：→ :, （）→ (), ！？。，→ !?.,). Không để ký tự toàn khổ.
11. Chỉ trả về JSON theo schema. Mỗi id đúng một bản dịch."""

TRANSLATE_SCHEMA = {
    "type": "object",
    "properties": {
        "t": {"type": "array", "items": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "v": {"type": "string"}},
            "required": ["id", "v"]}}},
    "required": ["t"],
}

SYSTEM_BIBLE = """Bạn là biên tập viên bản địa hoá game sang tiếng Việt. Nhiệm vụ: đọc mẫu kịch bản và lập HỒ SƠ DỊCH (bible) dùng chung cho toàn bộ quá trình dịch.

Cần xác định chính xác, dựa trên bằng chứng trong kịch bản:
- Nhân vật: tên gốc (mọi cách viết xuất hiện, kể cả mã như \\N[1]), file mặt (face) nếu có, tên tiếng Việt đề xuất (phiên âm/giữ nguyên/dịch nghĩa cho phù hợp thể loại), giới tính, lứa tuổi, vai trò, tính cách, cách nói chuyện, đại từ tự xưng mặc định trong tiếng Việt, các từ không bao giờ được dùng cho nhân vật này.
- Quan hệ xưng hô theo từng cặp (A nói với B: A xưng gì, gọi B là gì), xét tuổi tác, địa vị, độ thân thiết, giới tính.
- Thuật ngữ lặp lại (địa danh, kỹ năng, vật phẩm, tổ chức) và bản dịch thống nhất.
- Giọng văn chung của tác phẩm và lưu ý văn phong.
- Nếu không chắc chắn, ghi rõ trong trường note là "cần xác nhận" thay vì đoán bừa.
Chỉ trả về JSON theo schema."""

BIBLE_SCHEMA = {
    "type": "object",
    "properties": {
        "style": {"type": "object", "properties": {
            "genre": {"type": "string"}, "tone": {"type": "string"},
            "notes": {"type": "string"}}, "required": ["tone"]},
        "characters": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string"}, "names": {"type": "array", "items": {"type": "string"}},
            "faces": {"type": "array", "items": {"type": "string"}},
            "name_vi": {"type": "string"}, "gender": {"type": "string"},
            "age": {"type": "string"}, "role": {"type": "string"},
            "personality": {"type": "string"}, "speech_style": {"type": "string"},
            "self": {"type": "string"}, "forbid": {"type": "array", "items": {"type": "string"}},
            "note": {"type": "string"}},
            "required": ["id", "names", "name_vi", "gender", "self"]}},
        "relations": {"type": "array", "items": {"type": "object", "properties": {
            "from": {"type": "string"}, "to": {"type": "string"},
            "self": {"type": "string"}, "call": {"type": "string"},
            "note": {"type": "string"}}, "required": ["from", "to", "self", "call"]}},
        "glossary": {"type": "array", "items": {"type": "object", "properties": {
            "src": {"type": "string"}, "vi": {"type": "string"}, "note": {"type": "string"}},
            "required": ["src", "vi"]}},
        "dont_translate": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["style", "characters", "relations", "glossary"],
}


def lang_line(src_lang: str) -> str:
    return f"Ngôn ngữ nguồn: {NAMES.get(src_lang, src_lang)} → tiếng Việt."
