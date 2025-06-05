import subprocess
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dateutil import parser
import pytz
from config import (
    DEFAULT_CALENDAR_NAME, 
    DEFAULT_EVENT_DURATION, 
    DEFAULT_EVENT_START_TIME,
    APPLESCRIPT_DATE_FORMAT
)


class CalendarTools:
    """macOS 캘린더와 상호작용하는 도구 클래스"""
    
    def __init__(self, calendar_name: str = DEFAULT_CALENDAR_NAME):
        self.calendar_name = calendar_name
        self.timezone = pytz.timezone('Asia/Seoul')
    
    def _run_applescript(self, script: str) -> str:
        """AppleScript를 실행하고 결과를 반환합니다."""
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"AppleScript 실행 오류: {e.stderr}")
    
    def _parse_korean_date(self, date_str: str) -> datetime:
        """한국어 날짜 표현을 파싱합니다."""
        import re
        
        # 현재 연도 기준
        current_year = datetime.now().year
        
        # 월, 일 추출
        month_match = re.search(r'(\d+)월', date_str)
        day_match = re.search(r'(\d+)일', date_str)
        
        if month_match and day_match:
            month = int(month_match.group(1))
            day = int(day_match.group(1))
            
            # 시간 정보가 있는지 확인
            time_match = re.search(r'(\d{1,2}):(\d{2})', date_str)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
            else:
                # 오후/오전 시간 처리
                afternoon_match = re.search(r'오후\s*(\d{1,2})시', date_str)
                morning_match = re.search(r'오전\s*(\d{1,2})시', date_str)
                hour_match = re.search(r'(\d{1,2})시', date_str)
                
                if afternoon_match:
                    hour = int(afternoon_match.group(1))
                    if hour != 12:  # 오후 12시는 12시 그대로
                        hour += 12
                    minute = 0
                elif morning_match:
                    hour = int(morning_match.group(1))
                    if hour == 12:  # 오전 12시는 0시
                        hour = 0
                    minute = 0
                elif hour_match:
                    hour = int(hour_match.group(1))
                    minute = 0
                else:
                    # 기본 시간 설정
                    hour, minute = map(int, DEFAULT_EVENT_START_TIME.split(':'))
            
            return datetime(current_year, month, day, hour, minute)
        
        # 일반적인 날짜 파싱 시도 (연도 보정)
        try:
            parsed_date = parser.parse(date_str)
            # 연도가 현재 연도와 다르면 현재 연도로 변경
            if parsed_date.year != current_year:
                parsed_date = parsed_date.replace(year=current_year)
            return parsed_date
        except:
            raise ValueError(f"날짜 파싱 실패: {date_str}")
    
    def _format_applescript_date(self, dt: datetime) -> str:
        """AppleScript에서 사용할 날짜 형식으로 변환합니다."""
        # 영어 요일 매핑 (macOS AppleScript는 영어 요일명을 사용)
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday = weekdays[dt.weekday()]
        
        # AppleScript가 인식할 수 있는 형식으로 변경
        return f"{weekday}, {dt.month}/{dt.day}/{dt.year} {dt.hour:02d}:{dt.minute:02d}:00"
    
    def create_event(self, date_str: str, title: str, time_str: Optional[str] = None, 
                    duration_minutes: int = DEFAULT_EVENT_DURATION) -> Dict[str, Any]:
        """캘린더에 새 일정을 생성합니다."""
        try:
            # 날짜 파싱
            if time_str:
                full_date_str = f"{date_str} {time_str}"
            else:
                full_date_str = date_str
            
            start_dt = self._parse_korean_date(full_date_str)
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            # AppleScript에서 날짜를 직접 생성하는 방식 사용
            script = f'''
            tell application "Calendar"
                tell calendar "{self.calendar_name}"
                    set startDate to (current date)
                    set year of startDate to {start_dt.year}
                    set month of startDate to {start_dt.month}
                    set day of startDate to {start_dt.day}
                    set hours of startDate to {start_dt.hour}
                    set minutes of startDate to {start_dt.minute}
                    set seconds of startDate to 0
                    
                    set endDate to (current date)
                    set year of endDate to {end_dt.year}
                    set month of endDate to {end_dt.month}
                    set day of endDate to {end_dt.day}
                    set hours of endDate to {end_dt.hour}
                    set minutes of endDate to {end_dt.minute}
                    set seconds of endDate to 0
                    
                    make new event at end with properties {{summary:"{title}", start date:startDate, end date:endDate}}
                end tell
            end tell
            '''
            
            self._run_applescript(script)
            
            return {
                "success": True,
                "message": f"'{title}' 일정을 {start_dt.strftime('%Y년 %m월 %d일 %H:%M')}에 추가했습니다.",
                "event": {
                    "title": title,
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"일정 생성 실패: {str(e)}",
                "error": str(e)
            }
    
    def get_events(self, date_str: Optional[str] = None, keywords: Optional[str] = None, 
                   months_range: int = 1) -> Dict[str, Any]:
        """캘린더에서 일정을 조회합니다."""
        try:
            # 모든 캘린더에서 검색하도록 수정
            calendar_names = ["캘린더", "Home", "홈", "Work", "집", "직장"]
            all_events = []
            
            # 기본 날짜 범위 설정 (현재 날짜 기준 전후 months_range 개월)
            today = datetime.now()
            if date_str:
                # 특정 날짜가 지정된 경우
                target_date = self._parse_korean_date(date_str)
                start_of_day = target_date.replace(hour=0, minute=0, second=0)
                end_of_day = target_date.replace(hour=23, minute=59, second=59)
                search_start = start_of_day
                search_end = end_of_day
            else:
                # 날짜가 지정되지 않은 경우 기본 범위 설정
                # 현재 날짜 기준 1개월 전부터 1개월 후까지
                search_start = today.replace(day=1) - timedelta(days=30 * months_range)
                search_end = today + timedelta(days=30 * months_range)
            
            for calendar_name in calendar_names:
                try:
                    # 날짜 범위를 적용한 검색
                    script = f'''
                    tell application "Calendar"
                        try
                            tell calendar "{calendar_name}"
                                set startDate to (current date)
                                set year of startDate to {search_start.year}
                                set month of startDate to {search_start.month}
                                set day of startDate to {search_start.day}
                                set hours of startDate to {search_start.hour}
                                set minutes of startDate to {search_start.minute}
                                set seconds of startDate to {search_start.second}
                                
                                set endDate to (current date)
                                set year of endDate to {search_end.year}
                                set month of endDate to {search_end.month}
                                set day of endDate to {search_end.day}
                                set hours of endDate to {search_end.hour}
                                set minutes of endDate to {search_end.minute}
                                set seconds of endDate to {search_end.second}
                                
                                set eventList to every event whose start date ≥ startDate and start date ≤ endDate
                                set eventInfo to {{}}
                                repeat with anEvent in eventList
                                    set eventTitle to (summary of anEvent)
                                    set eventStart to (start date of anEvent) as string
                                    set eventEnd to (end date of anEvent) as string
                                    set end of eventInfo to eventTitle & "|||" & eventStart & "|||" & eventEnd
                                end repeat
                                return eventInfo as string
                            end tell
                        on error
                            return ""
                        end try
                    end tell
                    '''
                    
                    result = self._run_applescript(script)
                    
                    # 결과 파싱
                    if result and result.strip():
                        event_strings = result.split(', ')
                        for event_str in event_strings:
                            if '|||' in event_str:
                                parts = event_str.split('|||')
                                if len(parts) >= 3:
                                    all_events.append({
                                        "title": parts[0].strip(),
                                        "start_time": parts[1].strip(),
                                        "end_time": parts[2].strip(),
                                        "calendar": calendar_name
                                    })
                            elif event_str.strip():
                                # 구분자가 없는 경우 제목만 있는 것으로 처리
                                all_events.append({
                                    "title": event_str.strip(),
                                    "start_time": "시간 정보 없음",
                                    "end_time": "시간 정보 없음",
                                    "calendar": calendar_name
                                })
                except Exception:
                    # 캘린더가 없거나 접근할 수 없는 경우 무시
                    continue
            
            # 키워드 필터링
            if keywords:
                all_events = [e for e in all_events if keywords.lower() in e["title"].lower()]
            
            # 날짜순 정렬 (시간 정보가 있는 경우)
            def sort_key(event):
                try:
                    if "시간 정보 없음" not in event["start_time"]:
                        # 한국어 날짜 문자열을 파싱하여 정렬
                        return event["start_time"]
                    return "9999-12-31"  # 시간 정보가 없는 경우 마지막에 정렬
                except:
                    return "9999-12-31"
            
            all_events.sort(key=sort_key)
            
            # 검색 범위 정보 추가
            range_info = ""
            if not date_str:
                range_info = f" (검색 범위: {search_start.strftime('%Y년 %m월 %d일')} ~ {search_end.strftime('%Y년 %m월 %d일')})"
            
            return {
                "success": True,
                "message": f"{len(all_events)}개의 일정을 찾았습니다.{range_info}",
                "events": all_events,
                "search_range": {
                    "start": search_start.isoformat(),
                    "end": search_end.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"일정 조회 실패: {str(e)}",
                "error": str(e)
            }
    
    def update_event(self, original_title: str, new_date_str: Optional[str] = None, 
                    new_time_str: Optional[str] = None, new_title: Optional[str] = None) -> Dict[str, Any]:
        """기존 일정을 수정합니다."""
        try:
            # 먼저 기존 일정 찾기
            script = f'''
            tell application "Calendar"
                tell calendar "{self.calendar_name}"
                    set targetEvent to first event whose summary is "{original_title}"
                    if targetEvent exists then
                        return "found"
                    else
                        return "not found"
                    end if
                end tell
            end tell
            '''
            
            result = self._run_applescript(script)
            if result != "found":
                return {
                    "success": False,
                    "message": f"'{original_title}' 일정을 찾을 수 없습니다."
                }
            
            # 수정 스크립트 생성
            update_commands = []
            
            if new_title:
                update_commands.append(f'set summary of targetEvent to "{new_title}"')
            
            if new_date_str or new_time_str:
                if new_date_str and new_time_str:
                    full_date_str = f"{new_date_str} {new_time_str}"
                elif new_date_str:
                    full_date_str = new_date_str
                else:
                    # 시간만 변경하는 경우는 복잡하므로 현재는 지원하지 않음
                    return {
                        "success": False,
                        "message": "시간만 변경하는 기능은 아직 지원되지 않습니다."
                    }
                
                new_start_dt = self._parse_korean_date(full_date_str)
                # 기존 일정의 지속시간을 유지한다고 가정 (1시간)
                new_end_dt = new_start_dt + timedelta(minutes=DEFAULT_EVENT_DURATION)
                
                start_date_str = self._format_applescript_date(new_start_dt)
                end_date_str = self._format_applescript_date(new_end_dt)
                
                update_commands.append(f'set start date of targetEvent to date "{start_date_str}"')
                update_commands.append(f'set end date of targetEvent to date "{end_date_str}"')
            
            if not update_commands:
                return {
                    "success": False,
                    "message": "수정할 내용이 없습니다."
                }
            
            script = f'''
            tell application "Calendar"
                tell calendar "{self.calendar_name}"
                    set targetEvent to first event whose summary is "{original_title}"
                    {chr(10).join(update_commands)}
                end tell
            end tell
            '''
            
            self._run_applescript(script)
            
            return {
                "success": True,
                "message": f"'{original_title}' 일정이 수정되었습니다."
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"일정 수정 실패: {str(e)}",
                "error": str(e)
            }
    
    def delete_event(self, title: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        """일정을 삭제합니다."""
        try:
            if date_str:
                # 특정 날짜의 일정 삭제
                target_date = self._parse_korean_date(date_str)
                start_of_day = target_date.replace(hour=0, minute=0, second=0)
                end_of_day = target_date.replace(hour=23, minute=59, second=59)
                
                start_date_str = self._format_applescript_date(start_of_day)
                end_date_str = self._format_applescript_date(end_of_day)
                
                script = f'''
                tell application "Calendar"
                    tell calendar "{self.calendar_name}"
                        set targetEvents to every event whose summary is "{title}" and start date ≥ date "{start_date_str}" and start date ≤ date "{end_date_str}"
                        if (count of targetEvents) > 0 then
                            delete first item of targetEvents
                            return "deleted"
                        else
                            return "not found"
                        end if
                    end tell
                end tell
                '''
            else:
                # 제목으로만 일정 삭제 (첫 번째 일치하는 일정)
                script = f'''
                tell application "Calendar"
                    tell calendar "{self.calendar_name}"
                        set targetEvent to first event whose summary is "{title}"
                        if targetEvent exists then
                            delete targetEvent
                            return "deleted"
                        else
                            return "not found"
                        end if
                    end tell
                end tell
                '''
            
            result = self._run_applescript(script)
            
            if result == "deleted":
                return {
                    "success": True,
                    "message": f"'{title}' 일정이 삭제되었습니다."
                }
            else:
                return {
                    "success": False,
                    "message": f"'{title}' 일정을 찾을 수 없습니다."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"일정 삭제 실패: {str(e)}",
                "error": str(e)
            } 