# ニセ漢字チェッカー（コピペで動きます・Python標準機能だけ使用）
# 使い方: python3 nise_kanji_check.py 調べたいファイル.txt
import sys

def is_japanese(ch):
    """日本語の「公式名簿」（JIS規格のエンコーディング）に載っている字か？"""
    for enc in ("shift_jis_2004", "euc_jis_2004", "iso2022_jp_2004"):
        try:
            ch.encode(enc)
            return True
        except Exception:
            pass
    return False

# 要注意リスト1：中国語専用なのにJISの名簿に載っている105字（Unicode公式データとの照合で機械生成）
SIMP = set("䉤两个丰么众伙佣俦儿关养减凑划刘匀叠吓吧吨启吴呕响哪啊园囱圣垩壳复娄宁岭巩帘帮广开异您惊惮扑撑极构柜栾橱欤殁毡汹沄沟沪泻洼涂渗灵灶灾烬猬瓯疴瘘瞩确离种窑笔筹籼糇肤胶脍腊腭荣蔂虬蜡蝼衅袜踌蹰达迁运适阳阴隽霉霡鼗鼹")
# 要注意リスト2：旧字体15字（AIが現代文で書いたらほぼ誤り）
# ※人名・古典の引用を含む文章を調べるときは、次の1行を消してください
SIMP |= set("假兩區圈增寢對收效斷疊續缺賣默")

def check(text):
    found = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for ch in line:
            if not ("一" <= ch <= "鿿" or "㐀" <= ch <= "䶿"):
                continue  # 漢字でなければ対象外
            if (not is_japanese(ch)) or ch in SIMP:
                found.append((lineno, ch, line.strip()[:30]))
    return found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 nise_kanji_check.py 調べたいファイル.txt"); sys.exit(1)
    text = open(sys.argv[1], encoding="utf-8").read()
    hits = check(text)
    if not hits:
        print("ニセ漢字は見つかりませんでした（※現在の手段では未検出、の意味です）")
    for lineno, ch, ctx in hits:
        print(f"{lineno}行目: 「{ch}」 ← この行にあります: {ctx}")
