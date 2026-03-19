import json
import urllib.request
import urllib.parse
import re
import os
from bs4 import BeautifulSoup

HTML_FILE = 'index.html'

def fetch_lotto_naver(draw_no):
    url = f"https://search.naver.com/search.naver?query={urllib.parse.quote(str(draw_no) + '회로또')}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            title_elem = soup.select_one('a._text')
            if not title_elem:
                return None
                
            match = re.search(r'(\d+)회차\s*\((.*?)\)', title_elem.text)
            if not match: return None
            
            page_draw_no = int(match.group(1))
            if page_draw_no != draw_no:
                # 미래 회차 검색 시 네이버가 가장 최신 회차를 보여주므로 걸러냅니다.
                return None
                
            date_str = match.group(2).strip('.')
            
            balls = soup.find_all('span', class_=re.compile('ball'))
            if len(balls) < 7: return None
            
            numbers = sorted([int(b.text) for b in balls[:6]])
            bonus = int(balls[6].text)
            
            return {
                "draw": draw_no,
                "date": date_str,
                "numbers": numbers,
                "bonus": bonus
            }
    except Exception as e:
        print(f"Error fetching draw {draw_no} from Naver: {e}")
        return None

def update_html():
    if not os.path.exists(HTML_FILE):
        print(f"{HTML_FILE} 파일을 찾을 수 없습니다!")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # EMBEDDED_RAW 탐색
    match = re.search(r'const\s+EMBEDDED_RAW\s*=\s*(\[.*?\]);', content, re.DOTALL)
    if not match:
        print("index.html 내에서 EMBEDDED_RAW 배열을 찾을 수 없습니다.")
        return

    raw_json_str = match.group(1)
    try:
        embedded_data = json.loads(raw_json_str)
    except Exception as e:
        print("EMBEDDED_RAW 파싱 중 오류 발생:", e)
        return

    if not embedded_data:
        print("EMBEDDED_RAW가 비어있습니다.")
        return

    last_draw = embedded_data[-1][0]
    print(f"현재 HTML에 저장된 최신 회차: {last_draw}회")

    new_draws = []
    current = last_draw + 1
    
    print("신규 회차 데이터를 네이버 검색을 통해 확인 중입니다...")
    while True:
        draw_data = fetch_lotto_naver(current)
        if draw_data:
            date_str = draw_data["date"].replace("-", ".")
            print(f"새로운 당첨 번호 발견: {current}회 ({date_str})")
            
            new_row = [
                draw_data["draw"],
                date_str,
                *draw_data["numbers"],
                draw_data["bonus"]
            ]
            
            new_draws.append(new_row)
            embedded_data.append(new_row)
            current += 1
        else:
            break

    if new_draws:
        new_json_str = json.dumps(embedded_data, separators=(',', ':'))
        new_content = content.replace(match.group(0), f'const EMBEDDED_RAW = {new_json_str};')
        
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"\n성공적으로 {len(new_draws)}개의 신규 회차를 추가하여 {HTML_FILE} 파일을 갱신했습니다!")
    else:
        print("\n추가할 신규 회차가 없습니다. (이미 최신 상태입니다)")

if __name__ == '__main__':
    update_html()
