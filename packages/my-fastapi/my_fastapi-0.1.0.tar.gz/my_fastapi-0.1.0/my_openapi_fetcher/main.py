from fastapi import FastAPI
import uvicorn
import httpx
app = FastAPI()
import json
@app.get("/")
async def read_root():
    """
    8000번 포트에서 실행 중인 FastAPI 서버의 openapi.json을 가져옵니다.
    수정
    """
    target_url = "http://localhost:8000/openapi.json"
    openapi_data_from_8000 = None
    error_message = None

    try:
        # 비동기 HTTP 클라이언트 사용
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url)
            response.raise_for_status()  # 200 OK가 아니면 예외 발생
            openapi_data_from_8000 = response.json()
            print(f"성공적으로 8000번 포트에서 OpenAPI JSON을 가져왔습니다.")
            # 가져온 JSON 데이터를 콘솔에 출력 (디버깅용)
            # print(json.dumps(openapi_data_from_8000, indent=2, ensure_ascii=False))

    except httpx.RequestError as exc:
        error_message = f"8000번 포트 서버 연결 오류: {exc}"
        print(error_message)
    except json.JSONDecodeError:
        error_message = f"8000번 포트 서버 응답이 유효한 JSON이 아닙니다. URL: {target_url}"
        print(error_message)
    except Exception as exc:
        error_message = f"알 수 없는 오류 발생: {exc}"
        print(error_message)

    return {
        "message": "8001번 포트의 API입니다.",
        "fetched_openapi_from_8000": openapi_data_from_8000,
        "error_fetching_openapi": error_message
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
