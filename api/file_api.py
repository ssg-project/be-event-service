#storage-server/api/file_api.py
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile
from sqlalchemy.orm import Session
from services.file_service import FileService
from dto.dto import *
from utils.database import get_db
import asyncio

router = APIRouter(prefix='/file', tags=['file'])

@router.post('/upload', description='파일 업로드')
async def upload_files(
    request: Request,
    files: List[UploadFile]=File(...),
    db: Session = Depends(get_db),
):
    file_service = FileService(db)

    try:
        file_list = []
                
        try:
            user_id = request.cookies.get('user_id')
            user_email = request.cookies.get('user_email')

            # S3 업로드 병렬 처리
            results = await asyncio.gather(
                *[file_service.upload_s3_file(
                    file_name=f"{user_email}/{file.filename}",
                    file_content=await file.read(),
                   ) for file in files],
                return_exceptions=True
            )
            
            # 성공한 파일만 필터링
            for result in results:
                if isinstance(result, dict):
                    file_list.append({
                        "user_id": user_id,
                        "file_key": result['file_name'],
                        "file_url": result["file_url"]
                    })
            
            # DB에 파일 정보 저장
            if file_list:
                file_service.insert_db_files(file_list)

            return

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")        
                                
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
        
@router.post('/delete', description='파일 삭제')
def delete_files(
    request: Request,
    request_body: FileDeleteRequest,
    db: Session = Depends(get_db),
):
    file_service = FileService(db)

    try:
        # db get files
        files = file_service.get_files_by_file_ids(
            user_id=request.cookies.get('user_id'),
            file_ids=request_body.file_ids,
        )
        file_names = [file['file_key'] for file in files]
       
        # db delete
        file_service.delete_db_files(file_ids=request_body.file_ids)

        # s3 file delete
        file_service.delete_s3_files(file_names=file_names)

        return    
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
    
@router.get('/list', response_model=GetFileListResponse, description='파일 리스트 조회')
def get_files(
    request: Request,
    db: Session = Depends(get_db),
):
    file_service = FileService(db)

    try:
        # db get files
        files = file_service.get_files(user_id=request.cookies.get('user_id'))
        return GetFileListResponse(data=files)
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.get('/download', description='파일 다운로드 링크 생성')
def get_presigned_url(
    file_key: str,
    request: Request,
    db: Session = Depends(get_db),
):
    file_service = FileService(db)

    try:
        # Presigned URL 생성
        presigned_url = file_service.generate_presigned_url(file_key=file_key)
        return {"url": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate download link: {str(e)}")