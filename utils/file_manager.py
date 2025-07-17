import os
import shutil
from datetime import datetime
from typing import List, Dict, Tuple

class FileManager:
    def __init__(self, save_dir: str = "saved_reports"):
        self.save_dir = save_dir
        self._ensure_directory()
    
    def _ensure_directory(self):
        """저장 디렉토리가 존재하는지 확인하고 없으면 생성합니다."""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_json_report(self, contract_address: str, analysis_result: Dict) -> str:
        """JSON 분석 결과를 저장합니다."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_{contract_address}_{timestamp}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        print(f"JSON 파일 저장 중: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            import json
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print(f"JSON 파일 저장 완료: {filename}")
        return filename
    
    def save_pdf_report(self, contract_address: str, pdf_bytes: bytes) -> str:
        """PDF 보고서를 저장합니다."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"security_report_{contract_address}_{timestamp}.pdf"
        filepath = os.path.join(self.save_dir, filename)
        
        print(f"PDF 파일 저장 중: {filepath}")
        
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"PDF 파일 저장 완료: {filename}")
        return filename
    
    def get_saved_files(self) -> List[Dict]:
        """저장된 파일 목록을 반환합니다."""
        files = []
        if os.path.exists(self.save_dir):
            for filename in os.listdir(self.save_dir):
                if filename.endswith(('.json', '.pdf')):
                    filepath = os.path.join(self.save_dir, filename)
                    file_stat = os.stat(filepath)
                    
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_stat.st_size,
                        'modified': datetime.fromtimestamp(file_stat.st_mtime),
                        'type': 'JSON' if filename.endswith('.json') else 'PDF'
                    })
        
        # 수정일 기준으로 정렬 (최신순)
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def delete_file(self, filename: str) -> bool:
        """파일을 삭제합니다."""
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def get_file_content(self, filename: str) -> bytes:
        """파일 내용을 반환합니다."""
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'rb') as f:
            return f.read()
    
    def get_file_info(self, filename: str) -> Dict:
        """파일 정보를 반환합니다."""
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            file_stat = os.stat(filepath)
            return {
                'filename': filename,
                'size': file_stat.st_size,
                'modified': datetime.fromtimestamp(file_stat.st_mtime),
                'type': 'JSON' if filename.endswith('.json') else 'PDF'
            }
        return {}
    
    def clear_old_files(self, days: int = 30) -> int:
        """지정된 일수보다 오래된 파일들을 삭제합니다."""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_info in self.get_saved_files():
            if file_info['modified'].timestamp() < cutoff_date:
                if self.delete_file(file_info['filename']):
                    deleted_count += 1
        
        return deleted_count
    
    def get_storage_info(self) -> Dict:
        """저장소 정보를 반환합니다."""
        files = self.get_saved_files()
        total_size = sum(f['size'] for f in files)
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'json_files': len([f for f in files if f['type'] == 'JSON']),
            'pdf_files': len([f for f in files if f['type'] == 'PDF'])
        } 