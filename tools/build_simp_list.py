# 要注意リスト（SIMP）の生成スクリプト
# Unicode公式のUnihanデータベースとJIS系エンコーディングを照合し、
# 「簡体字なのに日本語の名簿（JIS）に載っている字」を機械的に洗い出します。
#
# 使い方: python3 build_simp_list.py
#   （初回実行時に unicode.org から Unihan.zip 約8MB をダウンロードします）
import io
import urllib.request
import zipfile

UNIHAN_URL = "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip"

# 手動補完7字：機械照合の網にかからない中国語専用字
#   吧・哪・啊・您 = 中国語の助詞・呼びかけ（簡体字属性を持たない）
#   个・广・儿   = JIS基本名簿（第1・第2水準）に古くから収録されている中国語頻出字
MANUAL_CN = "个儿广吧哪啊您"

# 旧字体15字：AIが現代文で書いたらほぼ誤り（実運用の誤り記録から採録）
# ※人名・古典の引用を含む文章を調べる場合はこのグループを外すこと
OLD_FORMS = "假兩區收增對寢斷效疊缺續賣默圈"


def is_jis(ch):
    """日本語の「公式名簿」（JIS規格のエンコーディング）に載っている字か？"""
    for enc in ("shift_jis_2004", "euc_jis_2004", "iso2022_jp_2004"):
        try:
            ch.encode(enc)
            return True
        except Exception:
            pass
    return False


def is_jis_basic(ch):
    """JIS基本名簿（JIS X 0208＝第1・第2水準）に載っている字か？"""
    try:
        ch.encode("shift_jis")
        return True
    except Exception:
        return False


def load_simplified():
    """Unihanから「簡体字」（自分と異なる繁体字を持つ字）の集合を作る"""
    print("Unihan.zip をダウンロード中...")
    data = urllib.request.urlopen(UNIHAN_URL, timeout=60).read()
    simplified = set()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        with z.open("Unihan_Variants.txt") as f:
            for raw in f:
                line = raw.decode("utf-8").strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) < 3 or parts[1] != "kTraditionalVariant":
                    continue
                ch = chr(int(parts[0][2:], 16))
                targets = [chr(int(x[2:], 16)) for x in parts[2].split()]
                if any(t != ch for t in targets):
                    simplified.add(ch)
    return simplified


def main():
    simplified = load_simplified()
    print(f"簡体字（繁体字と字形が異なるもの）: {len(simplified)}字")

    # 簡体字 かつ JIS拡張名簿に収録 かつ 基本名簿には無い ＝ 名簿の「穴」
    machine = sorted(
        (ch for ch in simplified
         if is_jis(ch) and not is_jis_basic(ch) and ord(ch) < 0x10000),
        key=ord,
    )
    print(f"機械生成（名簿に載ってしまっている簡体字）: {len(machine)}字")

    simp_cn = "".join(sorted(set(machine) | set(MANUAL_CN), key=ord))
    old = "".join(sorted(OLD_FORMS, key=ord))
    print(f"\n中国語系（機械生成＋手動補完）: {len(simp_cn)}字")
    print(f'SIMP = set("{simp_cn}")')
    print(f"\n旧字体: {len(old)}字")
    print(f'SIMP |= set("{old}")')


if __name__ == "__main__":
    main()
